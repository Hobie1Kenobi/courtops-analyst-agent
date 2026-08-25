"""Deterministic seed runner for Corpus Christi municipal shift simulation."""

import random
from datetime import date, datetime, timedelta

import yaml
from pathlib import Path
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.db.session import Base, SessionLocal, engine
from app.models import (
    Case, CaseStatus,
    ChangeRequest, ChangeRequestStatus,
    Device, DeviceStatus,
    Patch, PatchStatus, PatchType,
    Ticket, TicketCategory, TicketPriority, TicketStatus,
    User, UserRole,
    AuditEvent, AuditAction,
)
from app.connectors.public_data.corpus_christi_arcgis import fetch_service_categories, get_locations
from app.connectors.public_data.corpus_christi_311 import generate_synthetic_311_records

PROFILES_DIR = Path(__file__).resolve().parents[1] / "profiles"
SCENARIOS_DIR = Path(__file__).resolve().parents[1] / "scenarios"


def load_profile(name: str) -> dict:
    path = PROFILES_DIR / f"{name}.yaml"
    return yaml.safe_load(path.read_text())


def load_scenario(name: str) -> dict:
    path = SCENARIOS_DIR / f"{name}.yaml"
    return yaml.safe_load(path.read_text())


DEFENDANT_PATTERNS = [
    "Garcia", "Rodriguez", "Martinez", "Hernandez", "Lopez",
    "Gonzalez", "Perez", "Sanchez", "Ramirez", "Torres",
    "Rivera", "Smith", "Johnson", "Williams", "Brown",
    "Davis", "Miller", "Wilson", "Moore", "Taylor",
]


def run_seed(
    profile_name: str = "corpus_christi",
    scenario_name: str = "municipal_shift",
    seed: int = 20260225,
    sim_date: date | None = None,
    reset: bool = False,
) -> dict:
    profile = load_profile(profile_name)
    scenario = load_scenario(scenario_name)
    rng = random.Random(seed)
    ref_date = sim_date or date.today()

    if reset:
        Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        _create_users(db, profile)
        categories = fetch_service_categories()
        records_311 = generate_synthetic_311_records(rng, count=80, reference_date=ref_date)

        sd = scenario.get("seed_data", {})
        n_cases = sd.get("cases", 500)
        n_tickets = sd.get("tickets", 120)
        n_devices = sd.get("devices", 50)
        n_patches = sd.get("patches", 25)
        n_crs = sd.get("change_requests", 3)

        _create_cases(db, rng, profile, n_cases, ref_date)
        _create_tickets(db, rng, profile, n_tickets, ref_date)
        _create_devices(db, rng, profile, n_devices, ref_date)
        _create_patches(db, rng, n_patches, ref_date)
        _create_change_requests(db, rng, n_crs)
        _create_demo_guarantee(db, ref_date)
        _inject_audit_events(db, rng, ref_date)

        return {
            "profile": profile_name,
            "scenario": scenario_name,
            "seed": seed,
            "date": ref_date.isoformat(),
            "cases": n_cases,
            "tickets": n_tickets,
            "devices": n_devices,
            "patches": n_patches,
            "data_sources": ["corpus_christi_arcgis", "corpus_christi_311_synthetic", "corpus_christi_finance_metadata"],
        }
    finally:
        db.close()


def _create_users(db: Session, profile: dict):
    users = [
        ("supervisor", "Shift Supervisor", "supervisor@courtops.demo", UserRole.SUPERVISOR),
        ("analyst", "Court Analyst", "analyst@courtops.demo", UserRole.ANALYST),
        ("clerk", "Court Clerk", "clerk@courtops.demo", UserRole.CLERK),
        ("itsupport", "IT Support", "itsupport@courtops.demo", UserRole.IT_SUPPORT),
        ("readonly", "Read Only", "readonly@courtops.demo", UserRole.READ_ONLY),
    ]
    for username, full_name, email, role in users:
        if db.query(User).filter(User.username == username).first():
            continue
        db.add(User(
            username=username, full_name=full_name, email=email,
            role=role, hashed_password=get_password_hash("password"), is_active=True,
        ))
    db.commit()


def _create_cases(db: Session, rng: random.Random, profile: dict, count: int, ref_date: date):
    charges = profile.get("charge_types", {})
    traffic = charges.get("traffic", ["Speeding"])
    code_enf = charges.get("code_enforcement", ["Code Violation"])
    parking = charges.get("parking", ["Parking Violation"])
    all_charges = traffic + code_enf + parking
    judges = profile.get("judges", ["Judge Smith"])
    clerks = profile.get("clerks", ["Clerk A"])
    courtrooms = profile.get("courtrooms", ["A"])

    for i in range(count):
        days_ago = rng.randint(0, 180)
        filing = ref_date - timedelta(days=days_ago)
        status = rng.choice(list(CaseStatus))
        disposition = filing + timedelta(days=rng.randint(1, 90)) if status in {CaseStatus.DISPOSED, CaseStatus.DISMISSED, CaseStatus.PAID} else None
        charge = rng.choice(all_charges)
        prefix = "E" if charge in traffic else ("C" if charge in code_enf else "P")
        case_number = f"{prefix}{4000 + i:06d}"
        fine = rng.choice([100.0, 150.0, 195.0, 215.0, 250.0, 350.0, 500.0, 1500.0])
        paid = 0.0 if status in {CaseStatus.FTA, CaseStatus.WARRANT} else rng.choice([0.0, 50.0, 100.0, fine])
        defendant_last = rng.choice(DEFENDANT_PATTERNS)
        defendant = f"{defendant_last}, {chr(65 + (i % 26))}."

        db.add(Case(
            case_number=case_number, defendant_name=defendant, charge_type=charge,
            status=status, court="Corpus Christi Municipal Court",
            courtroom=rng.choice(courtrooms), clerk=rng.choice(clerks), judge=rng.choice(judges),
            filing_date=filing,
            hearing_date=filing + timedelta(days=rng.randint(7, 60)),
            disposition_date=disposition, fine_amount=fine, amount_paid=paid,
        ))

    for i, (citation, defendant, charge, fine, days_ago) in enumerate([
        ("E009901", "Rodriguez, J.", "Speeding > 20 mph", 350.00, 120),
        ("E009902", "Hernandez, T.", "No Proof of Insurance", 500.00, 117),
        ("E009903", "Garcia, M.", "Speeding > 10 mph", 215.00, 96),
        ("C002901", "Properties LLC", "City Ordinance Violation (Code Enforcement)", 1500.00, 160),
        ("E009904", "Smith, K.", "Expired Registration", 150.00, 95),
        ("E009905", "Davis, R.", "Running Red Light", 250.00, 100),
    ]):
        filing = ref_date - timedelta(days=days_ago + 30)
        hearing = ref_date - timedelta(days=days_ago)
        db.add(Case(
            case_number=citation, defendant_name=defendant, charge_type=charge,
            status=CaseStatus.FTA if i % 2 == 0 else CaseStatus.WARRANT,
            court="Corpus Christi Municipal Court", courtroom="A",
            clerk="Clerk Salazar", judge="Judge Hernandez",
            filing_date=filing, hearing_date=hearing,
            fine_amount=fine, amount_paid=0.0,
        ))
    db.commit()


def _create_tickets(db: Session, rng: random.Random, profile: dict, count: int, ref_date: date):
    users = db.query(User).all()
    if not users:
        return
    now = datetime.utcnow()
    for i in range(count):
        created = now - timedelta(hours=rng.randint(0, 180 * 24))
        requester = rng.choice(users)
        assignee = rng.choice(users)
        category = rng.choice(list(TicketCategory))
        priority = rng.choice(list(TicketPriority))
        status = rng.choice(list(TicketStatus))
        t = Ticket(
            title=f"{category.value.title()} issue {i}",
            description=f"Corpus Christi Municipal Court - {category.value} ticket {i}",
            category=category, priority=priority, status=status,
            requester_id=requester.id, assignee_id=assignee.id, created_at=created,
        )
        t.set_due_from_sla()
        if status in {TicketStatus.RESOLVED, TicketStatus.CLOSED}:
            t.resolved_at = created + timedelta(hours=rng.randint(1, 72))
        db.add(t)
    db.commit()


def _create_devices(db: Session, rng: random.Random, profile: dict, count: int, ref_date: date):
    locations = profile.get("device_locations", ["Office"])
    for i in range(count):
        warranty_end = ref_date + timedelta(days=rng.randint(-90, 365))
        last_patch = ref_date + timedelta(days=rng.randint(-120, 0))
        db.add(Device(
            asset_tag=f"CC-{1000 + i}",
            type=rng.choice(["Desktop", "Laptop", "Printer", "Scanner", "Kiosk"]),
            location=rng.choice(locations),
            assigned_user=rng.choice(["Clerk Salazar", "Clerk Kim", "Clerk Vasquez", "IT Support", "Front Desk"]),
            warranty_end=warranty_end, last_patch_date=last_patch,
            status=rng.choice(list(DeviceStatus)),
        ))
    db.commit()


def _create_patches(db: Session, rng: random.Random, count: int, ref_date: date):
    for i in range(count):
        requested = ref_date - timedelta(days=rng.randint(0, 120))
        status = rng.choice(list(PatchStatus))
        scheduled = requested + timedelta(days=rng.randint(1, 14))
        deployed = scheduled + timedelta(days=rng.randint(1, 14)) if status in {PatchStatus.DEPLOYED, PatchStatus.VERIFIED} else None
        verified = deployed + timedelta(days=3) if status == PatchStatus.VERIFIED and deployed else None
        db.add(Patch(
            title=f"CC Patch {i}", type=rng.choice(list(PatchType)),
            status=status, target_version=rng.choice(["v2.1.0", "v2.1.1", "v2.2.0"]),
            requested_date=requested, scheduled_date=scheduled,
            deployed_date=deployed, verified_date=verified,
            testing_notes="Checklist completed" if status in {PatchStatus.TESTED, PatchStatus.DEPLOYED, PatchStatus.VERIFIED} else None,
            change_log="Corpus Christi Municipal Court system update.",
        ))
    db.commit()


def _create_change_requests(db: Session, rng: random.Random, count: int):
    titles = [
        "Online payment workflow enhancement",
        "Docket scheduling notification improvement",
        "Compliance review reporting field addition",
    ]
    for i, title in enumerate(titles[:count]):
        db.add(ChangeRequest(
            title=title,
            requested_by=rng.choice(["Clerk Salazar", "Judge Hernandez", "Court Manager"]),
            current_process="Manual spreadsheet-based process.",
            proposed_change="Automate within CourtOps application.",
            impact_users="Clerks, supervisors, IT support.",
            impact_data="Case records, payment records.",
            impact_security="Requires role-based access and audit logging.",
            status=rng.choice(list(ChangeRequestStatus)),
        ))
    db.commit()


def _create_demo_guarantee(db: Session, ref_date: date):
    users = db.query(User).all()
    if not users:
        return
    user = users[0]
    now = datetime.utcnow()

    for title, desc in [
        ("CC Access - password reset needed", "Court clerk password reset requested"),
        ("CC Access - RBAC check", "New hire role assignment for case entry"),
        ("CC Access - login lockout", "Account locked after failed attempts"),
        ("CC Access - VPN request", "Remote access request for court system"),
        ("CC Access - shared drive", "Read access to reports shared drive"),
    ]:
        if db.query(Ticket).filter(Ticket.title == title).first():
            continue
        t = Ticket(
            title=title, description=desc,
            category=TicketCategory.ACCESS, priority=TicketPriority.HIGH,
            status=TicketStatus.OPEN, requester_id=user.id, assignee_id=user.id,
            created_at=now - timedelta(days=1),
        )
        t.set_due_from_sla()
        db.add(t)

    for i in range(2):
        title = f"CC Overdue ticket {i+1}"
        if db.query(Ticket).filter(Ticket.title == title).first():
            continue
        t = Ticket(
            title=title, description="Overdue ticket for SLA sweep demo.",
            category=TicketCategory.APPLICATION, priority=TicketPriority.HIGH,
            status=TicketStatus.OPEN, requester_id=user.id, assignee_id=user.id,
            created_at=now - timedelta(days=5),
        )
        t.set_due_from_sla()
        db.add(t)

    for tag, loc in [("CC-DEMO-1", "Courtroom A"), ("CC-DEMO-2", "Records Room"), ("CC-DEMO-3", "Front Desk Kiosk")]:
        if db.query(Device).filter(Device.asset_tag == tag).first():
            continue
        db.add(Device(
            asset_tag=tag, type="Desktop", location=loc,
            assigned_user="Clerk Salazar",
            warranty_end=ref_date + timedelta(days=14),
            last_patch_date=ref_date - timedelta(days=100),
            status=DeviceStatus.IN_SERVICE,
        ))
    db.commit()


def _inject_audit_events(db: Session, rng: random.Random, ref_date: date):
    users = db.query(User).all()
    if not users:
        return
    readonly_user = next((u for u in users if u.role == UserRole.READ_ONLY), users[-1])
    clerk_user = next((u for u in users if u.role == UserRole.CLERK), users[0])

    db.add(AuditEvent(
        user_id=clerk_user.id, action=AuditAction.REPORT_EXPORT,
        entity_type="report", entity_id="monthly_ops",
        event_metadata='{"time": "23:45", "type": "after_hours_export"}',
        created_at=datetime.combine(ref_date, datetime.min.time().replace(hour=23, minute=45)),
    ))
    db.add(AuditEvent(
        user_id=readonly_user.id, action=AuditAction.RECORD_EDIT,
        entity_type="case", entity_id="attempted_edit",
        event_metadata='{"type": "role_mismatch", "attempted_action": "case_edit"}',
        created_at=datetime.combine(ref_date, datetime.min.time().replace(hour=9, minute=15)),
    ))
    for i in range(6):
        db.add(AuditEvent(
            user_id=rng.choice(users).id, action=AuditAction.LOGIN_FAILURE,
            event_metadata=f'{{"attempt": {i+1}, "type": "suspicious_burst"}}',
            created_at=datetime.combine(ref_date, datetime.min.time().replace(hour=8, minute=30 + i)),
        ))
    db.commit()


if __name__ == "__main__":
    import sys
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 20260225
    result = run_seed(seed=seed, reset="--reset" in sys.argv)
    print(f"Seed complete: {result}")

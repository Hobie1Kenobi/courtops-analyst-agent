import random
from datetime import date, datetime, timedelta

from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.db.session import Base, SessionLocal, engine
from app.models import (
    Case,
    CaseStatus,
    ChangeRequest,
    ChangeRequestStatus,
    Device,
    DeviceStatus,
    Patch,
    PatchStatus,
    PatchType,
    Ticket,
    TicketCategory,
    TicketPriority,
    TicketStatus,
    User,
    UserRole,
)


def create_users(db: Session) -> None:
    users = [
        ("supervisor", "Supervisor User", "supervisor@example.org", UserRole.SUPERVISOR),
        ("analyst", "Court Analyst", "analyst@example.org", UserRole.ANALYST),
        ("clerk", "Court Clerk", "clerk@example.org", UserRole.CLERK),
        ("itsupport", "IT Support", "itsupport@example.org", UserRole.IT_SUPPORT),
        ("readonly", "Read Only", "readonly@example.org", UserRole.READ_ONLY),
    ]
    for username, full_name, email, role in users:
        if db.query(User).filter(User.username == username).first():
            continue
        user = User(
            username=username,
            full_name=full_name,
            email=email,
            role=role,
            hashed_password=get_password_hash("password"),
            is_active=True,
        )
        db.add(user)
    db.commit()


DEFENDANT_LAST_NAMES = [
    "Rodriguez", "Smith", "Nguyen", "Davis", "Garcia", "Martinez", "Johnson", "Williams",
    "Brown", "Jones", "Miller", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor",
]

TRAFFIC_CHARGES = ["Speeding > 15mph", "Speeding > 10mph", "Exp. Registration", "No Insurance"]
CODE_CHARGES = ["City Ordinance (Code Enforcement)"]
OTHER_CHARGES = ["Parking"]


def create_cases(db: Session, months: int = 6) -> None:
    today = date.today()
    all_charges = TRAFFIC_CHARGES + CODE_CHARGES + OTHER_CHARGES
    traffic_range = (0, len(TRAFFIC_CHARGES) - 1)
    code_range = (len(TRAFFIC_CHARGES), len(TRAFFIC_CHARGES) + len(CODE_CHARGES) - 1)
    for i in range(600):
        days_ago = random.randint(0, months * 30)
        filing_date = today - timedelta(days=days_ago)
        status = random.choice(list(CaseStatus))
        disposition_date = None
        if status in {CaseStatus.DISPOSED, CaseStatus.DISMISSED, CaseStatus.PAID}:
            disposition_date = filing_date + timedelta(days=random.randint(1, 90))

        charge_idx = random.randint(0, len(all_charges) - 1)
        charge_type = all_charges[charge_idx]
        if charge_idx <= traffic_range[1]:
            citation_prefix = "E"
            citation_num = 4592 + i
        elif charge_idx <= code_range[1]:
            citation_prefix = "C"
            citation_num = 1124 + i
        else:
            citation_prefix = "P"
            citation_num = 2000 + i
        case_number = f"{citation_prefix}{citation_num:06d}"

        hearing_date = filing_date + timedelta(days=random.randint(7, 60))
        if status in {CaseStatus.FTA, CaseStatus.WARRANT} and i % 12 == 0:
            hearing_date = today - timedelta(days=random.randint(90, 180))

        fine_amount = random.choice([100.0, 150.0, 195.0, 215.0, 220.0, 250.0, 350.0, 1500.0])
        amount_paid = 0.0 if status in {CaseStatus.FTA, CaseStatus.WARRANT} else random.choice([0.0, 50.0, 100.0, 150.0, 250.0, 300.0, fine_amount])

        defendant = random.choice(DEFENDANT_LAST_NAMES)
        if charge_type == "City Ordinance (Code Enforcement)":
            defendant = f"{defendant} LLC" if random.random() > 0.5 else defendant
        defendant_name = f"{defendant}, {chr(65 + (i % 26))}."

        case = Case(
            case_number=case_number,
            defendant_name=defendant_name,
            charge_type=charge_type,
            status=status,
            court="Municipal Court",
            courtroom=random.choice(["101", "102", "201"]),
            clerk=random.choice(["Clerk A", "Clerk B", "Clerk C"]),
            judge=random.choice(["Judge Smith", "Judge Garcia", "Judge Lee"]),
            filing_date=filing_date,
            hearing_date=hearing_date,
            disposition_date=disposition_date,
            fine_amount=fine_amount,
            amount_paid=amount_paid,
        )
        db.add(case)

    fta_seed = [
        ("E009901", "Rodriguez, J.", "Speeding > 15mph", 215.00, 120),
        ("E009902", "Nguyen, T.", "No Insurance", 350.00, 117),
        ("E009903", "Garcia, M.", "Speeding > 10mph", 220.00, 96),
        ("C002901", "Properties LLC", "City Ordinance (Code Enforcement)", 1500.00, 160),
        ("E009904", "Smith, K.", "Exp. Registration", 150.00, 95),
        ("E009905", "Davis, R.", "Speeding > 10mph", 195.00, 100),
    ]
    for i, (citation, defendant, charge, fine, days_ago) in enumerate(fta_seed):
        filing_date = today - timedelta(days=days_ago + 30)
        hearing_date = today - timedelta(days=days_ago)
        case = Case(
            case_number=citation,
            defendant_name=defendant,
            charge_type=charge,
            status=CaseStatus.FTA if i % 2 == 0 else CaseStatus.WARRANT,
            court="Municipal Court",
            courtroom="101",
            clerk="Clerk A",
            judge="Judge Smith",
            filing_date=filing_date,
            hearing_date=hearing_date,
            disposition_date=None,
            fine_amount=fine,
            amount_paid=0.0,
        )
        db.add(case)
    db.commit()


def create_tickets(db: Session, months: int = 6) -> None:
    users = db.query(User).all()
    if not users:
        return
    today = datetime.utcnow()
    for i in range(150):
        created_at = today - timedelta(hours=random.randint(0, months * 30 * 24))
        requester = random.choice(users)
        assignee = random.choice(users)
        category = random.choice(list(TicketCategory))
        priority = random.choice(list(TicketPriority))
        status = random.choice(list(TicketStatus))

        ticket = Ticket(
            title=f"{category.value.title()} issue {i}",
            description=f"Simulated {category.value} ticket {i}",
            category=category,
            priority=priority,
            status=status,
            requester_id=requester.id,
            assignee_id=assignee.id,
            created_at=created_at,
        )
        ticket.set_due_from_sla()
        if status in {TicketStatus.RESOLVED, TicketStatus.CLOSED}:
            ticket.resolved_at = created_at + timedelta(hours=random.randint(1, 72))
        db.add(ticket)
    db.commit()


def create_devices(db: Session) -> None:
    for i in range(60):
        warranty_end = date.today() + timedelta(days=random.randint(-180, 365))
        last_patch = date.today() + timedelta(days=random.randint(-120, 0))
        device = Device(
            asset_tag=f"MC-{1000 + i}",
            type=random.choice(["Desktop", "Laptop", "Printer", "Scanner"]),
            location=random.choice(["Clerk Office", "Courtroom 101", "Courtroom 201", "Records"]),
            assigned_user=random.choice(["Clerk A", "Clerk B", "Analyst", "IT Support"]),
            warranty_end=warranty_end,
            last_patch_date=last_patch,
            status=random.choice(list(DeviceStatus)),
        )
        db.add(device)
    db.commit()


def create_patches(db: Session) -> None:
    for i in range(30):
        requested = date.today() - timedelta(days=random.randint(0, 120))
        status = random.choice(list(PatchStatus))
        scheduled = requested + timedelta(days=random.randint(1, 14))
        deployed = scheduled + timedelta(days=random.randint(1, 14)) if status in {PatchStatus.DEPLOYED, PatchStatus.VERIFIED} else None
        verified = deployed + timedelta(days=3) if status == PatchStatus.VERIFIED and deployed else None
        patch = Patch(
            title=f"Patch {i}",
            type=random.choice(list(PatchType)),
            status=status,
            target_version=random.choice(["v1.0.1", "v1.0.2", "v1.1.0"]),
            device_asset_tag=None,
            requested_date=requested,
            scheduled_date=scheduled,
            deployed_date=deployed,
            verified_date=verified,
            testing_notes="Checklist completed" if status in {PatchStatus.TESTED, PatchStatus.DEPLOYED, PatchStatus.VERIFIED} else None,
            change_log="Auto-generated from demo seed.",
        )
        db.add(patch)
    db.commit()


def create_change_requests(db: Session) -> None:
    titles = [
        "Online payment workflow enhancement",
        "Improve docket scheduling notifications",
        "Add reporting field for compliance review",
    ]
    for i, title in enumerate(titles):
        cr = ChangeRequest(
            title=title,
            requested_by=random.choice(["Clerk A", "Judge Garcia", "Court Manager"]),
            current_process="Current process is documented as manual steps across spreadsheets.",
            proposed_change="Automate the workflow within the CourtOps application.",
            impact_users="Clerks, supervisors, and IT support.",
            impact_data="Case records, payment records, scheduling data.",
            impact_security="Requires role-based restrictions and audit logging.",
            status=random.choice(list(ChangeRequestStatus)),
        )
        db.add(cr)
    db.commit()


def main() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        create_users(db)
        create_cases(db)
        create_tickets(db)
        create_devices(db)
        create_patches(db)
        create_change_requests(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()


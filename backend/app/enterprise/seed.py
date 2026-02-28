"""Seed realistic synthetic data for all 3 enterprise systems.

Shaped by public information about Corpus Christi municipal operations.
All records are synthetic — no real data.
"""

import random
from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session
from app.db.session import SessionLocal, Base, engine
from app.enterprise.models import *

DEFENDANT_NAMES = [
    ("Garcia", "Maria"), ("Rodriguez", "Carlos"), ("Martinez", "Ana"),
    ("Hernandez", "Jose"), ("Lopez", "Rosa"), ("Gonzalez", "David"),
    ("Perez", "Elena"), ("Sanchez", "Miguel"), ("Torres", "Sofia"),
    ("Rivera", "Luis"), ("Smith", "James"), ("Johnson", "Robert"),
    ("Williams", "Patricia"), ("Brown", "Michael"), ("Davis", "Linda"),
    ("Miller", "Thomas"), ("Wilson", "Jennifer"), ("Moore", "William"),
]

CC_LOCATIONS = [
    ("CITY-HALL", "City Hall", "1201 Leopard St"),
    ("MUNI-COURT", "Municipal Court", "321 John Sartain St"),
    ("WATER-MAIN", "Water Treatment Plant - Main", "1402 Greenwood Dr"),
    ("WATER-SOUTH", "South Side Pump Station", "5700 S Padre Island Dr"),
    ("FLEET-YARD", "Fleet Maintenance Yard", "5352 Ayers St"),
    ("PARKS-HQ", "Parks & Recreation HQ", "1581 N Chaparral St"),
    ("FIRE-STA1", "Fire Station #1 - Downtown", "301 N Chaparral St"),
    ("POLICE-HQ", "Police HQ - CCPD", "321 John Sartain St"),
    ("LIBRARY-MAIN", "La Retama Central Library", "805 Comanche St"),
    ("ANIMAL-CTRL", "Animal Care Services", "2626 Holly Rd"),
]

CC_ASSETS = [
    ("FL-1001", "2019 Ford F-150 Fleet Truck", "VEHICLE", "FLEET-YARD"),
    ("FL-1002", "2020 Chevy Tahoe (CCPD)", "VEHICLE", "POLICE-HQ"),
    ("FL-1003", "2018 International Dump Truck", "VEHICLE", "FLEET-YARD"),
    ("FL-1004", "2021 Ford Transit Van", "VEHICLE", "PARKS-HQ"),
    ("FL-1005", "2017 Freightliner Refuse Truck", "VEHICLE", "FLEET-YARD"),
    ("WP-2001", "Influent Pump #1 - Main Plant", "PUMP", "WATER-MAIN"),
    ("WP-2002", "Effluent Pump #3 - Main Plant", "PUMP", "WATER-MAIN"),
    ("WP-2003", "Booster Pump - South Station", "PUMP", "WATER-SOUTH"),
    ("WP-2004", "Chemical Dosing Pump - Chlorine", "PUMP", "WATER-MAIN"),
    ("HV-3001", "HVAC Unit - City Hall 3rd Floor", "HVAC", "CITY-HALL"),
    ("HV-3002", "HVAC Unit - Court Building", "HVAC", "MUNI-COURT"),
    ("HV-3003", "HVAC Unit - Library Main", "HVAC", "LIBRARY-MAIN"),
    ("GN-4001", "Emergency Generator - City Hall", "GENERATOR", "CITY-HALL"),
    ("GN-4002", "Emergency Generator - Water Main", "GENERATOR", "WATER-MAIN"),
    ("GN-4003", "Emergency Generator - Fire Sta 1", "GENERATOR", "FIRE-STA1"),
    ("IT-5001", "Server Rack A - City Hall DC", "IT_EQUIPMENT", "CITY-HALL"),
    ("IT-5002", "UPS System - Court Building", "IT_EQUIPMENT", "MUNI-COURT"),
    ("IT-5003", "Network Switch - Police HQ", "IT_EQUIPMENT", "POLICE-HQ"),
]

CIP_PROJECTS = [
    ("CIP-2024-001", "Oso Creek Water Reclamation Facility Upgrade", "CONSTRUCTION", "Water Utilities", 45000000.0, "2019 Bond"),
    ("CIP-2024-002", "Staples Street Corridor Improvement", "CONSTRUCTION", "Engineering", 12500000.0, "2019 Bond"),
    ("CIP-2024-003", "Greenwood Wastewater Line Replacement", "DESIGN", "Water Utilities", 8700000.0, "2019 Bond"),
    ("CIP-2024-004", "Padre Island Seawall Repair Phase II", "BIDDING", "Engineering", 6200000.0, "Federal Grant"),
    ("CIP-2024-005", "City Hall ADA Compliance Renovation", "CONSTRUCTION", "Facilities", 2100000.0, "General Fund"),
    ("CIP-2024-006", "Southside Library Branch Construction", "PLANNING", "Library", 4500000.0, "2019 Bond"),
    ("CIP-2024-007", "Police Evidence Storage Expansion", "DESIGN", "Police", 1800000.0, "General Fund"),
    ("CIP-2024-008", "Leopard Street Drainage Improvement", "CONSTRUCTION", "Storm Water", 9300000.0, "2019 Bond"),
]


def seed_enterprise(seed: int = 20260225):
    rng = random.Random(seed)
    ref = date.today()

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        _seed_maximo(db, rng, ref)
        _seed_incode(db, rng, ref)
        _seed_ebuilder(db, rng, ref)
        return {"status": "ok", "maximo": "locations+assets+WOs+PMs+SRs+crons+messages", "incode": "defendants+citations+cases+payments+warrants+dockets", "ebuilder": "projects+costs+docs+RFIs+COs"}
    finally:
        db.close()


def _seed_maximo(db: Session, rng: random.Random, ref: date):
    for loc_id, desc, addr in CC_LOCATIONS:
        if not db.query(MaximoLocation).filter(MaximoLocation.location == loc_id).first():
            db.add(MaximoLocation(location=loc_id, description=desc, streetaddress=addr, type="OPERATING"))

    for asset_id, desc, atype, loc in CC_ASSETS:
        if not db.query(MaximoAsset).filter(MaximoAsset.assetnum == asset_id).first():
            db.add(MaximoAsset(
                assetnum=asset_id, description=desc, assettype=atype, location=loc,
                purchaseprice=rng.uniform(5000, 250000),
                installdate=ref - timedelta(days=rng.randint(365, 2000)),
                warrantyexpdate=ref + timedelta(days=rng.randint(-180, 365)),
                ytdcost=rng.uniform(500, 25000),
            ))

    for i in range(40):
        wonum = f"WO-{100000 + i}"
        if db.query(MaximoWorkOrder).filter(MaximoWorkOrder.wonum == wonum).first():
            continue
        asset = rng.choice(CC_ASSETS)
        status = rng.choice(list(MaximoWOStatus))
        db.add(MaximoWorkOrder(
            wonum=wonum,
            description=f"{'PM' if i % 3 == 0 else 'CM'} - {asset[1][:50]}",
            status=status,
            worktype="PM" if i % 3 == 0 else "CM",
            assetnum=asset[0], location=asset[3],
            priority=rng.choice([1, 2, 3, 4, 5]),
            reportdate=datetime.combine(ref - timedelta(days=rng.randint(0, 90)), datetime.min.time()),
            pmnum=f"PM-{1000 + i}" if i % 3 == 0 else None,
            estdur=rng.uniform(1, 16),
            actlabhrs=rng.uniform(0, 12) if status in {MaximoWOStatus.COMP, MaximoWOStatus.CLOSE} else 0,
            actmatcost=rng.uniform(0, 5000) if status in {MaximoWOStatus.COMP, MaximoWOStatus.CLOSE} else 0,
            reportedby="SYSTEM" if i % 3 == 0 else rng.choice(["JSMITH", "MGARCIA", "RJOHNSON"]),
        ))

    for i in range(14):
        pmnum = f"PM-{1000 + i}"
        if db.query(MaximoPM).filter(MaximoPM.pmnum == pmnum).first():
            continue
        asset = CC_ASSETS[i % len(CC_ASSETS)]
        db.add(MaximoPM(
            pmnum=pmnum, description=f"Preventive Maintenance - {asset[1][:40]}",
            status=MaximoPMStatus.ACTIVE if i < 10 else MaximoPMStatus.INACTIVE,
            assetnum=asset[0], location=asset[3],
            frequency=rng.choice([7, 14, 30, 90, 180, 365]),
            frequnit="DAYS",
            nextdate=ref + timedelta(days=rng.randint(-30, 60)),
            lastcompdate=ref - timedelta(days=rng.randint(1, 180)),
            priority=rng.choice([1, 2, 3]),
        ))

    for name, desc, active, last in [
        ("PMWOGEN", "PM Work Order Generation", True, ref - timedelta(hours=rng.randint(1, 48))),
        ("REORDERCRON", "Inventory Reorder Point Check", True, ref - timedelta(hours=rng.randint(1, 24))),
        ("ESCALATION", "Work Order Escalation", True, ref - timedelta(hours=rng.randint(1, 12))),
        ("JABORECALC", "JA BO Record Recalculation", False, ref - timedelta(days=30)),
    ]:
        if not db.query(MaximoCronTask).filter(MaximoCronTask.crontaskname == name).first():
            db.add(MaximoCronTask(
                crontaskname=name, description=desc, active=active,
                schedule="1h" if active else None,
                lastrun=datetime.combine(last, datetime.min.time()),
                nextrun=datetime.combine(last + timedelta(hours=1), datetime.min.time()) if active else None,
            ))

    for i in range(5):
        db.add(MaximoIntMessage(
            extsysname="ABORFINANCE", ifacename="MXGLINTERFACE",
            messagetype="Publish",
            status="ERROR" if i < 3 else "PROCESSED",
            msgerror=f"BMXAA4211E - Connection refused: Finance GL endpoint unreachable" if i < 3 else None,
            msgdata=f'{{"wonum": "WO-{100000+i}", "glaccount": "501-6110-{i}00"}}',
        ))
    db.commit()


def _seed_incode(db: Session, rng: random.Random, ref: date):
    for i, (last, first) in enumerate(DEFENDANT_NAMES):
        did = 5000 + i
        if db.query(IncodeDefendant).filter(IncodeDefendant.defendant_id == did).first():
            continue
        db.add(IncodeDefendant(
            defendant_id=did, last_name=last, first_name=first,
            date_of_birth=date(rng.randint(1965, 2000), rng.randint(1, 12), rng.randint(1, 28)),
            dl_state="TX", city="Corpus Christi", state="TX",
        ))

    violations = [
        ("SPD10", "Speeding 10+ MPH Over Limit", 195.0),
        ("SPD20", "Speeding 20+ MPH Over Limit", 280.0),
        ("EXPREG", "Expired Registration", 150.0),
        ("NOINS", "No Proof of Insurance", 350.0),
        ("REDLT", "Running Red Light", 250.0),
        ("STPSN", "Failure to Stop at Stop Sign", 200.0),
        ("PRKVL", "Parking Violation", 75.0),
        ("CODVL", "City Ordinance Violation", 500.0),
    ]

    for i in range(120):
        cnum = f"CIT-{ref.year}-{10000 + i}"
        if db.query(IncodeCitation).filter(IncodeCitation.citation_number == cnum).first():
            continue
        viol = rng.choice(violations)
        did = 5000 + rng.randint(0, len(DEFENDANT_NAMES) - 1)
        vdate = ref - timedelta(days=rng.randint(0, 180))
        imp_status = "IMPORTED" if i < 115 else "ERROR"
        db.add(IncodeCitation(
            citation_number=cnum, violation_code=viol[0], violation_desc=viol[1],
            defendant_id=did, officer_id=f"OFC-{rng.randint(100,500)}",
            officer_name=rng.choice(["Ofc. Ramirez", "Ofc. Thompson", "Ofc. Nguyen", "Ofc. Davis"]),
            violation_date=vdate, violation_location=rng.choice(["SPID & Staples", "Leopard & Port", "Ayers & Holly", "Crosstown & Agnes"]),
            vehicle_plate=f"{rng.choice('ABCDEFGHJKLMNPRSTUVWXYZ')}{rng.choice('ABCDEFGHJKLMNPRSTUVWXYZ')}{rng.choice('ABCDEFGHJKLMNPRSTUVWXYZ')}-{rng.randint(1000,9999)}",
            vehicle_state="TX",
            import_status=imp_status,
            import_batch=f"BATCH-{vdate.strftime('%Y%m%d')}",
            import_error="XML Parse Error: Unexpected element 'VehicleMake2' at line 89" if imp_status == "ERROR" else None,
        ))

    judges = [("JDG-001", "Judge Hernandez"), ("JDG-002", "Judge Mitchell"), ("JDG-003", "Judge Trevino")]
    for i in range(100):
        casenum = f"MC-{ref.year}-{20000 + i}"
        if db.query(IncodeCaseRecord).filter(IncodeCaseRecord.case_number == casenum).first():
            continue
        viol = rng.choice(violations)
        did = 5000 + rng.randint(0, len(DEFENDANT_NAMES) - 1)
        status = rng.choice(list(IncodeCaseStatus))
        fine = viol[2]
        costs = rng.choice([45.0, 55.0, 65.0])
        total = fine + costs
        paid = total if status in {IncodeCaseStatus.PAID, IncodeCaseStatus.DISPOSED} else rng.choice([0.0, 50.0, 100.0])
        judge = rng.choice(judges)
        db.add(IncodeCaseRecord(
            case_number=casenum, citation_number=f"CIT-{ref.year}-{10000 + i}",
            defendant_id=did, status=status,
            violation_code=viol[0], violation_desc=viol[1],
            court_date=ref + timedelta(days=rng.randint(-60, 30)),
            courtroom=rng.choice(["A", "B", "C"]),
            judge_id=judge[0], judge_name=judge[1],
            fine_amount=fine, court_costs=costs,
            total_due=total, total_paid=paid, balance_due=total - paid,
            filing_date=ref - timedelta(days=rng.randint(0, 180)),
            warrant_issued=status in {IncodeCaseStatus.WARRANT, IncodeCaseStatus.FTA},
        ))

    for i in range(200):
        db.add(IncodePayment(
            case_number=f"MC-{ref.year}-{20000 + rng.randint(0, 99)}",
            defendant_id=5000 + rng.randint(0, len(DEFENDANT_NAMES) - 1),
            amount=rng.choice([50.0, 75.0, 100.0, 150.0, 195.0, 250.0, 280.0, 350.0]),
            payment_method=rng.choice(["CASH", "CHECK", "CREDIT", "ONLINE"]),
            payment_source=rng.choice(["WINDOW", "ONLINE", "MAIL"]),
            receipt_number=f"RCP-{300000 + i}",
            payment_date=datetime.combine(ref - timedelta(days=rng.randint(0, 90)), datetime.min.time()),
            posted=True if i < 195 else False,
            gl_account=f"410-{rng.choice(['4110', '4120', '4130'])}",
            batch_id=f"PAY-{(ref - timedelta(days=rng.randint(0, 30))).strftime('%Y%m%d')}",
            gateway_txn_id=f"GW-{rng.randint(100000, 999999)}" if rng.random() > 0.5 else None,
            reconciled=True if i < 180 else False,
        ))

    for i in range(3):
        ddate = ref + timedelta(days=7 * (i + 1))
        judge = judges[i % 3]
        db.add(IncodeDocket(
            docket_date=ddate, courtroom=["A", "B", "C"][i],
            judge_id=judge[0], judge_name=judge[1],
            case_count=rng.randint(20, 50),
            status="DRAFT" if i == 2 else "FINAL",
        ))
    db.commit()


def _seed_ebuilder(db: Session, rng: random.Random, ref: date):
    for pid, name, status_str, dept, budget, fund in CIP_PROJECTS:
        if db.query(EBuilderProject).filter(EBuilderProject.project_id == pid).first():
            continue
        status = EBuilderProjectStatus(status_str)
        pct = {"PLANNING": 5, "DESIGN": 25, "BIDDING": 40, "CONSTRUCTION": 65, "CLOSEOUT": 95, "COMPLETE": 100, "ON HOLD": 30}
        actual = budget * (pct.get(status_str, 50) / 100) * rng.uniform(0.85, 1.15)
        committed = actual * rng.uniform(1.0, 1.2)
        db.add(EBuilderProject(
            project_id=pid, project_name=name, status=status,
            department=dept, fund_source=fund,
            project_manager=rng.choice(["J. Salazar", "M. Patel", "R. Thompson", "A. Nguyen"]),
            contractor=rng.choice(["Bay Ltd.", "Haas Anderson", "SpawGlass", "Flatiron", "Granite Construction"]) if status_str not in ("PLANNING", "DESIGN") else None,
            budget_total=budget, committed_cost=round(committed, 2),
            actual_cost=round(actual, 2), budget_remaining=round(budget - actual, 2),
            start_date=ref - timedelta(days=rng.randint(180, 900)),
            planned_end_date=ref + timedelta(days=rng.randint(90, 730)),
            percent_complete=pct.get(status_str, 50) + rng.uniform(-5, 5),
            schedule_variance_days=rng.randint(-30, 60),
            location_address=rng.choice(["Oso Creek & Staples", "Greenwood Dr", "Leopard St Corridor", "Padre Island", "Chaparral St"]),
        ))

    for pid, _, _, _, budget, _ in CIP_PROJECTS:
        for j in range(rng.randint(3, 8)):
            cat = rng.choice(["Design", "Construction", "Materials", "Labor", "Inspection", "Contingency"])
            budgeted = budget * rng.uniform(0.05, 0.3)
            actual = budgeted * rng.uniform(0.6, 1.2)
            db.add(EBuilderCostItem(
                project_id=pid, cost_code=f"{cat[:3].upper()}-{100+j}",
                description=f"{cat} - Phase {j+1}",
                category=cat, budgeted=round(budgeted, 2),
                committed=round(budgeted * rng.uniform(0.9, 1.1), 2),
                actual=round(actual, 2),
                variance=round(budgeted - actual, 2),
                vendor=rng.choice(["Bay Ltd.", "Haas Anderson", "SpawGlass", "Local Vendor A"]),
                posted_to_finance=rng.random() > 0.2,
            ))

    for pid, _, _, _, _, _ in CIP_PROJECTS[:5]:
        for j in range(rng.randint(2, 5)):
            sync_ok = rng.random() > 0.15
            db.add(EBuilderDocument(
                project_id=pid, doc_type=rng.choice(["SUBMITTAL", "DRAWING", "SPEC", "REPORT", "PERMIT"]),
                title=f"Document {j+1} - {pid}",
                filename=f"{pid}_doc_{j+1}.pdf",
                status="APPROVED" if sync_ok else "PENDING_REVIEW",
                uploaded_by=rng.choice(["J. Salazar", "Contractor Rep"]),
                sync_status="SYNCED" if sync_ok else "ERROR",
                sync_error="SharePoint API timeout — document not synced" if not sync_ok else None,
            ))

    for pid, _, _, _, _, _ in CIP_PROJECTS[:4]:
        for j in range(rng.randint(1, 4)):
            days_open = rng.randint(1, 45)
            status = "CLOSED" if days_open < 14 else ("OPEN" if days_open < 30 else "OVERDUE")
            db.add(EBuilderRFI(
                project_id=pid, rfi_number=f"RFI-{pid[-3:]}-{j+1:03d}",
                subject=rng.choice(["Foundation soil condition clarification", "Pipe material substitution request", "Electrical panel relocation", "ADA ramp grade specification"]),
                status=status, submitted_by="Contractor",
                assigned_to=rng.choice(["City Engineer", "Project Manager", "Inspector"]),
                submitted_date=ref - timedelta(days=days_open),
                due_date=ref - timedelta(days=days_open - 14),
                days_open=days_open,
                cost_impact=rng.random() > 0.7,
                schedule_impact=rng.random() > 0.8,
            ))

    for pid, _, _, _, _, _ in CIP_PROJECTS[:3]:
        for j in range(rng.randint(1, 3)):
            db.add(EBuilderChangeOrder(
                project_id=pid, co_number=f"CO-{pid[-3:]}-{j+1:02d}",
                description=rng.choice(["Unforeseen soil conditions", "Design revision per city request", "Material cost escalation", "Additional scope: utility relocation"]),
                status=rng.choice(["PENDING", "APPROVED", "REJECTED"]),
                amount=rng.uniform(10000, 500000),
                days_added=rng.randint(0, 45),
                requested_by="Contractor", requested_date=ref - timedelta(days=rng.randint(5, 60)),
                reason_code=rng.choice(["UNFORESEEN", "DESIGN_CHG", "SCOPE_CHG", "ESCALATION"]),
            ))
    db.commit()


if __name__ == "__main__":
    result = seed_enterprise()
    print(f"Enterprise seed complete: {result}")

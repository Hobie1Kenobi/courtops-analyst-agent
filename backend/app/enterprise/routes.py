"""Enterprise system simulation API routes."""

from typing import List
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.enterprise.models import *
from app.enterprise.seed import seed_enterprise

router = APIRouter(prefix="/enterprise", tags=["enterprise"])


# ── Seed ──
@router.post("/seed")
def seed_all(seed: int = Query(default=20260225)):
    return seed_enterprise(seed)


# ── Maximo ──
class MaximoWORead(BaseModel):
    wonum: str; description: str; status: str; worktype: str | None = None
    assetnum: str | None = None; location: str | None = None; priority: int | None = None
    pmnum: str | None = None; estdur: float | None = None
    actlabhrs: float = 0; actmatcost: float = 0
    class Config: from_attributes = True

class MaximoAssetRead(BaseModel):
    assetnum: str; description: str; status: str; assettype: str | None = None
    location: str | None = None; warrantyexpdate: date | None = None; ytdcost: float = 0
    class Config: from_attributes = True

class MaximoPMRead(BaseModel):
    pmnum: str; description: str; status: str; assetnum: str | None = None
    frequency: int | None = None; frequnit: str | None = None
    nextdate: date | None = None; lastcompdate: date | None = None
    class Config: from_attributes = True

@router.get("/maximo/workorders", response_model=List[MaximoWORead])
def maximo_workorders(status: str | None = None, db: Session = Depends(get_db)):
    q = db.query(MaximoWorkOrder).order_by(MaximoWorkOrder.reportdate.desc()).limit(100)
    if status:
        q = q.filter(MaximoWorkOrder.status == status)
    return [MaximoWORead.model_validate(r) for r in q.all()]

@router.get("/maximo/assets", response_model=List[MaximoAssetRead])
def maximo_assets(db: Session = Depends(get_db)):
    return [MaximoAssetRead.model_validate(r) for r in db.query(MaximoAsset).limit(100).all()]

@router.get("/maximo/pms", response_model=List[MaximoPMRead])
def maximo_pms(db: Session = Depends(get_db)):
    return [MaximoPMRead.model_validate(r) for r in db.query(MaximoPM).limit(50).all()]

@router.get("/maximo/crontasks")
def maximo_crons(db: Session = Depends(get_db)):
    return [{"name": c.crontaskname, "description": c.description, "active": c.active,
             "lastrun": str(c.lastrun) if c.lastrun else None, "nextrun": str(c.nextrun) if c.nextrun else None}
            for c in db.query(MaximoCronTask).all()]

@router.get("/maximo/messages")
def maximo_messages(status: str = "ERROR", db: Session = Depends(get_db)):
    return [{"msgid": m.msgid, "extsysname": m.extsysname, "ifacename": m.ifacename,
             "status": m.status, "msgerror": m.msgerror, "createdate": str(m.createdate)}
            for m in db.query(MaximoIntMessage).filter(MaximoIntMessage.status == status).limit(50).all()]

@router.get("/maximo/stats")
def maximo_stats(db: Session = Depends(get_db)):
    total_wo = db.query(MaximoWorkOrder).count()
    open_wo = db.query(MaximoWorkOrder).filter(MaximoWorkOrder.status.in_(["WAPPR", "APPR", "INPRG", "WMATL", "WSCH"])).count()
    overdue_pm = db.query(MaximoPM).filter(MaximoPM.status == "ACTIVE", MaximoPM.nextdate < date.today()).count()
    error_msgs = db.query(MaximoIntMessage).filter(MaximoIntMessage.status == "ERROR").count()
    return {"total_workorders": total_wo, "open_workorders": open_wo, "overdue_pms": overdue_pm, "integration_errors": error_msgs}


# ── Tyler Incode ──
class IncodeCaseRead(BaseModel):
    case_number: str; citation_number: str | None = None; status: str
    violation_desc: str | None = None; court_date: date | None = None
    judge_name: str | None = None; fine_amount: float = 0; total_paid: float = 0; balance_due: float = 0
    class Config: from_attributes = True

class IncodePaymentRead(BaseModel):
    payment_id: int; case_number: str; amount: float
    payment_method: str | None = None; payment_source: str | None = None
    posted: bool = True; reconciled: bool = False
    class Config: from_attributes = True

@router.get("/incode/cases", response_model=List[IncodeCaseRead])
def incode_cases(status: str | None = None, db: Session = Depends(get_db)):
    q = db.query(IncodeCaseRecord).order_by(IncodeCaseRecord.filing_date.desc()).limit(100)
    if status:
        q = q.filter(IncodeCaseRecord.status == status)
    return [IncodeCaseRead.model_validate(r) for r in q.all()]

@router.get("/incode/payments", response_model=List[IncodePaymentRead])
def incode_payments(reconciled: bool | None = None, db: Session = Depends(get_db)):
    q = db.query(IncodePayment).order_by(IncodePayment.payment_date.desc()).limit(200)
    if reconciled is not None:
        q = q.filter(IncodePayment.reconciled == reconciled)
    return [IncodePaymentRead.model_validate(r) for r in q.all()]

@router.get("/incode/citations/errors")
def incode_citation_errors(db: Session = Depends(get_db)):
    errors = db.query(IncodeCitation).filter(IncodeCitation.import_status == "ERROR").all()
    return [{"citation_number": c.citation_number, "violation_desc": c.violation_desc,
             "import_error": c.import_error, "import_batch": c.import_batch}
            for c in errors]

@router.get("/incode/warrants")
def incode_warrants(status: str = "ACTIVE", db: Session = Depends(get_db)):
    return [{"warrant_number": w.warrant_number, "case_number": w.case_number,
             "status": w.status, "issue_date": str(w.issue_date),
             "tcic_status": w.tcic_status, "upload_error": w.upload_error}
            for w in db.query(IncodeWarrant).filter(IncodeWarrant.status == status).limit(50).all()]

@router.get("/incode/stats")
def incode_stats(db: Session = Depends(get_db)):
    total = db.query(IncodeCaseRecord).count()
    open_cases = db.query(IncodeCaseRecord).filter(IncodeCaseRecord.status == "OPEN").count()
    fta = db.query(IncodeCaseRecord).filter(IncodeCaseRecord.status.in_(["FTA", "WARRANT"])).count()
    unreconciled = db.query(IncodePayment).filter(IncodePayment.reconciled == False).count()
    import_errors = db.query(IncodeCitation).filter(IncodeCitation.import_status == "ERROR").count()
    total_balance = sum(c.balance_due for c in db.query(IncodeCaseRecord).all() if c.balance_due > 0)
    return {"total_cases": total, "open_cases": open_cases, "fta_warrant": fta,
            "unreconciled_payments": unreconciled, "import_errors": import_errors,
            "total_outstanding": round(total_balance, 2)}


# ── e-Builder ──
class EBuilderProjectRead(BaseModel):
    project_id: str; project_name: str; status: str; department: str | None = None
    budget_total: float = 0; actual_cost: float = 0; budget_remaining: float = 0
    percent_complete: float = 0; schedule_variance_days: int = 0
    project_manager: str | None = None; contractor: str | None = None
    class Config: from_attributes = True

@router.get("/ebuilder/projects", response_model=List[EBuilderProjectRead])
def ebuilder_projects(db: Session = Depends(get_db)):
    return [EBuilderProjectRead.model_validate(r) for r in db.query(EBuilderProject).all()]

@router.get("/ebuilder/costs")
def ebuilder_costs(project_id: str | None = None, db: Session = Depends(get_db)):
    q = db.query(EBuilderCostItem)
    if project_id:
        q = q.filter(EBuilderCostItem.project_id == project_id)
    return [{"cost_id": c.cost_id, "project_id": c.project_id, "cost_code": c.cost_code,
             "description": c.description, "category": c.category,
             "budgeted": c.budgeted, "actual": c.actual, "variance": c.variance,
             "posted_to_finance": c.posted_to_finance}
            for c in q.limit(100).all()]

@router.get("/ebuilder/documents")
def ebuilder_documents(sync_status: str | None = None, db: Session = Depends(get_db)):
    q = db.query(EBuilderDocument)
    if sync_status:
        q = q.filter(EBuilderDocument.sync_status == sync_status)
    return [{"doc_id": d.doc_id, "project_id": d.project_id, "doc_type": d.doc_type,
             "title": d.title, "status": d.status, "sync_status": d.sync_status,
             "sync_error": d.sync_error}
            for d in q.limit(100).all()]

@router.get("/ebuilder/rfis")
def ebuilder_rfis(status: str | None = None, db: Session = Depends(get_db)):
    q = db.query(EBuilderRFI)
    if status:
        q = q.filter(EBuilderRFI.status == status)
    return [{"rfi_id": r.rfi_id, "project_id": r.project_id, "rfi_number": r.rfi_number,
             "subject": r.subject, "status": r.status, "days_open": r.days_open,
             "cost_impact": r.cost_impact, "schedule_impact": r.schedule_impact}
            for r in q.limit(50).all()]

@router.get("/ebuilder/stats")
def ebuilder_stats(db: Session = Depends(get_db)):
    projects = db.query(EBuilderProject).all()
    total_budget = sum(p.budget_total for p in projects)
    total_actual = sum(p.actual_cost for p in projects)
    behind = sum(1 for p in projects if p.schedule_variance_days > 14)
    doc_errors = db.query(EBuilderDocument).filter(EBuilderDocument.sync_status == "ERROR").count()
    open_rfis = db.query(EBuilderRFI).filter(EBuilderRFI.status.in_(["OPEN", "OVERDUE"])).count()
    return {"total_projects": len(projects), "total_budget": round(total_budget, 2),
            "total_spent": round(total_actual, 2), "behind_schedule": behind,
            "document_sync_errors": doc_errors, "open_rfis": open_rfis}

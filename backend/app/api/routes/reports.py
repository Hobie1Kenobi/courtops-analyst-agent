from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import Case, Device, Ticket
from app.services.reporting import run_monthly_report


REPORT_ROOT = Path(__file__).resolve().parents[3] / "reports"

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("/monthly/generate")
def generate_monthly_report_now(
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> dict:
    """Generate the monthly operations report bundle for the current month. Creates PDF and summary under reports/YYYY-MM."""
    period = run_monthly_report(db, period=None)
    return {"period": period, "message": f"Report generated for {period}. Refresh the list to download."}


@router.get("/monthly")
def list_monthly_reports(
    _user=Depends(get_current_user),
) -> List[dict]:
    """Return available monthly report bundles discovered under reports/YYYY-MM."""
    if not REPORT_ROOT.exists():
        return []
    results: list[dict] = []
    for period_dir in sorted(REPORT_ROOT.iterdir()):
        if not period_dir.is_dir():
            continue
        pdfs = list(period_dir.glob("*.pdf"))
        results.append(
            {
                "period": period_dir.name,
                "pdf_files": [pdf.name for pdf in pdfs],
            }
        )
    return results


@router.get("/monthly/{period}/pdf")
def download_monthly_pdf(
    period: str,
    _user=Depends(get_current_user),
) -> FileResponse:
    """Download the primary PDF for a given period, if present."""
    period_dir = REPORT_ROOT / period
    if not period_dir.exists():
        raise HTTPException(status_code=404, detail="Report period not found")
    pdfs = list(period_dir.glob("*.pdf"))
    if not pdfs:
        raise HTTPException(status_code=404, detail="No PDF report for period")
    pdf = pdfs[0]
    return FileResponse(pdf, media_type="application/pdf", filename=pdf.name)


@router.get("/custom-query.csv")
def custom_query_csv(
    entity: str,
    _user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StreamingResponse:
    """
    Very small 'Crystal Reports style' custom query builder:
    caller chooses an entity (cases, tickets, devices) and gets a CSV export
    of a curated subset of fields.
    """
    import csv
    from io import StringIO

    buffer = StringIO()
    writer = csv.writer(buffer)

    entity = entity.lower()
    if entity == "cases":
        writer.writerow(["case_number", "status", "court", "filing_date", "disposition_date", "fine_amount"])
        for c in db.query(Case).limit(500):
            writer.writerow([c.case_number, c.status.value, c.court, c.filing_date, c.disposition_date, c.fine_amount])
    elif entity == "tickets":
        writer.writerow(["id", "title", "category", "priority", "status", "created_at", "due_at"])
        for t in db.query(Ticket).limit(500):
            writer.writerow(
                [t.id, t.title, t.category.value, t.priority.value, t.status.value, t.created_at, t.due_at]
            )
    elif entity == "devices":
        writer.writerow(["asset_tag", "type", "location", "assigned_user", "warranty_end", "last_patch_date"])
        for d in db.query(Device).limit(500):
            writer.writerow(
                [d.asset_tag, d.type, d.location, d.assigned_user, d.warranty_end, d.last_patch_date]
            )
    else:
        raise HTTPException(status_code=400, detail="Unsupported entity")

    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{entity}_report.csv"'},
    )


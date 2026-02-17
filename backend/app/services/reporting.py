from datetime import date, datetime
from pathlib import Path
from typing import Iterable

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from sqlalchemy.orm import Session

from app.models import Case, Ticket, Device


REPORT_ROOT = Path(__file__).resolve().parents[2] / "reports"


def ensure_report_dir(period: str) -> Path:
    """Ensure reports/YYYY-MM exists and return its path."""
    directory = REPORT_ROOT / period
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def generate_monthly_operations_pdf(
    period: str,
    cases: Iterable[Case],
    tickets: Iterable[Ticket],
    devices: Iterable[Device],
) -> Path:
    """Create a concise, Crystal-Reports-style PDF summary for the month."""
    report_dir = ensure_report_dir(period)
    pdf_path = report_dir / f"monthly_operations_{period}.pdf"

    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 14)
    c.drawString(72, height - 72, "Municipal Court Operations - Monthly Summary")
    c.setFont("Helvetica", 10)
    c.drawString(72, height - 90, f"Period: {period}")
    c.drawString(72, height - 105, f"Generated at (UTC): {datetime.utcnow().isoformat()}")

    # Simple metrics
    total_cases = len(list(cases))
    total_tickets = len(list(tickets))
    total_devices = len(list(devices))

    y = height - 140
    c.setFont("Helvetica-Bold", 12)
    c.drawString(72, y, "Key Metrics")
    y -= 20

    c.setFont("Helvetica", 10)
    c.drawString(90, y, f"Total cases in system: {total_cases}")
    y -= 15
    c.drawString(90, y, f"Total help desk tickets: {total_tickets}")
    y -= 15
    c.drawString(90, y, f"Tracked hardware assets: {total_devices}")

    c.showPage()
    c.save()
    return pdf_path


def run_monthly_report(
    db: Session,
    period: str | None = None,
) -> str:
    """
    Generate the monthly operations report bundle (PDF + summary) for the given
    period. If period is None, uses current month (YYYY-MM). Returns the period.
    """
    if period is None:
        period = date.today().strftime("%Y-%m")
    cases = db.query(Case).all()
    tickets = db.query(Ticket).all()
    devices = db.query(Device).all()
    pdf_path = generate_monthly_operations_pdf(period, cases, tickets, devices)
    reports_dir = ensure_report_dir(period)
    (reports_dir / "summary.txt").write_text(
        f"Monthly report generated for {period}\nPDF: {pdf_path.name}\n",
        encoding="utf-8",
    )
    return period


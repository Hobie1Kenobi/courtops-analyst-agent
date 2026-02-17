from collections import defaultdict
from datetime import date, datetime
from pathlib import Path
from typing import Iterable

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from sqlalchemy.orm import Session

from app.models import Case, Ticket, Device
from app.models.cases import CaseStatus, violation_group


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


def get_revenue_at_risk_cases(
    db: Session,
    min_days_overdue: int = 90,
) -> list[tuple[str, list[tuple[Case, int, float]], float]]:
    """
    Cases in FTA or WARRANT status with days_overdue >= min_days_overdue,
    grouped by violation group. Returns list of (group_name, [(case, days_overdue, outstanding_balance), ...], subtotal).
    """
    cases = db.query(Case).filter(Case.status.in_([CaseStatus.FTA, CaseStatus.WARRANT])).all()
    grouped: dict[str, list[tuple[Case, int, float]]] = defaultdict(list)
    for c in cases:
        days = c.days_overdue()
        if days is None or days < min_days_overdue:
            continue
        bal = c.outstanding_balance()
        if bal <= 0:
            continue
        group = violation_group(c.charge_type)
        grouped[group].append((c, days, bal))
    order = ["Traffic Violations (High Priority)", "City Ordinance (Code Enforcement)", "Other"]
    result: list[tuple[str, list[tuple[Case, int, float]], float]] = []
    for name in order:
        if name not in grouped:
            continue
        rows = grouped[name]
        subtotal = sum(r[2] for r in rows)
        result.append((name, rows, subtotal))
    for name, rows in grouped.items():
        if name in order:
            continue
        result.append((name, rows, sum(r[2] for r in rows)))
    return result


def generate_revenue_at_risk_pdf(
    period: str,
    grouped: list[tuple[str, list[tuple[Case, int, float]], float]],
) -> Path:
    """Crystal Reports-style PDF: Municipal Court Quarterly Revenue at Risk (FTA)."""
    report_dir = ensure_report_dir(period)
    pdf_path = report_dir / "revenue_at_risk_fta.pdf"
    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 14)
    c.drawString(72, height - 72, "Municipal Court: Quarterly Revenue at Risk (FTA)")
    c.setFont("Helvetica", 10)
    c.drawString(72, height - 90, f"Period: {period}")
    c.drawString(72, height - 105, f"Generated at (UTC): {datetime.utcnow().isoformat()}")

    y = height - 130
    total_revenue_at_risk = 0.0
    for group_name, rows, subtotal in grouped:
        total_revenue_at_risk += subtotal
        c.setFont("Helvetica-Bold", 11)
        c.drawString(72, y, f"Group: {group_name}")
        y -= 18
        c.setFont("Helvetica", 9)
        c.drawString(72, y, "Citation")
        c.drawString(180, y, "Defendant")
        c.drawString(320, y, "Days Overdue")
        c.drawString(420, y, "Outstanding Bal.")
        y -= 14
        for case, days_overdue, outstanding in rows:
            if y < 100:
                c.showPage()
                y = height - 72
            def_name = case.defendant_name[:24] if len(case.defendant_name) > 24 else case.defendant_name
            days_str = f"{days_overdue}+" if days_overdue >= 120 else str(days_overdue)
            c.drawString(72, y, case.case_number)
            c.drawString(180, y, def_name)
            c.drawString(320, y, days_str)
            c.drawString(420, y, f"${outstanding:,.2f}")
            y -= 14
        c.setFont("Helvetica-Bold", 9)
        c.drawString(320, y, "Subtotal")
        c.drawString(420, y, f"${subtotal:,.2f}")
        y -= 20

    c.setFont("Helvetica-Bold", 12)
    c.drawString(72, y, f"TOTAL REVENUE AT RISK: ${total_revenue_at_risk:,.2f}")
    c.showPage()
    c.save()
    return pdf_path


def run_revenue_at_risk_report(
    db: Session,
    period: str | None = None,
    min_days_overdue: int = 90,
) -> Path:
    """Generate Revenue at Risk (FTA) PDF for the given period. Returns path to PDF."""
    if period is None:
        period = date.today().strftime("%Y-%m")
    grouped = get_revenue_at_risk_cases(db, min_days_overdue=min_days_overdue)
    return generate_revenue_at_risk_pdf(period, grouped)


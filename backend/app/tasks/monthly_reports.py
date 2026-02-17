from celery import shared_task

from app.db.session import SessionLocal
from app.services.reporting import run_monthly_report


@shared_task(name="app.tasks.monthly_reports.run_monthly_reports")
def run_monthly_reports() -> str:
    """Generate a monthly operations report package and store it under reports/YYYY-MM."""
    db = SessionLocal()
    try:
        period = run_monthly_report(db, period=None)
        return f"monthly_reports_completed:{period}"
    finally:
        db.close()



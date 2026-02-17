from datetime import date, timedelta

from celery import shared_task
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models import Case, CaseStatus, Patch, PatchStatus


@shared_task(name="app.tasks.weekly_checks.run_weekly_checks")
def run_weekly_checks() -> str:
    """
    Weekly agent job:
    - Identify patches deployed but not yet verified for follow-up
    - Run simple data quality checks on cases (e.g., inconsistent dispositions)
    """
    db: Session = SessionLocal()
    try:
        today = date.today()
        # Patches that were deployed more than 7 days ago but not verified
        pending_verification = (
            db.query(Patch)
            .filter(
                Patch.status == PatchStatus.DEPLOYED,
                Patch.deployed_date != None,  # noqa: E711
            )
            .all()
        )
        pending_verification = [
            p for p in pending_verification if (today - p.deployed_date).days >= 7  # type: ignore[arg-type]
        ]

        # Data quality: cases with disposition date but non-disposed status
        dq_issues = (
            db.query(Case)
            .filter(
                Case.disposition_date != None,  # noqa: E711
                Case.status.notin_(
                    [CaseStatus.DISPOSED, CaseStatus.DISMISSED, CaseStatus.PAID]
                ),
            )
            .all()
        )

        return f"weekly_checks_completed:pending_verification={len(pending_verification)},dq_issues={len(dq_issues)}"
    finally:
        db.close()


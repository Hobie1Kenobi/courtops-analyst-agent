from celery import shared_task
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models import Device, Ticket, TicketStatus, AuditEvent
from app.services.audit_rules import detect_repeated_failed_logins


@shared_task(name="app.tasks.daily_checks.run_daily_checks")
def run_daily_checks() -> str:
    """
    Daily agent job:
    - Identify overdue SLA tickets
    - Flag devices with expiring warranty / missing recent patches
    - Detect suspicious bursts of failed logins
    """
    db: Session = SessionLocal()
    try:
        overdue_tickets = [
            t
            for t in db.query(Ticket)
            .filter(Ticket.status.in_([TicketStatus.OPEN, TicketStatus.IN_PROGRESS]))
            .all()
            if t.is_overdue()
        ]

        # Devices with warranty expiring in 30 days or patches older than 90 days
        from datetime import date, timedelta

        today = date.today()
        risky_devices = []
        for d in db.query(Device).all():
            if d.is_warranty_expiring_within_days(30):
                risky_devices.append(d)
            elif d.last_patch_date and (today - d.last_patch_date) > timedelta(days=90):
                risky_devices.append(d)

        # Suspicious login activity
        recent_events = (
            db.query(AuditEvent)
            .order_by(AuditEvent.created_at.desc())
            .limit(200)
            .all()
        )
        suspicious_logins = detect_repeated_failed_logins(recent_events)

        # For demo purposes we simply return a summary string; in a real deployment
        # these would create escalation tickets and supervisor notifications.
        return f"daily_checks_completed:overdue={len(overdue_tickets)},risky_devices={len(risky_devices)},suspicious_logins={int(suspicious_logins)}"
    finally:
        db.close()


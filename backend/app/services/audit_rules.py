from datetime import datetime, timedelta
from typing import Iterable

from app.models.audit import AuditAction, AuditEvent


def detect_repeated_failed_logins(
    events: Iterable[AuditEvent],
    threshold: int = 5,
    window_minutes: int = 15,
) -> bool:
    """Flag suspicious bursts of failed logins within a short time window."""
    failures = [e for e in events if e.action == AuditAction.LOGIN_FAILURE]
    failures.sort(key=lambda e: e.created_at)
    for i in range(len(failures)):
        window_start = failures[i].created_at
        window_end = window_start + timedelta(minutes=window_minutes)
        count = sum(1 for e in failures if window_start <= e.created_at <= window_end)
        if count >= threshold:
            return True
    return False


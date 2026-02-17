from datetime import datetime, timedelta

from app.models.audit import AuditAction, AuditEvent


def detect_repeated_failed_logins(events: list[AuditEvent], threshold: int = 5, window_minutes: int = 15) -> bool:
    """Simple helper to flag suspicious bursts of failed logins."""
    failures = [e for e in events if e.action == AuditAction.LOGIN_FAILURE]
    failures.sort(key=lambda e: e.created_at)
    for i in range(len(failures)):
        window_start = failures[i].created_at
        window_end = window_start + timedelta(minutes=window_minutes)
        count = sum(1 for e in failures if window_start <= e.created_at <= window_end)
        if count >= threshold:
            return True
    return False


def test_detect_repeated_failed_logins_flags_burst():
    base = datetime(2024, 1, 1, 8, 0, 0)
    events = [
        AuditEvent(id=i, user_id=1, action=AuditAction.LOGIN_FAILURE, entity_type=None, entity_id=None, metadata=None, ip_address=None, created_at=base + timedelta(minutes=i))
        for i in range(6)
    ]
    assert detect_repeated_failed_logins(events) is True


def test_detect_repeated_failed_logins_ignores_sparse():
    base = datetime(2024, 1, 1, 8, 0, 0)
    events = [
        AuditEvent(id=i, user_id=1, action=AuditAction.LOGIN_FAILURE, entity_type=None, entity_id=None, metadata=None, ip_address=None, created_at=base + timedelta(minutes=i * 20))
        for i in range(4)
    ]
    assert detect_repeated_failed_logins(events) is False


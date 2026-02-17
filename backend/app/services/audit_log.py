import hashlib
import json
from typing import Any

from sqlalchemy.orm import Session

from app.models import AuditEvent
from app.models.audit import AuditAction


def _args_hash(args: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(args, sort_keys=True, default=str).encode()).hexdigest()[:16]


def log_agent_tool(
    db: Session,
    user_id: int | None,
    tool_name: str,
    args: dict[str, Any],
    result_summary: str,
) -> AuditEvent:
    event = AuditEvent(
        user_id=user_id,
        action=AuditAction.AGENT_TOOL,
        entity_type="agent_tool",
        entity_id=tool_name,
        event_metadata=json.dumps({"args_hash": _args_hash(args), "result_summary": result_summary[:500]}),
        ip_address=None,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event

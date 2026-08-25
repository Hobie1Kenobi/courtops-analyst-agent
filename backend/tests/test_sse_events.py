"""Test SSE event emission includes required keys."""

import json
from unittest.mock import MagicMock

from app.ops.stream import publish_ops_event


def test_sse_event_keys():
    mock_db = MagicMock()
    mock_db.add = MagicMock()
    mock_db.commit = MagicMock()

    import queue
    from app.ops.stream import subscribe, unsubscribe

    q = subscribe()
    try:
        publish_ops_event(
            db=mock_db,
            agent="test_agent",
            action="test_action",
            work_order_id=42,
            status="ok",
            kpis={"open_tickets": 10},
            artifact={"name": "test.pdf", "path": "/tmp/test.pdf", "type": "application/pdf"},
        )

        data_str = q.get_nowait()
        data = json.loads(data_str)

        required_keys = {"ts", "sim_time", "phase", "agent", "work_order_id", "action", "status", "kpis", "artifact"}
        assert required_keys.issubset(set(data.keys())), f"Missing keys: {required_keys - set(data.keys())}"
        assert data["agent"] == "test_agent"
        assert data["action"] == "test_action"
        assert data["work_order_id"] == 42
        assert data["kpis"]["open_tickets"] == 10
        assert data["artifact"]["name"] == "test.pdf"
    finally:
        unsubscribe(q)

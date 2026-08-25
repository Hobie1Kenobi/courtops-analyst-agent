"""SSE event stream and publisher for the Ops Console."""

import asyncio
import json
import queue
import threading
from datetime import datetime

from sqlalchemy.orm import Session

from app.ops.models import OpsEvent
from app.sim.clock import sim_clock

_subscribers: list[queue.Queue] = []
_sub_lock = threading.Lock()


def publish_ops_event(
    db: Session | None,
    agent: str,
    action: str,
    work_order_id: int | None = None,
    status: str = "ok",
    kpis: dict | None = None,
    artifact: dict | None = None,
):
    clock_state = sim_clock.state()
    event_data = {
        "ts": datetime.utcnow().isoformat(),
        "sim_time": clock_state["sim_time"],
        "phase": clock_state["phase"],
        "agent": agent,
        "work_order_id": work_order_id,
        "action": action,
        "status": status,
        "kpis": kpis,
        "artifact": artifact,
    }

    from app.sim.logger import log_ops_event
    log_ops_event(
        agent=agent, action=action,
        work_order_id=work_order_id, status=status,
        kpis=kpis, artifact=artifact,
        phase=clock_state["phase"], sim_time=clock_state["sim_time"],
    )

    if db is not None:
        try:
            ev = OpsEvent(
                sim_time=clock_state["sim_time"],
                phase=clock_state["phase"],
                agent=agent,
                work_order_id=work_order_id,
                action=action,
                status=status,
                kpis_json=json.dumps(kpis) if kpis else None,
                artifact_json=json.dumps(artifact) if artifact else None,
            )
            db.add(ev)
            db.commit()
        except Exception:
            db.rollback()

    json_str = json.dumps(event_data, default=str)
    with _sub_lock:
        for q in _subscribers:
            try:
                q.put_nowait(json_str)
            except queue.Full:
                pass


def subscribe() -> queue.Queue:
    q: queue.Queue = queue.Queue(maxsize=200)
    with _sub_lock:
        _subscribers.append(q)
    return q


def unsubscribe(q: queue.Queue):
    with _sub_lock:
        if q in _subscribers:
            _subscribers.remove(q)

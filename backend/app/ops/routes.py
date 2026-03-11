import json
import queue
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.ops.models import OpsEvent
from app.ops.stream import subscribe, unsubscribe
from app.sim.clock import sim_clock
from app.work_orders.service import get_kpis, pending_count_by_queue

router = APIRouter(prefix="/ops", tags=["ops"])


@router.get("/clock")
def get_clock():
    return sim_clock.state()


@router.post("/clock/start")
def start_clock(speed: float = 30.0, sim_date: str | None = None):
    dt = None
    if sim_date:
        dt = datetime.fromisoformat(sim_date)
    sim_clock.start(speed=speed, sim_date=dt)
    return sim_clock.state()


@router.post("/clock/stop")
def stop_clock():
    sim_clock.stop()
    return sim_clock.state()


@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db)):
    kpis = get_kpis(db)
    queues = pending_count_by_queue(db)
    return {
        "clock": sim_clock.state(),
        "kpis": kpis,
        "queues": queues,
    }


class OpsEventRead(BaseModel):
    id: int
    ts: datetime | None = None
    sim_time: str | None = None
    phase: str | None = None
    agent: str | None = None
    work_order_id: int | None = None
    action: str
    status: str | None = None

    class Config:
        from_attributes = True


@router.get("/events", response_model=List[OpsEventRead])
def list_events(
    since: str | None = None,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    q = db.query(OpsEvent).order_by(OpsEvent.id.desc())
    if since:
        try:
            since_dt = datetime.fromisoformat(since)
            q = q.filter(OpsEvent.ts >= since_dt)
        except ValueError:
            pass
    return [OpsEventRead.model_validate(e) for e in q.limit(limit).all()]


@router.get("/stream")
async def sse_stream(request: Request):
    q = subscribe()

    async def event_generator():
        try:
            while True:
                if await request.is_disconnected():
                    break
                try:
                    data = q.get_nowait()
                    yield f"data: {data}\n\n"
                except queue.Empty:
                    yield ": heartbeat\n\n"
                import asyncio
                await asyncio.sleep(0.5)
        finally:
            unsubscribe(q)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )

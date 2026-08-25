"""Base agent loop: observe -> plan -> act -> document -> publish."""

import json
import time
from datetime import datetime

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.ops.stream import publish_ops_event
from app.sim.clock import sim_clock
from app.work_orders.models import WorkOrder, WorkOrderQueue, WorkOrderStatus
from app.work_orders.service import claim_work_order, complete_work_order, fail_work_order, get_kpis


class BaseAgent:
    name: str = "base_agent"
    queue: WorkOrderQueue = WorkOrderQueue.CLERK_OPS

    def tick(self):
        if not sim_clock.running:
            return
        db = SessionLocal()
        try:
            wo = claim_work_order(db, self.queue, self.name)
            if wo is None:
                return

            wo.status = WorkOrderStatus.IN_PROGRESS
            db.commit()

            publish_ops_event(
                db, agent=self.name,
                action=f"started:{wo.type.value}",
                work_order_id=wo.id,
                status="in_progress",
            )

            try:
                actions, artifacts, note = self.execute(db, wo)
                complete_work_order(db, wo, actions, artifacts, note)
                kpis = get_kpis(db)
                artifact_data = artifacts[0] if artifacts else None
                publish_ops_event(
                    db, agent=self.name,
                    action=f"completed:{wo.type.value}",
                    work_order_id=wo.id,
                    status="completed",
                    kpis=kpis,
                    artifact=artifact_data,
                )
            except Exception as exc:
                fail_work_order(db, wo, str(exc))
                publish_ops_event(
                    db, agent=self.name,
                    action=f"failed:{wo.type.value}",
                    work_order_id=wo.id,
                    status="failed",
                )
        finally:
            db.close()

    def execute(self, db: Session, wo: WorkOrder) -> tuple[list[str], list[dict], str]:
        raise NotImplementedError

"""Shift Director: monitors KPIs, generates phase work orders, triggers month-end."""

import time

from app.db.session import SessionLocal
from app.ops.stream import publish_ops_event
from app.sim.clock import sim_clock
from app.sim.events import generate_phase_work_orders
from app.work_orders.service import get_kpis, pending_count_by_queue


class ShiftDirector:
    name = "shift_director"

    def __init__(self):
        self._last_phase = None
        self._phases_generated: set[str] = set()
        self._dispatch_count: dict[str, int] = {}

    def tick(self):
        if not sim_clock.running:
            return
        if sim_clock.shift_complete:
            return

        current_phase = sim_clock.phase
        db = SessionLocal()
        try:
            if current_phase not in self._phases_generated:
                self._phases_generated.add(current_phase)
                self._dispatch_count[current_phase] = 0
                wo_ids = generate_phase_work_orders(db, current_phase)
                self._dispatch_count[current_phase] += 1
                kpis = get_kpis(db)
                publish_ops_event(
                    db, agent=self.name,
                    action=f"phase_start:{current_phase}",
                    status="ok",
                    kpis=kpis,
                )
                publish_ops_event(
                    db, agent=self.name,
                    action=f"dispatched:{len(wo_ids)}_work_orders",
                    status="ok",
                )

            queues = pending_count_by_queue(db)
            total_pending = sum(queues.values())
            dispatches = self._dispatch_count.get(current_phase, 0)
            if total_pending == 0 and dispatches < 4:
                wo_ids = generate_phase_work_orders(db, current_phase)
                self._dispatch_count[current_phase] = dispatches + 1
                publish_ops_event(
                    db, agent=self.name,
                    action=f"redispatch:{len(wo_ids)}_work_orders",
                    status="ok",
                )

            if self._last_phase != current_phase:
                self._last_phase = current_phase

            kpis = get_kpis(db)
            publish_ops_event(
                db, agent=self.name,
                action="kpi_update",
                status="ok",
                kpis=kpis,
            )
        finally:
            db.close()

    def reset(self):
        self._last_phase = None
        self._phases_generated.clear()
        self._dispatch_count.clear()

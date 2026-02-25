"""In-process sim runner using background threads (no Celery required for demo)."""

import threading
import time

from app.agents.director import ShiftDirector
from app.agents.clerk_it_hybrid import ClerkITHybridAgent
from app.agents.it_functional import ITFunctionalAgent
from app.agents.finance_audit import FinanceAuditAgent
from app.sim.clock import sim_clock

_thread: threading.Thread | None = None
_stop_event = threading.Event()


def _run_all_agents():
    director = ShiftDirector()
    clerk = ClerkITHybridAgent()
    it_func = ITFunctionalAgent()
    finance = FinanceAuditAgent()

    agents = [director, clerk, it_func, finance]
    cycle = 0

    while not _stop_event.is_set():
        if not sim_clock.running or sim_clock.shift_complete:
            if sim_clock.shift_complete:
                from app.db.session import SessionLocal
                from app.ops.stream import publish_ops_event
                from app.work_orders.service import get_kpis
                db = SessionLocal()
                try:
                    kpis = get_kpis(db)
                    publish_ops_event(db, agent="shift_director", action="shift_complete", status="ok", kpis=kpis)
                finally:
                    db.close()
                break
            time.sleep(1)
            continue

        director.tick()
        time.sleep(0.5)

        if cycle % 2 == 0:
            clerk.tick()
        if cycle % 2 == 1:
            it_func.tick()
        if cycle % 3 == 0:
            finance.tick()

        cycle += 1
        time.sleep(2)


def start_sim_runner():
    global _thread
    _stop_event.clear()
    if _thread is not None and _thread.is_alive():
        return
    _thread = threading.Thread(target=_run_all_agents, daemon=True)
    _thread.start()


def stop_sim_runner():
    _stop_event.set()
    global _thread
    if _thread is not None:
        _thread.join(timeout=5)
        _thread = None

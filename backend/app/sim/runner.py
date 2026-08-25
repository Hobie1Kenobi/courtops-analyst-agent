"""In-process sim runner using background threads (no Celery required for demo)."""

import json
import threading
import time
from datetime import datetime
from pathlib import Path

from app.agents.director import ShiftDirector
from app.agents.clerk_it_hybrid import ClerkITHybridAgent
from app.agents.it_functional import ITFunctionalAgent
from app.agents.finance_audit import FinanceAuditAgent
from app.sim.clock import sim_clock
from app.sim.logger import start_log, stop_log, get_counters

_thread: threading.Thread | None = None
_stop_event = threading.Event()
_run_result: dict | None = None


def _run_all_agents(seed: int, speed: float):
    global _run_result
    log_path = start_log(seed=seed, speed=speed)

    director = ShiftDirector()
    clerk = ClerkITHybridAgent()
    it_func = ITFunctionalAgent()
    finance = FinanceAuditAgent()

    cycle = 0
    started_at = time.time()

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
        time.sleep(0.3)

        clerk.tick()
        time.sleep(0.3)

        it_func.tick()
        time.sleep(0.3)

        finance.tick()

        cycle += 1
        time.sleep(1.5)

    elapsed = time.time() - started_at
    summary = stop_log()
    summary["elapsed_real_seconds"] = round(elapsed, 1)
    summary["elapsed_real_minutes"] = round(elapsed / 60, 1)
    summary["total_agent_cycles"] = cycle
    summary["speed"] = speed
    summary["seed"] = seed

    LOGS_DIR = Path(__file__).resolve().parents[2] / "sim_logs"
    summary_path = LOGS_DIR / f"shift_summary_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    summary_path.write_text(json.dumps(summary, indent=2, default=str))
    summary["summary_file"] = str(summary_path)
    _run_result = summary


def start_sim_runner(seed: int = 20260225, speed: float = 30.0):
    global _thread, _run_result
    _run_result = None
    _stop_event.clear()
    if _thread is not None and _thread.is_alive():
        return
    _thread = threading.Thread(target=_run_all_agents, args=(seed, speed), daemon=True)
    _thread.start()


def stop_sim_runner() -> dict | None:
    _stop_event.set()
    global _thread
    if _thread is not None:
        _thread.join(timeout=10)
        _thread = None
    return _run_result


def get_run_result() -> dict | None:
    return _run_result

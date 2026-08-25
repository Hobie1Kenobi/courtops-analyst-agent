"""Comprehensive simulation logger that writes every event to a structured log file."""

import json
import os
import threading
from datetime import datetime
from pathlib import Path

LOGS_DIR = Path(__file__).resolve().parents[2] / "sim_logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

_log_lock = threading.Lock()
_log_file = None
_log_path = None
_counters = {
    "events_total": 0,
    "by_agent": {},
    "by_action": {},
    "by_phase": {},
    "work_orders_created": 0,
    "work_orders_completed": 0,
    "work_orders_failed": 0,
    "artifacts_generated": 0,
    "phase_transitions": [],
}


def start_log(seed: int, speed: float):
    global _log_file, _log_path, _counters
    _counters = {
        "events_total": 0,
        "by_agent": {},
        "by_action": {},
        "by_phase": {},
        "work_orders_created": 0,
        "work_orders_completed": 0,
        "work_orders_failed": 0,
        "artifacts_generated": 0,
        "phase_transitions": [],
    }
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    _log_path = LOGS_DIR / f"shift_log_{ts}_seed{seed}.jsonl"
    _log_file = open(_log_path, "w")
    _log_event("system", "log_started", meta={
        "seed": seed, "speed": speed,
        "start_time_utc": datetime.utcnow().isoformat(),
    })
    return str(_log_path)


def _log_event(agent: str, action: str, **kwargs):
    global _log_file
    if _log_file is None:
        return
    entry = {
        "ts_utc": datetime.utcnow().isoformat(),
        "agent": agent,
        "action": action,
        **kwargs,
    }
    with _log_lock:
        _counters["events_total"] += 1
        _counters["by_agent"][agent] = _counters["by_agent"].get(agent, 0) + 1
        _counters["by_action"][action] = _counters["by_action"].get(action, 0) + 1
        if "phase" in kwargs:
            p = kwargs["phase"]
            _counters["by_phase"][p] = _counters["by_phase"].get(p, 0) + 1
        if "completed:" in action:
            _counters["work_orders_completed"] += 1
        if "failed:" in action:
            _counters["work_orders_failed"] += 1
        if "dispatched:" in action or "redispatch:" in action:
            try:
                n = int(action.split(":")[1].split("_")[0])
                _counters["work_orders_created"] += n
            except (ValueError, IndexError):
                pass
        if kwargs.get("artifact"):
            _counters["artifacts_generated"] += 1
        if "phase_start:" in action:
            _counters["phase_transitions"].append({
                "phase": action.split(":")[1],
                "ts_utc": datetime.utcnow().isoformat(),
            })
        try:
            _log_file.write(json.dumps(entry, default=str) + "\n")
            _log_file.flush()
        except Exception:
            pass


def log_ops_event(agent: str, action: str, work_order_id: int | None = None,
                  status: str = "ok", kpis: dict | None = None,
                  artifact: dict | None = None, phase: str | None = None,
                  sim_time: str | None = None):
    meta = {}
    if work_order_id is not None:
        meta["work_order_id"] = work_order_id
    if status:
        meta["status"] = status
    if kpis:
        meta["kpis"] = kpis
    if artifact:
        meta["artifact"] = artifact
    if phase:
        meta["phase"] = phase
    if sim_time:
        meta["sim_time"] = sim_time
    _log_event(agent, action, **meta)


def stop_log() -> dict:
    global _log_file
    _log_event("system", "log_stopped", meta={
        "end_time_utc": datetime.utcnow().isoformat(),
        "counters": _counters.copy(),
    })
    if _log_file:
        _log_file.close()
        _log_file = None

    summary = _counters.copy()
    summary["log_file"] = str(_log_path) if _log_path else None
    return summary


def get_counters() -> dict:
    with _log_lock:
        return _counters.copy()

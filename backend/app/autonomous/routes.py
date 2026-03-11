"""Autonomous agent API routes."""

from fastapi import APIRouter, Query
from app.autonomous.engine import (
    start_autonomous_shift, stop_autonomous_shift,
    get_shift_log, get_shift_summary, run_agent_turn,
    AGENT_CONFIGS,
)
from app.autonomous.tools import TOOL_REGISTRY

router = APIRouter(prefix="/autonomous", tags=["autonomous"])


@router.post("/shift/start")
def start_shift(speed: float = Query(default=60.0), seed: int = Query(default=20260225)):
    start_autonomous_shift(speed=speed, seed=seed)
    return {"status": "started", "speed": speed, "seed": seed, "agents": list(AGENT_CONFIGS.keys())}


@router.post("/shift/stop")
def stop_shift():
    return stop_autonomous_shift()


@router.get("/shift/log")
def shift_log():
    return get_shift_log()


@router.get("/shift/summary")
def shift_summary():
    return get_shift_summary()


@router.get("/tools")
def list_tools():
    return {name: {"description": t["description"]} for name, t in TOOL_REGISTRY.items()}


@router.get("/agents")
def list_agents():
    return {name: {"prompt_preview": cfg["prompt"][:200] + "...", "color": cfg["color"]} for name, cfg in AGENT_CONFIGS.items()}


@router.post("/agent/{agent_name}/turn")
def manual_agent_turn(agent_name: str, context: str = Query(default="Check all systems for issues.")):
    result = run_agent_turn(agent_name, context)
    return result


@router.get("/lab-status")
def lab_status():
    from app.autonomous.lab_tools import check_lab_services
    return check_lab_services()


@router.post("/sql")
def run_sql(query: str = Query(...), description: str = Query(default="")):
    from app.autonomous.lab_tools import run_sql_query
    return run_sql_query(query=query, description=description)


@router.get("/schema")
def get_schema():
    from app.autonomous.lab_tools import get_database_schema
    return get_database_schema()

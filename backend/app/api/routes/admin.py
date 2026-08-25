"""Admin endpoints: seeding, sim control, logging."""

from datetime import date, datetime

from fastapi import APIRouter, Query

from app.seed.seed_runner import run_seed
from app.sim.clock import sim_clock
from app.sim.runner import start_sim_runner, stop_sim_runner, get_run_result
from app.sim.logger import get_counters

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/seed")
def seed_database(
    profile: str = Query(default="corpus_christi"),
    scenario: str = Query(default="municipal_shift"),
    seed: int = Query(default=20260225),
    sim_date: str | None = Query(default=None),
    reset: bool = Query(default=False),
):
    dt = None
    if sim_date:
        dt = date.fromisoformat(sim_date)
    result = run_seed(
        profile_name=profile,
        scenario_name=scenario,
        seed=seed,
        sim_date=dt,
        reset=reset,
    )
    return result


@router.post("/sim/start")
def start_sim(
    speed: float = Query(default=30.0),
    seed: int = Query(default=20260225),
    sim_date: str | None = Query(default=None),
):
    dt = None
    if sim_date:
        dt = datetime.fromisoformat(sim_date)
    sim_clock.start(speed=speed, sim_date=dt)
    start_sim_runner(seed=seed, speed=speed)
    return {"status": "started", "clock": sim_clock.state()}


@router.post("/sim/stop")
def stop_sim():
    sim_clock.stop()
    result = stop_sim_runner()
    return {"status": "stopped", "clock": sim_clock.state(), "summary": result}


@router.get("/sim/status")
def sim_status():
    return {
        "clock": sim_clock.state(),
        "counters": get_counters(),
        "result": get_run_result(),
    }

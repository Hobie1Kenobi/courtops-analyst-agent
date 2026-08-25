"""Celery tasks that drive the simulation agents."""

import time

from app.celery_app import celery_app
from app.agents.director import ShiftDirector
from app.agents.clerk_it_hybrid import ClerkITHybridAgent
from app.agents.it_functional import ITFunctionalAgent
from app.agents.finance_audit import FinanceAuditAgent
from app.sim.clock import sim_clock


@celery_app.task(name="app.tasks.sim_runner.run_director_loop")
def run_director_loop():
    director = ShiftDirector()
    while sim_clock.running and not sim_clock.shift_complete:
        director.tick()
        time.sleep(3)
    return "director_loop_done"


@celery_app.task(name="app.tasks.sim_runner.run_clerk_ops_loop")
def run_clerk_ops_loop():
    agent = ClerkITHybridAgent()
    while sim_clock.running and not sim_clock.shift_complete:
        agent.tick()
        time.sleep(4)
    return "clerk_ops_done"


@celery_app.task(name="app.tasks.sim_runner.run_it_ops_loop")
def run_it_ops_loop():
    agent = ITFunctionalAgent()
    while sim_clock.running and not sim_clock.shift_complete:
        agent.tick()
        time.sleep(4)
    return "it_ops_done"


@celery_app.task(name="app.tasks.sim_runner.run_finance_audit_loop")
def run_finance_audit_loop():
    agent = FinanceAuditAgent()
    while sim_clock.running and not sim_clock.shift_complete:
        agent.tick()
        time.sleep(4)
    return "finance_audit_done"

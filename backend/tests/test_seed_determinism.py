"""Test that seeding with the same seed produces deterministic results."""

from app.seed.seed_runner import run_seed
from app.db.session import Base, engine, SessionLocal
from app.models import Case, Ticket, Device
from app.work_orders.service import get_kpis


def test_seed_determinism():
    result1 = run_seed(seed=12345, reset=True)
    db1 = SessionLocal()
    cases1 = db1.query(Case).count()
    tickets1 = db1.query(Ticket).count()
    devices1 = db1.query(Device).count()
    kpis1 = get_kpis(db1)
    db1.close()

    result2 = run_seed(seed=12345, reset=True)
    db2 = SessionLocal()
    cases2 = db2.query(Case).count()
    tickets2 = db2.query(Ticket).count()
    devices2 = db2.query(Device).count()
    kpis2 = get_kpis(db2)
    db2.close()

    assert cases1 == cases2, f"Case count mismatch: {cases1} vs {cases2}"
    assert tickets1 == tickets2, f"Ticket count mismatch: {tickets1} vs {tickets2}"
    assert devices1 == devices2, f"Device count mismatch: {devices1} vs {devices2}"
    assert kpis1["fta_cases"] == kpis2["fta_cases"]
    assert kpis1["revenue_at_risk"] == kpis2["revenue_at_risk"]

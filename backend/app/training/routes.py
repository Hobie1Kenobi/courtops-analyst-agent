"""Training Twin API routes."""

from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.training.models import TrainingTask, TaskStatus, SkillProgress, LabResult, SkillDomain
from app.training.agents.engine import (
    AGENT_ROSTER, seed_scenario,
    start_training, stop_training,
)
from app.training.content.scenarios import SCENARIOS as SCENARIO_DATA, LABS as LAB_DATA

router = APIRouter(prefix="/training", tags=["training"])


class TaskRead(BaseModel):
    id: int
    title: str
    domain: str
    scenario: str | None = None
    status: str
    assigned_agent: str | None = None
    description: str | None = None
    business_context: str | None = None
    evidence_reviewed: str | None = None
    decision_made: str | None = None
    technical_detail: str | None = None
    sql_or_config: str | None = None
    why_correct: str | None = None
    what_to_document: str | None = None
    what_to_test: str | None = None
    mentor_explanation: str | None = None
    interview_answer: str | None = None
    skills_practiced: str | None = None
    sim_phase: str | None = None

    class Config:
        from_attributes = True


class SkillRead(BaseModel):
    domain: str
    tasks_completed: int
    quizzes_passed: int
    confidence_score: float
    last_practiced: datetime | None = None

    class Config:
        from_attributes = True


@router.get("/scenarios")
def list_scenarios():
    return {k: {"name": v["name"], "description": v["description"], "task_count": len(v["tasks"])} for k, v in SCENARIO_DATA.items()}


@router.post("/scenarios/{scenario_key}/seed")
def seed(scenario_key: str, db: Session = Depends(get_db)):
    return seed_scenario(scenario_key, db)


@router.post("/scenarios/{scenario_key}/start")
def start(scenario_key: str, speed: float = Query(default=5.0)):
    start_training(scenario_key, speed)
    return {"status": "started", "scenario": scenario_key, "speed": speed}


@router.post("/stop")
def stop():
    stop_training()
    return {"status": "stopped"}


@router.get("/tasks", response_model=List[TaskRead])
def list_tasks(
    scenario: str | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
):
    q = db.query(TrainingTask).order_by(TrainingTask.id)
    if scenario:
        q = q.filter(TrainingTask.scenario == scenario)
    if status:
        q = q.filter(TrainingTask.status == status)
    return [TaskRead.model_validate(t) for t in q.limit(100).all()]


@router.get("/tasks/{task_id}", response_model=TaskRead)
def get_task(task_id: int, db: Session = Depends(get_db)):
    t = db.query(TrainingTask).filter(TrainingTask.id == task_id).first()
    if not t:
        from fastapi import HTTPException
        raise HTTPException(404, "Task not found")
    return TaskRead.model_validate(t)


@router.get("/skills", response_model=List[SkillRead])
def list_skills(db: Session = Depends(get_db)):
    skills = db.query(SkillProgress).all()
    all_domains = {d.value for d in SkillDomain}
    existing = {s.domain.value for s in skills}
    result = [SkillRead.model_validate(s) for s in skills]
    for d in all_domains - existing:
        result.append(SkillRead(domain=d, tasks_completed=0, quizzes_passed=0, confidence_score=0.0))
    return sorted(result, key=lambda s: s.domain)


@router.get("/agents")
def list_agents():
    return AGENT_ROSTER


@router.get("/labs")
def list_labs():
    return {k: {"id": v["id"], "name": v["name"], "domain": v["domain"], "description": v["description"], "exercise_count": len(v["exercises"])} for k, v in LAB_DATA.items()}


@router.get("/labs/{lab_id}")
def get_lab(lab_id: str):
    lab = LAB_DATA.get(lab_id)
    if not lab:
        from fastapi import HTTPException
        raise HTTPException(404, "Lab not found")
    return lab


@router.post("/labs/{lab_id}/submit")
def submit_lab(lab_id: str, exercise_id: str = Query(...), answer: str = Query(default=""), db: Session = Depends(get_db)):
    lab = LAB_DATA.get(lab_id)
    if not lab:
        from fastapi import HTTPException
        raise HTTPException(404, "Lab not found")
    exercise = next((e for e in lab["exercises"] if e["id"] == exercise_id), None)
    if not exercise:
        from fastapi import HTTPException
        raise HTTPException(404, "Exercise not found")

    result = LabResult(
        lab_id=lab_id,
        lab_name=lab["name"],
        completed=True,
        score=80.0,
        answers_json=f'{{"exercise_id": "{exercise_id}", "answer": "submitted"}}',
        feedback=exercise.get("explanation", "Review the expected answer above."),
        completed_at=datetime.utcnow(),
    )
    db.add(result)
    db.commit()

    return {
        "exercise_id": exercise_id,
        "feedback": exercise.get("explanation"),
        "expected_answer": exercise.get("expected_answer"),
        "tip": exercise.get("tip"),
        "oracle_equivalent": exercise.get("oracle_equivalent"),
    }

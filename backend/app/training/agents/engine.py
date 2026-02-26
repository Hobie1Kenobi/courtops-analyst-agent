"""Training Twin agent engine — runs scenarios through specialized agents with teaching."""

import json
import time
import threading
from datetime import datetime

from app.db.session import SessionLocal
from app.training.models import TrainingTask, TaskStatus, SkillDomain, SkillProgress
from app.training.content.scenarios import SCENARIOS
from app.ops.stream import publish_ops_event
from app.sim.clock import sim_clock

AGENT_ROSTER = {
    "shift_director": {"label": "Shift Director", "color": "purple", "role": "Routes work, monitors KPIs, manages phases"},
    "requirements_docs": {"label": "Requirements & Documentation", "color": "blue", "role": "Business requirements, functional specs, SOPs, change requests"},
    "sql_reporting": {"label": "SQL & Reporting", "color": "green", "role": "SQL Server, Oracle, SSRS, Crystal Reports, Power BI queries"},
    "app_integration": {"label": "Application & Integration", "color": "orange", "role": "Web services, APIs, IIS/Apache, SharePoint, ERP support"},
    "qa_debugging": {"label": "QA & Debugging", "color": "red", "role": "Bug reproduction, root cause analysis, test scenarios, defect docs"},
    "mentor_coach": {"label": "Mentor / Learning Coach", "color": "indigo", "role": "Explains concepts, quizzes user, provides interview prep"},
}

DOMAIN_TO_AGENT = {
    "sql_reporting": "sql_reporting",
    "app_integration": "app_integration",
    "requirements_docs": "requirements_docs",
    "qa_debugging": "qa_debugging",
    "audit_compliance": "requirements_docs",
    "infrastructure": "app_integration",
}

_thread = None
_stop = threading.Event()


def seed_scenario(scenario_key: str, db=None):
    close = False
    if db is None:
        db = SessionLocal()
        close = True
    try:
        scenario = SCENARIOS.get(scenario_key)
        if not scenario:
            return {"error": f"Unknown scenario: {scenario_key}"}

        created = []
        for task_def in scenario["tasks"]:
            agent = DOMAIN_TO_AGENT.get(task_def["domain"], "requirements_docs")
            t = TrainingTask(
                title=task_def["title"],
                domain=task_def["domain"],
                scenario=scenario_key,
                status=TaskStatus.QUEUED,
                priority=task_def.get("priority", 5),
                assigned_agent=agent,
                description=task_def.get("description"),
                business_context=task_def.get("business_context"),
                evidence_reviewed=task_def.get("evidence_reviewed"),
                decision_made=task_def.get("decision_made"),
                technical_detail=task_def.get("technical_detail"),
                sql_or_config=task_def.get("sql_or_config"),
                why_correct=task_def.get("why_correct"),
                what_to_document=task_def.get("what_to_document"),
                what_to_test=task_def.get("what_to_test"),
                mentor_explanation=task_def.get("mentor_explanation"),
                interview_answer=task_def.get("interview_answer"),
                skills_practiced=task_def.get("skills_practiced"),
                sim_phase=task_def.get("phase"),
            )
            db.add(t)
            db.flush()
            created.append(t.id)
        db.commit()
        return {"scenario": scenario_key, "tasks_created": len(created), "task_ids": created}
    finally:
        if close:
            db.close()


def _run_training_loop(scenario_key: str, speed: float):
    db = SessionLocal()
    try:
        tasks = db.query(TrainingTask).filter(
            TrainingTask.scenario == scenario_key,
            TrainingTask.status == TaskStatus.QUEUED,
        ).order_by(TrainingTask.id).all()

        for task in tasks:
            if _stop.is_set():
                break

            task.status = TaskStatus.ACTIVE
            db.commit()
            agent = task.assigned_agent or "requirements_docs"

            publish_ops_event(
                db, agent=agent,
                action=f"training:started:{task.title[:50]}",
                work_order_id=task.id,
                status="active",
            )
            time.sleep(max(1, 5 / speed))

            task.status = TaskStatus.TEACHING
            db.commit()
            publish_ops_event(
                db, agent="mentor_coach",
                action=f"teaching:{task.title[:50]}",
                work_order_id=task.id,
                status="teaching",
            )
            time.sleep(max(1, 4 / speed))

            task.status = TaskStatus.COMPLETED
            db.commit()

            if task.skills_practiced:
                for skill_name in task.skills_practiced.split(","):
                    skill_name = skill_name.strip()
                    try:
                        domain = SkillDomain(skill_name)
                    except ValueError:
                        continue
                    prog = db.query(SkillProgress).filter(SkillProgress.domain == domain).first()
                    if not prog:
                        prog = SkillProgress(domain=domain)
                        db.add(prog)
                    prog.tasks_completed += 1
                    prog.confidence_score = min(100.0, prog.confidence_score + 5.0)
                    prog.last_practiced = datetime.utcnow()
                db.commit()

            publish_ops_event(
                db, agent=agent,
                action=f"training:completed:{task.title[:50]}",
                work_order_id=task.id,
                status="completed",
            )
            time.sleep(max(0.5, 2 / speed))

        publish_ops_event(db, agent="shift_director", action="training:scenario_complete", status="ok")
    finally:
        db.close()


def start_training(scenario_key: str, speed: float = 5.0):
    global _thread
    _stop.clear()
    if _thread is not None and _thread.is_alive():
        _stop.set()
        _thread.join(timeout=3)
    _stop.clear()
    db = SessionLocal()
    try:
        db.query(TrainingTask).delete()
        db.query(SkillProgress).delete()
        db.commit()
        seed_scenario(scenario_key, db)
    finally:
        db.close()
    _thread = threading.Thread(target=_run_training_loop, args=(scenario_key, speed), daemon=True)
    _thread.start()


def stop_training():
    _stop.set()
    global _thread
    if _thread:
        _thread.join(timeout=5)
        _thread = None

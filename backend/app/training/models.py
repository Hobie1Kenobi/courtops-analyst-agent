"""Training Twin data models — realistic enterprise analyst training schemas."""

import enum
from datetime import datetime
from sqlalchemy import Column, DateTime, Enum, Integer, String, Text, Float, Boolean
from sqlalchemy.sql import func
from app.db.session import Base


class SkillDomain(str, enum.Enum):
    SQL_SERVER = "sql_server"
    ORACLE_SQL = "oracle_sql"
    STORED_PROCEDURES = "stored_procedures"
    CRYSTAL_REPORTS = "crystal_reports"
    SSRS = "ssrs"
    POWER_BI = "power_bi"
    IIS_APACHE = "iis_apache"
    WEB_SERVICES = "web_services"
    DOTNET_JAVA = "dotnet_java"
    POWERSHELL = "powershell"
    DEBUGGING = "debugging"
    REQUIREMENTS = "requirements"
    PROCESS_DOCS = "process_docs"
    CHANGE_MGMT = "change_mgmt"
    SHAREPOINT = "sharepoint"
    ERP_ASSET = "erp_asset"


class TaskDomain(str, enum.Enum):
    SQL_REPORTING = "sql_reporting"
    APP_INTEGRATION = "app_integration"
    REQUIREMENTS_DOCS = "requirements_docs"
    QA_DEBUGGING = "qa_debugging"
    INFRASTRUCTURE = "infrastructure"
    AUDIT_COMPLIANCE = "audit_compliance"


class TaskStatus(str, enum.Enum):
    QUEUED = "queued"
    ACTIVE = "active"
    TEACHING = "teaching"
    COMPLETED = "completed"


class LearningMode(str, enum.Enum):
    BEGINNER = "beginner"
    ANALYST = "analyst"
    INTERVIEW_PREP = "interview_prep"


class TrainingTask(Base):
    __tablename__ = "training_tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    domain = Column(Enum(TaskDomain), nullable=False, index=True)
    scenario = Column(String, nullable=True)
    status = Column(Enum(TaskStatus), default=TaskStatus.QUEUED, index=True)
    priority = Column(Integer, default=5)
    assigned_agent = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    business_context = Column(Text, nullable=True)
    evidence_reviewed = Column(Text, nullable=True)
    decision_made = Column(Text, nullable=True)
    technical_detail = Column(Text, nullable=True)
    sql_or_config = Column(Text, nullable=True)
    why_correct = Column(Text, nullable=True)
    what_to_document = Column(Text, nullable=True)
    what_to_test = Column(Text, nullable=True)
    mentor_explanation = Column(Text, nullable=True)
    interview_answer = Column(Text, nullable=True)
    artifacts_json = Column(Text, nullable=True)
    skills_practiced = Column(String, nullable=True)
    sim_phase = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())


class SkillProgress(Base):
    __tablename__ = "skill_progress"
    id = Column(Integer, primary_key=True, index=True)
    domain = Column(Enum(SkillDomain), nullable=False, index=True)
    tasks_completed = Column(Integer, default=0)
    quizzes_passed = Column(Integer, default=0)
    confidence_score = Column(Float, default=0.0)
    last_practiced = Column(DateTime, nullable=True)


class LabResult(Base):
    __tablename__ = "lab_results"
    id = Column(Integer, primary_key=True, index=True)
    lab_id = Column(String, nullable=False, index=True)
    lab_name = Column(String, nullable=False)
    completed = Column(Boolean, default=False)
    score = Column(Float, default=0.0)
    answers_json = Column(Text, nullable=True)
    feedback = Column(Text, nullable=True)
    completed_at = Column(DateTime, nullable=True)

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from app.db.session import Base


class OpsEvent(Base):
    __tablename__ = "ops_events"

    id = Column(Integer, primary_key=True, index=True)
    ts = Column(DateTime, server_default=func.now(), index=True)
    sim_time = Column(String, nullable=True)
    phase = Column(String, nullable=True)
    agent = Column(String, nullable=True)
    work_order_id = Column(Integer, nullable=True)
    action = Column(String, nullable=False)
    status = Column(String, nullable=True)
    kpis_json = Column(Text, nullable=True)
    artifact_json = Column(Text, nullable=True)

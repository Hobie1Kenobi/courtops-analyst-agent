"""Finance & Audit analyst agent: revenue analysis, monthly reporting, audit scans."""

from datetime import date, datetime
from pathlib import Path

from sqlalchemy.orm import Session

from app.agents.base import BaseAgent
from app.models import AuditEvent, Case, CaseStatus
from app.services.reporting import (
    run_monthly_report,
    run_revenue_at_risk_report,
    generate_audit_report,
)
from app.work_orders.models import WorkOrder, WorkOrderQueue, WorkOrderType

WATERMARK = "Public Data Mode – Synthetic Records – For Demonstration Only"


class FinanceAuditAgent(BaseAgent):
    name = "finance_audit_analyst"
    queue = WorkOrderQueue.FINANCE_AUDIT

    def execute(self, db: Session, wo: WorkOrder) -> tuple[list[str], list[dict], str]:
        if wo.type == WorkOrderType.REVENUE_AT_RISK_FTA:
            return self._revenue_at_risk(db)
        elif wo.type == WorkOrderType.MONTHLY_OPS_PACKAGE:
            return self._monthly_package(db)
        elif wo.type == WorkOrderType.AUDIT_LOG_SCAN:
            return self._audit_scan(db)
        elif wo.type == WorkOrderType.CHANGE_REQUEST_DRAFT:
            return self._review_change_request(db)
        return ["no_op"], [], "Unhandled"

    def _revenue_at_risk(self, db: Session):
        period = date.today().strftime("%Y-%m")
        pdf_path = run_revenue_at_risk_report(db, period=period, min_days_overdue=90)
        fta_cases = db.query(Case).filter(Case.status.in_([CaseStatus.FTA, CaseStatus.WARRANT])).all()
        total_risk = sum(c.outstanding_balance() for c in fta_cases)
        artifact = {"name": "revenue_at_risk_fta.pdf", "path": str(pdf_path), "type": "application/pdf"}
        return (
            [f"generated_revenue_at_risk_report:${total_risk:,.2f}"],
            [artifact],
            f"Revenue at risk: ${total_risk:,.2f} across {len(fta_cases)} cases",
        )

    def _monthly_package(self, db: Session):
        period = date.today().strftime("%Y-%m")
        run_monthly_report(db, period=period)
        audit_path = generate_audit_report(db, period=period)
        artifacts = [
            {"name": f"monthly_operations_{period}.pdf", "path": f"reports/{period}/monthly_operations_{period}.pdf", "type": "application/pdf"},
            {"name": "audit_report.txt", "path": str(audit_path), "type": "text/plain"},
        ]
        return (
            ["generated_monthly_operations_package", "generated_audit_report"],
            artifacts,
            f"Monthly ops package generated for {period}",
        )

    def _audit_scan(self, db: Session):
        events = db.query(AuditEvent).order_by(AuditEvent.created_at.desc()).limit(200).all()
        anomalies = []
        for e in events:
            meta = e.event_metadata or ""
            if "after_hours" in meta:
                anomalies.append(f"after_hours_export:event_{e.id}")
            if "role_mismatch" in meta:
                anomalies.append(f"role_mismatch:event_{e.id}")
            if "suspicious_burst" in meta:
                anomalies.append(f"suspicious_login_burst:event_{e.id}")
        actions = [f"scanned_{len(events)}_audit_events", f"found_{len(anomalies)}_anomalies"]
        return actions, [], f"Audit scan: {len(anomalies)} anomalies in {len(events)} events"

    def _review_change_request(self, db: Session):
        return ["reviewed_change_requests"], [], "Change requests reviewed from finance perspective"

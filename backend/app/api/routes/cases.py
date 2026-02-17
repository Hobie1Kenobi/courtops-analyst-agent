from collections import defaultdict
from datetime import date
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import Case
from app.schemas.cases import CaseMetrics, CaseRead


router = APIRouter(prefix="/cases", tags=["cases"])


@router.get("/", response_model=List[CaseRead])
def list_cases(
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> List[CaseRead]:
    cases = db.query(Case).order_by(Case.filing_date.desc()).limit(200).all()
    return [
        CaseRead.model_validate(c)
        for c in cases
    ]


@router.get("/metrics/monthly", response_model=List[CaseMetrics])
def monthly_metrics(
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> List[CaseMetrics]:
    cases = db.query(Case).all()
    grouped: dict[str, list[Case]] = defaultdict(list)
    for case in cases:
        key = case.filing_date.strftime("%Y-%m")
        grouped[key].append(case)

    metrics: list[CaseMetrics] = []
    for month, cs in sorted(grouped.items()):
        total = len(cs)
        disposed = [c for c in cs if c.status.name in {"DISPOSED", "DISMISSED", "PAID"}]
        non_disposed = total - len(disposed)
        disposed_pct = (len(disposed) / total * 100.0) if total > 0 else 0.0
        avg_age = sum(c.case_age_days() for c in cs) / total if total > 0 else 0.0

        ttd_values = [c.time_to_disposition_days() for c in disposed if c.time_to_disposition_days() is not None]
        avg_ttd = sum(ttd_values) / len(ttd_values) if ttd_values else None

        metrics.append(
            CaseMetrics(
                month=month,
                total_cases=total,
                disposed_cases=len(disposed),
                non_disposed_cases=non_disposed,
                disposed_pct=disposed_pct,
                avg_case_age_days=avg_age,
                avg_time_to_disposition_days=avg_ttd,
            )
        )

    return metrics


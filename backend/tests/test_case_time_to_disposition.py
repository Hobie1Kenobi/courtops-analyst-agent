from datetime import date

from app.models.cases import Case, CaseStatus


def test_time_to_disposition():
    filing = date(2024, 1, 1)
    disposition = date(2024, 1, 15)
    case = Case(
        id=1,
        case_number="MC-2024-00001",
        defendant_name="Test",
        charge_type="Speeding",
        status=CaseStatus.DISPOSED,
        court="Municipal Court",
        courtroom="101",
        clerk="Clerk A",
        judge="Judge B",
        filing_date=filing,
        hearing_date=None,
        disposition_date=disposition,
        fine_amount=100.0,
        amount_paid=0.0,
    )
    assert case.time_to_disposition_days() == (disposition - filing).days


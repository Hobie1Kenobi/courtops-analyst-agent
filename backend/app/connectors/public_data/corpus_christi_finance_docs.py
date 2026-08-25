"""Metadata connector for Corpus Christi public finance documents.

Uses only public information (report titles, compliance terminology, fiscal year
structure) as metadata inspiration for realistic report generation. No actual
document content is downloaded or stored.
"""

CC_FISCAL_YEAR_START_MONTH = 10

CC_FINANCE_REPORT_TITLES = [
    "Comprehensive Annual Financial Report (CAFR)",
    "Annual Budget Document",
    "Capital Improvement Program (CIP)",
    "Monthly Revenue & Expenditure Report",
    "Quarterly Investment Report",
    "Annual Audit Report – Independent Auditor",
    "Single Audit Report (Federal Grants)",
    "Popular Annual Financial Report (PAFR)",
]

CC_COMPLIANCE_TERMS = [
    "GASB 34 compliance",
    "Single Audit Act (Uniform Guidance)",
    "GFOA Certificate of Achievement",
    "Nueces County Tax Appraisal",
    "Municipal bond disclosure (SEC EMMA)",
    "Enterprise fund self-sufficiency",
    "Hotel Occupancy Tax (HOT) allocation",
]

CC_DEPARTMENT_NAMES = [
    "Municipal Court",
    "Police Department",
    "Fire Department",
    "Development Services",
    "Water Utilities",
    "Solid Waste Operations",
    "Parks & Recreation",
    "Streets Operations",
    "Information Technology",
    "Finance Department",
    "City Manager's Office",
    "City Secretary",
]


def get_report_terminology() -> dict:
    return {
        "report_titles": CC_FINANCE_REPORT_TITLES,
        "compliance_terms": CC_COMPLIANCE_TERMS,
        "departments": CC_DEPARTMENT_NAMES,
        "fiscal_year_start_month": CC_FISCAL_YEAR_START_MONTH,
    }

"""
Generate CourtOps Executive Report PDF (Run 3 – LinkedIn showcase).
Run from repo root: python scripts/generate_executive_report_pdf.py
Requires: pip install reportlab
Output: docs/CourtOps-Executive-Report.pdf
Content aligned to docs/agent-run-review-run-3.md and docs/results_run_3.
"""
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

OUTPUT_DIR = Path(__file__).resolve().parents[1] / "docs"
OUTPUT_PATH = OUTPUT_DIR / "CourtOps-Executive-Report.pdf"

NAVY = colors.HexColor("#1e3a5f")
BLUE = colors.HexColor("#2563eb")
SLATE_900 = colors.HexColor("#0f172a")
SLATE_600 = colors.HexColor("#475569")
SLATE_200 = colors.HexColor("#e2e8f0")
WHITE = colors.white

W, H = letter


def draw_page1(c: canvas.Canvas) -> None:
    c.setFillColor(NAVY)
    c.rect(0, H - 1.1 * inch, W, 1.1 * inch, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(W / 2, H - 0.55 * inch, "Daily Operations Executive Report")
    c.setFont("Helvetica", 12)
    c.drawCentredString(W / 2, H - 0.85 * inch, "CourtOps Analyst Agent  |  Period: October 2023  |  Generated: February 18, 2026")

    c.setFillColor(SLATE_600)
    c.setFont("Helvetica", 9)
    c.drawString(0.75 * inch, H - 1.35 * inch, "Cycle: Daily Operations & Functional Analysis  |  Prepared By: Hobie Cunningham")
    c.drawString(0.75 * inch, H - 1.55 * inch, "Liberty ChainGuard Consulting LLC  |  CourtOps Analyst Agent Portfolio")

    c.setFillColor(SLATE_900)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(0.75 * inch, H - 1.95 * inch, "Executive Summary")
    c.setFont("Helvetica", 10)
    y = H - 2.25 * inch
    for line in [
        "In the October 2023 operational cycle, the CourtOps Analyst Agent successfully executed a full-stack",
        "Municipal Court Functional Analyst workflow in a single automated run. The agent completed: public data",
        "refresh, help-desk triage and resolution, SLA sweep and escalation, inventory compliance check, patch",
        "record creation, and automated monthly operations report generation. All 12 tool calls completed",
        "successfully with zero failures. This run demonstrates technical readiness to support modern Municipal",
        "Court IT environments with scalable, audit-friendly, LLM-driven workflows and real downloadable artifacts.",
    ]:
        c.drawString(0.75 * inch, y, line[:95] if len(line) > 95 else line)
        y -= 0.22 * inch

    c.setFont("Helvetica-Bold", 12)
    c.drawString(0.75 * inch, y - 0.15 * inch, "1. Operational Dashboard")
    y -= 0.45 * inch
    c.setFillColor(SLATE_200)
    c.roundRect(0.75 * inch, y - 0.1 * inch, W - 1.5 * inch, 1.35 * inch, 6, fill=1, stroke=0)
    c.setFillColor(SLATE_900)
    c.setFont("Helvetica", 10)
    c.drawString(1 * inch, y + 1.0 * inch, "Total Revenue at Risk: $25,460  |  39 Citations (FTA/overdue cohort)")
    c.drawString(1 * inch, y + 0.7 * inch, "Help Desk SLA: 121 tickets escalated to high priority (this run)")
    c.drawString(1 * inch, y + 0.4 * inch, "System Load: 1,206 active cases (demo data)")
    c.drawString(1 * inch, y + 0.1 * inch, "Access issues: 13 triaged, 2 resolved in this run")
    y -= 1.6 * inch

    c.setFont("Helvetica-Bold", 12)
    c.drawString(0.75 * inch, y, "2. Detailed Findings")
    y -= 0.25 * inch
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(BLUE)
    c.drawString(0.75 * inch, y, "2.1 Financial & Risk (Revenue at Risk)")
    c.setFillColor(SLATE_900)
    c.setFont("Helvetica", 9)
    y -= 0.28 * inch
    c.drawString(0.9 * inch, y, "System tracks $25,460 revenue at risk (FTA/overdue); ~81% Traffic, ~17% Ordinance.")
    y -= 0.28 * inch
    c.drawString(0.9 * inch, y, "Revenue at Risk report can be generated on demand; this run produced the monthly operations report.")
    y -= 0.4 * inch
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(BLUE)
    c.drawString(0.75 * inch, y, "2.2 IT Service Management (Help Desk)")
    c.setFillColor(SLATE_900)
    c.setFont("Helvetica", 9)
    y -= 0.28 * inch
    c.drawString(0.9 * inch, y, "Triage: 50 open tickets; 13 access-issue tickets identified. Resolved in this run: 2 (IDs 274, 299).")
    y -= 0.28 * inch
    c.drawString(0.9 * inch, y, "SLA: 121 overdue tickets identified and escalated to high priority.")
    y -= 0.5 * inch

    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(BLUE)
    c.drawString(0.75 * inch, y, "2.3 Inventory & Patch Compliance")
    c.setFillColor(SLATE_900)
    c.setFont("Helvetica", 9)
    y -= 0.28 * inch
    c.drawString(0.9 * inch, y, "30 devices out of compliance (warranty expiring and/or patch overdue).")
    y -= 0.28 * inch
    c.drawString(0.9 * inch, y, "Action: 4 patch records created (IDs 35-38) for MC-1000, MC-1001, MC-1002, MC-1004.")
    y -= 0.28 * inch
    c.drawString(0.9 * inch, y, "Remaining 26 devices flagged for follow-up or manual scheduling.")
    y -= 0.5 * inch

    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(BLUE)
    c.drawString(0.75 * inch, y, "2.4 Public Data Integration")
    c.setFillColor(SLATE_900)
    c.setFont("Helvetica", 9)
    y -= 0.28 * inch
    c.drawString(0.9 * inch, y, "Source: Somerville Traffic Citations (public). Path: .../somerville_traffic_citations.csv. Status: Refreshed successfully.")

    c.setFillColor(SLATE_600)
    c.setFont("Helvetica", 8)
    c.drawCentredString(W / 2, 0.5 * inch, "Liberty ChainGuard Consulting  |  CourtOps Analyst Agent  |  Oct 2023  |  1 of 3")


def draw_page2(c: canvas.Canvas) -> None:
    y = H - 0.75 * inch
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(0.75 * inch, y, "3. Run Methodology & Portfolio Context")
    y -= 0.35 * inch
    c.setFillColor(SLATE_900)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(0.75 * inch, y, "How This Report Was Produced")
    c.setFont("Helvetica", 9)
    y -= 0.28 * inch
    c.drawString(0.9 * inch, y, "Run type: Single automated cycle (dry run off). 12 tool calls, 0 failures.")
    y -= 0.26 * inch
    c.drawString(0.9 * inch, y, "Agent stack: LLM (Ollama) + whitelisted tools only; no shell access. Every tool call is audit-logged.")
    y -= 0.26 * inch
    c.drawString(0.9 * inch, y, "Tools used: refresh_public_dataset, triage_tickets, resolve_ticket (x2), sla_sweep,")
    y -= 0.26 * inch
    c.drawString(0.9 * inch, y, "escalate_overdue_tickets, inventory_compliance_check, create_patch_record (x4), generate_monthly_operations_report.")
    y -= 0.26 * inch
    c.drawString(0.9 * inch, y, "Output: Real files on disk (e.g. reports/2023-10/monthly_operations_2023-10.pdf), downloadable via Reports UI.")
    y -= 0.45 * inch
    c.setFont("Helvetica-Bold", 10)
    c.drawString(0.75 * inch, y, "Portfolio Context")
    c.setFont("Helvetica", 9)
    y -= 0.28 * inch
    c.drawString(0.9 * inch, y, "Municipal Court Functional Analyst portfolio build. CourtOps maps to analyst duties: help desk/SLA,")
    y -= 0.26 * inch
    c.drawString(0.9 * inch, y, "case metrics and FTA, Revenue at Risk, inventory and patch compliance, change requests and audit trails.")
    y -= 0.26 * inch
    c.drawString(0.9 * inch, y, "Crystal Reports-style PDF/CSV outputs; role-based access. Suitable for LinkedIn as a technical portfolio showcase.")
    y -= 0.6 * inch

    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(0.75 * inch, y, "4. Generated Artifacts")
    y -= 0.3 * inch
    c.setFillColor(SLATE_900)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(0.75 * inch, y, "Generated in this run (recorded):")
    c.setFont("Helvetica", 9)
    y -= 0.28 * inch
    c.drawString(0.9 * inch, y, "Monthly Operations Report (PDF): reports/2023-10/monthly_operations_2023-10.pdf")
    y -= 0.26 * inch
    c.drawString(0.9 * inch, y, "System Summary (TXT): reports/2023-10/summary.txt")
    y -= 0.4 * inch
    c.setFont("Helvetica-Bold", 10)
    c.drawString(0.75 * inch, y, "Available in report directory (this or prior runs):")
    c.setFont("Helvetica", 9)
    y -= 0.28 * inch
    c.drawString(0.9 * inch, y, "Revenue-at-Risk FTA Report (PDF): reports/2023-10/revenue_at_risk_fta.pdf")
    y -= 0.26 * inch
    c.drawString(0.9 * inch, y, "Audit Summary Report (TXT): reports/2023-10/audit_report.txt")
    y -= 0.28 * inch
    c.drawString(0.9 * inch, y, "All files under reports/2023-10/ are downloadable via the application Reports page.")

    c.setFillColor(SLATE_600)
    c.setFont("Helvetica", 8)
    c.drawCentredString(W / 2, 0.5 * inch, "Liberty ChainGuard Consulting  |  CourtOps Analyst Agent  |  Oct 2023  |  2 of 3")


def draw_page3(c: canvas.Canvas) -> None:
    y = H - 0.75 * inch
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(0.75 * inch, y, "5. Recommendations")
    y -= 0.4 * inch
    c.setFillColor(SLATE_900)
    c.setFont("Helvetica", 10)
    c.drawString(0.75 * inch, y, "1. Revenue recovery: Prioritize collections for high-balance FTA/traffic accounts (e.g. exceeding $1,000).")
    y -= 0.35 * inch
    c.drawString(0.75 * inch, y, "2. SLA remediation: Assign Tier 1 support to clear the 121 escalated tickets.")
    y -= 0.35 * inch
    c.drawString(0.75 * inch, y, "3. Hardware lifecycle: Process warranty renewals and patch scheduling for the remaining 26")
    y -= 0.28 * inch
    c.drawString(0.9 * inch, y, "out-of-compliance devices (MC-1005 through MC-DEMO-3).")
    y -= 0.35 * inch
    c.drawString(0.75 * inch, y, "4. Follow-up runs: Use the agent to generate Revenue at Risk and audit reports in a subsequent")
    y -= 0.28 * inch
    c.drawString(0.9 * inch, y, "run for a full report bundle.")
    y -= 0.7 * inch

    c.setFillColor(SLATE_200)
    c.roundRect(0.75 * inch, y - 0.2 * inch, W - 1.5 * inch, 1.0 * inch, 6, fill=1, stroke=0)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(1 * inch, y + 0.55 * inch, "CourtOps Analyst Agent — Portfolio project for Municipal Court Functional Analyst roles")
    c.setFont("Helvetica", 9)
    c.drawString(1 * inch, y + 0.2 * inch, "End-to-end: help desk, cases, inventory, reports, audit, LLM-driven agent with whitelisted tools and audit logging.")
    c.drawString(1 * inch, y - 0.15 * inch, "GitHub: github.com/Hobie1Kenobi/courtops-analyst-agent  |  All tasks in this run completed successfully.")

    c.setFillColor(SLATE_600)
    c.setFont("Helvetica", 8)
    c.drawCentredString(W / 2, 0.5 * inch, "Liberty ChainGuard Consulting LLC  |  CourtOps Analyst Agent  |  Oct 2023  |  3 of 3")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(OUTPUT_PATH), pagesize=letter)
    draw_page1(c)
    c.showPage()
    draw_page2(c)
    c.showPage()
    draw_page3(c)
    c.save()
    print(f"Created: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()

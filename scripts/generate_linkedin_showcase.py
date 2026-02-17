"""
Generate a LinkedIn showcase PDF for CourtOps Analyst Agent.
Run from repo root: python scripts/generate_linkedin_showcase.py
Requires: pip install reportlab
Output: docs/linkedin-courtops-showcase.pdf
"""
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

OUTPUT_DIR = Path(__file__).resolve().parents[1] / "docs"
OUTPUT_PATH = OUTPUT_DIR / "linkedin-courtops-showcase.pdf"

NAVY = colors.HexColor("#1e3a5f")
BLUE = colors.HexColor("#2563eb")
SLATE_900 = colors.HexColor("#0f172a")
SLATE_600 = colors.HexColor("#475569")
SLATE_200 = colors.HexColor("#e2e8f0")
WHITE = colors.white

W, H = letter


def draw_title_slide(c: canvas.Canvas) -> None:
    c.setFillColor(NAVY)
    c.rect(0, H - 2 * inch, W, 2 * inch, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(W / 2, H - 1.15 * inch, "CourtOps Analyst Agent")
    c.setFont("Helvetica", 14)
    c.drawCentredString(W / 2, H - 1.55 * inch, "From data silos to actionable intelligence")
    c.setFillColor(SLATE_600)
    c.setFont("Helvetica", 11)
    c.drawCentredString(W / 2, H - 2.2 * inch, "A full-stack portfolio build for Municipal Court Functional Analyst roles")
    c.setFillColor(SLATE_900)
    c.setFont("Helvetica", 10)
    c.drawCentredString(W / 2, 0.75 * inch, "Next.js  •  FastAPI  •  PostgreSQL  •  Celery  •  Ollama")


def draw_challenge_slide(c: canvas.Canvas) -> None:
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(0.75 * inch, H - 1 * inch, "The challenge")
    c.setFillColor(SLATE_900)
    c.setFont("Helvetica", 12)
    c.drawString(0.75 * inch, H - 1.5 * inch, "Municipal courts sit on massive amounts of data —")
    c.drawString(0.75 * inch, H - 1.75 * inch, "cases, tickets, inventory, audits — but turning that into")
    c.drawString(0.75 * inch, H - 2 * inch, "actionable intelligence is hard.")
    c.setFillColor(SLATE_600)
    c.setFont("Helvetica", 11)
    y = H - 2.6 * inch
    for line in [
        "• Failure-to-appear (FTA) cases slip through the cracks",
        "• Revenue at risk is invisible without custom reports",
        "• Help desk, inventory, and reporting live in separate worlds",
        "• Compliance and audit trails are manual and reactive",
    ]:
        c.drawString(0.9 * inch, y, line)
        y -= 0.28 * inch
    c.setFillColor(BLUE)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(0.75 * inch, H - 4.2 * inch, "What if one platform could tie it all together — and an AI agent could run the ops?")


def draw_vision_slide(c: canvas.Canvas) -> None:
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(0.75 * inch, H - 1 * inch, "One platform, end to end")
    c.setFillColor(SLATE_900)
    c.setFont("Helvetica", 11)
    y = H - 1.45 * inch
    for line in [
        "Help desk with SLA tracking and triage  →  Court case metrics and backlog",
        "Hardware inventory and compliance  →  Patch and change management",
        "Monthly operations reports  →  Revenue at Risk (FTA) and audit reports",
        "Change requests  →  Auto-generated functional specs, SOPs, release notes",
    ]:
        c.drawString(0.75 * inch, y, line)
        y -= 0.35 * inch
    c.setFillColor(SLATE_200)
    c.roundRect(0.75 * inch, H - 5.5 * inch, W - 1.5 * inch, 1.2 * inch, 6, fill=1, stroke=0)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(1 * inch, H - 5.05 * inch, "All with role-based access, full audit logging, and public/synthetic data only —")
    c.drawString(1 * inch, H - 5.45 * inch, "no proprietary court data.")


def draw_built_for_job_slide(c: canvas.Canvas) -> None:
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(0.75 * inch, H - 1 * inch, "Built for the job")
    c.setFillColor(SLATE_600)
    c.setFont("Helvetica", 10)
    c.drawString(0.75 * inch, H - 1.3 * inch, "Functional Analyst duties mapped to real features")
    c.setFillColor(SLATE_900)
    c.setFont("Helvetica", 11)
    blocks = [
        ("Help desk & work orders", "Tickets, SLA, triage, escalation"),
        ("Court case operations", "Case metrics, FTA, time-to-disposition, Revenue at Risk"),
        ("Hardware inventory", "Assets, warranty, patches, compliance checks"),
        ("Patch / upgrade lifecycle", "Requested → scheduled → tested → deployed → verified"),
        ("Change requests & docs", "Functional specs, SOP updates, release notes"),
        ("Security & audit", "RBAC, login/export/role audit, anomaly detection"),
    ]
    y = H - 1.75 * inch
    for title, desc in blocks:
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(BLUE)
        c.drawString(0.75 * inch, y, title)
        c.setFont("Helvetica", 10)
        c.setFillColor(SLATE_900)
        c.drawString(0.75 * inch, y - 0.2 * inch, desc)
        y -= 0.6 * inch


def draw_tech_slide(c: canvas.Canvas) -> None:
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(0.75 * inch, H - 1 * inch, "Tech stack")
    c.setFillColor(SLATE_900)
    c.setFont("Helvetica", 11)
    y = H - 1.5 * inch
    c.drawString(0.75 * inch, y, "Frontend: Next.js (App Router), TypeScript, Tailwind, shadcn-style UI")
    y -= 0.4 * inch
    c.drawString(0.75 * inch, y, "Backend: FastAPI, SQLAlchemy, JWT auth, Celery + Redis")
    y -= 0.4 * inch
    c.drawString(0.75 * inch, y, "Data: PostgreSQL, public data connector, synthetic demo data")
    y -= 0.5 * inch
    c.setFillColor(BLUE)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(0.75 * inch, y, "AI agent: Ollama (local LLM) + whitelisted tools only")
    y -= 0.35 * inch
    c.setFont("Helvetica", 10)
    c.setFillColor(SLATE_600)
    c.drawString(0.75 * inch, y, "No shell access. Every tool call is audit-logged. Crystal Reports–style outputs.")
    y -= 0.6 * inch
    c.setFillColor(SLATE_200)
    c.roundRect(0.75 * inch, y - 0.3 * inch, W - 1.5 * inch, 0.5 * inch, 4, fill=1, stroke=0)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(1 * inch, y - 0.05 * inch, "Deploy: Docker Compose locally • Fly.io / Render for cloud demo")


def draw_agent_slide(c: canvas.Canvas) -> None:
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(0.75 * inch, H - 1 * inch, "The AI agent")
    c.setFillColor(SLATE_900)
    c.setFont("Helvetica", 11)
    c.drawString(0.75 * inch, H - 1.4 * inch, "An LLM-driven CourtOps Agent runs a full \"daily ops\" demo:")
    y = H - 1.85 * inch
    for line in [
        "1. Refresh public dataset cache",
        "2. Triage tickets and resolve access issues",
        "3. SLA sweep and escalate overdue work orders",
        "4. Inventory compliance check and create patch records",
        "5. Generate monthly operations report bundle",
        "6. Generate Revenue at Risk (FTA) report",
        "7. Generate audit report",
        "8. Create change request and generate docs",
    ]:
        c.drawString(0.9 * inch, y, line)
        y -= 0.28 * inch
    c.setFillColor(BLUE)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(0.75 * inch, H - 4.5 * inch, "One preset, one click — dry run or live. Built to showcase potential, not replace analysts.")


def draw_revenue_slide(c: canvas.Canvas) -> None:
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(0.75 * inch, H - 1 * inch, "Revenue at Risk (FTA)")
    c.setFillColor(SLATE_600)
    c.setFont("Helvetica", 10)
    c.drawString(0.75 * inch, H - 1.3 * inch, "Crystal Reports–style: FTA/warrant cases, grouped by violation type")
    c.setFillColor(SLATE_900)
    c.setFont("Helvetica", 11)
    c.drawString(0.75 * inch, H - 1.65 * inch, "Judges get pre-sorted dockets. Managers see total revenue at risk.")
    c.setFillColor(SLATE_200)
    c.roundRect(0.75 * inch, H - 3.2 * inch, W - 1.5 * inch, 1.5 * inch, 6, fill=1, stroke=0)
    c.setFillColor(SLATE_900)
    c.setFont("Helvetica", 10)
    c.drawString(1 * inch, H - 2.5 * inch, "Group: Traffic Violations (High Priority)")
    c.drawString(1 * inch, H - 2.75 * inch, "  Citation | Defendant | Days Overdue | Outstanding Bal. | Subtotal")
    c.drawString(1 * inch, H - 3 * inch, "Group: City Ordinance (Code Enforcement)")
    c.drawString(1 * inch, H - 3.25 * inch, "  Citation | Defendant | Days Overdue | Outstanding Bal. | Subtotal")
    c.setFont("Helvetica-Bold", 10)
    c.drawString(1 * inch, H - 3.6 * inch, "TOTAL REVENUE AT RISK: $X,XXX.XX")
    c.setFillColor(BLUE)
    c.setFont("Helvetica", 10)
    c.drawString(0.75 * inch, H - 4.2 * inch, "From raw data silos to actionable intelligence — the core of the portfolio story.")


def draw_demo_slide(c: canvas.Canvas) -> None:
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(0.75 * inch, H - 1 * inch, "Run it yourself")
    c.setFillColor(SLATE_900)
    c.setFont("Helvetica", 11)
    c.drawString(0.75 * inch, H - 1.4 * inch, "One-command demo (Windows): run_demo.bat")
    c.drawString(0.75 * inch, H - 1.7 * inch, "Starts Ollama, Docker Compose, seed data — then open the Agent Console.")
    c.setFillColor(SLATE_600)
    c.setFont("Helvetica", 10)
    y = H - 2.2 * inch
    for line in [
        "• Local: http://localhost:3000  (login: supervisor / password)",
        "• Deploy: Fly.io or Render from the repo — terminal-driven setup",
        "• No proprietary data: public datasets + synthetic data only",
    ]:
        c.drawString(0.9 * inch, y, line)
        y -= 0.35 * inch
    c.setFillColor(BLUE)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(0.75 * inch, H - 3.8 * inch, "Built to show what’s possible when functional analysis meets full-stack + AI.")


def draw_cta_slide(c: canvas.Canvas) -> None:
    c.setFillColor(NAVY)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(W / 2, H / 2 + 0.3 * inch, "CourtOps Analyst Agent")
    c.setFont("Helvetica", 13)
    c.drawCentredString(W / 2, H / 2 - 0.15 * inch, "Portfolio project for Municipal Court Functional Analyst roles")
    c.setFont("Helvetica", 11)
    c.drawCentredString(W / 2, H / 2 - 0.7 * inch, "GitHub: github.com/Hobie1Kenobi/courtops-analyst-agent")
    c.drawCentredString(W / 2, H / 2 - 1.1 * inch, "End-to-end: help desk, cases, inventory, reports, audit, AI agent")
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(W / 2, 1.2 * inch, "Let’s connect.")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(OUTPUT_PATH), pagesize=letter)
    slides = [
        draw_title_slide,
        draw_challenge_slide,
        draw_vision_slide,
        draw_built_for_job_slide,
        draw_tech_slide,
        draw_agent_slide,
        draw_revenue_slide,
        draw_demo_slide,
        draw_cta_slide,
    ]
    for i, draw in enumerate(slides):
        if i > 0:
            c.showPage()
        draw(c)
    c.save()
    print(f"Created: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()

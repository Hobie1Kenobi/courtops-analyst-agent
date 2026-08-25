"""Generate the Enterprise Training Twin Phase 1-4 Summary Report PDF."""

import json
from datetime import datetime
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib import colors

REPORTS_DIR = Path(__file__).resolve().parents[1] / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
PDF_PATH = REPORTS_DIR / "Enterprise_Training_Twin_Phase_Report.pdf"

PRIMARY = HexColor("#1e1b4b")
ACCENT = HexColor("#4f46e5")
MAXIMO_BLUE = HexColor("#2563eb")
INCODE_PURPLE = HexColor("#7c3aed")
EBUILDER_ORANGE = HexColor("#ea580c")
MUTED = HexColor("#64748b")
LIGHT_BG = HexColor("#f1f5f9")
WHITE = colors.white

WATERMARK = "Training Twin – Synthetic Records – Demonstration Only"
BRANDING = "Liberty ChainGuard Consulting"


class FooterCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pages = []
    def showPage(self):
        self.pages.append(dict(self.__dict__))
        self._startPage()
    def save(self):
        for i, page in enumerate(self.pages):
            self.__dict__.update(page)
            self.setFont("Helvetica", 6)
            self.setFillColor(MUTED)
            self.drawString(72, 28, WATERMARK)
            self.drawRightString(540, 28, f"{BRANDING} · Page {i+1} of {len(self.pages)}")
            self.setStrokeColor(HexColor("#e2e8f0"))
            self.line(72, 38, 540, 38)
            super().showPage()
        super().save()


def build():
    doc = SimpleDocTemplate(str(PDF_PATH), pagesize=letter, topMargin=72, bottomMargin=60, leftMargin=72, rightMargin=72)
    styles = getSampleStyleSheet()
    styles["Normal"].fontSize = 9
    styles["Normal"].leading = 13
    styles["Normal"].alignment = TA_JUSTIFY

    def h1(t): return Paragraph(f'<font size="16" color="#1e1b4b"><b>{t}</b></font>', styles["Normal"])
    def h2(t): return Paragraph(f'<font size="12" color="#4f46e5"><b>{t}</b></font>', styles["Normal"])
    def h3(t): return Paragraph(f'<font size="10" color="#1e1b4b"><b>{t}</b></font>', styles["Normal"])
    def p(t): return Paragraph(t, styles["Normal"])
    def b(t): return Paragraph(f'<bullet>&bull;</bullet> {t}', styles["Normal"])
    def sm(t): return Paragraph(f'<font size="7" color="#64748b">{t}</font>', styles["Normal"])

    def tbl(headers, rows, widths=None):
        data = [headers] + rows
        t = Table(data, colWidths=widths, repeatRows=1)
        t.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), ACCENT), ("TEXTCOLOR", (0,0), (-1,0), WHITE),
            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"), ("FONTSIZE", (0,0), (-1,-1), 8),
            ("ALIGN", (0,0), (-1,-1), "LEFT"), ("VALIGN", (0,0), (-1,-1), "TOP"),
            ("GRID", (0,0), (-1,-1), 0.5, HexColor("#e2e8f0")),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [WHITE, LIGHT_BG]),
            ("TOPPADDING", (0,0), (-1,-1), 4), ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ]))
        return t

    els = []

    # COVER
    els.append(Spacer(1, 80))
    els.append(Paragraph('<font size="22" color="#1e1b4b"><b>Enterprise Training Twin</b></font>', styles["Normal"]))
    els.append(Spacer(1, 6))
    els.append(Paragraph('<font size="14" color="#4f46e5">Phase 1–4 Build Summary Report</font>', styles["Normal"]))
    els.append(Spacer(1, 6))
    els.append(Paragraph('<font size="10" color="#64748b">IBM Maximo · Tyler Technologies Incode · e-Builder / Trimble Unity Construct</font>', styles["Normal"]))
    els.append(Spacer(1, 25))
    cover_rows = [
        ["Date", "February 28, 2026"], ["Systems Simulated", "3 (Maximo, Incode, e-Builder)"],
        ["Total Scenarios", "23"], ["Total Labs", "11 (22 exercises)"],
        ["Enterprise DB Tables", "18"], ["Teaching Panels/Task", "8"],
        ["Live Action Handlers", "10"], ["Data Classification", "SYNTHETIC — Public Data Only"],
    ]
    els.append(tbl(["Field", "Value"], cover_rows, [140, 320]))
    els.append(Spacer(1, 20))
    els.append(Paragraph('<font size="8" color="#f59e0b"><b>TRAINING TWIN — SYNTHETIC RECORDS — DEMONSTRATION ONLY</b></font>', styles["Normal"]))
    els.append(PageBreak())

    # TOC
    els.append(h1("Table of Contents"))
    els.append(Spacer(1, 10))
    for item in [
        "1. Executive Summary", "2. Phase 1: Enterprise System Schemas & Simulated Data",
        "3. Phase 2: 20 Enterprise Scenarios with Full Teaching Content",
        "4. Phase 3: Live Tool Interaction & Agent Actions",
        "5. Phase 4: Advanced Labs, Interview Prep & Remaining Scenarios",
        "6. The Six Training Agents — Roles & Responsibilities",
        "7. Scenario-by-Scenario Breakdown: IBM Maximo (M1–M7)",
        "8. Scenario-by-Scenario Breakdown: Tyler Incode (T1–T7)",
        "9. Scenario-by-Scenario Breakdown: e-Builder (E1–E6)",
        "10. Complete Lab Inventory (11 Labs, 22 Exercises)",
        "11. Skills Coverage Matrix",
        "12. Teaching Methodology: The 8-Panel System",
    ]:
        els.append(p(item)); els.append(Spacer(1, 2))
    els.append(PageBreak())

    # 1. EXECUTIVE SUMMARY
    els.append(h1("1. Executive Summary"))
    els.append(Spacer(1, 8))
    els.append(p(
        "In four sequential build phases, we created a comprehensive enterprise IT training platform that simulates "
        "three real legacy systems used in municipal government: IBM Maximo for asset management, Tyler Technologies "
        "Incode for court case management, and e-Builder (Trimble Unity Construct) for capital improvement project management. "
        "The system contains 23 realistic scenarios, 11 hands-on labs with 22 exercises, 18 simulated database tables, "
        "and 10 live tool interaction handlers — all powered by 6 specialized training agents."
    ))
    els.append(Spacer(1, 6))
    summary_rows = [
        ["Phase 1", "Enterprise Schemas & Data", "18 DB tables, seed data for all 3 systems, API endpoints, /systems UI"],
        ["Phase 2", "Scenario Content Library", "10 enterprise scenarios (M1-M3, T1-T4, E1-E3) with 8-panel teaching"],
        ["Phase 3", "Live Tool Interaction", "10 action handlers executing real SQL, enterprise labs (Maximo/Incode/e-Builder), Tool View panel"],
        ["Phase 4", "Advanced Labs & Completion", "10 more scenarios (M4-M7, T5-T7, E4-E6), PowerShell/debugging/interview labs"],
    ]
    els.append(tbl(["Phase", "Focus", "Deliverables"], summary_rows, [55, 130, 275]))
    els.append(PageBreak())

    # 2. PHASE 1
    els.append(h1("2. Phase 1: Enterprise System Schemas & Simulated Data"))
    els.append(Spacer(1, 8))
    els.append(p("Phase 1 created the foundational data layer — 18 database tables modeling the actual schema patterns of IBM Maximo, Tyler Incode, and e-Builder. Each table uses column names, data types, and relationships that approximate the real systems, enabling realistic SQL training."))
    els.append(Spacer(1, 6))
    els.append(h3("IBM Maximo Tables (7)"))
    mx_tables = [
        ["mx_workorder", "Work orders (PM + corrective)", "40 records", "WONUM, STATUS, ASSETNUM, LOCATION, PRIORITY, PMNUM"],
        ["mx_asset", "City fleet vehicles, pumps, HVAC, IT", "18 records", "ASSETNUM, DESCRIPTION, STATUS, ASSETTYPE, WARRANTY"],
        ["mx_locations", "City facilities (City Hall, Court, etc.)", "10 records", "LOCATION, DESCRIPTION, STREETADDRESS"],
        ["mx_pm", "Preventive maintenance schedules", "14 records", "PMNUM, ASSETNUM, FREQUENCY, NEXTDATE, STATUS"],
        ["mx_sr", "Service requests", "—", "TICKETID, DESCRIPTION, STATUS, ASSETNUM"],
        ["mx_crontaskdef", "Cron task definitions", "4 records", "CRONTASKNAME, ACTIVE, LASTRUN, NEXTRUN"],
        ["mx_maxintmsgtrk", "Integration message tracking", "5 records", "EXTSYSNAME, STATUS, MSGERROR"],
    ]
    els.append(tbl(["Table", "Purpose", "Records", "Key Columns"], mx_tables, [90, 130, 55, 185]))
    els.append(Spacer(1, 6))
    els.append(h3("Tyler Incode Tables (6)"))
    ic_tables = [
        ["ic_citation", "Traffic citations from PD", "120 records", "CITATION_NUMBER, VIOLATION, DEFENDANT_ID, IMPORT_STATUS"],
        ["ic_defendant", "Defendant records", "18 records", "LAST_NAME, FIRST_NAME, DOB, DL_NUMBER"],
        ["ic_case", "Court cases", "100 records", "CASE_NUMBER, STATUS, FINE, TOTAL_PAID, BALANCE_DUE"],
        ["ic_payment", "Payment transactions", "200 records", "CASE_NUMBER, AMOUNT, METHOD, POSTED, GATEWAY_TXN_ID"],
        ["ic_warrant", "Active warrants", "—", "WARRANT_NUMBER, CASE_NUMBER, STATUS, TCIC_STATUS"],
        ["ic_docket", "Court docket schedules", "3 records", "DOCKET_DATE, COURTROOM, JUDGE_ID, CASE_COUNT"],
    ]
    els.append(tbl(["Table", "Purpose", "Records", "Key Columns"], ic_tables, [90, 120, 55, 195]))
    els.append(Spacer(1, 6))
    els.append(h3("e-Builder / Trimble Tables (5)"))
    eb_tables = [
        ["eb_project", "CIP projects ($90.1M total)", "8 records", "PROJECT_ID, NAME, STATUS, BUDGET, ACTUAL, SCHEDULE_VAR"],
        ["eb_cost_item", "Project cost line items", "~40 records", "PROJECT_ID, COST_CODE, BUDGETED, ACTUAL, POSTED"],
        ["eb_document", "Construction documents", "~20 records", "PROJECT_ID, DOC_TYPE, SYNC_STATUS, SYNC_ERROR"],
        ["eb_rfi", "Requests for Information", "~12 records", "RFI_NUMBER, STATUS, DAYS_OPEN, COST_IMPACT"],
        ["eb_change_order", "Contract change orders", "~8 records", "CO_NUMBER, AMOUNT, STATUS, REASON_CODE"],
    ]
    els.append(tbl(["Table", "Purpose", "Records", "Key Columns"], eb_tables, [90, 120, 55, 195]))
    els.append(PageBreak())

    # 3. PHASE 2
    els.append(h1("3. Phase 2: Enterprise Scenarios with Full Teaching Content"))
    els.append(Spacer(1, 8))
    els.append(p("Phase 2 built the first 10 enterprise scenarios — each containing a realistic municipal IT incident with complete teaching material across 8 panels. Every scenario includes the business context, evidence review, SQL queries, config commands, mentor explanations, and STAR-format interview answers."))
    els.append(Spacer(1, 6))
    phase2_rows = [
        ["M1", "Maximo", "PM Work Order Generation Failure", "SQL, Cron, Debugging", "PMWOGen crash from decommissioned asset"],
        ["M2", "Maximo", "Duplicate Key Error on WOACTIVITY", "SQL Server, Performance", "Outdated statistics + sequence race condition"],
        ["M3", "Maximo", "GL Integration Failure", "Web Services, SOAP", "Finance endpoint URL changed during maintenance"],
        ["T1", "Incode", "Citation Import Failure", "XML, Integration", "Schema mismatch from PD RMS update"],
        ["T2", "Incode", "Payment Posting Mismatch", "SQL, Financial", "$340 variance from warrant business rule"],
        ["T3", "Incode", "Docket Generation Error", "Crystal Reports, SP", "NULL judge_id drops all rows in INNER JOIN"],
        ["T4", "Incode", "Warrant Interface Failure", "PowerShell, Certs", "TCIC/NCIC certificate expiration"],
        ["E1", "e-Builder", "API Authentication Failure", "REST API, Config", "Key rotation broke CIP data sync"],
        ["E2", "e-Builder", "CIP Budget Variance", "SQL, Reporting", "$180K gap from unposted invoices during outage"],
        ["E3", "e-Builder", "Document Sync Failure", "SharePoint, OAuth2", "Service account password expired"],
    ]
    els.append(tbl(["ID", "System", "Scenario", "Skills", "Root Cause"], phase2_rows, [25, 45, 130, 90, 170]))
    els.append(PageBreak())

    # 4. PHASE 3
    els.append(h1("4. Phase 3: Live Tool Interaction & Agent Actions"))
    els.append(Spacer(1, 8))
    els.append(p("Phase 3 brought the scenarios to life. Instead of just reading about what an analyst would do, the system now executes real SQL queries against the simulated enterprise databases, shows the results, applies fixes, and verifies. The Tool View panel shows step-by-step what the agent 'sees' inside each tool."))
    els.append(Spacer(1, 6))
    els.append(h3("How Live Tool Interaction Works"))
    for item in [
        "<b>Step 1 — Open Tool:</b> Agent opens the simulated tool panel (e.g., Maximo Cron Task Setup)",
        "<b>Step 2 — Run Query:</b> Executes a real SQL query against the simulated DB tables and returns JSON results",
        "<b>Step 3 — Analyze:</b> Reads the results and identifies the problem (e.g., 'PM-1003 references decommissioned asset')",
        "<b>Step 4 — Apply Fix:</b> Executes an UPDATE/INSERT against the DB to fix the issue",
        "<b>Step 5 — Verify:</b> Runs a verification query to confirm the fix worked",
        "<b>Each step shows:</b> Tool name, panel opened, SQL executed, JSON results, and Analyst Observation",
    ]:
        els.append(b(item))
    els.append(Spacer(1, 6))
    els.append(h3("Enterprise Labs Added"))
    labs_p3 = [
        ["IBM Maximo Lab", "3", "Query overdue PMs, find PMs on decommissioned assets, check integration errors"],
        ["Tyler Incode Lab", "3", "Reconcile payments, calculate FTA revenue-at-risk, debug NULL docket join"],
        ["e-Builder Lab", "2", "CIP budget vs actual with CASE, find unposted costs with HAVING"],
    ]
    els.append(tbl(["Lab", "Exercises", "Topics"], labs_p3, [100, 45, 315]))
    els.append(PageBreak())

    # 5. PHASE 4
    els.append(h1("5. Phase 4: Advanced Labs, Interview Prep & Remaining Scenarios"))
    els.append(Spacer(1, 8))
    els.append(p("Phase 4 completed the system with 10 more enterprise scenarios, 3 advanced labs, and interview preparation exercises. This brought the total to 23 scenarios and 11 labs (22 exercises), covering every major skill domain an IT Applications Analyst III needs."))
    els.append(Spacer(1, 6))
    phase4_scenarios = [
        ["M4", "Maximo", "Asset Transfer Reconciliation", "SQL comparison + audit report for 23 fleet vehicles"],
        ["M5", "Maximo", "Slow Query Performance", "Missing index, stale statistics, 30s → 45ms improvement"],
        ["M6", "Maximo", "Inventory Reorder Failure", "Silent cron failure from wrong SITEID parameter"],
        ["M7", "Maximo", "IoT Meter Integration", "Requirements + REST API design for 500 water sensors"],
        ["T5", "Incode", "Court Statistics Mismatch", "WHERE clause missing DISMISSED status (15% undercount)"],
        ["T6", "Incode", "Version Upgrade Testing", "35-test-case plan for Incode v10 → v11"],
        ["T7", "Incode", "Online Payment Portal", "PayGov gateway configuration + end-to-end testing"],
        ["E4", "e-Builder", "RFI Workflow Stuck", "Workflow stall from reviewer on leave + no escalation"],
        ["E5", "e-Builder", "CIP Executive Report", "RAG status dashboard with CASE expressions"],
        ["E6", "e-Builder", "Department Onboarding", "Role matrix, federal grant compliance, dual-approval"],
    ]
    els.append(tbl(["ID", "System", "Scenario", "Key Teaching Point"], phase4_scenarios, [25, 45, 130, 260]))
    els.append(Spacer(1, 8))
    els.append(h3("Advanced Labs Added"))
    labs_p4 = [
        ["PowerShell Lab", "3", "Certificate expiry check, IIS log parsing, service health monitoring"],
        ["Advanced Debugging Lab", "2", ".NET stack trace analysis, formal Root Cause Analysis document"],
        ["Interview Preparation Lab", "2", "STAR answer crafting, systematic methodology frameworks"],
    ]
    els.append(tbl(["Lab", "Exercises", "Topics"], labs_p4, [120, 45, 295]))
    els.append(PageBreak())

    # 6. THE SIX AGENTS
    els.append(h1("6. The Six Training Agents — Roles & Responsibilities"))
    els.append(Spacer(1, 8))
    els.append(p("The Training Twin uses six specialized agents that mirror the actual roles and responsibilities of a municipal IT Applications team. Each agent handles specific types of work orders and provides domain-specific teaching content."))
    els.append(Spacer(1, 6))
    agents = [
        ["Shift Director", "purple", "Monitors backlog and KPIs, routes work by SLA/priority/business impact, manages shift phases, coordinates other agents. Does not do technical work — orchestrates the team.",
         "Dispatches work orders by matching incident type to the right specialist. Monitors the queue and re-dispatches if an agent's queue is empty. Triggers phase transitions (morning → midday → end-of-day). Ensures SLA deadlines are met."],
        ["Requirements & Documentation", "blue", "Turns user requests into formal deliverables: business requirements, functional specs, process flows, SOPs, change requests, release notes, test plans.",
         "Handles M7 (IoT integration design), T6 (upgrade test plan), T7 (payment portal requirements), E5 (executive report), E6 (department onboarding). Produces formal documents that match municipal IT standards."],
        ["SQL & Reporting", "green", "Handles all database and reporting tasks: SQL Server queries, Oracle SQL, stored procedures, Crystal Reports, SSRS, Power BI. Debugs report totals, fixes stored procedures, creates new reports.",
         "Handles M4 (asset reconciliation SQL), M5 (query performance tuning), T2 (payment reconciliation), T3 (docket Crystal Report), T5 (statistics WHERE fix), E2 (budget variance), E5 (CIP RAG report). Writes and explains every SQL query."],
        ["Application & Integration", "orange", "Handles enterprise application support, web service failures, API integrations, IIS/Apache configs, SharePoint sync, ERP workflows. Diagnoses endpoint failures, authentication issues, and data mapping problems.",
         "Handles M1 (Maximo cron task), M3 (SOAP GL interface), M6 (reorder cron), T1 (citation XML import), T4 (TCIC/NCIC certs), T7 (PayGov gateway), E1 (API key rotation), E3 (SharePoint sync), E4 (RFI workflow)."],
        ["QA & Debugging", "red", "Handles bug reproduction, root cause analysis, log review, regression testing, UAT validation, defect documentation. Teaches systematic debugging methodology.",
         "Handles M2 (duplicate key debugging), T6 (upgrade regression testing). Teaches: how to read .NET stack traces, how to write defect reports, how to create test plans, how to prove a fix worked."],
        ["Mentor / Learning Coach", "indigo", "After every task: summarizes what happened, explains why that action was taken, defines the technical concept, provides a mini-lesson, and generates interview-ready STAR answers.",
         "Active on EVERY scenario. Provides the 'Ask Why' explanation, the 'Mentor Explanation' deep-dive, and the 'Interview Prep' STAR answer. Adapts language for beginner, analyst, or interview-prep modes."],
    ]
    for name, color, role, how in agents:
        els.append(h3(f"{name} Agent"))
        els.append(p(f"<b>Role:</b> {role}"))
        els.append(p(f"<b>How it handles scenarios:</b> {how}"))
        els.append(Spacer(1, 4))
    els.append(PageBreak())

    # 7. MAXIMO SCENARIOS
    els.append(h1("7. Maximo Scenarios (M1–M7)"))
    els.append(Spacer(1, 8))
    mx_detail = [
        ["M1", "PM Work Order Generation Failure", "PMWOGen cron crashes on decommissioned asset", "Shift Director detects overdue PMs → App & Integration agent opens Cron Task Setup, queries mx_pm + mx_asset, finds orphaned PM-1003, deactivates it, restarts cron → Mentor explains batch processing and data integrity validation"],
        ["M2", "Duplicate Key on WOACTIVITY", "SQL Server error 2601 from stale statistics", "QA & Debugging agent reads SQL Server error log → checks sys.dm_exec_query_stats and sys.dm_db_missing_index_details → updates statistics with FULLSCAN → rebuilds indexes → performance: 9,875ms → 23ms"],
        ["M3", "GL Integration Failure", "Finance endpoint URL changed silently", "App & Integration agent checks mx_maxintmsgtrk → finds 'Connection refused' errors → checks endpoint config → updates URL → reprocesses 47 messages → Mentor teaches integration monitoring patterns"],
        ["M4", "Asset Transfer Reconciliation", "23 vehicles have wrong locations", "SQL & Reporting agent writes comparison JOIN → identifies 23 mismatches → bulk updates with audit trail → generates reconciliation report for City Auditor"],
        ["M5", "Slow Work Order Queries", "Missing composite index + stale stats", "SQL & Reporting agent uses DMVs to find slow queries → creates covering index on (status, location) → updates statistics → verifies execution plan shows Index Seek"],
        ["M6", "Inventory Reorder Failure", "Wrong SITEID in cron task parameter", "App & Integration agent identifies the 'silent failure' pattern → finds SITEID = 'MAIN' instead of 'CCTX' → fixes parameter → manually triggers emergency POs → Mentor teaches silent failure detection"],
        ["M7", "IoT Meter Integration Design", "New integration from scratch", "Requirements agent gathers requirements from Water Utility → designs CSV → PowerShell ETL → Maximo REST API architecture → creates functional spec → Mentor teaches requirements-to-design lifecycle"],
    ]
    els.append(tbl(["ID", "Scenario", "Root Cause", "Agent Handling"], mx_detail, [20, 100, 120, 220]))
    els.append(PageBreak())

    # 8. INCODE SCENARIOS
    els.append(h1("8. Tyler Incode Scenarios (T1–T7)"))
    els.append(Spacer(1, 8))
    ic_detail = [
        ["T1", "Citation Import Failure", "XML schema v3.1 vs v3.2 mismatch", "App & Integration agent checks ic_citation import errors → compares XSD versions → adds VehicleMake2 element → reprocesses 142 citations → Mentor teaches XML schema management"],
        ["T2", "Payment Posting Mismatch", "$340 from warrant business rule", "SQL & Reporting agent writes reconciliation query joining ic_payment + ic_case → finds unposted payments on WARRANT cases → recalls warrants, posts payments → Mentor teaches payment reconciliation methodology"],
        ["T3", "Docket Report Blank", "NULL judge_id in INNER JOIN", "SQL & Reporting agent traces Crystal Report to stored procedure → finds NULL judge_id → explains NULL = NULL evaluates to FALSE → fixes docket record + adds COALESCE to SP → Mentor teaches NULL handling"],
        ["T4", "TCIC/NCIC Warrant Upload", "SSL certificate expired", "App & Integration agent reads upload log → checks certificate store → finds expired cert → generates new cert via PowerShell → Mentor teaches certificate lifecycle and mTLS"],
        ["T5", "Statistics Mismatch", "WHERE excludes DISMISSED status", "SQL & Reporting agent compares report definition against legal definition of 'disposition' → fixes IN clause → validates against 6 months of history → Mentor teaches domain knowledge importance"],
        ["T6", "Version Upgrade Testing", "35-case test plan needed", "QA & Debugging agent creates 5-category test plan → data migration, regression, new features, performance, integrations → Requirements agent documents go/no-go recommendation"],
        ["T7", "Online Payment Portal", "PayGov gateway configuration", "App & Integration agent configures gateway settings → maps transaction fields → Requirements agent creates test cases → QA agent executes → Mentor teaches payment gateway integration patterns"],
    ]
    els.append(tbl(["ID", "Scenario", "Root Cause", "Agent Handling"], ic_detail, [20, 100, 110, 230]))
    els.append(PageBreak())

    # 9. E-BUILDER SCENARIOS
    els.append(h1("9. e-Builder Scenarios (E1–E6)"))
    els.append(Spacer(1, 8))
    eb_detail = [
        ["E1", "API Auth Failure", "API key rotated without notification", "App & Integration agent checks HTTP 401 → generates new key in e-Builder admin → updates config → backfills 2-day data gap → Mentor teaches API key lifecycle management"],
        ["E2", "CIP Budget Variance", "$180K from unposted invoices", "SQL & Reporting agent queries eb_cost_item → finds 3 unposted items totaling $180K → posts to finance → verifies zero variance → generates reconciliation memo for City Manager"],
        ["E3", "Document Sync Failure", "SharePoint service account expired", "App & Integration agent checks eb_document sync errors → identifies OAuth2 token failure → resets service account password → resyncs 34 documents → Mentor teaches service account management"],
        ["E4", "RFI Workflow Stuck", "Reviewer on leave, no backup routing", "App & Integration agent finds RFI-001-001 stuck 12 days → reassigns to deputy engineer → adds escalation rules to all CIP workflows → Mentor teaches workflow exception handling"],
        ["E5", "CIP Executive Report", "Monthly council report needed", "SQL & Reporting agent writes RAG status queries with CASE expressions → joins project, cost, RFI, and change order data → generates executive dashboard → Mentor teaches executive communication"],
        ["E6", "Department Onboarding", "New team needs e-Builder access", "Requirements agent creates role matrix → configures accounts with least-privilege → adds federal grant compliance modules → creates training docs → Mentor teaches onboarding methodology"],
    ]
    els.append(tbl(["ID", "Scenario", "Root Cause/Need", "Agent Handling"], eb_detail, [20, 95, 115, 230]))
    els.append(PageBreak())

    # 10. LABS
    els.append(h1("10. Complete Lab Inventory"))
    els.append(Spacer(1, 8))
    all_labs = [
        ["SQL Fundamentals", "3", "sql_server", "CREATE TABLE, LEFT JOIN, Cartesian product debugging, SQL Server vs Oracle"],
        ["Reporting & BI", "1", "crystal_reports", "Parameterized stored procedures for SSRS/Crystal Reports"],
        ["Integration & Web Services", "1", "web_services", "REST API 500 error diagnosis, NullReferenceException fix"],
        ["Debugging & QA", "1", "debugging", "Complete defect report writing with severity/priority"],
        ["Requirements & Docs", "1", "requirements", "Business requirements from vague user request"],
        ["IBM Maximo", "3", "sql_server", "Query overdue PMs, find orphaned PMs, check integration errors"],
        ["Tyler Incode", "3", "sql_server", "Reconcile payments, calculate FTA revenue, debug NULL join"],
        ["e-Builder / Trimble", "2", "sql_server", "CIP budget health with CASE, find unposted costs with HAVING"],
        ["PowerShell Automation", "3", "powershell", "Certificate monitoring, IIS log parsing, service health checks"],
        ["Advanced Debugging", "2", "debugging", ".NET stack trace analysis, formal Root Cause Analysis writing"],
        ["Interview Preparation", "2", "requirements", "STAR answer crafting, report debugging methodology framework"],
    ]
    els.append(tbl(["Lab Name", "Exercises", "Domain", "Skills Taught"], all_labs, [100, 45, 65, 250]))
    els.append(PageBreak())

    # 11. SKILLS MATRIX
    els.append(h1("11. Skills Coverage Matrix"))
    els.append(Spacer(1, 8))
    skills = [
        ["SQL Server", "M1, M2, M4, M5, T2, T3, T5, E2, E5", "All SQL labs", "Queries, joins, indexes, statistics, DMVs"],
        ["Stored Procedures", "M1, T3, T5", "Reporting lab", "Parameters, CASE, NULLIF, ALTER PROCEDURE"],
        ["Crystal Reports / SSRS", "T3, T5", "Reporting lab", "SP data sources, NULL handling, parameterized reports"],
        ["Power BI", "E5", "—", "Executive dashboards, RAG status, KPIs"],
        ["Web Services (REST/SOAP)", "M3, T1, T4, T7, E1, E3", "Integration lab", "SOAP faults, REST 401/500, mTLS, OAuth2"],
        ["PowerShell", "T4, M7, E3", "PowerShell lab", "Certificates, IIS logs, service monitoring, ETL"],
        ["IIS / Apache", "M2, T4", "PowerShell lab", "SSL bindings, log analysis, app pool management"],
        ["Debugging", "M1, M2, M6, T3, T5, E4", "Both debug labs", "Stack traces, RCA writing, systematic isolation"],
        ["Requirements", "M7, T6, T7, E5, E6", "Requirements lab", "Business reqs, functional specs, test plans"],
        ["Process Documentation", "All scenarios", "All labs", "Incident tickets, change requests, SOPs, runbooks"],
        ["Change Management", "M1, M3, M6, T1, T4, E1, E4", "—", "Change requests, approval workflows, release notes"],
        ["SharePoint", "E3, E6", "—", "Document sync, service accounts, OAuth2"],
        ["ERP / Asset Management", "M1-M7", "Maximo lab", "Work orders, PMs, assets, locations, inventory"],
    ]
    els.append(tbl(["Skill Domain", "Scenarios", "Labs", "Concepts Taught"], skills, [85, 120, 75, 180]))
    els.append(PageBreak())

    # 12. TEACHING METHODOLOGY
    els.append(h1("12. Teaching Methodology: The 8-Panel System"))
    els.append(Spacer(1, 8))
    els.append(p("Every training task provides 8 distinct learning perspectives, accessible via panel buttons in the Training Ops Console. This multi-angle approach ensures users understand not just WHAT to do, but WHY, HOW, and how to EXPLAIN it."))
    els.append(Spacer(1, 6))
    panels = [
        ["1. Teach Me", "Business context, evidence reviewed, decision made, mentor explanation", "Teaches the analyst thought process from business problem to technical investigation"],
        ["2. Tool View", "Step-by-step tool interaction with live SQL results", "Shows exactly what the agent opened, queried, and observed inside each system"],
        ["3. Technical Detail", "Detailed technical analysis: SQL queries, system internals, error patterns", "Provides the deep technical knowledge needed to diagnose independently"],
        ["4. Show SQL / Config", "Exact SQL statements, PowerShell scripts, configuration changes", "The precise commands an analyst would execute — copy-paste ready"],
        ["5. Ask Why", "Root cause reasoning, why this approach over alternatives", "Develops critical thinking about diagnostic methodology"],
        ["6. Documentation", "What a human analyst should document: tickets, CRs, specs, reports", "Teaches the documentation discipline required in enterprise IT"],
        ["7. Testing", "What to test after the fix: verification steps, regression checks", "Ensures fixes are proven, not assumed"],
        ["8. Interview Prep", "STAR-format answer ready for hiring panels", "Translates technical work into career-advancing interview responses"],
    ]
    els.append(tbl(["Panel", "Content", "Learning Objective"], panels, [80, 190, 190]))
    els.append(Spacer(1, 15))
    els.append(p(f'<i>Report generated: {datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")} · {BRANDING}</i>'))

    doc.build(els, canvasmaker=FooterCanvas)
    print(f"Report generated: {PDF_PATH} ({PDF_PATH.stat().st_size // 1024} KB, {len(els)} elements)")


if __name__ == "__main__":
    build()

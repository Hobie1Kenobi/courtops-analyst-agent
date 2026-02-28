"""Enterprise agent actions — live queries and fixes against simulated legacy schemas.

Each action represents what an analyst would do inside the real tool:
open it, run a query, read the result, apply a fix, verify.
Results are returned as structured steps the UI can render as a live walkthrough.
"""

import json
from datetime import date, datetime, timedelta
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.enterprise.models import *


def execute_scenario_actions(db: Session, scenario_key: str) -> list[dict]:
    """Run the concrete DB actions for a scenario and return step-by-step results."""
    dispatch = {
        "maximo_pm_failure": _maximo_pm_failure,
        "maximo_duplicate_key": _maximo_duplicate_key,
        "maximo_finance_integration": _maximo_finance_integration,
        "incode_citation_import": _incode_citation_import,
        "incode_payment_mismatch": _incode_payment_mismatch,
        "incode_docket_error": _incode_docket_error,
        "incode_warrant_interface": _incode_warrant_interface,
        "ebuilder_api_auth": _ebuilder_api_auth,
        "ebuilder_cost_mismatch": _ebuilder_cost_mismatch,
        "ebuilder_doc_sync": _ebuilder_doc_sync,
    }
    handler = dispatch.get(scenario_key)
    if not handler:
        return [{"step": 1, "tool": "system", "action": "No handler for scenario", "sql": None, "result": None}]
    return handler(db)


# ================================================================
#  MAXIMO ACTIONS
# ================================================================

def _maximo_pm_failure(db: Session) -> list[dict]:
    steps = []

    # Step 1: Check cron task
    cron = db.query(MaximoCronTask).filter(MaximoCronTask.crontaskname == "PMWOGEN").first()
    steps.append({
        "step": 1, "tool": "maximo", "panel": "Cron Task Setup",
        "action": "Open Cron Task Setup — check PMWOGEN status",
        "sql": "SELECT crontaskname, active, lastrun, nextrun FROM mx_crontaskdef WHERE crontaskname = 'PMWOGEN';",
        "result": {"crontaskname": cron.crontaskname, "active": cron.active,
                   "lastrun": str(cron.lastrun), "nextrun": str(cron.nextrun)} if cron else "NOT FOUND",
        "observation": f"PMWOGEN last ran {cron.lastrun.strftime('%Y-%m-%d %H:%M') if cron and cron.lastrun else 'NEVER'}. Checking overdue PMs...",
    })

    # Step 2: Find overdue PMs
    overdue = db.query(MaximoPM).filter(MaximoPM.status == "ACTIVE", MaximoPM.nextdate < date.today()).all()
    steps.append({
        "step": 2, "tool": "maximo", "panel": "Preventive Maintenance",
        "action": f"Query overdue PMs — found {len(overdue)} past due",
        "sql": "SELECT pmnum, description, assetnum, nextdate, status FROM mx_pm WHERE status = 'ACTIVE' AND nextdate < CURRENT_DATE;",
        "result": [{"pmnum": p.pmnum, "assetnum": p.assetnum, "nextdate": str(p.nextdate)} for p in overdue[:5]],
        "observation": f"{len(overdue)} PMs are overdue. Checking asset statuses for these PMs...",
    })

    # Step 3: Find the bad PM (active PM on decommissioned asset)
    bad_pms = []
    for pm in db.query(MaximoPM).filter(MaximoPM.status == "ACTIVE").all():
        if pm.assetnum:
            asset = db.query(MaximoAsset).filter(MaximoAsset.assetnum == pm.assetnum).first()
            if asset and asset.status == MaximoAssetStatus.DECOMMISSIONED:
                bad_pms.append({"pmnum": pm.pmnum, "assetnum": pm.assetnum, "asset_status": asset.status.value})
    steps.append({
        "step": 3, "tool": "maximo", "panel": "PM / Asset Cross-Reference",
        "action": f"Cross-reference PMs with asset status — found {len(bad_pms)} PMs on decommissioned assets",
        "sql": "SELECT p.pmnum, p.assetnum, a.status AS asset_status FROM mx_pm p JOIN mx_asset a ON p.assetnum = a.assetnum WHERE p.status = 'ACTIVE' AND a.status = 'DECOMMISSIONED';",
        "result": bad_pms if bad_pms else [{"note": "No mismatched PMs found (may already be fixed)"}],
        "observation": "ROOT CAUSE IDENTIFIED: Active PM references a decommissioned asset, causing PMWOGen batch failure." if bad_pms else "No bad PMs found — may have been fixed already.",
    })

    # Step 4: Apply fix
    fixed = 0
    for pm in db.query(MaximoPM).filter(MaximoPM.status == "ACTIVE").all():
        if pm.assetnum:
            asset = db.query(MaximoAsset).filter(MaximoAsset.assetnum == pm.assetnum).first()
            if asset and asset.status == MaximoAssetStatus.DECOMMISSIONED:
                pm.status = MaximoPMStatus.INACTIVE
                fixed += 1
    db.commit()
    steps.append({
        "step": 4, "tool": "maximo", "panel": "PM Record — Apply Fix",
        "action": f"Deactivated {fixed} PMs linked to decommissioned assets",
        "sql": "UPDATE mx_pm SET status = 'INACTIVE' WHERE pmnum IN (SELECT p.pmnum FROM mx_pm p JOIN mx_asset a ON p.assetnum = a.assetnum WHERE p.status = 'ACTIVE' AND a.status = 'DECOMMISSIONED');",
        "result": {"pms_deactivated": fixed},
        "observation": f"Fix applied: {fixed} PMs deactivated. Restarting PMWOGEN cron task...",
    })

    # Step 5: "Restart" cron and verify
    if cron:
        cron.lastrun = datetime.utcnow()
        cron.nextrun = datetime.utcnow() + timedelta(hours=1)
        db.commit()
    remaining_overdue = db.query(MaximoPM).filter(MaximoPM.status == "ACTIVE", MaximoPM.nextdate < date.today()).count()
    steps.append({
        "step": 5, "tool": "maximo", "panel": "Verification",
        "action": "Cron task restarted — verifying PM generation",
        "sql": "SELECT COUNT(*) AS remaining_overdue FROM mx_pm WHERE status = 'ACTIVE' AND nextdate < CURRENT_DATE;",
        "result": {"remaining_overdue": remaining_overdue, "cron_restarted": True},
        "observation": f"Verification complete. {remaining_overdue} PMs still need WO generation (will be processed by next cron run). Incident resolved.",
    })

    return steps


def _maximo_duplicate_key(db: Session) -> list[dict]:
    steps = []
    wo_count = db.query(MaximoWorkOrder).count()
    steps.append({
        "step": 1, "tool": "maximo", "panel": "Work Order List",
        "action": "Open Work Order application — check for error pattern",
        "sql": "SELECT wonum, status, worktype, assetnum, reportdate FROM mx_workorder ORDER BY reportdate DESC LIMIT 10;",
        "result": [{"wonum": w.wonum, "status": w.status.value, "assetnum": w.assetnum} for w in db.query(MaximoWorkOrder).order_by(MaximoWorkOrder.reportdate.desc()).limit(5).all()],
        "observation": f"System has {wo_count} work orders. Error is intermittent — checking database statistics...",
    })
    steps.append({
        "step": 2, "tool": "sql_server", "panel": "Database Maintenance",
        "action": "Check and update database statistics",
        "sql": "UPDATE STATISTICS mx_workorder WITH FULLSCAN;\nALTER INDEX ALL ON mx_workorder REBUILD;",
        "result": {"statistics_updated": True, "indexes_rebuilt": True, "performance_before_ms": 9875, "performance_after_ms": 23},
        "observation": "Statistics updated. Query performance improved from 9,875ms to 23ms. This reduces the race condition window for duplicate key generation.",
    })
    steps.append({
        "step": 3, "tool": "maximo", "panel": "Verification",
        "action": "Verify — create 3 test work orders simultaneously",
        "sql": "-- Test: Create 3 work orders in rapid succession\n-- Result: All 3 created without duplicate key error ✓",
        "result": {"test_work_orders_created": 3, "duplicate_errors": 0},
        "observation": "Fix verified — no duplicate key errors. Setting up weekly statistics maintenance job.",
    })
    return steps


def _maximo_finance_integration(db: Session) -> list[dict]:
    steps = []
    errors = db.query(MaximoIntMessage).filter(MaximoIntMessage.status == "ERROR").all()
    steps.append({
        "step": 1, "tool": "maximo", "panel": "Integration > Message Tracking",
        "action": f"Open Message Tracking — found {len(errors)} error messages",
        "sql": "SELECT msgid, extsysname, ifacename, status, msgerror FROM mx_maxintmsgtrk WHERE status = 'ERROR';",
        "result": [{"msgid": m.msgid, "error": m.msgerror[:80] if m.msgerror else ""} for m in errors[:3]],
        "observation": f"{len(errors)} messages stuck in ERROR. All show 'Connection refused' — endpoint issue.",
    })
    steps.append({
        "step": 2, "tool": "maximo", "panel": "Integration > End Points",
        "action": "Check endpoint configuration — URL is outdated",
        "sql": "-- Endpoint: ABORFINANCE\n-- Current URL: https://finance-old.cctx.gov/gl/soap  ← WRONG\n-- Correct URL: https://finance.cctx.gov/api/gl/soap",
        "result": {"current_url": "https://finance-old.cctx.gov/gl/soap", "correct_url": "https://finance.cctx.gov/api/gl/soap"},
        "observation": "Finance system migrated to new URL during weekend maintenance. Updating endpoint...",
    })
    for m in errors:
        m.status = "PROCESSED"
    db.commit()
    steps.append({
        "step": 3, "tool": "maximo", "panel": "Message Reprocessing",
        "action": f"Updated endpoint URL and reprocessed {len(errors)} messages",
        "sql": "-- Update endpoint URL in Maximo Integration config\n-- Reprocess all ERROR messages\nUPDATE mx_maxintmsgtrk SET status = 'PROCESSED' WHERE status = 'ERROR';",
        "result": {"messages_reprocessed": len(errors), "all_successful": True},
        "observation": f"All {len(errors)} messages reprocessed successfully. GL postings confirmed by Finance team.",
    })
    return steps


def _incode_citation_import(db: Session) -> list[dict]:
    steps = []
    errors = db.query(IncodeCitation).filter(IncodeCitation.import_status == "ERROR").all()
    steps.append({
        "step": 1, "tool": "incode", "panel": "Citation Import Queue",
        "action": f"Open Import Queue — found {len(errors)} failed citations",
        "sql": "SELECT citation_number, violation_desc, import_status, import_error FROM ic_citation WHERE import_status = 'ERROR';",
        "result": [{"citation": c.citation_number, "error": c.import_error[:70] if c.import_error else ""} for c in errors[:3]],
        "observation": f"{len(errors)} citations failed with XML parse error. Unexpected element 'VehicleMake2' — schema mismatch.",
    })
    steps.append({
        "step": 2, "tool": "incode", "panel": "Import Configuration",
        "action": "Compare XSD schema versions — v3.1 vs v3.2",
        "sql": "-- Our XSD: version 3.1 — missing VehicleMake2 element\n-- PD RMS export: version 3.2 — added VehicleMake2\n-- Fix: Add <xs:element name=\"VehicleMake2\" type=\"xs:string\" minOccurs=\"0\"/>",
        "result": {"our_version": "3.1", "pd_version": "3.2", "missing_element": "VehicleMake2"},
        "observation": "Schema mismatch confirmed. Updating XSD and reprocessing...",
    })
    for c in errors:
        c.import_status = "IMPORTED"
        c.import_error = None
    db.commit()
    steps.append({
        "step": 3, "tool": "incode", "panel": "Import Reprocessing",
        "action": f"Updated XSD schema, reprocessed {len(errors)} citations",
        "sql": "UPDATE ic_citation SET import_status = 'IMPORTED', import_error = NULL WHERE import_status = 'ERROR';",
        "result": {"citations_imported": len(errors), "errors_remaining": 0},
        "observation": f"All {len(errors)} citations imported successfully. Clerks can now process arraignments.",
    })
    return steps


def _incode_payment_mismatch(db: Session) -> list[dict]:
    steps = []
    unposted = db.query(IncodePayment).filter(IncodePayment.posted == False, IncodePayment.gateway_txn_id != None).all()
    total_unposted = sum(p.amount for p in unposted)
    steps.append({
        "step": 1, "tool": "incode", "panel": "Payment Reconciliation",
        "action": f"Run reconciliation — found {len(unposted)} unposted gateway payments totaling ${total_unposted:,.2f}",
        "sql": "SELECT p.payment_id, p.case_number, p.amount, p.gateway_txn_id, c.status AS case_status FROM ic_payment p JOIN ic_case c ON p.case_number = c.case_number WHERE p.posted = FALSE AND p.gateway_txn_id IS NOT NULL;",
        "result": [{"payment_id": p.payment_id, "case": p.case_number, "amount": p.amount} for p in unposted[:5]],
        "observation": f"Found ${total_unposted:,.2f} in unposted payments. Checking case statuses...",
    })
    steps.append({
        "step": 2, "tool": "incode", "panel": "Case Status Review",
        "action": "Unposted payments are for WARRANT-status cases — business rule rejection",
        "sql": "-- Cases in WARRANT status reject online payments\n-- Need to recall warrants first, then post payments",
        "result": {"cause": "WARRANT status business rule blocks payment posting", "action_needed": "Recall warrants, post payments, update balances"},
        "observation": "Business rule confirmed: payments on WARRANT cases require warrant recall first.",
    })
    for p in unposted:
        p.posted = True
        p.posted_date = datetime.utcnow()
    db.commit()
    steps.append({
        "step": 3, "tool": "incode", "panel": "Payment Posting",
        "action": f"Recalled warrants and posted {len(unposted)} payments — ${total_unposted:,.2f}",
        "sql": "UPDATE ic_payment SET posted = TRUE, posted_date = CURRENT_TIMESTAMP WHERE posted = FALSE AND gateway_txn_id IS NOT NULL;",
        "result": {"payments_posted": len(unposted), "total_posted": total_unposted, "variance_remaining": 0},
        "observation": f"Reconciliation complete. All payments posted. Variance: $0.00 ✓",
    })
    return steps


def _incode_docket_error(db: Session) -> list[dict]:
    steps = []
    docket_b = db.query(IncodeDocket).filter(IncodeDocket.courtroom == "B").first()
    steps.append({
        "step": 1, "tool": "incode", "panel": "Docket Management",
        "action": "Open Courtroom B docket — check judge assignment",
        "sql": "SELECT docket_id, docket_date, courtroom, judge_id, judge_name, case_count FROM ic_docket WHERE courtroom = 'B';",
        "result": {"docket_id": docket_b.docket_id if docket_b else None, "judge_id": docket_b.judge_id if docket_b else "NULL", "judge_name": docket_b.judge_name if docket_b else "NULL"} if docket_b else {"error": "No docket found"},
        "observation": f"Courtroom B docket has judge_id = {'NULL — this is the problem!' if docket_b and not docket_b.judge_id else docket_b.judge_id if docket_b else 'N/A'}",
    })
    steps.append({
        "step": 2, "tool": "crystal_reports", "panel": "Report Data Source",
        "action": "Crystal Report sp_GenerateDocket uses INNER JOIN on judge_id — NULL drops all rows",
        "sql": "-- The stored procedure:\n-- FROM ic_case c INNER JOIN ic_docket d\n--   ON c.courtroom = d.courtroom AND c.judge_id = d.judge_id\n-- When d.judge_id IS NULL, no rows match (NULL ≠ NULL in SQL)",
        "result": {"root_cause": "INNER JOIN on NULL judge_id returns 0 rows", "fix": "Update judge assignment + fix SP to handle NULL"},
        "observation": "NULL handling bug confirmed. NULL = NULL evaluates to FALSE in SQL, so INNER JOIN drops everything.",
    })
    if docket_b:
        docket_b.judge_id = "JDG-002"
        docket_b.judge_name = "Judge Mitchell"
        db.commit()
    steps.append({
        "step": 3, "tool": "incode", "panel": "Docket Fix + Verification",
        "action": "Updated Courtroom B judge assignment and regenerated docket",
        "sql": "UPDATE ic_docket SET judge_id = 'JDG-002', judge_name = 'Judge Mitchell' WHERE courtroom = 'B';\n-- Regenerate: EXEC sp_GenerateDocket @Courtroom = 'B';",
        "result": {"judge_assigned": "JDG-002 - Judge Mitchell", "docket_regenerated": True},
        "observation": "Docket now generates correctly. Added COALESCE to stored procedure to prevent future NULL issues.",
    })
    return steps


def _incode_warrant_interface(db: Session) -> list[dict]:
    steps = []
    steps.append({
        "step": 1, "tool": "incode", "panel": "Warrant Upload Status",
        "action": "Check TCIC/NCIC upload status — authentication failures detected",
        "sql": "SELECT warrant_number, case_number, status, tcic_status, upload_error FROM ic_warrant WHERE status = 'ACTIVE' AND (tcic_status = 'ERROR' OR tcic_status IS NULL);",
        "result": {"warrants_affected": 15, "error": "SSL Handshake Error: Certificate expired 2026-02-24"},
        "observation": "CRITICAL: 15 active warrants not in state system. Certificate expired yesterday.",
    })
    steps.append({
        "step": 2, "tool": "powershell", "panel": "Certificate Management",
        "action": "Check certificate expiration and generate new CSR",
        "sql": "# PowerShell:\nGet-ChildItem Cert:\\LocalMachine\\My | Where-Object {$_.Subject -like '*Warrant*'}\n# Result: CN=CCTX-Warrant-Upload, NotAfter=2/24/2026 ← EXPIRED\n\n$cert = New-SelfSignedCertificate -Subject 'CN=CCTX-Warrant-Upload' -KeyAlgorithm RSA -KeyLength 2048 -NotAfter (Get-Date).AddYears(2)",
        "result": {"old_cert_expired": "2026-02-24", "new_cert_generated": True, "new_expiry": "2028-02-26"},
        "observation": "New certificate generated. Submitting CSR to DPS for signing...",
    })
    steps.append({
        "step": 3, "tool": "incode", "panel": "Interface Restoration",
        "action": "Installed signed cert, reprocessed 15 warrant uploads",
        "sql": "-- Install signed cert in IIS\n-- Update Incode warrant upload certificate config\n-- Reprocess failed uploads",
        "result": {"cert_installed": True, "warrants_uploaded": 15, "tcic_confirmed": True},
        "observation": "All 15 warrants now in TCIC/NCIC. Interface restored. Added 30-day expiry monitoring alert.",
    })
    return steps


def _ebuilder_api_auth(db: Session) -> list[dict]:
    steps = []
    steps.append({
        "step": 1, "tool": "ebuilder", "panel": "API Integration Log",
        "action": "Check API sync log — 401 Unauthorized since key rotation",
        "sql": "-- Integration log:\n-- POST https://api2.e-builder.net/api/v2/costs\n-- Response: 401 Unauthorized\n-- Body: {\"error\": \"Invalid or expired API key\"}",
        "result": {"http_status": 401, "error": "Invalid or expired API key", "days_down": 2},
        "observation": "API key was rotated during security maintenance. Old key invalidated.",
    })
    steps.append({
        "step": 2, "tool": "ebuilder", "panel": "Admin > API Access",
        "action": "Generate new API key and update integration config",
        "sql": "# e-Builder Admin > Administration Tools > APIs > Access\n# Click 'Create Key' > Select API User > Download\n# Test: curl -H 'Authorization: Bearer NEW_KEY' https://api2.e-builder.net/api/v2/projects",
        "result": {"new_key_generated": True, "test_response": "200 OK", "projects_returned": 8},
        "observation": "New key works. Updating integration config and triggering 2-day backfill sync...",
    })
    steps.append({
        "step": 3, "tool": "ebuilder", "panel": "Sync Verification",
        "action": "Config updated, 2-day data gap synced successfully",
        "sql": "SELECT project_id, COUNT(*) AS cost_items, SUM(actual) AS total FROM eb_cost_item WHERE invoice_date >= '2026-02-23' GROUP BY project_id;",
        "result": {"config_updated": True, "days_backfilled": 2, "cost_items_synced": "all"},
        "observation": "API sync restored. All project cost data current. Added integration team to security maintenance notifications.",
    })
    return steps


def _ebuilder_cost_mismatch(db: Session) -> list[dict]:
    steps = []
    unposted = db.query(EBuilderCostItem).filter(EBuilderCostItem.project_id == "CIP-2024-001", EBuilderCostItem.posted_to_finance == False).all()
    unposted_total = sum(c.actual for c in unposted)
    steps.append({
        "step": 1, "tool": "ebuilder", "panel": "Cost Management",
        "action": f"Query Oso Creek project unposted costs — found {len(unposted)} items, ${unposted_total:,.2f}",
        "sql": "SELECT cost_id, cost_code, description, actual, posted_to_finance FROM eb_cost_item WHERE project_id = 'CIP-2024-001' AND posted_to_finance = FALSE;",
        "result": [{"cost_code": c.cost_code, "actual": c.actual, "posted": c.posted_to_finance} for c in unposted[:5]],
        "observation": f"Variance identified: {len(unposted)} invoices totaling ${unposted_total:,.2f} not synced to finance during API outage.",
    })
    for c in unposted:
        c.posted_to_finance = True
    db.commit()
    total = sum(c.actual for c in db.query(EBuilderCostItem).filter(EBuilderCostItem.project_id == "CIP-2024-001").all())
    posted = sum(c.actual for c in db.query(EBuilderCostItem).filter(EBuilderCostItem.project_id == "CIP-2024-001", EBuilderCostItem.posted_to_finance == True).all())
    steps.append({
        "step": 2, "tool": "ebuilder", "panel": "Finance Reconciliation",
        "action": f"Posted {len(unposted)} items to finance — variance resolved",
        "sql": "UPDATE eb_cost_item SET posted_to_finance = TRUE WHERE project_id = 'CIP-2024-001' AND posted_to_finance = FALSE;",
        "result": {"items_posted": len(unposted), "ebuilder_total": round(total, 2), "finance_total": round(posted, 2), "variance": 0},
        "observation": f"Reconciliation complete. e-Builder: ${total:,.2f}, Finance: ${posted:,.2f}. Variance: $0.00 ✓",
    })
    return steps


def _ebuilder_doc_sync(db: Session) -> list[dict]:
    steps = []
    stuck = db.query(EBuilderDocument).filter(EBuilderDocument.sync_status == "ERROR").all()
    steps.append({
        "step": 1, "tool": "ebuilder", "panel": "Document Sync Queue",
        "action": f"Check sync queue — found {len(stuck)} documents with ERROR status",
        "sql": "SELECT doc_id, project_id, title, sync_status, sync_error FROM eb_document WHERE sync_status = 'ERROR';",
        "result": [{"doc_id": d.doc_id, "title": d.title, "error": d.sync_error[:50] if d.sync_error else ""} for d in stuck[:4]],
        "observation": f"{len(stuck)} docs stuck. Error: 'SharePoint API timeout'. Checking service account...",
    })
    steps.append({
        "step": 2, "tool": "azure_ad", "panel": "Service Account",
        "action": "Service account password expired — reset and update config",
        "sql": "# Azure AD > Users > eb-sync-service@cctx.onmicrosoft.com\n# Password expired (90-day rotation policy)\n# Reset password > Update e-Builder sync config > Test Connection ✓",
        "result": {"password_reset": True, "connection_test": "SUCCESS"},
        "observation": "Service account password reset. Connection restored.",
    })
    for d in stuck:
        d.sync_status = "SYNCED"
        d.sync_error = None
    db.commit()
    steps.append({
        "step": 3, "tool": "ebuilder", "panel": "Sync Verification",
        "action": f"Resynced {len(stuck)} documents to SharePoint",
        "sql": "UPDATE eb_document SET sync_status = 'SYNCED', sync_error = NULL WHERE sync_status = 'ERROR';",
        "result": {"documents_synced": len(stuck), "errors_remaining": 0},
        "observation": f"All {len(stuck)} documents synced to SharePoint. Field teams can access current drawings.",
    })
    return steps

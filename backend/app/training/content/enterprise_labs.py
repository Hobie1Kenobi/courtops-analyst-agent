"""Enterprise legacy system hands-on labs."""

ENTERPRISE_LABS = {
    "maximo_lab": {
        "id": "maximo_lab",
        "name": "IBM Maximo Lab",
        "domain": "sql_server",
        "description": "Practice Maximo DBA tasks: query work orders, diagnose PM failures, check cron tasks, fix integration messages.",
        "exercises": [
            {
                "id": "mx_1",
                "title": "Query Overdue Preventive Maintenance",
                "instruction": "Write a SQL query to find all ACTIVE preventive maintenance records in the mx_pm table where the nextdate is before today. Include the PM number, description, asset number, and next date. Sort by next date ascending.",
                "expected_answer": "SELECT pmnum, description, assetnum, nextdate\nFROM mx_pm\nWHERE status = 'ACTIVE'\n  AND nextdate < CURRENT_DATE\nORDER BY nextdate ASC;",
                "explanation": "In Maximo, PM records drive preventive maintenance scheduling. When nextdate is in the past, it means the PM work order should have been generated but wasn't. This is the first query you run when investigating a PMWOGen failure. Always filter on status = 'ACTIVE' because INACTIVE PMs should be ignored.",
                "tip": "In production Maximo, the mx_pm table is actually called PM in the Maximo object layer, but maps to the WORKORDER table with a specific WORKTYPE. Our training schema uses a dedicated table for clarity."
            },
            {
                "id": "mx_2",
                "title": "Find Active PMs on Decommissioned Assets",
                "instruction": "Write a SQL query joining mx_pm and mx_asset to find any ACTIVE PMs that reference assets with a DECOMMISSIONED status. Return the PM number, asset number, PM status, and asset status.",
                "expected_answer": "SELECT p.pmnum, p.assetnum,\n       p.status AS pm_status,\n       a.status AS asset_status\nFROM mx_pm p\nJOIN mx_asset a ON p.assetnum = a.assetnum\nWHERE p.status = 'ACTIVE'\n  AND a.status = 'DECOMMISSIONED';",
                "explanation": "This is the root cause query for the M1 scenario. An active PM pointing to a decommissioned asset is a data integrity issue that can crash the PMWOGen cron task. In enterprise asset management, assets go through lifecycle stages (OPERATING → NOT READY → DECOMMISSIONED). When an asset is decommissioned, all associated PMs should be deactivated. This query finds cases where that cleanup was missed.",
                "tip": "Always use explicit JOIN syntax (not comma-separated tables in FROM) for clarity. In Maximo SQL, always include the SITEID in your WHERE clause for multi-site installations."
            },
            {
                "id": "mx_3",
                "title": "Check Integration Message Errors",
                "instruction": "Write a SQL query to find all ERROR messages in the mx_maxintmsgtrk table for the ABORFINANCE external system. Return the message ID, interface name, error text, and creation date. Sort by creation date descending.",
                "expected_answer": "SELECT msgid, ifacename, msgerror, createdate\nFROM mx_maxintmsgtrk\nWHERE extsysname = 'ABORFINANCE'\n  AND status = 'ERROR'\nORDER BY createdate DESC;",
                "explanation": "The mx_maxintmsgtrk table (Message Tracking) is where Maximo logs all integration messages. When messages fail, they stay in ERROR status until manually reprocessed or the issue is fixed. This is the first query an analyst runs when investigating an integration outage. The msgerror column contains the specific error message that points to the root cause (connection refused, authentication failure, data validation error, etc.).",
                "tip": "In production Maximo, you can also check the Integration > Message Reprocessing UI. But SQL gives you faster access to patterns — for example, you can GROUP BY msgerror to see if all errors have the same cause, or GROUP BY createdate to see when the errors started."
            },
        ],
    },
    "incode_lab": {
        "id": "incode_lab",
        "name": "Tyler Incode Lab",
        "domain": "sql_server",
        "description": "Practice court case management queries: reconcile payments, investigate import failures, debug Crystal Reports.",
        "exercises": [
            {
                "id": "ic_1",
                "title": "Reconcile Unposted Payments",
                "instruction": "Write a SQL query to find all payments in ic_payment that have a gateway_txn_id (not NULL) but are not yet posted (posted = FALSE). Join with ic_case to show the case status. Return payment ID, case number, amount, gateway transaction ID, and case status.",
                "expected_answer": "SELECT p.payment_id, p.case_number, p.amount,\n       p.gateway_txn_id, c.status AS case_status\nFROM ic_payment p\nJOIN ic_case c ON p.case_number = c.case_number\nWHERE p.posted = FALSE\n  AND p.gateway_txn_id IS NOT NULL\nORDER BY p.payment_date DESC;",
                "explanation": "This is the core payment reconciliation query. When the payment gateway processes a transaction but the court system doesn't post it, money has been collected but not recorded. The gateway_txn_id proves the payment was processed externally. The case status tells you WHY it wasn't posted (e.g., WARRANT status blocks automatic posting). This query is run daily as part of the court cashier's reconciliation process.",
                "tip": "Always use IS NOT NULL (not != NULL or <> NULL) when checking for NULL values. In SQL, NULL is not equal to anything, including itself. The expression gateway_txn_id != NULL always evaluates to UNKNOWN (effectively FALSE)."
            },
            {
                "id": "ic_2",
                "title": "Calculate Revenue at Risk — FTA Cases",
                "instruction": "Write a SQL query against ic_case to find all cases with status FTA or WARRANT that have an outstanding balance (balance_due > 0). Group by violation_desc and calculate total balance per violation type, plus count of cases. Order by total balance descending.",
                "expected_answer": "SELECT violation_desc,\n       COUNT(*) AS case_count,\n       SUM(balance_due) AS total_at_risk\nFROM ic_case\nWHERE status IN ('FTA', 'WARRANT')\n  AND balance_due > 0\nGROUP BY violation_desc\nORDER BY total_at_risk DESC;",
                "explanation": "Revenue at Risk (FTA) is a critical report for municipal court management. FTA (Failure to Appear) and WARRANT cases represent money the court has assessed but not collected. Grouping by violation type shows which categories have the most outstanding revenue. This report typically goes to the Court Administrator and is used for collection strategy decisions. The total_at_risk column tells management how much money is potentially uncollectable.",
                "tip": "The IN operator is cleaner than multiple OR conditions. Use SUM() for monetary amounts and COUNT(*) for row counts. Always add a balance_due > 0 filter to exclude cases that have been paid (balance = 0) but still carry the FTA/WARRANT status."
            },
            {
                "id": "ic_3",
                "title": "Debug the NULL Judge Docket Bug",
                "instruction": "Explain in plain English why this Crystal Report stored procedure returns 0 rows for Courtroom B but works for Courtroom A:\n\nSELECT c.case_number, c.violation_desc, d.judge_name\nFROM ic_case c\nINNER JOIN ic_docket d\n  ON c.courtroom = d.courtroom\n  AND c.judge_id = d.judge_id\nWHERE d.courtroom = 'B';",
                "expected_answer": "The bug is that Courtroom B's docket record has judge_id = NULL (the judge was reassigned but the docket wasn't updated). In SQL, NULL = NULL evaluates to FALSE, not TRUE. So the INNER JOIN condition c.judge_id = d.judge_id fails for every row because d.judge_id is NULL — nothing can equal NULL.\n\nFix options:\n1. Update the docket: SET judge_id = 'JDG-002' WHERE courtroom = 'B'\n2. Fix the SP: Use LEFT JOIN or change the join to:\n   ON c.courtroom = d.courtroom\n   AND (c.judge_id = d.judge_id OR d.judge_id IS NULL)\n3. Use COALESCE: AND c.judge_id = COALESCE(d.judge_id, c.judge_id)",
                "explanation": "This is one of the most important SQL concepts for report debugging: NULL comparison behavior. In SQL's three-valued logic, any comparison with NULL returns UNKNOWN (not TRUE or FALSE). This means WHERE x = NULL is never true, and INNER JOIN on a NULL column drops all rows. This is the #1 cause of 'missing data' in Crystal Reports and SSRS. The fix should address both the immediate data issue AND the stored procedure logic to prevent recurrence.",
                "tip": "When a report returns fewer rows than expected, the debugging checklist is: (1) Check for NULL join keys, (2) Check for INNER JOINs that should be LEFT JOINs, (3) Check WHERE clause filters that might be too restrictive, (4) Compare against a direct table count to quantify the gap."
            },
        ],
    },
    "ebuilder_lab": {
        "id": "ebuilder_lab",
        "name": "e-Builder / Trimble Lab",
        "domain": "sql_server",
        "description": "Practice CIP project management queries: analyze budgets, reconcile costs, find document sync issues.",
        "exercises": [
            {
                "id": "eb_1",
                "title": "CIP Budget vs Actual Summary",
                "instruction": "Write a SQL query against eb_project to produce an executive summary showing each project's name, status, budget, actual cost, remaining budget, and percent complete. Add a calculated column 'budget_health' that shows 'OVER BUDGET' if actual exceeds budget, 'ON TRACK' otherwise. Order by budget_total descending.",
                "expected_answer": "SELECT project_name, status,\n       budget_total,\n       actual_cost,\n       budget_remaining,\n       percent_complete,\n       CASE\n           WHEN actual_cost > budget_total THEN 'OVER BUDGET'\n           ELSE 'ON TRACK'\n       END AS budget_health\nFROM eb_project\nORDER BY budget_total DESC;",
                "explanation": "This is a standard CIP executive summary query. The CASE expression adds business logic to raw data — translating numbers into status labels that executives can quickly scan. In municipal CIP reporting, bond-funded projects are closely watched by City Council and the public. An 'OVER BUDGET' flag triggers immediate review. The ORDER BY budget_total DESC puts the largest projects first, which is how executives expect to see CIP reports.",
                "tip": "CASE expressions are one of the most powerful tools in SQL reporting. They let you add business rules directly in the query without modifying application code. You can nest CASE expressions for more complex logic (e.g., OVER BUDGET > 10%, OVER BUDGET > 5%, AT RISK, ON TRACK)."
            },
            {
                "id": "eb_2",
                "title": "Find Unposted Cost Items",
                "instruction": "Write a SQL query to find all cost items in eb_cost_item that have not been posted to the finance system (posted_to_finance = FALSE). Group by project_id and show the count and total dollar amount of unposted items per project. Only include projects with at least $10,000 in unposted costs.",
                "expected_answer": "SELECT project_id,\n       COUNT(*) AS unposted_items,\n       SUM(actual) AS unposted_total\nFROM eb_cost_item\nWHERE posted_to_finance = FALSE\nGROUP BY project_id\nHAVING SUM(actual) >= 10000\nORDER BY unposted_total DESC;",
                "explanation": "This query supports the finance reconciliation process for CIP projects. When cost items are recorded in e-Builder but not posted to the city's financial system, budget reports will show discrepancies. The HAVING clause filters to significant amounts (>$10K) so you focus on material variances first. This is exactly the query you'd run to investigate the E2 scenario.",
                "tip": "HAVING filters on aggregate values (after GROUP BY), while WHERE filters on individual rows (before GROUP BY). A common mistake is putting aggregate conditions in WHERE — this will cause a SQL error. Remember: WHERE filters rows, HAVING filters groups."
            },
        ],
    },
}

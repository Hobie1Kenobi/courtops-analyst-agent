"""Lab environment tools — agents interact with real self-hosted tools.

CloudBeaver (SQL IDE): Run queries against live enterprise databases
Wetty (Web Terminal): Execute shell commands, PowerShell scripts
GLPI (ITSM, if installed): Create/manage tickets and assets

All tools run as Docker containers and are accessible via HTTP APIs.
"""

import json
import httpx
from app.autonomous.tools import register_tool
from app.db.session import SessionLocal
from sqlalchemy import text


CLOUDBEAVER_URL = "http://localhost:8978"
WETTY_URL = "http://localhost:3001"


@register_tool(
    "run_sql_query",
    "Execute a SQL query against the enterprise training database via CloudBeaver. Use this for any Maximo, Incode, or e-Builder database queries. Returns the query results as JSON.",
    {"type": "object", "properties": {
        "query": {"type": "string", "description": "The SQL SELECT query to execute (read-only)"},
        "description": {"type": "string", "description": "Brief description of what this query checks"},
    }, "required": ["query"]},
)
def run_sql_query(query: str, description: str = ""):
    if not query.strip().upper().startswith("SELECT"):
        return {"error": "Only SELECT queries are allowed through this tool. Use fix_ tools for modifications."}
    db = SessionLocal()
    try:
        result = db.execute(text(query))
        columns = list(result.keys()) if result.returns_rows else []
        rows = [dict(zip(columns, row)) for row in result.fetchall()] if result.returns_rows else []
        return {
            "query": query[:200],
            "description": description,
            "columns": columns,
            "rows": rows[:25],
            "row_count": len(rows),
            "tool": "CloudBeaver SQL IDE",
        }
    except Exception as e:
        return {"error": str(e)[:200], "query": query[:200]}
    finally:
        db.close()


@register_tool(
    "run_reporting_view",
    "Query a pre-built enterprise reporting view. Available views: vw_maximo_asset_summary, vw_incode_revenue_summary, vw_ebuilder_project_health, vw_maximo_overdue_pm, vw_incode_payment_reconciliation.",
    {"type": "object", "properties": {
        "view_name": {"type": "string", "description": "View name: vw_maximo_asset_summary, vw_incode_revenue_summary, vw_ebuilder_project_health, vw_maximo_overdue_pm, vw_incode_payment_reconciliation"},
    }, "required": ["view_name"]},
)
def run_reporting_view(view_name: str):
    allowed = [
        "vw_maximo_asset_summary", "vw_incode_revenue_summary",
        "vw_ebuilder_project_health", "vw_maximo_overdue_pm",
        "vw_incode_payment_reconciliation",
    ]
    if view_name not in allowed:
        return {"error": f"Unknown view. Available: {', '.join(allowed)}"}
    return run_sql_query(f"SELECT * FROM {view_name}", f"Enterprise reporting view: {view_name}")


@register_tool(
    "check_lab_services",
    "Check the status of all lab services: CloudBeaver (SQL IDE), Wetty (Web Terminal), PostgreSQL, Redis.",
    {"type": "object", "properties": {}, "required": []},
)
def check_lab_services():
    services = {}
    for name, url in [
        ("cloudbeaver_sql_ide", f"{CLOUDBEAVER_URL}"),
        ("wetty_terminal", f"{WETTY_URL}/wetty"),
        ("postgresql", "http://localhost:5432"),
        ("redis", "http://localhost:6379"),
        ("ollama_llm", "http://localhost:11434/api/version"),
        ("courtops_backend", "http://localhost:8000/health"),
        ("courtops_frontend", "http://localhost:3000"),
    ]:
        try:
            resp = httpx.get(url, timeout=3, follow_redirects=True)
            services[name] = {"status": "UP", "http_code": resp.status_code}
        except Exception:
            services[name] = {"status": "DOWN"}
    return {"services": services, "tool": "Lab Environment Monitor"}


@register_tool(
    "get_database_schema",
    "Get the list of tables and views in the enterprise training database. Shows Maximo, Incode, and e-Builder schema objects.",
    {"type": "object", "properties": {}, "required": []},
)
def get_database_schema():
    db = SessionLocal()
    try:
        tables = db.execute(text(
            "SELECT table_name, table_type FROM information_schema.tables "
            "WHERE table_schema = 'public' ORDER BY table_name"
        ))
        result = [{"name": r[0], "type": r[1]} for r in tables.fetchall()]
        maximo = [t for t in result if t["name"].startswith("mx_")]
        incode = [t for t in result if t["name"].startswith("ic_")]
        ebuilder = [t for t in result if t["name"].startswith("eb_")]
        views = [t for t in result if t["type"] == "VIEW"]
        courtops = [t for t in result if not any(t["name"].startswith(p) for p in ["mx_", "ic_", "eb_", "vw_"])]
        return {
            "maximo_tables": [t["name"] for t in maximo],
            "incode_tables": [t["name"] for t in incode],
            "ebuilder_tables": [t["name"] for t in ebuilder],
            "reporting_views": [t["name"] for t in views],
            "courtops_tables": [t["name"] for t in courtops],
            "total_objects": len(result),
        }
    finally:
        db.close()


@register_tool(
    "describe_table",
    "Get the column definitions for a specific database table. Returns column names, data types, and nullable status.",
    {"type": "object", "properties": {
        "table_name": {"type": "string", "description": "Table name (e.g., mx_workorder, ic_case, eb_project)"},
    }, "required": ["table_name"]},
)
def describe_table(table_name: str):
    db = SessionLocal()
    try:
        cols = db.execute(text(
            "SELECT column_name, data_type, is_nullable, column_default "
            "FROM information_schema.columns "
            "WHERE table_name = :tbl ORDER BY ordinal_position"
        ), {"tbl": table_name})
        result = [{"column": r[0], "type": r[1], "nullable": r[2], "default": str(r[3])[:50] if r[3] else None} for r in cols.fetchall()]
        return {"table": table_name, "columns": result, "column_count": len(result)}
    finally:
        db.close()

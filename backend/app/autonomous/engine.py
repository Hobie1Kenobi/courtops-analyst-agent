"""LLM-powered autonomous agent engine.

Each agent uses Ollama (qwen3:8b or nemotron-3-super) to reason about
what tools to call based on the current state of the enterprise systems.
The engine runs a standard ReAct loop: observe → reason → act → document.
"""

import json
import time
import threading
from datetime import datetime
from typing import Optional

from app.autonomous.tools import get_openai_tools, execute_tool, TOOL_REGISTRY
from app.autonomous.prompts import (
    SHIFT_DIRECTOR_PROMPT, CLERK_IT_PROMPT,
    IT_FUNCTIONAL_PROMPT, FINANCE_AUDIT_PROMPT,
)
from app.core.config import settings
from app.ops.stream import publish_ops_event
from app.db.session import SessionLocal
from app.sim.clock import sim_clock

_shift_thread: Optional[threading.Thread] = None
_stop_event = threading.Event()
_shift_log: list[dict] = []


AGENT_CONFIGS = {
    "shift_director": {"prompt": SHIFT_DIRECTOR_PROMPT, "color": "purple"},
    "clerk_it_agent": {"prompt": CLERK_IT_PROMPT, "color": "blue"},
    "it_functional_agent": {"prompt": IT_FUNCTIONAL_PROMPT, "color": "green"},
    "finance_audit_agent": {"prompt": FINANCE_AUDIT_PROMPT, "color": "amber"},
}


def _call_llm(system_prompt: str, user_message: str, tools: list[dict]) -> dict:
    """Call Ollama LLM with tools. Returns the assistant message."""
    import httpx

    base_url = settings.ollama_base_url.rstrip("/")
    if not base_url.endswith("/v1"):
        base_url = base_url.rstrip("/")
    chat_url = f"{base_url}/chat/completions"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]

    try:
        resp = httpx.post(
            chat_url,
            json={
                "model": settings.ollama_model,
                "messages": messages,
                "tools": tools[:6] if tools else None,
                "temperature": 0.1,
                "max_tokens": 200,
            },
            timeout=90,
        )
        if resp.status_code == 200:
            data = resp.json()
            return data.get("choices", [{}])[0].get("message", {})
        else:
            return {"role": "assistant", "content": f"LLM returned status {resp.status_code}"}
    except Exception as e:
        return {"role": "assistant", "content": f"LLM call failed: {str(e)[:200]}. Falling back to rule-based actions."}


def run_agent_turn(agent_name: str, context: str) -> dict:
    """Run a single agent turn: LLM reasons about context, calls tools, returns summary."""
    config = AGENT_CONFIGS.get(agent_name, AGENT_CONFIGS["shift_director"])
    tools = get_openai_tools()

    turn_log = {
        "agent": agent_name,
        "timestamp": datetime.utcnow().isoformat(),
        "context": context[:200],
        "reasoning": "",
        "tool_calls": [],
        "summary": "",
    }

    llm_response = _call_llm(config["prompt"], context, tools)

    content = llm_response.get("content", "")
    tool_calls = llm_response.get("tool_calls", [])

    if content:
        turn_log["reasoning"] = content[:500]

    if tool_calls:
        for tc in tool_calls:
            fn = tc.get("function", {})
            tool_name = fn.get("name", "")
            try:
                args = json.loads(fn.get("arguments", "{}"))
            except json.JSONDecodeError:
                args = {}

            result = execute_tool(tool_name, args)
            turn_log["tool_calls"].append({
                "tool": tool_name,
                "args": args,
                "result": result[:500] if isinstance(result, str) else str(result)[:500],
            })

            db = SessionLocal()
            try:
                publish_ops_event(
                    db, agent=agent_name,
                    action=f"autonomous:tool:{tool_name}",
                    status="ok",
                )
            finally:
                db.close()
    else:
        _run_fallback_actions(agent_name, turn_log)

    summary_parts = []
    if turn_log["reasoning"]:
        summary_parts.append(turn_log["reasoning"][:200])
    for tc in turn_log["tool_calls"]:
        summary_parts.append(f"Called {tc['tool']}")
    turn_log["summary"] = " | ".join(summary_parts) if summary_parts else "No actions taken"

    _shift_log.append(turn_log)

    db = SessionLocal()
    try:
        publish_ops_event(
            db, agent=agent_name,
            action=f"autonomous:turn_complete",
            status="ok",
        )
    finally:
        db.close()

    return turn_log


def _run_fallback_actions(agent_name: str, turn_log: dict):
    """If LLM doesn't return tool calls, run rule-based actions based on agent role."""
    if agent_name == "shift_director":
        result = execute_tool("get_kpi_dashboard", {})
        turn_log["tool_calls"].append({"tool": "get_kpi_dashboard", "args": {}, "result": result[:500]})
        turn_log["reasoning"] = "Checking KPIs for the current shift phase."

    elif agent_name == "clerk_it_agent":
        result = execute_tool("query_incode_citation_errors", {})
        turn_log["tool_calls"].append({"tool": "query_incode_citation_errors", "args": {}, "result": result[:500]})
        parsed = json.loads(result)
        if parsed.get("count", 0) > 0:
            fix_result = execute_tool("fix_incode_import_errors", {})
            turn_log["tool_calls"].append({"tool": "fix_incode_import_errors", "args": {}, "result": fix_result[:500]})
        unreconciled = execute_tool("query_incode_unreconciled_payments", {})
        turn_log["tool_calls"].append({"tool": "query_incode_unreconciled_payments", "args": {}, "result": unreconciled[:500]})
        parsed_u = json.loads(unreconciled)
        if parsed_u.get("count", 0) > 0:
            fix_pay = execute_tool("fix_incode_post_payments", {})
            turn_log["tool_calls"].append({"tool": "fix_incode_post_payments", "args": {}, "result": fix_pay[:500]})
        turn_log["reasoning"] = "Checking court system: citation imports and payment reconciliation."

    elif agent_name == "it_functional_agent":
        result = execute_tool("query_maximo_overdue_pms", {})
        turn_log["tool_calls"].append({"tool": "query_maximo_overdue_pms", "args": {}, "result": result[:500]})
        fix_pm = execute_tool("fix_maximo_pm_on_decommissioned", {})
        turn_log["tool_calls"].append({"tool": "fix_maximo_pm_on_decommissioned", "args": {}, "result": fix_pm[:500]})
        int_errors = execute_tool("query_maximo_integration_errors", {})
        turn_log["tool_calls"].append({"tool": "query_maximo_integration_errors", "args": {}, "result": int_errors[:500]})
        parsed_ie = json.loads(int_errors)
        if parsed_ie.get("count", 0) > 0:
            fix_int = execute_tool("fix_maximo_integration_messages", {})
            turn_log["tool_calls"].append({"tool": "fix_maximo_integration_messages", "args": {}, "result": fix_int[:500]})
        turn_log["reasoning"] = "Checking Maximo: overdue PMs, decommissioned asset cleanup, integration health."

    elif agent_name == "finance_audit_agent":
        projects = execute_tool("query_ebuilder_projects", {})
        turn_log["tool_calls"].append({"tool": "query_ebuilder_projects", "args": {}, "result": projects[:500]})
        doc_errors = execute_tool("query_ebuilder_doc_errors", {})
        turn_log["tool_calls"].append({"tool": "query_ebuilder_doc_errors", "args": {}, "result": doc_errors[:500]})
        parsed_de = json.loads(doc_errors)
        if parsed_de.get("count", 0) > 0:
            fix_docs = execute_tool("fix_ebuilder_doc_sync", {})
            turn_log["tool_calls"].append({"tool": "fix_ebuilder_doc_sync", "args": {}, "result": fix_docs[:500]})
        turn_log["reasoning"] = "Checking CIP projects, document sync status, and preparing financial review."


# =====================================================================
#  SHIFT ORCHESTRATOR — Runs the full 8-hour day
# =====================================================================

PHASE_AGENTS = {
    "morning_intake": ["shift_director", "clerk_it_agent", "it_functional_agent"],
    "midday_it_ops": ["shift_director", "it_functional_agent", "clerk_it_agent", "finance_audit_agent"],
    "endofday_monthend_audit": ["shift_director", "finance_audit_agent", "it_functional_agent", "clerk_it_agent"],
}


def _run_autonomous_shift(speed: float, seed: int):
    """Main shift loop — runs for the full simulated day."""
    global _shift_log
    _shift_log = []

    from app.seed.seed_runner import run_seed
    from app.enterprise.seed import seed_enterprise

    run_seed(seed=seed, reset=True)
    seed_enterprise(seed=seed)

    sim_clock.start(speed=speed)

    db = SessionLocal()
    try:
        publish_ops_event(db, agent="shift_director", action="autonomous:shift_start", status="ok")
    finally:
        db.close()

    last_phase = None
    cycle = 0

    while not _stop_event.is_set() and not sim_clock.shift_complete:
        current_phase = sim_clock.phase
        agents_for_phase = PHASE_AGENTS.get(current_phase, ["shift_director"])

        if current_phase != last_phase:
            last_phase = current_phase
            db = SessionLocal()
            try:
                publish_ops_event(db, agent="shift_director", action=f"autonomous:phase:{current_phase}", status="ok")
            finally:
                db.close()

        for agent_name in agents_for_phase:
            if _stop_event.is_set():
                break

            clock_state = sim_clock.state()
            context = (
                f"Current shift time: {clock_state['sim_time'][:19]}. "
                f"Phase: {current_phase}. Progress: {clock_state['progress']*100:.1f}%. "
                f"Cycle: {cycle}. "
                f"Check the enterprise systems for issues that need attention. "
                f"Use your tools to investigate and fix problems."
            )

            run_agent_turn(agent_name, context)
            time.sleep(max(1, 3 / speed))

        cycle += 1
        time.sleep(max(2, 10 / speed))

    db = SessionLocal()
    try:
        from app.work_orders.service import get_kpis
        kpis = get_kpis(db)
        publish_ops_event(db, agent="shift_director", action="autonomous:shift_complete", status="ok", kpis=kpis)
    finally:
        db.close()


def start_autonomous_shift(speed: float = 60.0, seed: int = 20260225):
    global _shift_thread
    _stop_event.clear()
    if _shift_thread and _shift_thread.is_alive():
        _stop_event.set()
        _shift_thread.join(timeout=5)
    _stop_event.clear()
    _shift_thread = threading.Thread(target=_run_autonomous_shift, args=(speed, seed), daemon=True)
    _shift_thread.start()


def stop_autonomous_shift() -> dict:
    _stop_event.set()
    sim_clock.stop()
    global _shift_thread
    if _shift_thread:
        _shift_thread.join(timeout=10)
        _shift_thread = None
    return {
        "status": "stopped",
        "total_turns": len(_shift_log),
        "total_tool_calls": sum(len(t.get("tool_calls", [])) for t in _shift_log),
    }


def get_shift_log() -> list[dict]:
    return _shift_log[-50:]


def get_shift_summary() -> dict:
    total_turns = len(_shift_log)
    total_tools = sum(len(t.get("tool_calls", [])) for t in _shift_log)
    by_agent = {}
    tool_usage = {}
    for entry in _shift_log:
        a = entry["agent"]
        by_agent[a] = by_agent.get(a, 0) + 1
        for tc in entry.get("tool_calls", []):
            t = tc["tool"]
            tool_usage[t] = tool_usage.get(t, 0) + 1
    return {
        "total_turns": total_turns,
        "total_tool_calls": total_tools,
        "turns_by_agent": by_agent,
        "tool_usage": dict(sorted(tool_usage.items(), key=lambda x: -x[1])),
        "clock": sim_clock.state(),
    }

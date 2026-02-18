import json
from typing import Any

from sqlalchemy.orm import Session

from app.agent.llm_client import get_llm_client, get_llm_model
from app.agent.tools import OPENAI_TOOLS, run_tool

SYSTEM_PROMPT = """You are the CourtOps Analyst Agent. You execute Municipal Court functional analyst duties using ONLY the tools provided.

RULES:
- Only call the tools you are given. Do not assume or invent data.
- Call one tool at a time. Wait for the result before deciding the next step.
- Be audit-friendly: your actions are logged. Prefer clear, deterministic tool use.
- If a tool fails, report the error and continue with the next logical step when appropriate.
- When the user asks for a "daily ops demo" or preset, follow the exact sequence: refresh public dataset, triage and resolve access tickets, SLA sweep and escalate, inventory compliance check, create patch records for out-of-compliance assets, generate monthly operations report, generate revenue at risk report, generate audit report, create a change request and generate its docs. Do not skip generate_monthly_operations_report or generate_change_request_docs. Complete all steps before giving your final summary; do not stop after escalation.
- Return a brief final summary of what was accomplished and any artifact paths (reports/..., docs/generated/...)."""

MAX_TURNS = 45


def run_agent(
    db: Session,
    user_id: int | None,
    goal: str,
    mode: str = "demo",
    dry_run: bool = True,
    require_completion_tools: list[str] | None = None,
) -> dict[str, Any]:
    client = get_llm_client()
    model = get_llm_model()
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": goal},
    ]
    actions_taken: list[dict[str, Any]] = []
    artifact_paths: list[str] = []

    for turn in range(MAX_TURNS):
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=OPENAI_TOOLS,
            tool_choice="auto",
        )
        choice = response.choices[0]
        if not choice.message.content and not choice.message.tool_calls:
            break
        msg = choice.message
        assistant_msg: dict[str, Any] = {"role": "assistant", "content": msg.content or ""}
        if getattr(msg, "tool_calls", None):
            assistant_msg["tool_calls"] = [
                {"id": tc.id, "type": "function", "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                for tc in msg.tool_calls
            ]
        messages.append(assistant_msg)
        if not getattr(msg, "tool_calls", None):
            if require_completion_tools:
                called = {a["tool"] for a in actions_taken}
                missing = [t for t in require_completion_tools if t not in called]
                if missing:
                    messages.append({
                        "role": "user",
                        "content": f"You have not completed all required steps. The following tools must still be called (in order): {', '.join(missing)}. Call the next required tool now. Do not provide a final summary until all are done.",
                    })
                    continue
            break

        for tc in msg.tool_calls:
            name = tc.function.name if hasattr(tc.function, "name") else getattr(tc.function, "name", "")
            try:
                args = json.loads(tc.function.arguments) if getattr(tc.function, "arguments", None) else {}
            except Exception:
                args = {}
            out = run_tool(db, user_id, name, args, dry_run=dry_run)
            result_str = str(out)[:800]
            actions_taken.append({"tool": name, "args": args, "result": out})

            if isinstance(out, dict):
                p = out.get("path") or out.get("paths")
                if isinstance(p, str) and (p.startswith("reports/") or "generated" in p):
                    artifact_paths.append(p)
                elif isinstance(p, list):
                    artifact_paths.extend([x for x in p if isinstance(x, str)])

            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result_str,
            })

    summary = ""
    if messages and messages[-1].get("role") == "assistant" and messages[-1].get("content"):
        summary = messages[-1]["content"]
    elif actions_taken:
        summary = f"Completed {len(actions_taken)} tool call(s). See actions_taken for details."

    return {
        "summary": summary,
        "actions_taken": actions_taken,
        "artifact_paths": list(dict.fromkeys(artifact_paths)),
        "dry_run": dry_run,
    }

"use client";

import { useCallback, useEffect, useRef, useState } from "react";

const API = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

interface TurnLog {
  agent: string;
  timestamp: string;
  reasoning: string;
  tool_calls: { tool: string; args: any; result: string }[];
  summary: string;
}

interface ShiftSummary {
  total_turns: number;
  total_tool_calls: number;
  turns_by_agent: Record<string, number>;
  tool_usage: Record<string, number>;
  clock: any;
}

const AGENT_STYLES: Record<string, { bg: string; border: string; label: string; icon: string }> = {
  shift_director: { bg: "bg-purple-50", border: "border-purple-400", label: "Shift Director", icon: "👔" },
  clerk_it_agent: { bg: "bg-blue-50", border: "border-blue-400", label: "Clerk + IT", icon: "⚖️" },
  it_functional_agent: { bg: "bg-green-50", border: "border-green-400", label: "IT Functional", icon: "⚙️" },
  finance_audit_agent: { bg: "bg-amber-50", border: "border-amber-400", label: "Finance & Audit", icon: "📊" },
};

export default function AutonomousOpsPage() {
  const [log, setLog] = useState<TurnLog[]>([]);
  const [summary, setSummary] = useState<ShiftSummary | null>(null);
  const [speed, setSpeed] = useState(60);
  const [running, setRunning] = useState(false);
  const [expandedTurn, setExpandedTurn] = useState<number | null>(null);
  const feedRef = useRef<HTMLDivElement>(null);

  const fetchData = useCallback(async () => {
    try {
      const [l, s] = await Promise.all([
        fetch(`${API}/autonomous/shift/log`).then(r => r.json()),
        fetch(`${API}/autonomous/shift/summary`).then(r => r.json()),
      ]);
      setLog(l);
      setSummary(s);
      if (s.clock?.running) setRunning(true);
    } catch {}
  }, []);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 3000);
    return () => clearInterval(interval);
  }, [fetchData]);

  const handleStart = async () => {
    await fetch(`${API}/autonomous/shift/start?speed=${speed}&seed=20260225`, { method: "POST" });
    setRunning(true);
    fetchData();
  };

  const handleStop = async () => {
    await fetch(`${API}/autonomous/shift/stop`, { method: "POST" });
    setRunning(false);
    fetchData();
  };

  const progressPct = summary?.clock?.progress ? Math.round(summary.clock.progress * 100) : 0;
  const PHASE_LABELS: Record<string, string> = {
    morning_intake: "Morning Intake", midday_it_ops: "Midday IT Ops", endofday_monthend_audit: "End-of-Day Audit",
  };

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="rounded-lg border-2 border-violet-400 bg-gradient-to-r from-violet-50 to-indigo-50 px-4 py-3">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold text-violet-900">Autonomous Ops — LLM-Powered 8-Hour Shift</h2>
            <p className="text-xs text-violet-700">Ollama + Tool Calling · Agents reason about enterprise systems and take real actions</p>
          </div>
          <div className="flex items-center gap-2">
            <select value={speed} onChange={e => setSpeed(Number(e.target.value))} className="rounded border px-2 py-1 text-xs">
              <option value={30}>30x (20 min)</option>
              <option value={60}>60x (10 min)</option>
              <option value={120}>120x (5 min)</option>
              <option value={300}>300x (2 min)</option>
            </select>
            <button onClick={handleStart} className="rounded bg-violet-600 px-3 py-1 text-xs text-white hover:bg-violet-700" disabled={running}>
              {running ? "Running..." : "▶ Start 8-Hour Shift"}
            </button>
            <button onClick={handleStop} className="rounded bg-red-600 px-3 py-1 text-xs text-white hover:bg-red-700">Stop</button>
          </div>
        </div>
      </div>

      {/* Progress + Summary */}
      {summary && (
        <div className="grid gap-3 lg:grid-cols-4">
          <div className="lg:col-span-3 rounded-md border bg-white p-3">
            <div className="flex items-center justify-between text-sm mb-2">
              <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${summary.clock?.running ? "bg-green-100 text-green-800" : "bg-slate-100 text-slate-600"}`}>
                {summary.clock?.running ? (summary.clock?.shift_complete ? "SHIFT COMPLETE" : "RUNNING") : "STOPPED"}
              </span>
              <span className="font-mono text-xs text-slate-600">
                {summary.clock?.sim_time?.slice(11, 19) || "—"} · {PHASE_LABELS[summary.clock?.phase] || summary.clock?.phase}
              </span>
              <span className="text-xs text-slate-500">{progressPct}% · {summary.clock?.speed}x</span>
            </div>
            <div className="h-2 w-full rounded-full bg-slate-200">
              <div className="h-full rounded-full bg-gradient-to-r from-violet-500 via-indigo-500 to-purple-500 transition-all" style={{ width: `${progressPct}%` }} />
            </div>
            <div className="mt-2 grid grid-cols-4 gap-2 text-center">
              <div><div className="text-lg font-bold text-violet-700">{summary.total_turns}</div><div className="text-[9px] text-slate-500">Agent Turns</div></div>
              <div><div className="text-lg font-bold text-indigo-700">{summary.total_tool_calls}</div><div className="text-[9px] text-slate-500">Tool Calls</div></div>
              <div><div className="text-lg font-bold text-green-700">{Object.keys(summary.turns_by_agent).length}</div><div className="text-[9px] text-slate-500">Active Agents</div></div>
              <div><div className="text-lg font-bold text-amber-700">{Object.keys(summary.tool_usage).length}</div><div className="text-[9px] text-slate-500">Tools Used</div></div>
            </div>
          </div>

          {/* Agent Activity */}
          <div className="rounded-md border bg-white p-3">
            <h4 className="text-xs font-semibold text-slate-700 mb-2">Agent Turns</h4>
            {Object.entries(summary.turns_by_agent).map(([agent, count]) => {
              const style = AGENT_STYLES[agent];
              return (
                <div key={agent} className="flex items-center justify-between text-[10px] py-1 border-b last:border-0">
                  <span>{style?.icon} {style?.label || agent}</span>
                  <span className="font-bold">{count}</span>
                </div>
              );
            })}
            {Object.keys(summary.turns_by_agent).length === 0 && <p className="text-[9px] text-slate-400 italic">No activity yet</p>}
          </div>
        </div>
      )}

      {/* Agent Turn Log */}
      <div className="rounded-md border bg-white p-3">
        <h3 className="text-sm font-semibold text-slate-800 mb-2">Agent Reasoning &amp; Tool Call Log</h3>
        <div ref={feedRef} className="space-y-2 max-h-[500px] overflow-y-auto">
          {log.length === 0 && <p className="text-xs text-slate-400 italic py-4 text-center">Start an autonomous shift to see LLM reasoning and tool calls in real time.</p>}
          {[...log].reverse().map((turn, i) => {
            const style = AGENT_STYLES[turn.agent] || AGENT_STYLES.shift_director;
            const idx = log.length - 1 - i;
            const expanded = expandedTurn === idx;
            return (
              <div key={i} className={`rounded border-l-4 ${style.border} ${style.bg} p-2 cursor-pointer transition-all ${expanded ? "ring-2 ring-violet-300" : ""}`} onClick={() => setExpandedTurn(expanded ? null : idx)}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-sm">{style.icon}</span>
                    <span className="text-[10px] font-bold">{style.label}</span>
                    <span className="text-[9px] text-slate-500">{turn.timestamp?.slice(11, 19)}</span>
                    <span className="rounded bg-white/60 px-1 text-[9px]">{turn.tool_calls.length} tools</span>
                  </div>
                  <span className="text-[9px] text-slate-400">{expanded ? "▼" : "▶"}</span>
                </div>

                {/* Reasoning */}
                {turn.reasoning && (
                  <p className="mt-1 text-[10px] text-slate-700 italic">{turn.reasoning.slice(0, expanded ? 500 : 120)}{!expanded && turn.reasoning.length > 120 ? "..." : ""}</p>
                )}

                {/* Tool Calls (expanded) */}
                {expanded && turn.tool_calls.length > 0 && (
                  <div className="mt-2 space-y-1">
                    {turn.tool_calls.map((tc, j) => (
                      <div key={j} className="rounded bg-white border p-2">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="rounded bg-indigo-100 px-1.5 text-[9px] font-mono text-indigo-800">{tc.tool}</span>
                          {Object.keys(tc.args || {}).length > 0 && (
                            <span className="text-[9px] text-slate-400">{JSON.stringify(tc.args)}</span>
                          )}
                        </div>
                        <pre className="text-[9px] text-slate-600 bg-slate-50 rounded p-1 overflow-x-auto whitespace-pre-wrap max-h-32">{tc.result}</pre>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Tool Usage (if data) */}
      {summary && Object.keys(summary.tool_usage).length > 0 && (
        <div className="rounded-md border bg-white p-3">
          <h4 className="text-xs font-semibold text-slate-700 mb-2">Tool Usage Summary</h4>
          <div className="grid grid-cols-2 gap-1 sm:grid-cols-4">
            {Object.entries(summary.tool_usage).slice(0, 12).map(([tool, count]) => (
              <div key={tool} className="flex items-center justify-between rounded bg-slate-50 px-2 py-1 text-[9px]">
                <span className="font-mono truncate">{tool}</span>
                <span className="font-bold text-indigo-700 ml-1">{count}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="text-center text-[9px] text-slate-400">Training Twin – Synthetic Records – Demonstration Only · LLM: Ollama ({"{model}"})</div>
    </div>
  );
}

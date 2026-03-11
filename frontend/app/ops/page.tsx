"use client";

import { useCallback, useEffect, useRef, useState } from "react";

const API = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

interface ClockState {
  running: boolean;
  speed: number;
  sim_time: string;
  progress: number;
  phase: string;
  shift_complete: boolean;
}

interface KPIs {
  open_tickets: number;
  overdue_slas: number;
  devices_flagged: number;
  fta_cases: number;
  revenue_at_risk: number;
  patches_created: number;
  work_orders_completed: number;
}

interface OpsEventData {
  ts: string;
  sim_time: string;
  phase: string;
  agent: string;
  work_order_id: number | null;
  action: string;
  status: string;
  kpis: KPIs | null;
  artifact: { name: string; path: string; type: string } | null;
}

interface WorkOrder {
  id: number;
  type: string;
  status: string;
  queue: string;
  priority: number;
  assigned_agent: string | null;
  completion_note: string | null;
  sim_phase: string | null;
}

const AGENT_COLORS: Record<string, string> = {
  shift_director: "bg-purple-100 border-purple-400 text-purple-900",
  clerk_it_hybrid: "bg-blue-100 border-blue-400 text-blue-900",
  it_functional_analyst: "bg-green-100 border-green-400 text-green-900",
  finance_audit_analyst: "bg-amber-100 border-amber-400 text-amber-900",
};

const AGENT_LABELS: Record<string, string> = {
  shift_director: "Shift Director",
  clerk_it_hybrid: "Clerk + IT Hybrid",
  it_functional_analyst: "IT Functional Analyst",
  finance_audit_analyst: "Finance & Audit",
};

const LANE_AGENTS = ["clerk_it_hybrid", "it_functional_analyst", "finance_audit_analyst"];
const PHASE_LABELS: Record<string, string> = {
  morning_intake: "Morning Intake",
  midday_it_ops: "Midday IT Ops",
  endofday_monthend_audit: "End-of-Day / Month-End Audit",
};

export default function OpsConsolePage() {
  const [clock, setClock] = useState<ClockState | null>(null);
  const [kpis, setKpis] = useState<KPIs | null>(null);
  const [events, setEvents] = useState<OpsEventData[]>([]);
  const [artifacts, setArtifacts] = useState<{ name: string; path: string; type: string }[]>([]);
  const [workOrders, setWorkOrders] = useState<WorkOrder[]>([]);
  const [tourMode, setTourMode] = useState(false);
  const [tourLane, setTourLane] = useState(0);
  const [simSpeed, setSimSpeed] = useState(30);
  const [highlightAgent, setHighlightAgent] = useState<string | null>(null);
  const feedRef = useRef<HTMLDivElement>(null);
  const eventSourceRef = useRef<EventSource | null>(null);

  // Check URL for tour param
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    if (params.get("tour") === "1") setTourMode(true);
  }, []);

  // Tour mode rotation
  useEffect(() => {
    if (!tourMode) return;
    const interval = setInterval(() => {
      setTourLane((prev) => (prev + 1) % LANE_AGENTS.length);
    }, 12000);
    return () => clearInterval(interval);
  }, [tourMode]);

  useEffect(() => {
    if (tourMode) {
      setHighlightAgent(LANE_AGENTS[tourLane]);
      const timeout = setTimeout(() => setHighlightAgent(null), 3000);
      return () => clearTimeout(timeout);
    }
  }, [tourLane, tourMode]);

  // Fetch dashboard data
  const fetchDashboard = useCallback(async () => {
    try {
      const res = await fetch(`${API}/ops/dashboard`);
      const data = await res.json();
      setClock(data.clock);
      setKpis(data.kpis);
    } catch {}
  }, []);

  const fetchWorkOrders = useCallback(async () => {
    try {
      const res = await fetch(`${API}/work-orders/`);
      setWorkOrders(await res.json());
    } catch {}
  }, []);

  // Poll dashboard
  useEffect(() => {
    fetchDashboard();
    fetchWorkOrders();
    const interval = setInterval(() => {
      fetchDashboard();
      fetchWorkOrders();
    }, 3000);
    return () => clearInterval(interval);
  }, [fetchDashboard, fetchWorkOrders]);

  // SSE stream
  useEffect(() => {
    const es = new EventSource(`${API}/ops/stream`);
    eventSourceRef.current = es;
    es.onmessage = (e) => {
      try {
        const data: OpsEventData = JSON.parse(e.data);
        setEvents((prev) => [data, ...prev].slice(0, 100));
        if (data.kpis) setKpis(data.kpis);
        if (data.artifact) {
          setArtifacts((prev) => [data.artifact!, ...prev]);
        }
      } catch {}
    };
    return () => es.close();
  }, []);

  // Auto-scroll feed
  useEffect(() => {
    if (feedRef.current) {
      feedRef.current.scrollTop = 0;
    }
  }, [events]);

  const handleStart = async () => {
    await fetch(`${API}/admin/sim/start?speed=${simSpeed}`, { method: "POST" });
    fetchDashboard();
  };

  const handleStop = async () => {
    await fetch(`${API}/admin/sim/stop`, { method: "POST" });
    fetchDashboard();
  };

  const handleSeed = async () => {
    await fetch(`${API}/admin/seed?profile=corpus_christi&scenario=municipal_shift&seed=20260225&reset=true`, { method: "POST" });
    fetchDashboard();
    fetchWorkOrders();
  };

  const laneEvents = (agent: string) => events.filter((e) => e.agent === agent).slice(0, 8);
  const laneWOs = (queue: string) => workOrders.filter((wo) => wo.queue === queue).slice(0, 6);

  const progressPct = clock ? Math.round(clock.progress * 100) : 0;

  return (
    <div className="space-y-4">
      {/* Header Banner */}
      <div className="rounded-lg border-2 border-indigo-300 bg-indigo-50 px-4 py-3">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold text-indigo-900">
              Municipal Shift Ops Console
            </h2>
            <p className="text-xs text-indigo-700">
              Profile: <strong>Corpus Christi (Public Data Mode)</strong> · Scenario: <strong>municipal_shift</strong> · Seed: <strong>20260225</strong>
            </p>
          </div>
          <div className="flex items-center gap-2">
            <label className="text-xs text-slate-600">Speed:</label>
            <select
              value={simSpeed}
              onChange={(e) => setSimSpeed(Number(e.target.value))}
              className="rounded border px-1 py-0.5 text-xs"
            >
              <option value={15}>15x</option>
              <option value={30}>30x</option>
              <option value={60}>60x</option>
              <option value={120}>120x</option>
            </select>
            <button onClick={handleSeed} className="rounded bg-slate-200 px-2 py-1 text-xs hover:bg-slate-300">
              Seed
            </button>
            <button onClick={handleStart} className="rounded bg-green-600 px-3 py-1 text-xs text-white hover:bg-green-700">
              Start Sim
            </button>
            <button onClick={handleStop} className="rounded bg-red-600 px-3 py-1 text-xs text-white hover:bg-red-700">
              Stop
            </button>
            <button
              onClick={() => setTourMode(!tourMode)}
              className={`rounded px-2 py-1 text-xs ${tourMode ? "bg-yellow-400 text-black" : "bg-slate-200"}`}
            >
              {tourMode ? "Tour ON" : "Tour"}
            </button>
          </div>
        </div>
      </div>

      {/* Clock + Phase Bar */}
      {clock && (
        <div className="rounded-md border bg-white p-3">
          <div className="flex items-center justify-between text-sm">
            <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${clock.running ? "bg-green-100 text-green-800" : "bg-slate-100 text-slate-600"}`}>
              {clock.running ? (clock.shift_complete ? "SHIFT COMPLETE" : "RUNNING") : "STOPPED"}
            </span>
            <span className="font-mono text-xs text-slate-600">
              Sim: {new Date(clock.sim_time).toLocaleTimeString()} · Phase: <strong>{PHASE_LABELS[clock.phase] || clock.phase}</strong>
            </span>
            <span className="text-xs text-slate-500">{progressPct}% · {clock.speed}x speed</span>
          </div>
          <div className="mt-2 h-2 w-full overflow-hidden rounded-full bg-slate-200">
            <div
              className="h-full rounded-full bg-gradient-to-r from-blue-500 via-green-500 to-amber-500 transition-all"
              style={{ width: `${progressPct}%` }}
            />
          </div>
          <div className="mt-1 flex justify-between text-[10px] text-slate-400">
            <span>Morning Intake</span>
            <span>Midday IT Ops</span>
            <span>End-of-Day Audit</span>
          </div>
        </div>
      )}

      {/* KPI Cards */}
      {kpis && (
        <div className="grid grid-cols-3 gap-3 sm:grid-cols-4 lg:grid-cols-7">
          {[
            { label: "Open Tickets", value: kpis.open_tickets, color: "text-blue-700" },
            { label: "Overdue SLAs", value: kpis.overdue_slas, color: "text-red-700" },
            { label: "Devices Flagged", value: kpis.devices_flagged, color: "text-orange-700" },
            { label: "FTA Cases", value: kpis.fta_cases, color: "text-purple-700" },
            { label: "Revenue at Risk", value: `$${kpis.revenue_at_risk.toLocaleString()}`, color: "text-red-800" },
            { label: "Patches", value: kpis.patches_created, color: "text-green-700" },
            { label: "WOs Done", value: kpis.work_orders_completed, color: "text-indigo-700" },
          ].map((kpi) => (
            <div key={kpi.label} className="rounded-md border bg-white p-2 text-center">
              <div className={`text-lg font-bold ${kpi.color}`}>{kpi.value}</div>
              <div className="text-[10px] text-slate-500">{kpi.label}</div>
            </div>
          ))}
        </div>
      )}

      {/* 3 Agent Lanes */}
      <div className="grid gap-3 lg:grid-cols-3">
        {LANE_AGENTS.map((agent) => {
          const queueName = agent === "clerk_it_hybrid" ? "clerk_ops" : agent === "it_functional_analyst" ? "it_ops" : "finance_audit";
          const isHighlighted = highlightAgent === agent;
          const colorClass = AGENT_COLORS[agent] || "bg-slate-100 border-slate-300";
          const agentEvents = laneEvents(agent);
          const agentWOs = laneWOs(queueName);

          return (
            <div
              key={agent}
              className={`rounded-lg border-2 p-3 transition-all duration-500 ${colorClass} ${isHighlighted ? "ring-4 ring-yellow-400 ring-offset-2 scale-[1.02]" : ""}`}
            >
              <h3 className="text-sm font-bold">{AGENT_LABELS[agent]}</h3>
              <p className="text-[10px] opacity-70">Queue: {queueName}</p>

              {/* Current work orders */}
              <div className="mt-2 space-y-1">
                {agentWOs.length === 0 && (
                  <p className="text-[10px] italic opacity-50">No pending work orders</p>
                )}
                {agentWOs.map((wo) => (
                  <div key={wo.id} className="flex items-center justify-between rounded bg-white/60 px-2 py-0.5 text-[10px]">
                    <span className="truncate font-mono">{wo.type.replace(/_/g, " ")}</span>
                    <span className={`rounded-full px-1.5 ${wo.status === "completed" ? "bg-green-200" : wo.status === "in_progress" ? "bg-blue-200" : "bg-slate-200"}`}>
                      {wo.status}
                    </span>
                  </div>
                ))}
              </div>

              {/* Recent actions */}
              <div className="mt-2 border-t border-current/10 pt-1">
                <p className="text-[9px] font-semibold uppercase tracking-wider opacity-60">Recent Actions</p>
                {agentEvents.map((ev, i) => (
                  <div key={i} className={`mt-0.5 text-[10px] opacity-80 ${i === 0 && isHighlighted ? "font-bold" : ""}`}>
                    → {ev.action}
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>

      {/* Bottom: Live Feed + Artifacts */}
      <div className="grid gap-3 lg:grid-cols-3">
        {/* Live Feed */}
        <div className="col-span-2 rounded-md border bg-white p-3">
          <h3 className="text-sm font-semibold text-slate-800">Live Action Feed</h3>
          <div ref={feedRef} className="mt-2 h-48 overflow-y-auto space-y-0.5">
            {events.length === 0 && (
              <p className="text-xs text-slate-400 italic">Waiting for events… Start the simulation above.</p>
            )}
            {events.map((ev, i) => (
              <div key={i} className="flex items-start gap-2 text-[10px]">
                <span className="shrink-0 font-mono text-slate-400">
                  {new Date(ev.ts).toLocaleTimeString()}
                </span>
                <span className={`shrink-0 rounded px-1 ${AGENT_COLORS[ev.agent] || "bg-slate-100"}`}>
                  {AGENT_LABELS[ev.agent] || ev.agent}
                </span>
                <span className="text-slate-700">{ev.action}</span>
                {ev.status === "completed" && <span className="text-green-600">✓</span>}
                {ev.status === "failed" && <span className="text-red-600">✗</span>}
              </div>
            ))}
          </div>
        </div>

        {/* Artifacts Panel */}
        <div className="rounded-md border bg-white p-3">
          <h3 className="text-sm font-semibold text-slate-800">Artifacts</h3>
          <div className="mt-2 space-y-1">
            {artifacts.length === 0 && (
              <p className="text-xs text-slate-400 italic">No artifacts yet.</p>
            )}
            {artifacts.map((a, i) => (
              <div key={i} className="flex items-center gap-2 rounded bg-slate-50 px-2 py-1 text-[10px]">
                <span className="text-indigo-600">📄</span>
                <span className="truncate font-medium">{a.name}</span>
                <span className="text-slate-400">{a.type}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Footer watermark */}
      <div className="text-center text-[9px] text-slate-400">
        Public Data Mode – Synthetic Records – For Demonstration Only · Liberty ChainGuard Consulting
      </div>
    </div>
  );
}

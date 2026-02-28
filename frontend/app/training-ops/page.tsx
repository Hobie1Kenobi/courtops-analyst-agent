"use client";

import { useCallback, useEffect, useRef, useState } from "react";

const API = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

interface TrainingTask {
  id: number;
  title: string;
  domain: string;
  scenario: string | null;
  status: string;
  assigned_agent: string | null;
  description: string | null;
  business_context: string | null;
  evidence_reviewed: string | null;
  decision_made: string | null;
  technical_detail: string | null;
  sql_or_config: string | null;
  why_correct: string | null;
  what_to_document: string | null;
  what_to_test: string | null;
  mentor_explanation: string | null;
  interview_answer: string | null;
  skills_practiced: string | null;
  sim_phase: string | null;
}

interface Skill {
  domain: string;
  tasks_completed: number;
  confidence_score: number;
}

const AGENT_STYLES: Record<string, { bg: string; border: string; label: string }> = {
  requirements_docs: { bg: "bg-blue-50", border: "border-blue-400", label: "Requirements & Docs" },
  sql_reporting: { bg: "bg-green-50", border: "border-green-400", label: "SQL & Reporting" },
  app_integration: { bg: "bg-orange-50", border: "border-orange-400", label: "App & Integration" },
  qa_debugging: { bg: "bg-red-50", border: "border-red-400", label: "QA & Debugging" },
  mentor_coach: { bg: "bg-indigo-50", border: "border-indigo-400", label: "Mentor Coach" },
  shift_director: { bg: "bg-purple-50", border: "border-purple-400", label: "Shift Director" },
};

const DOMAIN_LABELS: Record<string, string> = {
  sql_server: "SQL Server", oracle_sql: "Oracle SQL", stored_procedures: "Stored Procs",
  crystal_reports: "Crystal Reports", ssrs: "SSRS", power_bi: "Power BI",
  iis_apache: "IIS/Apache", web_services: "Web Services", dotnet_java: ".NET/Java",
  powershell: "PowerShell", debugging: "Debugging", requirements: "Requirements",
  process_docs: "Process Docs", change_mgmt: "Change Mgmt", sharepoint: "SharePoint",
  erp_asset: "ERP/Asset Mgmt",
};

export default function TrainingOpsPage() {
  const [tasks, setTasks] = useState<TrainingTask[]>([]);
  const [skills, setSkills] = useState<Skill[]>([]);
  const [selectedTask, setSelectedTask] = useState<TrainingTask | null>(null);
  const [activePanel, setActivePanel] = useState<string>("teach");
  const [scenarios, setScenarios] = useState<Record<string, any>>({});
  const [running, setRunning] = useState(false);
  const [events, setEvents] = useState<any[]>([]);
  const feedRef = useRef<HTMLDivElement>(null);

  const fetchAll = useCallback(async () => {
    try {
      const [t, s, sc] = await Promise.all([
        fetch(`${API}/training/tasks`).then((r) => r.json()),
        fetch(`${API}/training/skills`).then((r) => r.json()),
        fetch(`${API}/training/scenarios`).then((r) => r.json()),
      ]);
      setTasks(t);
      setSkills(s);
      setScenarios(sc);
    } catch {}
  }, []);

  useEffect(() => {
    fetchAll();
    const interval = setInterval(fetchAll, 4000);
    return () => clearInterval(interval);
  }, [fetchAll]);

  useEffect(() => {
    const es = new EventSource(`${API}/ops/stream`);
    es.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data);
        if (data.action?.startsWith("training:")) {
          setEvents((prev) => [data, ...prev].slice(0, 50));
        }
      } catch {}
    };
    return () => es.close();
  }, []);

  const handleSeedAndStart = async (key: string) => {
    await fetch(`${API}/training/scenarios/${key}/start?speed=5`, { method: "POST" });
    setRunning(true);
    fetchAll();
  };

  const handleStop = async () => {
    await fetch(`${API}/training/stop`, { method: "POST" });
    setRunning(false);
  };

  const activeTask = tasks.find((t) => t.status === "active" || t.status === "teaching");
  const completedTasks = tasks.filter((t) => t.status === "completed");

  const agentTasks: Record<string, TrainingTask[]> = {};
  for (const t of tasks) {
    const a = t.assigned_agent || "shift_director";
    if (!agentTasks[a]) agentTasks[a] = [];
    agentTasks[a].push(t);
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="rounded-lg border-2 border-emerald-300 bg-emerald-50 px-4 py-3">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold text-emerald-900">Municipal Applications Analyst — Training Twin</h2>
            <p className="text-xs text-emerald-700">Interactive learning console · Enterprise IT analyst workflow simulation</p>
          </div>
          <div className="flex items-center gap-1 flex-wrap">
            {Object.entries(scenarios).map(([key, sc]: [string, any]) => {
              const sys = sc.system || "general";
              const colors: Record<string, string> = {
                general: "bg-emerald-600 hover:bg-emerald-700",
                maximo: "bg-blue-600 hover:bg-blue-700",
                incode: "bg-purple-600 hover:bg-purple-700",
                ebuilder: "bg-orange-600 hover:bg-orange-700",
              };
              const icons: Record<string, string> = { general: "▶", maximo: "⚙️", incode: "⚖️", ebuilder: "🏗️" };
              return (
                <button key={key} onClick={() => handleSeedAndStart(key)} className={`rounded px-2 py-1 text-[9px] text-white ${colors[sys] || colors.general}`} title={sc.description}>
                  {icons[sys] || "▶"} {sc.name?.length > 30 ? sc.name.slice(0, 30) + "…" : sc.name}
                </button>
              );
            })}
            <button onClick={handleStop} className="rounded bg-red-600 px-2 py-1 text-[9px] text-white hover:bg-red-700">Stop</button>
          </div>
        </div>
      </div>

      {/* Skills Progress */}
      <div className="rounded-md border bg-white p-3">
        <h3 className="text-sm font-semibold text-slate-800 mb-2">Skill Confidence Tracker</h3>
        <div className="grid grid-cols-4 gap-2 sm:grid-cols-8">
          {skills.filter(s => s.confidence_score > 0 || ["sql_server","debugging","requirements","web_services","stored_procedures","process_docs"].includes(s.domain)).slice(0, 8).map((s) => (
            <div key={s.domain} className="text-center">
              <div className="mx-auto h-10 w-10 rounded-full border-2 flex items-center justify-center text-xs font-bold" style={{ borderColor: s.confidence_score > 50 ? '#16a34a' : s.confidence_score > 0 ? '#f59e0b' : '#e2e8f0', color: s.confidence_score > 50 ? '#16a34a' : s.confidence_score > 0 ? '#f59e0b' : '#94a3b8' }}>
                {Math.round(s.confidence_score)}%
              </div>
              <div className="text-[9px] text-slate-500 mt-1">{DOMAIN_LABELS[s.domain] || s.domain}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="grid gap-3 lg:grid-cols-3">
        {/* Left: Agent Lanes + Task Queue */}
        <div className="space-y-3">
          <div className="rounded-md border bg-white p-3">
            <h3 className="text-sm font-semibold text-slate-800">Work Queue</h3>
            <div className="mt-2 space-y-1">
              {tasks.length === 0 && <p className="text-xs text-slate-400 italic">Select a scenario above to begin.</p>}
              {tasks.map((t) => (
                <button key={t.id} onClick={() => { setSelectedTask(t); setActivePanel("teach"); }} className={`w-full rounded px-2 py-1.5 text-left text-[11px] border transition-all ${t.status === "active" ? "border-yellow-400 bg-yellow-50 ring-2 ring-yellow-300" : t.status === "teaching" ? "border-indigo-400 bg-indigo-50 ring-2 ring-indigo-300" : t.status === "completed" ? "border-green-300 bg-green-50" : "border-slate-200 bg-slate-50"} ${selectedTask?.id === t.id ? "ring-2 ring-emerald-400" : ""}`}>
                  <div className="flex items-center justify-between">
                    <span className="font-medium truncate">{t.title}</span>
                    <span className={`shrink-0 rounded-full px-1.5 py-0.5 text-[9px] font-semibold ${t.status === "completed" ? "bg-green-200 text-green-800" : t.status === "active" ? "bg-yellow-200 text-yellow-800" : t.status === "teaching" ? "bg-indigo-200 text-indigo-800" : "bg-slate-200"}`}>{t.status}</span>
                  </div>
                  <div className="text-[9px] text-slate-500 mt-0.5">{AGENT_STYLES[t.assigned_agent || ""]?.label || t.assigned_agent} · {t.domain}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Agent Lanes */}
          {Object.entries(AGENT_STYLES).filter(([k]) => k !== "shift_director" && k !== "mentor_coach").map(([agent, style]) => (
            <div key={agent} className={`rounded-lg border-2 ${style.border} ${style.bg} p-2`}>
              <h4 className="text-xs font-bold">{style.label}</h4>
              {(agentTasks[agent] || []).slice(0, 3).map((t) => (
                <div key={t.id} className="mt-1 flex items-center justify-between text-[10px]">
                  <span className="truncate">{t.title}</span>
                  <span className={`rounded-full px-1 ${t.status === "completed" ? "bg-green-200" : "bg-slate-200"}`}>{t.status}</span>
                </div>
              ))}
              {!(agentTasks[agent]?.length) && <p className="text-[9px] italic opacity-50 mt-1">Idle</p>}
            </div>
          ))}
        </div>

        {/* Center: Detail Panel */}
        <div className="lg:col-span-2 space-y-3">
          {/* Panel Selector */}
          <div className="flex gap-1 flex-wrap">
            {[
              { key: "teach", label: "Teach Me", icon: "📖" },
              { key: "technical", label: "Technical Detail", icon: "⚙️" },
              { key: "sql", label: "Show SQL / Config", icon: "💾" },
              { key: "why", label: "Ask Why", icon: "❓" },
              { key: "document", label: "Documentation", icon: "📄" },
              { key: "test", label: "Testing", icon: "🧪" },
              { key: "interview", label: "Interview Prep", icon: "🎤" },
            ].map((p) => (
              <button key={p.key} onClick={() => setActivePanel(p.key)} className={`rounded px-2 py-1 text-[10px] font-medium ${activePanel === p.key ? "bg-emerald-600 text-white" : "bg-slate-100 text-slate-700 hover:bg-slate-200"}`}>
                {p.icon} {p.label}
              </button>
            ))}
          </div>

          {/* Content Panel */}
          <div className="rounded-md border bg-white p-4 min-h-[300px]">
            {!selectedTask ? (
              <div className="text-center text-sm text-slate-400 py-12">
                <p className="text-2xl mb-2">📋</p>
                <p>Select a task from the work queue to begin learning.</p>
                <p className="text-xs mt-1">Each task teaches a real enterprise analyst skill.</p>
              </div>
            ) : (
              <div className="space-y-3">
                <div>
                  <h3 className="text-sm font-bold text-slate-900">{selectedTask.title}</h3>
                  <div className="flex gap-2 mt-1">
                    <span className="rounded bg-slate-100 px-1.5 py-0.5 text-[9px] font-medium">{selectedTask.domain}</span>
                    <span className="rounded bg-slate-100 px-1.5 py-0.5 text-[9px] font-medium">{AGENT_STYLES[selectedTask.assigned_agent || ""]?.label}</span>
                    {selectedTask.skills_practiced && selectedTask.skills_practiced.split(",").map((s) => (
                      <span key={s} className="rounded bg-emerald-100 px-1.5 py-0.5 text-[9px] font-medium text-emerald-800">{DOMAIN_LABELS[s.trim()] || s.trim()}</span>
                    ))}
                  </div>
                </div>

                {activePanel === "teach" && (
                  <div className="space-y-3 text-xs">
                    {selectedTask.business_context && <div><h4 className="font-semibold text-slate-700">Business Context</h4><p className="text-slate-600 mt-1">{selectedTask.business_context}</p></div>}
                    {selectedTask.description && <div><h4 className="font-semibold text-slate-700">What We Need To Do</h4><p className="text-slate-600 mt-1">{selectedTask.description}</p></div>}
                    {selectedTask.evidence_reviewed && <div><h4 className="font-semibold text-slate-700">Evidence Reviewed</h4><p className="text-slate-600 mt-1 whitespace-pre-wrap">{selectedTask.evidence_reviewed}</p></div>}
                    {selectedTask.decision_made && <div><h4 className="font-semibold text-slate-700">Decision Made</h4><p className="text-slate-600 mt-1">{selectedTask.decision_made}</p></div>}
                    {selectedTask.mentor_explanation && <div className="rounded bg-indigo-50 border border-indigo-200 p-3"><h4 className="font-semibold text-indigo-800">🎓 Mentor Explanation</h4><p className="text-indigo-700 mt-1">{selectedTask.mentor_explanation}</p></div>}
                  </div>
                )}

                {activePanel === "technical" && (
                  <div className="space-y-3 text-xs">
                    <h4 className="font-semibold text-slate-700">Technical Detail</h4>
                    <pre className="rounded bg-slate-900 text-green-400 p-3 overflow-x-auto text-[11px] whitespace-pre-wrap">{selectedTask.technical_detail || "No technical detail for this task."}</pre>
                  </div>
                )}

                {activePanel === "sql" && (
                  <div className="space-y-3 text-xs">
                    <h4 className="font-semibold text-slate-700">SQL / Config / Command</h4>
                    <pre className="rounded bg-slate-900 text-emerald-400 p-3 overflow-x-auto text-[11px] whitespace-pre-wrap">{selectedTask.sql_or_config || "No SQL or config for this task."}</pre>
                  </div>
                )}

                {activePanel === "why" && (
                  <div className="space-y-3 text-xs">
                    <div className="rounded bg-amber-50 border border-amber-200 p-3">
                      <h4 className="font-semibold text-amber-800">❓ Why Was This The Right Approach?</h4>
                      <p className="text-amber-700 mt-1">{selectedTask.why_correct || "Explanation not available."}</p>
                    </div>
                    {selectedTask.mentor_explanation && <div className="rounded bg-indigo-50 border border-indigo-200 p-3"><h4 className="font-semibold text-indigo-800">🎓 Deeper Mentor Insight</h4><p className="text-indigo-700 mt-1">{selectedTask.mentor_explanation}</p></div>}
                  </div>
                )}

                {activePanel === "document" && (
                  <div className="space-y-3 text-xs">
                    <h4 className="font-semibold text-slate-700">What a Human Analyst Should Document</h4>
                    <div className="whitespace-pre-wrap text-slate-600 bg-slate-50 rounded p-3">{selectedTask.what_to_document || "No documentation guidance for this task."}</div>
                  </div>
                )}

                {activePanel === "test" && (
                  <div className="space-y-3 text-xs">
                    <h4 className="font-semibold text-slate-700">What Should Be Tested Next</h4>
                    <div className="whitespace-pre-wrap text-slate-600 bg-slate-50 rounded p-3">{selectedTask.what_to_test || "No testing guidance for this task."}</div>
                  </div>
                )}

                {activePanel === "interview" && (
                  <div className="space-y-3 text-xs">
                    <div className="rounded bg-violet-50 border border-violet-200 p-3">
                      <h4 className="font-semibold text-violet-800">🎤 Interview-Ready Answer (STAR Format)</h4>
                      <p className="text-violet-700 mt-1 whitespace-pre-wrap">{selectedTask.interview_answer || "No interview prep for this task."}</p>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Live Feed */}
          <div className="rounded-md border bg-white p-3">
            <h3 className="text-sm font-semibold text-slate-800">Training Feed</h3>
            <div ref={feedRef} className="mt-2 h-32 overflow-y-auto space-y-0.5">
              {events.length === 0 && <p className="text-xs text-slate-400 italic">Start a scenario to see agent activity.</p>}
              {events.map((ev, i) => (
                <div key={i} className="flex items-start gap-2 text-[10px]">
                  <span className="shrink-0 font-mono text-slate-400">{new Date(ev.ts).toLocaleTimeString()}</span>
                  <span className={`shrink-0 rounded px-1 ${AGENT_STYLES[ev.agent]?.bg || "bg-slate-100"}`}>{AGENT_STYLES[ev.agent]?.label || ev.agent}</span>
                  <span className="text-slate-700">{ev.action}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      <div className="text-center text-[9px] text-slate-400">Training Twin – Synthetic Records – Demonstration Only</div>
    </div>
  );
}

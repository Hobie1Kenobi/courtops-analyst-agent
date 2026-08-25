"use client";

import { useCallback, useEffect, useState } from "react";

const API = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

type Tab = "maximo" | "incode" | "ebuilder";

export default function SystemsPage() {
  const [tab, setTab] = useState<Tab>("maximo");
  const [mxStats, setMxStats] = useState<any>(null);
  const [mxWOs, setMxWOs] = useState<any[]>([]);
  const [mxCrons, setMxCrons] = useState<any[]>([]);
  const [mxMessages, setMxMessages] = useState<any[]>([]);
  const [icStats, setIcStats] = useState<any>(null);
  const [icCases, setIcCases] = useState<any[]>([]);
  const [icErrors, setIcErrors] = useState<any[]>([]);
  const [ebStats, setEbStats] = useState<any>(null);
  const [ebProjects, setEbProjects] = useState<any[]>([]);
  const [ebDocErrors, setEbDocErrors] = useState<any[]>([]);
  const [ebRfis, setEbRfis] = useState<any[]>([]);

  const fetchAll = useCallback(async () => {
    try {
      const f = (u: string) => fetch(`${API}${u}`).then(r => r.json());
      const [ms, mw, mc, mm, is_, ic, ie, es, ep, ed, er] = await Promise.all([
        f("/enterprise/maximo/stats"), f("/enterprise/maximo/workorders"),
        f("/enterprise/maximo/crontasks"), f("/enterprise/maximo/messages"),
        f("/enterprise/incode/stats"), f("/enterprise/incode/cases"),
        f("/enterprise/incode/citations/errors"),
        f("/enterprise/ebuilder/stats"), f("/enterprise/ebuilder/projects"),
        f("/enterprise/ebuilder/documents?sync_status=ERROR"),
        f("/enterprise/ebuilder/rfis?status=OVERDUE"),
      ]);
      setMxStats(ms); setMxWOs(mw); setMxCrons(mc); setMxMessages(mm);
      setIcStats(is_); setIcCases(ic); setIcErrors(ie);
      setEbStats(es); setEbProjects(ep); setEbDocErrors(ed); setEbRfis(er);
    } catch {}
  }, []);

  useEffect(() => { fetchAll(); }, [fetchAll]);

  const handleSeed = async () => {
    await fetch(`${API}/enterprise/seed?seed=20260225`, { method: "POST" });
    fetchAll();
  };

  const statCard = (label: string, value: string | number, color: string = "text-slate-900") => (
    <div className="rounded-md border bg-white p-3 text-center">
      <div className={`text-xl font-bold ${color}`}>{value}</div>
      <div className="text-[10px] text-slate-500">{label}</div>
    </div>
  );

  return (
    <div className="space-y-4">
      <div className="rounded-lg border-2 border-slate-300 bg-slate-800 px-4 py-3">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold text-white">Enterprise Systems Simulator</h2>
            <p className="text-xs text-slate-400">Simulated IBM Maximo · Tyler Incode · e-Builder (Trimble Unity Construct)</p>
          </div>
          <button onClick={handleSeed} className="rounded bg-slate-600 px-3 py-1 text-xs text-white hover:bg-slate-500">Reset &amp; Seed Data</button>
        </div>
      </div>

      {/* Tab Bar */}
      <div className="flex gap-1">
        {([
          { key: "maximo" as Tab, label: "IBM Maximo", icon: "⚙️", color: "bg-blue-600" },
          { key: "incode" as Tab, label: "Tyler Incode", icon: "⚖️", color: "bg-purple-600" },
          { key: "ebuilder" as Tab, label: "e-Builder / Trimble", icon: "🏗️", color: "bg-orange-600" },
        ]).map(t => (
          <button key={t.key} onClick={() => setTab(t.key)} className={`rounded-t px-4 py-2 text-xs font-semibold ${tab === t.key ? `${t.color} text-white` : "bg-slate-200 text-slate-700 hover:bg-slate-300"}`}>
            {t.icon} {t.label}
          </button>
        ))}
      </div>

      {/* === MAXIMO === */}
      {tab === "maximo" && (
        <div className="space-y-3">
          <div className="rounded-md border-2 border-blue-300 bg-blue-50 p-3">
            <h3 className="text-sm font-bold text-blue-900">IBM Maximo — Enterprise Asset Management</h3>
            <p className="text-[10px] text-blue-700">Fleet, Water/Wastewater, Facilities, Parks — Corpus Christi asset operations</p>
          </div>
          {mxStats && (
            <div className="grid grid-cols-4 gap-2">
              {statCard("Total Work Orders", mxStats.total_workorders)}
              {statCard("Open Work Orders", mxStats.open_workorders, "text-blue-700")}
              {statCard("Overdue PMs", mxStats.overdue_pms, "text-red-700")}
              {statCard("Integration Errors", mxStats.integration_errors, "text-red-700")}
            </div>
          )}
          <div className="grid gap-3 lg:grid-cols-2">
            <div className="rounded-md border bg-white p-3">
              <h4 className="text-xs font-semibold text-slate-800 mb-2">Work Orders</h4>
              <div className="overflow-x-auto">
                <table className="w-full text-[10px]">
                  <thead><tr className="border-b bg-blue-50"><th className="px-1 py-1 text-left">WO#</th><th className="px-1 py-1 text-left">Status</th><th className="px-1 py-1 text-left">Type</th><th className="px-1 py-1 text-left">Description</th><th className="px-1 py-1 text-left">Asset</th></tr></thead>
                  <tbody>{mxWOs.slice(0, 12).map(wo => (
                    <tr key={wo.wonum} className="border-b"><td className="px-1 py-0.5 font-mono">{wo.wonum}</td><td className={`px-1 py-0.5 ${wo.status === "INPRG" ? "text-blue-700 font-bold" : wo.status === "WAPPR" ? "text-amber-700" : ""}`}>{wo.status}</td><td className="px-1 py-0.5">{wo.worktype}</td><td className="px-1 py-0.5 truncate max-w-[150px]">{wo.description}</td><td className="px-1 py-0.5 font-mono text-[9px]">{wo.assetnum}</td></tr>
                  ))}</tbody>
                </table>
              </div>
            </div>
            <div className="space-y-3">
              <div className="rounded-md border bg-white p-3">
                <h4 className="text-xs font-semibold text-slate-800 mb-2">Cron Tasks</h4>
                {mxCrons.map(c => (
                  <div key={c.name} className="flex items-center justify-between text-[10px] py-0.5 border-b last:border-0">
                    <span className="font-mono">{c.name}</span>
                    <span className={`rounded-full px-1.5 ${c.active ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}`}>{c.active ? "ACTIVE" : "INACTIVE"}</span>
                  </div>
                ))}
              </div>
              <div className="rounded-md border border-red-200 bg-red-50 p-3">
                <h4 className="text-xs font-semibold text-red-800 mb-2">Integration Errors ({mxMessages.length})</h4>
                {mxMessages.slice(0, 3).map(m => (
                  <div key={m.msgid} className="text-[9px] text-red-700 py-0.5 border-b border-red-100">{m.msgerror?.slice(0, 70)}</div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* === INCODE === */}
      {tab === "incode" && (
        <div className="space-y-3">
          <div className="rounded-md border-2 border-purple-300 bg-purple-50 p-3">
            <h3 className="text-sm font-bold text-purple-900">Tyler Technologies Incode — Court Case Management</h3>
            <p className="text-[10px] text-purple-700">Citations, Cases, Payments, Warrants, Dockets — Municipal Court operations</p>
          </div>
          {icStats && (
            <div className="grid grid-cols-3 gap-2 sm:grid-cols-6">
              {statCard("Total Cases", icStats.total_cases)}
              {statCard("Open Cases", icStats.open_cases, "text-blue-700")}
              {statCard("FTA/Warrant", icStats.fta_warrant, "text-red-700")}
              {statCard("Unreconciled", icStats.unreconciled_payments, "text-amber-700")}
              {statCard("Import Errors", icStats.import_errors, "text-red-700")}
              {statCard("Outstanding $", `$${(icStats.total_outstanding || 0).toLocaleString()}`, "text-red-800")}
            </div>
          )}
          <div className="grid gap-3 lg:grid-cols-2">
            <div className="rounded-md border bg-white p-3">
              <h4 className="text-xs font-semibold text-slate-800 mb-2">Cases</h4>
              <table className="w-full text-[10px]">
                <thead><tr className="border-b bg-purple-50"><th className="px-1 py-1 text-left">Case#</th><th className="px-1 py-1 text-left">Status</th><th className="px-1 py-1 text-left">Violation</th><th className="px-1 py-1 text-right">Balance</th></tr></thead>
                <tbody>{icCases.slice(0, 12).map(c => (
                  <tr key={c.case_number} className="border-b"><td className="px-1 py-0.5 font-mono">{c.case_number}</td><td className={`px-1 py-0.5 ${["FTA","WARRANT"].includes(c.status) ? "text-red-700 font-bold" : ""}`}>{c.status}</td><td className="px-1 py-0.5 truncate max-w-[120px]">{c.violation_desc}</td><td className="px-1 py-0.5 text-right">${c.balance_due?.toFixed(2)}</td></tr>
                ))}</tbody>
              </table>
            </div>
            <div className="rounded-md border border-red-200 bg-red-50 p-3">
              <h4 className="text-xs font-semibold text-red-800 mb-2">Citation Import Errors ({icErrors.length})</h4>
              {icErrors.map((e: any, i: number) => (
                <div key={i} className="text-[9px] text-red-700 py-1 border-b border-red-100">
                  <span className="font-mono">{e.citation_number}</span>: {e.import_error?.slice(0, 60)}
                </div>
              ))}
              {icErrors.length === 0 && <p className="text-[9px] text-green-700 italic">No import errors</p>}
            </div>
          </div>
        </div>
      )}

      {/* === E-BUILDER === */}
      {tab === "ebuilder" && (
        <div className="space-y-3">
          <div className="rounded-md border-2 border-orange-300 bg-orange-50 p-3">
            <h3 className="text-sm font-bold text-orange-900">e-Builder / Trimble Unity Construct — Capital Improvement</h3>
            <p className="text-[10px] text-orange-700">Bond-funded CIP projects — Water, Sewer, Roads, Facilities</p>
          </div>
          {ebStats && (
            <div className="grid grid-cols-3 gap-2 sm:grid-cols-6">
              {statCard("Projects", ebStats.total_projects)}
              {statCard("Total Budget", `$${(ebStats.total_budget / 1e6).toFixed(1)}M`, "text-blue-700")}
              {statCard("Total Spent", `$${(ebStats.total_spent / 1e6).toFixed(1)}M`, "text-green-700")}
              {statCard("Behind Schedule", ebStats.behind_schedule, "text-red-700")}
              {statCard("Doc Sync Errors", ebStats.document_sync_errors, "text-red-700")}
              {statCard("Open RFIs", ebStats.open_rfis, "text-amber-700")}
            </div>
          )}
          <div className="rounded-md border bg-white p-3">
            <h4 className="text-xs font-semibold text-slate-800 mb-2">Capital Improvement Projects</h4>
            <table className="w-full text-[10px]">
              <thead><tr className="border-b bg-orange-50"><th className="px-1 py-1 text-left">ID</th><th className="px-1 py-1 text-left">Project</th><th className="px-1 py-1 text-left">Status</th><th className="px-1 py-1 text-right">Budget</th><th className="px-1 py-1 text-right">Spent</th><th className="px-1 py-1 text-right">%</th><th className="px-1 py-1 text-right">Sched Var</th></tr></thead>
              <tbody>{ebProjects.map(p => (
                <tr key={p.project_id} className="border-b"><td className="px-1 py-0.5 font-mono">{p.project_id}</td><td className="px-1 py-0.5 truncate max-w-[180px]">{p.project_name}</td><td className={`px-1 py-0.5 ${p.status === "ON HOLD" ? "text-red-700" : ""}`}>{p.status}</td><td className="px-1 py-0.5 text-right">${(p.budget_total/1e6).toFixed(1)}M</td><td className="px-1 py-0.5 text-right">${(p.actual_cost/1e6).toFixed(1)}M</td><td className="px-1 py-0.5 text-right">{p.percent_complete?.toFixed(0)}%</td><td className={`px-1 py-0.5 text-right ${p.schedule_variance_days > 14 ? "text-red-700 font-bold" : ""}`}>{p.schedule_variance_days > 0 ? `+${p.schedule_variance_days}d` : `${p.schedule_variance_days}d`}</td></tr>
              ))}</tbody>
            </table>
          </div>
          <div className="grid gap-3 lg:grid-cols-2">
            {ebDocErrors.length > 0 && (
              <div className="rounded-md border border-red-200 bg-red-50 p-3">
                <h4 className="text-xs font-semibold text-red-800 mb-2">Document Sync Errors ({ebDocErrors.length})</h4>
                {ebDocErrors.map((d: any) => (
                  <div key={d.doc_id} className="text-[9px] text-red-700 py-0.5 border-b border-red-100">{d.title}: {d.sync_error?.slice(0, 50)}</div>
                ))}
              </div>
            )}
            {ebRfis.length > 0 && (
              <div className="rounded-md border border-amber-200 bg-amber-50 p-3">
                <h4 className="text-xs font-semibold text-amber-800 mb-2">Overdue RFIs ({ebRfis.length})</h4>
                {ebRfis.map((r: any) => (
                  <div key={r.rfi_id} className="text-[9px] text-amber-700 py-0.5 border-b border-amber-100">{r.rfi_number}: {r.subject?.slice(0, 50)} ({r.days_open}d open)</div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      <div className="text-center text-[9px] text-slate-400">Training Twin – Synthetic Records – Demonstration Only</div>
    </div>
  );
}

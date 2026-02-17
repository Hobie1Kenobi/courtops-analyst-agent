"use client";

import { useState } from "react";
import { apiFetch } from "@/lib/api";

interface AgentRunResponse {
  summary: string;
  actions_taken: Array<{ tool: string; args: Record<string, unknown>; result: unknown }>;
  artifact_paths: string[];
  dry_run: boolean;
}

export default function AgentConsolePage() {
  const [goal, setGoal] = useState("");
  const [mode, setMode] = useState<"demo" | "interactive">("demo");
  const [dryRun, setDryRun] = useState(true);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<AgentRunResponse | null>(null);

  async function handleRun(preset?: string) {
    setError(null);
    setResult(null);
    setRunning(true);
    try {
      const body = preset
        ? { goal: "", mode: "demo", dry_run: dryRun, preset }
        : { goal: goal || "Run daily operations demo.", mode, dry_run: dryRun };
      const data = await apiFetch<AgentRunResponse>("/agent/run", {
        method: "POST",
        body: JSON.stringify(body),
      });
      setResult(data);
    } catch {
      setError("Run failed. Ensure you are logged in and the backend is running.");
    } finally {
      setRunning(false);
    }
  }

  const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
  const reportsBase = `${apiBase.replace(/\/$/, "")}/reports`;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold text-slate-900">Agent Console</h2>
        <p className="text-sm text-slate-600">
          Run the CourtOps Analyst Agent with whitelisted tools. Use dry run to
          simulate without making changes. Only Analyst, IT Support, or Supervisor
          can execute tools; Read-only may run with dry run only.
        </p>
      </div>

      {error && (
        <div className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">
          {error}
        </div>
      )}

      <section className="rounded-md border bg-white p-4">
        <h3 className="text-sm font-semibold text-slate-800">Goal</h3>
        <textarea
          value={goal}
          onChange={(e) => setGoal(e.target.value)}
          placeholder="Describe what the agent should do, or use a preset below."
          rows={4}
          className="mt-2 w-full rounded border border-slate-200 px-3 py-2 text-sm text-slate-900 placeholder:text-slate-400"
        />
        <div className="mt-3 flex flex-wrap items-center gap-4">
          <label className="flex items-center gap-2 text-sm text-slate-700">
            <span>Mode:</span>
            <select
              value={mode}
              onChange={(e) => setMode(e.target.value as "demo" | "interactive")}
              className="rounded border border-slate-200 px-2 py-1 text-sm"
            >
              <option value="demo">Demo</option>
              <option value="interactive">Interactive</option>
            </select>
          </label>
          <label className="flex cursor-pointer items-center gap-2 text-sm text-slate-700">
            <input
              type="checkbox"
              checked={dryRun}
              onChange={(e) => setDryRun(e.target.checked)}
              className="rounded border-slate-300"
            />
            Dry run (no changes)
          </label>
        </div>
        <div className="mt-3 flex flex-wrap gap-2">
          <button
            type="button"
            onClick={() => handleRun("daily_ops_demo")}
            disabled={running}
            className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-60"
          >
            {running ? "Running…" : "Run daily_ops_demo preset"}
          </button>
          <button
            type="button"
            onClick={() => handleRun()}
            disabled={running}
            className="rounded-md border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-60"
          >
            {running ? "Running…" : "Run custom goal"}
          </button>
        </div>
      </section>

      {result && (
        <section className="rounded-md border bg-white p-4">
          <h3 className="text-sm font-semibold text-slate-800">Result</h3>
          {result.dry_run && (
            <p className="mt-1 text-xs text-amber-700">Dry run: no changes were made.</p>
          )}
          <div className="mt-2 rounded border border-slate-100 bg-slate-50 p-3 text-sm text-slate-800">
            {result.summary || "No summary."}
          </div>

          {result.actions_taken.length > 0 && (
            <div className="mt-4">
              <h4 className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                Actions taken
              </h4>
              <ul className="mt-2 space-y-2">
                {result.actions_taken.map((action, i) => (
                  <li
                    key={i}
                    className="rounded border border-slate-200 bg-white p-3 text-xs"
                  >
                    <span className="font-mono font-semibold text-slate-700">
                      {action.tool}
                    </span>
                    {Object.keys(action.args).length > 0 && (
                      <pre className="mt-1 overflow-x-auto text-slate-600">
                        {JSON.stringify(action.args)}
                      </pre>
                    )}
                    <pre className="mt-1 overflow-x-auto text-slate-500">
                      {typeof action.result === "object"
                        ? JSON.stringify(action.result, null, 2)
                        : String(action.result)}
                    </pre>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {result.artifact_paths.length > 0 && (
            <div className="mt-4">
              <h4 className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                Artifacts
              </h4>
              <ul className="mt-2 space-y-1">
                {result.artifact_paths.map((path, i) => {
                  const isReport = path.startsWith("reports/");
                  const url = isReport
                    ? `${reportsBase}/${path.replace("reports/", "").split("/")[0]}/pdf`
                    : null;
                  return (
                    <li key={i} className="text-sm">
                      {url && path.includes(".pdf") ? (
                        <a
                          href={url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-primary hover:underline"
                        >
                          {path}
                        </a>
                      ) : (
                        <span className="text-slate-600">{path}</span>
                      )}
                    </li>
                  );
                })}
              </ul>
            </div>
          )}
        </section>
      )}
    </div>
  );
}

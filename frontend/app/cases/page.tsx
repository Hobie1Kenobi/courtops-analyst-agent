"use client";

import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";

interface CaseMetric {
  month: string;
  total_cases: number;
  disposed_cases: number;
  non_disposed_cases: number;
  disposed_pct: number;
  avg_case_age_days: number;
  avg_time_to_disposition_days?: number | null;
}

export default function CasesPage() {
  const [metrics, setMetrics] = useState<CaseMetric[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiFetch<CaseMetric[]>("/cases/metrics/monthly")
      .then(setMetrics)
      .catch(() => {
        setError(
          "Could not load case metrics. Ensure backend is running and you are logged in."
        );
      });
  }, []);

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-lg font-semibold text-slate-900">Court Cases</h2>
        <p className="text-sm text-slate-600">
          Monitor case backlog, case age, time to disposition, and statutory
          thresholds.
        </p>
      </div>
      <section className="rounded-md border bg-white p-4">
        <h3 className="text-sm font-semibold text-slate-800">Monthly Metrics</h3>
        {error && <p className="mt-2 text-xs text-red-600">{error}</p>}
        {!error && (
          <table className="mt-3 w-full table-auto border-collapse text-xs">
            <thead>
              <tr className="border-b bg-slate-50">
                <th className="px-2 py-1 text-left font-semibold">Month</th>
                <th className="px-2 py-1 text-right font-semibold">Total</th>
                <th className="px-2 py-1 text-right font-semibold">Disposed %</th>
                <th className="px-2 py-1 text-right font-semibold">
                  Avg Age (days)
                </th>
                <th className="px-2 py-1 text-right font-semibold">
                  Avg TTD (days)
                </th>
              </tr>
            </thead>
            <tbody>
              {metrics.map((m) => (
                <tr key={m.month} className="border-b last:border-0">
                  <td className="px-2 py-1">{m.month}</td>
                  <td className="px-2 py-1 text-right">{m.total_cases}</td>
                  <td className="px-2 py-1 text-right">
                    {m.disposed_pct.toFixed(1)}%
                  </td>
                  <td className="px-2 py-1 text-right">
                    {m.avg_case_age_days.toFixed(1)}
                  </td>
                  <td className="px-2 py-1 text-right">
                    {m.avg_time_to_disposition_days != null
                      ? m.avg_time_to_disposition_days.toFixed(1)
                      : "-"}
                  </td>
                </tr>
              ))}
              {metrics.length === 0 && !error && (
                <tr>
                  <td
                    colSpan={5}
                    className="px-2 py-2 text-center text-slate-500"
                  >
                    No metrics yet. Run the seed script to populate sample cases.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        )}
      </section>
    </div>
  );
}



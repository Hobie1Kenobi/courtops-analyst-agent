"use client";

import { useEffect, useState } from "react";
import { apiFetch, downloadWithAuth } from "@/lib/api";

interface MonthlyReport {
  period: string;
  pdf_files: string[];
}

export default function ReportsPage() {
  const [reports, setReports] = useState<MonthlyReport[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [downloading, setDownloading] = useState<string | null>(null);
  const [downloadError, setDownloadError] = useState<string | null>(null);
  const [generating, setGenerating] = useState(false);
  const [generateMessage, setGenerateMessage] = useState<string | null>(null);
  const [generatingRAR, setGeneratingRAR] = useState(false);
  const [generateRARMessage, setGenerateRARMessage] = useState<string | null>(null);

  function loadReports() {
    setError(null);
    apiFetch<MonthlyReport[]>("/reports/monthly")
      .then(setReports)
      .catch(() =>
        setError(
          "Could not load monthly reports. Ensure backend is running and you are logged in."
        )
      );
  }

  useEffect(() => {
    loadReports();
  }, []);

  async function handleCsvDownload(entity: string) {
    setDownloadError(null);
    setDownloading(entity);
    try {
      await downloadWithAuth(
        `/reports/custom-query.csv?entity=${entity}`,
        `${entity}_report.csv`
      );
    } catch {
      setDownloadError("Download failed. Make sure you are logged in.");
    } finally {
      setDownloading(null);
    }
  }

  async function handleGenerateMonthly() {
    setDownloadError(null);
    setGenerateMessage(null);
    setGenerating(true);
    try {
      const result = await apiFetch<{ period: string; message: string }>(
        "/reports/monthly/generate",
        { method: "POST" }
      );
      setGenerateMessage(result.message);
      loadReports();
    } catch {
      setDownloadError("Generate failed. Make sure you are logged in.");
    } finally {
      setGenerating(false);
    }
  }

  async function handlePdfDownload(period: string) {
    setDownloadError(null);
    setDownloading(`${period}-pdf`);
    try {
      await downloadWithAuth(
        `/reports/monthly/${period}/pdf`,
        `monthly_operations_${period}.pdf`
      );
    } catch {
      setDownloadError("Download failed. Make sure you are logged in.");
    } finally {
      setDownloading(null);
    }
  }

  async function handleGenerateRevenueAtRisk() {
    setDownloadError(null);
    setGenerateRARMessage(null);
    setGeneratingRAR(true);
    try {
      const result = await apiFetch<{ period: string; message: string }>(
        "/reports/revenue-at-risk/generate",
        { method: "POST" }
      );
      setGenerateRARMessage(result.message);
      loadReports();
    } catch {
      setDownloadError("Generate failed. Make sure you are logged in.");
    } finally {
      setGeneratingRAR(false);
    }
  }

  async function handleRevenueAtRiskPdfDownload(period: string) {
    setDownloadError(null);
    setDownloading(`rar-${period}`);
    try {
      await downloadWithAuth(
        `/reports/revenue-at-risk/${period}/pdf`,
        `revenue_at_risk_fta_${period}.pdf`
      );
    } catch {
      setDownloadError("Download failed. Make sure you are logged in.");
    } finally {
      setDownloading(null);
    }
  }

  async function handleRevenueAtRiskCsvDownload() {
    setDownloadError(null);
    setDownloading("rar-csv");
    try {
      await downloadWithAuth(
        "/reports/revenue-at-risk.csv",
        "revenue_at_risk_fta.csv"
      );
    } catch {
      setDownloadError("Download failed. Make sure you are logged in.");
    } finally {
      setDownloading(null);
    }
  }

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-lg font-semibold text-slate-900">Reports</h2>
        <p className="text-sm text-slate-600">
          Standard operational reports, audit summaries, SLA performance,
          inventory compliance, and a limited custom query builder.
        </p>
      </div>
      {downloadError && (
        <div className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">
          {downloadError}
        </div>
      )}
      <div className="grid gap-4 md:grid-cols-2">
        <section className="rounded-md border bg-white p-4">
          <h3 className="text-sm font-semibold text-slate-800">
            Monthly Operations Report
          </h3>
          <p className="mt-2 text-xs text-slate-600">
            Generate the current month&apos;s bundle (PDF + summary), then download below.
          </p>
          <button
            type="button"
            onClick={handleGenerateMonthly}
            disabled={generating}
            className="mt-2 rounded-md bg-primary px-3 py-1.5 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-60"
          >
            {generating ? "Generating…" : "Generate monthly report now"}
          </button>
          {generateMessage && (
            <p className="mt-2 text-xs text-green-700">{generateMessage}</p>
          )}
          {error && <p className="mt-2 text-xs text-red-600">{error}</p>}
          {!error && (
            <ul className="mt-2 space-y-1 text-xs text-slate-700">
              {reports.map((r) => (
                <li key={r.period}>
                  <button
                    type="button"
                    onClick={() => handlePdfDownload(r.period)}
                    disabled={downloading === `${r.period}-pdf`}
                    className="text-primary hover:underline disabled:opacity-60"
                  >
                    {downloading === `${r.period}-pdf`
                      ? "Downloading..."
                      : `${r.period} PDF`}
                  </button>
                </li>
              ))}
              {reports.length === 0 && (
                <li className="text-slate-500">
                  No monthly bundles detected yet. Let the monthly Celery task
                  run or trigger it manually.
                </li>
              )}
            </ul>
          )}
        </section>
        <section className="rounded-md border bg-white p-4">
          <h3 className="text-sm font-semibold text-slate-800">
            Revenue at Risk (FTA)
          </h3>
          <p className="mt-2 text-xs text-slate-600">
            Crystal Reports-style: FTA/warrant cases grouped by violation type with
            days overdue and outstanding balance. Generate PDF or download CSV.
          </p>
          <div className="mt-2 flex flex-wrap gap-2">
            <button
              type="button"
              onClick={handleGenerateRevenueAtRisk}
              disabled={generatingRAR}
              className="rounded-md bg-primary px-3 py-1.5 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-60"
            >
              {generatingRAR ? "Generating…" : "Generate Revenue at Risk report"}
            </button>
            <button
              type="button"
              onClick={() => handleRevenueAtRiskCsvDownload()}
              disabled={!!downloading}
              className="rounded-md border border-slate-300 bg-white px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-60"
            >
              {downloading === "rar-csv" ? "Downloading…" : "Download CSV"}
            </button>
          </div>
          {generateRARMessage && (
            <p className="mt-2 text-xs text-green-700">{generateRARMessage}</p>
          )}
          {!error && reports.length > 0 && (
            <p className="mt-2 text-xs text-slate-600">
              Download PDF:{" "}
              {[...new Set(reports.map((r) => r.period))].map((period) => (
                <button
                  key={period}
                  type="button"
                  onClick={() => handleRevenueAtRiskPdfDownload(period)}
                  disabled={downloading === `rar-${period}`}
                  className="mr-2 text-primary hover:underline disabled:opacity-60"
                >
                  {period}
                </button>
              ))}
            </p>
          )}
        </section>
        <section className="rounded-md border bg-white p-4">
          <h3 className="text-sm font-semibold text-slate-800">
            Custom Query Builder
          </h3>
          <p className="mt-2 text-xs text-slate-600">
            Download quick CSV snapshots of key entities (uses your login):
          </p>
          <ul className="mt-2 space-y-2 text-xs">
            <li>
              <button
                type="button"
                onClick={() => handleCsvDownload("cases")}
                disabled={!!downloading}
                className="rounded-md bg-primary px-2 py-1 text-white hover:bg-blue-700 disabled:opacity-60"
              >
                {downloading === "cases" ? "Downloading..." : "Cases CSV"}
              </button>
            </li>
            <li>
              <button
                type="button"
                onClick={() => handleCsvDownload("tickets")}
                disabled={!!downloading}
                className="rounded-md bg-primary px-2 py-1 text-white hover:bg-blue-700 disabled:opacity-60"
              >
                {downloading === "tickets" ? "Downloading..." : "Tickets CSV"}
              </button>
            </li>
            <li>
              <button
                type="button"
                onClick={() => handleCsvDownload("devices")}
                disabled={!!downloading}
                className="rounded-md bg-primary px-2 py-1 text-white hover:bg-blue-700 disabled:opacity-60"
              >
                {downloading === "devices" ? "Downloading..." : "Devices CSV"}
              </button>
            </li>
          </ul>
        </section>
      </div>
    </div>
  );
}



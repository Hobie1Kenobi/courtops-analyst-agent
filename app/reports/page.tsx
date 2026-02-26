"use client";

import { useState } from "react";
import {
  Download,
  FileText,
  FileSpreadsheet,
  FileJson,
  Eye,
  X,
  ChevronDown,
  Plus,
  Search,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

/* ------------------------------------------------------------------ */
/*  Mock data                                                          */
/* ------------------------------------------------------------------ */

type ReportFormat = "pdf" | "csv" | "docx" | "json" | "txt";

const formatConfig: Record<
  ReportFormat,
  { icon: React.ElementType; variant: "danger" | "success" | "info" | "warning" | "muted" }
> = {
  pdf: { icon: FileText, variant: "danger" },
  csv: { icon: FileSpreadsheet, variant: "success" },
  docx: { icon: FileText, variant: "info" },
  json: { icon: FileJson, variant: "warning" },
  txt: { icon: FileText, variant: "muted" },
};

interface Report {
  id: number;
  name: string;
  project: string;
  type: string;
  createdAt: string;
  format: ReportFormat;
  size: string;
  summary?: string;
}

const reports: Report[] = [
  {
    id: 1,
    name: "Monthly Operations Summary - Feb 2026",
    project: "FY2026 Operations",
    type: "Monthly",
    createdAt: "Feb 26, 2026",
    format: "pdf",
    size: "2.1 MB",
    summary:
      "Executive summary covering case backlog (1,204 open), SLA performance (87% met), help desk metrics (47 open tickets, 12 overdue), and revenue-at-risk analysis ($23.4K identified).",
  },
  {
    id: 2,
    name: "SLA Compliance Report - Week 9",
    project: "FY2026 Operations",
    type: "Weekly",
    createdAt: "Feb 25, 2026",
    format: "csv",
    size: "340 KB",
    summary:
      "Detailed SLA compliance data for 547 tickets. Overall compliance: 87%. Priority 1 tickets: 92% met. Priority 3: 78% met.",
  },
  {
    id: 3,
    name: "Revenue-at-Risk Analysis",
    project: "FY2026 Operations",
    type: "Ad Hoc",
    createdAt: "Feb 24, 2026",
    format: "pdf",
    size: "1.5 MB",
    summary:
      "Analysis of $23,400 in revenue at risk from 156 FTA cases. Breakdown by charge type, aging, and recommended collection actions.",
  },
  {
    id: 4,
    name: "Audit Findings - Feb 2026",
    project: "FY2026 Operations",
    type: "Audit",
    createdAt: "Feb 24, 2026",
    format: "docx",
    size: "890 KB",
    summary:
      "3 anomalies flagged: 1 off-hours bulk export, 2 failed login attempts from unusual IPs. Recommended actions included.",
  },
  {
    id: 5,
    name: "Inventory Compliance Snapshot",
    project: "FY2026 Operations",
    type: "Daily",
    createdAt: "Feb 23, 2026",
    format: "json",
    size: "156 KB",
  },
  {
    id: 6,
    name: "Case Disposition Metrics",
    project: "FY2026 Operations",
    type: "Monthly",
    createdAt: "Feb 22, 2026",
    format: "csv",
    size: "280 KB",
  },
  {
    id: 7,
    name: "Patch Status Report",
    project: "FY2026 Operations",
    type: "Weekly",
    createdAt: "Feb 21, 2026",
    format: "pdf",
    size: "720 KB",
  },
  {
    id: 8,
    name: "Help Desk Performance Q1",
    project: "FY2026 Operations",
    type: "Quarterly",
    createdAt: "Feb 20, 2026",
    format: "docx",
    size: "1.3 MB",
  },
  {
    id: 9,
    name: "Daily Operations Log",
    project: "FY2026 Operations",
    type: "Daily",
    createdAt: "Feb 19, 2026",
    format: "txt",
    size: "45 KB",
  },
  {
    id: 10,
    name: "Change Request Summary",
    project: "FY2026 Operations",
    type: "Ad Hoc",
    createdAt: "Feb 18, 2026",
    format: "csv",
    size: "112 KB",
  },
];

const typeOptions = ["All Types", "Monthly", "Weekly", "Daily", "Quarterly", "Audit", "Ad Hoc"];
const formatOptions = ["All Formats", "PDF", "CSV", "DOCX", "JSON", "TXT"];

/* ------------------------------------------------------------------ */

export default function ReportsPage() {
  const [typeFilter, setTypeFilter] = useState("All Types");
  const [formatFilter, setFormatFilter] = useState("All Formats");
  const [searchQuery, setSearchQuery] = useState("");
  const [previewReport, setPreviewReport] = useState<Report | null>(null);

  const filteredReports = reports.filter((r) => {
    if (typeFilter !== "All Types" && r.type !== typeFilter) return false;
    if (
      formatFilter !== "All Formats" &&
      r.format !== formatFilter.toLowerCase()
    )
      return false;
    if (
      searchQuery &&
      !r.name.toLowerCase().includes(searchQuery.toLowerCase())
    )
      return false;
    return true;
  });

  return (
    <div className="space-y-6">
      {/* Filter Bar */}
      <Card>
        <CardContent className="flex flex-wrap items-center gap-3 p-4">
          <div className="relative min-w-[200px] flex-1">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <input
              type="text"
              placeholder="Search reports..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="h-9 w-full rounded-md border bg-card pl-9 pr-3 text-sm text-foreground placeholder:text-muted-foreground focus:border-primary focus:outline-none focus:ring-1 focus:ring-ring"
            />
          </div>

          <div className="relative">
            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
              className="h-9 appearance-none rounded-md border bg-card px-3 pr-8 text-sm font-medium text-foreground focus:border-primary focus:outline-none focus:ring-1 focus:ring-ring"
            >
              {typeOptions.map((opt) => (
                <option key={opt}>{opt}</option>
              ))}
            </select>
            <ChevronDown className="pointer-events-none absolute right-2 top-1/2 h-3 w-3 -translate-y-1/2 text-muted-foreground" />
          </div>

          <div className="relative">
            <select
              value={formatFilter}
              onChange={(e) => setFormatFilter(e.target.value)}
              className="h-9 appearance-none rounded-md border bg-card px-3 pr-8 text-sm font-medium text-foreground focus:border-primary focus:outline-none focus:ring-1 focus:ring-ring"
            >
              {formatOptions.map((opt) => (
                <option key={opt}>{opt}</option>
              ))}
            </select>
            <ChevronDown className="pointer-events-none absolute right-2 top-1/2 h-3 w-3 -translate-y-1/2 text-muted-foreground" />
          </div>

          <Button variant="primary" size="md">
            <Plus className="mr-1 h-3.5 w-3.5" />
            Generate Report
          </Button>
        </CardContent>
      </Card>

      {/* Report Table */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Reports</CardTitle>
          <Badge variant="muted">{filteredReports.length} reports</Badge>
        </CardHeader>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b bg-muted/40 text-left text-xs font-medium uppercase tracking-wider text-muted-foreground">
                  <th className="px-4 py-2.5">Report</th>
                  <th className="hidden px-4 py-2.5 sm:table-cell">Type</th>
                  <th className="px-4 py-2.5">Format</th>
                  <th className="hidden px-4 py-2.5 md:table-cell">Created</th>
                  <th className="hidden px-4 py-2.5 lg:table-cell">Size</th>
                  <th className="px-4 py-2.5 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {filteredReports.map((report) => {
                  const fmt = formatConfig[report.format];
                  const FormatIcon = fmt.icon;

                  return (
                    <tr
                      key={report.id}
                      className="transition-colors hover:bg-muted/30"
                    >
                      <td className="px-4 py-3">
                        <div className="min-w-0">
                          <p className="truncate font-medium text-foreground">
                            {report.name}
                          </p>
                          <p className="text-xs text-muted-foreground">
                            {report.project}
                          </p>
                        </div>
                      </td>
                      <td className="hidden px-4 py-3 sm:table-cell">
                        <Badge variant="muted">{report.type}</Badge>
                      </td>
                      <td className="px-4 py-3">
                        <Badge variant={fmt.variant}>
                          <FormatIcon className="mr-1 h-3 w-3" />
                          {report.format.toUpperCase()}
                        </Badge>
                      </td>
                      <td className="hidden px-4 py-3 text-muted-foreground md:table-cell">
                        {report.createdAt}
                      </td>
                      <td className="hidden px-4 py-3 text-muted-foreground lg:table-cell">
                        {report.size}
                      </td>
                      <td className="px-4 py-3 text-right">
                        <div className="flex items-center justify-end gap-1">
                          {report.summary && (
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => setPreviewReport(report)}
                            >
                              <Eye className="mr-1 h-3 w-3" />
                              Preview
                            </Button>
                          )}
                          <Button variant="ghost" size="sm">
                            <Download className="mr-1 h-3 w-3" />
                            Download
                          </Button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Preview Drawer */}
      {previewReport && (
        <div className="fixed inset-0 z-50 flex justify-end">
          <div
            className="absolute inset-0 bg-foreground/30"
            onClick={() => setPreviewReport(null)}
          />
          <aside className="relative z-10 flex h-full w-full max-w-lg flex-col bg-card shadow-xl">
            <div className="flex items-center justify-between border-b px-6 py-4">
              <h2 className="text-lg font-semibold text-foreground">
                Report Preview
              </h2>
              <button
                onClick={() => setPreviewReport(null)}
                className="rounded-md p-1 text-muted-foreground hover:text-foreground"
              >
                <X className="h-5 w-5" />
                <span className="sr-only">Close preview</span>
              </button>
            </div>
            <div className="flex-1 space-y-6 overflow-y-auto p-6">
              <div>
                <h3 className="text-base font-semibold text-foreground">
                  {previewReport.name}
                </h3>
                <p className="mt-1 text-sm text-muted-foreground">
                  {previewReport.project}
                </p>
              </div>

              <div className="flex flex-wrap gap-2">
                <Badge variant="muted">{previewReport.type}</Badge>
                <Badge variant={formatConfig[previewReport.format].variant}>
                  {previewReport.format.toUpperCase()}
                </Badge>
                <Badge variant="muted">{previewReport.size}</Badge>
              </div>

              <div>
                <h4 className="text-sm font-semibold text-foreground">
                  Summary
                </h4>
                <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
                  {previewReport.summary}
                </p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="rounded-md border p-3">
                  <p className="text-xs text-muted-foreground">Created</p>
                  <p className="mt-1 text-sm font-medium text-foreground">
                    {previewReport.createdAt}
                  </p>
                </div>
                <div className="rounded-md border p-3">
                  <p className="text-xs text-muted-foreground">File Size</p>
                  <p className="mt-1 text-sm font-medium text-foreground">
                    {previewReport.size}
                  </p>
                </div>
              </div>

              <Button variant="primary" size="lg" className="w-full">
                <Download className="mr-2 h-4 w-4" />
                Download Report
              </Button>
            </div>
          </aside>
        </div>
      )}
    </div>
  );
}

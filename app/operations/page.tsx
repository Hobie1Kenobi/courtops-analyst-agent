"use client";

import {
  Play,
  Clock,
  CheckCircle2,
  XCircle,
  Loader2,
  Shield,
  CalendarRange,
  GraduationCap,
  RotateCcw,
  Download,
  FileText,
  Zap,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";

/* ------------------------------------------------------------------ */
/*  Mock data                                                          */
/* ------------------------------------------------------------------ */

type JobStatus = "completed" | "running" | "failed" | "queued";

const statusBadge: Record<
  JobStatus,
  { variant: "success" | "info" | "danger" | "muted"; icon: React.ElementType }
> = {
  completed: { variant: "success", icon: CheckCircle2 },
  running: { variant: "info", icon: Loader2 },
  failed: { variant: "danger", icon: XCircle },
  queued: { variant: "muted", icon: Clock },
};

const operationCards = [
  {
    name: "Run Daily Ops",
    description:
      "Execute the full daily operations pipeline: ingest data, run SLA checks, flag overdue tickets, and generate daily summary.",
    icon: Zap,
    lastRun: "Today, 09:14 AM",
    status: "completed" as JobStatus,
  },
  {
    name: "Run Audit Scan",
    description:
      "Scan for security anomalies: failed logins, off-hours data exports, bulk changes, and escalation pattern analysis.",
    icon: Shield,
    lastRun: "Yesterday, 06:00 PM",
    status: "completed" as JobStatus,
  },
  {
    name: "Run Monthly Package",
    description:
      "Generate the full monthly reporting package including executive summary, SLA report, revenue-at-risk analysis, and audit findings.",
    icon: CalendarRange,
    lastRun: "Feb 1, 2026",
    status: "completed" as JobStatus,
  },
  {
    name: "Run Training Scenario",
    description:
      "Launch a training twin scenario for interactive learning and testing of court operations procedures.",
    icon: GraduationCap,
    lastRun: "Feb 24, 2026",
    status: "completed" as JobStatus,
  },
];

const activeJob = {
  name: "Daily Operations Pipeline",
  progress: 72,
  currentStep: "Running SLA compliance checks...",
  startedAt: "10:30 AM",
  steps: [
    { label: "Data ingestion", done: true },
    { label: "Ticket triage", done: true },
    { label: "SLA compliance checks", done: false },
    { label: "Case aging analysis", done: false },
    { label: "Revenue-at-risk calc", done: false },
    { label: "Generate summary", done: false },
  ],
};

interface JobHistory {
  id: number;
  name: string;
  type: string;
  started: string;
  duration: string;
  status: JobStatus;
  artifacts: number;
}

const jobHistory: JobHistory[] = [
  {
    id: 1,
    name: "Daily Ops Pipeline",
    type: "Daily",
    started: "Feb 26, 09:14 AM",
    duration: "4m 32s",
    status: "completed",
    artifacts: 3,
  },
  {
    id: 2,
    name: "Audit Scan",
    type: "Audit",
    started: "Feb 25, 06:00 PM",
    duration: "2m 18s",
    status: "completed",
    artifacts: 1,
  },
  {
    id: 3,
    name: "Daily Ops Pipeline",
    type: "Daily",
    started: "Feb 25, 09:12 AM",
    duration: "5m 01s",
    status: "completed",
    artifacts: 3,
  },
  {
    id: 4,
    name: "Training Scenario",
    type: "Training",
    started: "Feb 24, 02:15 PM",
    duration: "12m 44s",
    status: "completed",
    artifacts: 0,
  },
  {
    id: 5,
    name: "Monthly Package",
    type: "Monthly",
    started: "Feb 1, 12:00 AM",
    duration: "8m 22s",
    status: "completed",
    artifacts: 5,
  },
  {
    id: 6,
    name: "Daily Ops Pipeline",
    type: "Daily",
    started: "Jan 31, 09:10 AM",
    duration: "--",
    status: "failed",
    artifacts: 0,
  },
];

/* ------------------------------------------------------------------ */

export default function OperationsPage() {
  return (
    <div className="space-y-6">
      {/* Run Controls */}
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {operationCards.map((op) => {
          const Icon = op.icon;
          const st = statusBadge[op.status];
          const StatusIcon = st.icon;

          return (
            <Card key={op.name}>
              <CardContent className="flex flex-col gap-3 p-4">
                <div className="flex items-start justify-between">
                  <div className="rounded-lg bg-primary/10 p-2">
                    <Icon className="h-5 w-5 text-primary" />
                  </div>
                  <Badge variant={st.variant}>
                    <StatusIcon className="mr-1 h-3 w-3" />
                    {op.status.charAt(0).toUpperCase() + op.status.slice(1)}
                  </Badge>
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-foreground">
                    {op.name}
                  </h3>
                  <p className="mt-1 text-xs leading-relaxed text-muted-foreground">
                    {op.description}
                  </p>
                </div>
                <div className="flex items-center justify-between pt-1">
                  <span className="flex items-center gap-1 text-[11px] text-muted-foreground">
                    <Clock className="h-3 w-3" /> {op.lastRun}
                  </span>
                  <Button variant="primary" size="sm">
                    <Play className="mr-1 h-3 w-3" />
                    Run
                  </Button>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Active Job Progress */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div className="flex items-center gap-2">
            <Loader2 className="h-4 w-4 animate-spin text-primary" />
            <CardTitle>Active Job: {activeJob.name}</CardTitle>
          </div>
          <Badge variant="info">
            {activeJob.progress}% complete
          </Badge>
        </CardHeader>
        <CardContent className="space-y-4">
          <Progress value={activeJob.progress} variant="primary" />

          <div className="flex items-center justify-between text-xs text-muted-foreground">
            <span>{activeJob.currentStep}</span>
            <span>Started {activeJob.startedAt}</span>
          </div>

          <div className="flex flex-wrap gap-2">
            {activeJob.steps.map((step) => (
              <Badge
                key={step.label}
                variant={step.done ? "success" : "muted"}
              >
                {step.done && (
                  <CheckCircle2 className="mr-1 h-3 w-3" />
                )}
                {step.label}
              </Badge>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Job History */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Job History</CardTitle>
          <Button variant="ghost" size="sm">
            <RotateCcw className="mr-1 h-3 w-3" />
            Refresh
          </Button>
        </CardHeader>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b bg-muted/40 text-left text-xs font-medium uppercase tracking-wider text-muted-foreground">
                  <th className="px-4 py-2.5">Job Name</th>
                  <th className="px-4 py-2.5">Type</th>
                  <th className="px-4 py-2.5 hidden sm:table-cell">Started</th>
                  <th className="px-4 py-2.5">Duration</th>
                  <th className="px-4 py-2.5">Status</th>
                  <th className="px-4 py-2.5 text-right">Artifacts</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {jobHistory.map((job) => {
                  const st = statusBadge[job.status];
                  const StatusIcon = st.icon;
                  return (
                    <tr
                      key={job.id}
                      className="transition-colors hover:bg-muted/30"
                    >
                      <td className="px-4 py-3 font-medium text-foreground">
                        {job.name}
                      </td>
                      <td className="px-4 py-3">
                        <Badge variant="muted">{job.type}</Badge>
                      </td>
                      <td className="px-4 py-3 text-muted-foreground hidden sm:table-cell">
                        {job.started}
                      </td>
                      <td className="px-4 py-3 text-muted-foreground">
                        {job.duration}
                      </td>
                      <td className="px-4 py-3">
                        <Badge variant={st.variant}>
                          <StatusIcon className="mr-1 h-3 w-3" />
                          {job.status.charAt(0).toUpperCase() + job.status.slice(1)}
                        </Badge>
                      </td>
                      <td className="px-4 py-3 text-right">
                        {job.artifacts > 0 ? (
                          <Button variant="ghost" size="sm">
                            <Download className="mr-1 h-3 w-3" />
                            {job.artifacts}
                          </Button>
                        ) : (
                          <span className="text-xs text-muted-foreground">
                            --
                          </span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

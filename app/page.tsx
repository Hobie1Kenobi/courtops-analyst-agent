import {
  Ticket,
  AlertTriangle,
  Monitor,
  Gavel,
  DollarSign,
  Wrench,
  TrendingUp,
  TrendingDown,
  ArrowRight,
  Upload,
  Play,
  FileText,
  Clock,
  CheckCircle2,
  XCircle,
  FileUp,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import Link from "next/link";

/* ------------------------------------------------------------------ */
/*  Static mock data — will be replaced with live API calls by Cursor */
/* ------------------------------------------------------------------ */

const kpis = [
  {
    label: "Open Tickets",
    value: "47",
    change: "+3",
    trend: "up" as const,
    icon: Ticket,
    color: "text-primary",
    bg: "bg-primary/10",
  },
  {
    label: "Overdue SLAs",
    value: "12",
    change: "+2",
    trend: "up" as const,
    icon: AlertTriangle,
    color: "text-danger",
    bg: "bg-danger/10",
  },
  {
    label: "Devices Flagged",
    value: "8",
    change: "-1",
    trend: "down" as const,
    icon: Monitor,
    color: "text-warning",
    bg: "bg-warning/10",
  },
  {
    label: "FTA Cases",
    value: "156",
    change: "+14",
    trend: "up" as const,
    icon: Gavel,
    color: "text-info",
    bg: "bg-info/10",
  },
  {
    label: "Revenue at Risk",
    value: "$23.4K",
    change: "+$1.2K",
    trend: "up" as const,
    icon: DollarSign,
    color: "text-warning",
    bg: "bg-warning/10",
  },
  {
    label: "Patches Pending",
    value: "5",
    change: "-2",
    trend: "down" as const,
    icon: Wrench,
    color: "text-success",
    bg: "bg-success/10",
  },
];

const recentActivity = [
  {
    id: 1,
    action: "Daily operations run completed",
    detail: "47 tickets, 156 cases processed",
    time: "12 min ago",
    icon: CheckCircle2,
    iconColor: "text-success",
  },
  {
    id: 2,
    action: "Monthly report generated",
    detail: "February 2026 operations summary",
    time: "2 hours ago",
    icon: FileText,
    iconColor: "text-primary",
  },
  {
    id: 3,
    action: "File imported successfully",
    detail: "cases_export_feb2026.csv — 1,204 rows",
    time: "4 hours ago",
    icon: FileUp,
    iconColor: "text-info",
  },
  {
    id: 4,
    action: "Audit scan flagged 3 anomalies",
    detail: "Off-hours bulk export, 2 failed logins",
    time: "6 hours ago",
    icon: AlertTriangle,
    iconColor: "text-warning",
  },
  {
    id: 5,
    action: "Patch verification failed",
    detail: "CMS v4.2.1 patch on Server-03",
    time: "Yesterday",
    icon: XCircle,
    iconColor: "text-danger",
  },
];

const quickActions = [
  { label: "Upload Files", href: "/uploads", icon: Upload },
  { label: "Run Daily Ops", href: "/operations", icon: Play },
  { label: "View Reports", href: "/reports", icon: FileText },
];

/* ------------------------------------------------------------------ */

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      {/* KPI Row */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
        {kpis.map((kpi) => {
          const Icon = kpi.icon;
          return (
            <Card key={kpi.label}>
              <CardContent className="flex items-start gap-3 px-4 py-4">
                <div className={`rounded-lg p-2 ${kpi.bg}`}>
                  <Icon className={`h-4 w-4 ${kpi.color}`} />
                </div>
                <div className="min-w-0 flex-1">
                  <p className="text-xs font-medium text-muted-foreground">
                    {kpi.label}
                  </p>
                  <p className="mt-0.5 text-xl font-bold text-foreground">
                    {kpi.value}
                  </p>
                  <div className="mt-1 flex items-center gap-1">
                    {kpi.trend === "up" ? (
                      <TrendingUp className="h-3 w-3 text-danger" />
                    ) : (
                      <TrendingDown className="h-3 w-3 text-success" />
                    )}
                    <span
                      className={`text-[11px] font-medium ${
                        kpi.trend === "up"
                          ? "text-danger"
                          : "text-success"
                      }`}
                    >
                      {kpi.change}
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Recent Activity */}
        <Card className="lg:col-span-2">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>Recent Activity</CardTitle>
            <Badge variant="muted">Live</Badge>
          </CardHeader>
          <CardContent className="p-0">
            <ul className="divide-y">
              {recentActivity.map((item) => {
                const Icon = item.icon;
                return (
                  <li
                    key={item.id}
                    className="flex items-start gap-3 px-4 py-3"
                  >
                    <Icon
                      className={`mt-0.5 h-4 w-4 shrink-0 ${item.iconColor}`}
                    />
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-medium text-foreground">
                        {item.action}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {item.detail}
                      </p>
                    </div>
                    <span className="shrink-0 text-[11px] text-muted-foreground flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      {item.time}
                    </span>
                  </li>
                );
              })}
            </ul>
          </CardContent>
        </Card>

        {/* Quick Actions + Project Info */}
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {quickActions.map((action) => {
                const Icon = action.icon;
                return (
                  <Link
                    key={action.href}
                    href={action.href}
                    className="flex items-center gap-3 rounded-md border px-3 py-2.5 text-sm font-medium text-foreground transition-colors hover:bg-muted"
                  >
                    <Icon className="h-4 w-4 text-primary" />
                    <span className="flex-1">{action.label}</span>
                    <ArrowRight className="h-3.5 w-3.5 text-muted-foreground" />
                  </Link>
                );
              })}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Project Overview</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Workspace</span>
                <span className="font-medium text-foreground">
                  Municipal Court Demo
                </span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Project</span>
                <span className="font-medium text-foreground">
                  FY2026 Operations
                </span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Last Import</span>
                <span className="font-medium text-foreground">
                  Feb 26, 2026
                </span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Status</span>
                <Badge variant="success">Active</Badge>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

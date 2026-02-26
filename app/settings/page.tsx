import {
  Building2,
  Users,
  ShieldCheck,
  Plug,
  Clock,
  Globe,
  AlertTriangle,
  CheckCircle2,
  LogIn,
  FileDown,
  UserCog,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

/* ------------------------------------------------------------------ */
/*  Mock data                                                          */
/* ------------------------------------------------------------------ */

const workspaceInfo = {
  name: "Municipal Court Demo",
  description: "Demonstration workspace for CourtOps Analyst Agent platform.",
  plan: "Professional",
  region: "US-East",
  created: "Jan 15, 2026",
};

type UserRole = "Supervisor" | "Analyst" | "IT Support" | "Clerk" | "Read-only";

const roleBadge: Record<UserRole, "danger" | "info" | "warning" | "success" | "muted"> = {
  Supervisor: "danger",
  Analyst: "info",
  "IT Support": "warning",
  Clerk: "success",
  "Read-only": "muted",
};

interface User {
  id: number;
  name: string;
  email: string;
  role: UserRole;
  lastLogin: string;
  status: "Active" | "Inactive";
}

const users: User[] = [
  {
    id: 1,
    name: "Sarah Martinez",
    email: "s.martinez@courtops.dev",
    role: "Supervisor",
    lastLogin: "Feb 26, 2026 09:01 AM",
    status: "Active",
  },
  {
    id: 2,
    name: "David Chen",
    email: "d.chen@courtops.dev",
    role: "Analyst",
    lastLogin: "Feb 26, 2026 08:45 AM",
    status: "Active",
  },
  {
    id: 3,
    name: "James Wilson",
    email: "j.wilson@courtops.dev",
    role: "IT Support",
    lastLogin: "Feb 25, 2026 04:30 PM",
    status: "Active",
  },
  {
    id: 4,
    name: "Maria Lopez",
    email: "m.lopez@courtops.dev",
    role: "Clerk",
    lastLogin: "Feb 25, 2026 02:15 PM",
    status: "Active",
  },
  {
    id: 5,
    name: "Robert Kim",
    email: "r.kim@courtops.dev",
    role: "Read-only",
    lastLogin: "Feb 20, 2026 11:00 AM",
    status: "Inactive",
  },
];

interface AuditEvent {
  id: number;
  action: string;
  user: string;
  time: string;
  icon: React.ElementType;
  severity: "info" | "warning" | "danger";
}

const auditLog: AuditEvent[] = [
  {
    id: 1,
    action: "User login from new IP address",
    user: "d.chen@courtops.dev",
    time: "Feb 26, 08:45 AM",
    icon: LogIn,
    severity: "info",
  },
  {
    id: 2,
    action: "Bulk data export (1,204 rows)",
    user: "s.martinez@courtops.dev",
    time: "Feb 26, 09:14 AM",
    icon: FileDown,
    severity: "warning",
  },
  {
    id: 3,
    action: "Failed login attempt (3 consecutive)",
    user: "r.kim@courtops.dev",
    time: "Feb 25, 11:32 PM",
    icon: AlertTriangle,
    severity: "danger",
  },
  {
    id: 4,
    action: "Role changed: Clerk -> Analyst",
    user: "m.lopez@courtops.dev",
    time: "Feb 24, 03:00 PM",
    icon: UserCog,
    severity: "info",
  },
  {
    id: 5,
    action: "Password reset completed",
    user: "j.wilson@courtops.dev",
    time: "Feb 24, 10:20 AM",
    icon: ShieldCheck,
    severity: "info",
  },
];

/* ------------------------------------------------------------------ */

export default function SettingsPage() {
  return (
    <div className="space-y-6">
      {/* Workspace Configuration */}
      <Card>
        <CardHeader className="flex flex-row items-center gap-2">
          <Building2 className="h-4 w-4 text-muted-foreground" />
          <CardTitle>Workspace Configuration</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-6 md:grid-cols-2">
            <div className="space-y-4">
              <div>
                <label className="text-xs font-medium text-muted-foreground">
                  Workspace Name
                </label>
                <input
                  type="text"
                  defaultValue={workspaceInfo.name}
                  className="mt-1 block h-9 w-full rounded-md border bg-card px-3 text-sm text-foreground focus:border-primary focus:outline-none focus:ring-1 focus:ring-ring"
                  readOnly
                />
              </div>
              <div>
                <label className="text-xs font-medium text-muted-foreground">
                  Description
                </label>
                <textarea
                  defaultValue={workspaceInfo.description}
                  rows={3}
                  className="mt-1 block w-full resize-none rounded-md border bg-card px-3 py-2 text-sm text-foreground focus:border-primary focus:outline-none focus:ring-1 focus:ring-ring"
                  readOnly
                />
              </div>
            </div>
            <div className="space-y-3">
              <div className="flex items-center justify-between rounded-md border px-3 py-2.5">
                <span className="text-sm text-muted-foreground">Plan</span>
                <Badge variant="default">{workspaceInfo.plan}</Badge>
              </div>
              <div className="flex items-center justify-between rounded-md border px-3 py-2.5">
                <span className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Globe className="h-3.5 w-3.5" />
                  Region
                </span>
                <span className="text-sm font-medium text-foreground">
                  {workspaceInfo.region}
                </span>
              </div>
              <div className="flex items-center justify-between rounded-md border px-3 py-2.5">
                <span className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Clock className="h-3.5 w-3.5" />
                  Created
                </span>
                <span className="text-sm font-medium text-foreground">
                  {workspaceInfo.created}
                </span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* User & Role Management */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div className="flex items-center gap-2">
            <Users className="h-4 w-4 text-muted-foreground" />
            <CardTitle>Users & Roles</CardTitle>
          </div>
          <Button variant="primary" size="sm">
            Invite User
          </Button>
        </CardHeader>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b bg-muted/40 text-left text-xs font-medium uppercase tracking-wider text-muted-foreground">
                  <th className="px-4 py-2.5">User</th>
                  <th className="px-4 py-2.5">Role</th>
                  <th className="hidden px-4 py-2.5 md:table-cell">
                    Last Login
                  </th>
                  <th className="px-4 py-2.5">Status</th>
                  <th className="px-4 py-2.5 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {users.map((user) => (
                  <tr
                    key={user.id}
                    className="transition-colors hover:bg-muted/30"
                  >
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-3">
                        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary/10 text-xs font-bold text-primary">
                          {user.name
                            .split(" ")
                            .map((n) => n[0])
                            .join("")}
                        </div>
                        <div className="min-w-0">
                          <p className="truncate font-medium text-foreground">
                            {user.name}
                          </p>
                          <p className="truncate text-xs text-muted-foreground">
                            {user.email}
                          </p>
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <Badge variant={roleBadge[user.role]}>
                        {user.role}
                      </Badge>
                    </td>
                    <td className="hidden px-4 py-3 text-muted-foreground md:table-cell">
                      {user.lastLogin}
                    </td>
                    <td className="px-4 py-3">
                      <Badge
                        variant={
                          user.status === "Active" ? "success" : "muted"
                        }
                      >
                        {user.status}
                      </Badge>
                    </td>
                    <td className="px-4 py-3 text-right">
                      <Button variant="ghost" size="sm">
                        Edit
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Audit Log */}
        <Card>
          <CardHeader className="flex flex-row items-center gap-2">
            <ShieldCheck className="h-4 w-4 text-muted-foreground" />
            <CardTitle>Recent Audit Events</CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <ul className="divide-y">
              {auditLog.map((event) => {
                const Icon = event.icon;
                const severityColor = {
                  info: "text-info",
                  warning: "text-warning",
                  danger: "text-danger",
                };
                return (
                  <li
                    key={event.id}
                    className="flex items-start gap-3 px-4 py-3"
                  >
                    <Icon
                      className={`mt-0.5 h-4 w-4 shrink-0 ${severityColor[event.severity]}`}
                    />
                    <div className="min-w-0 flex-1">
                      <p className="text-sm text-foreground">
                        {event.action}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {event.user} &middot; {event.time}
                      </p>
                    </div>
                  </li>
                );
              })}
            </ul>
          </CardContent>
        </Card>

        {/* API & Integrations */}
        <Card>
          <CardHeader className="flex flex-row items-center gap-2">
            <Plug className="h-4 w-4 text-muted-foreground" />
            <CardTitle>API & Integrations</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between rounded-md border px-3 py-2.5">
              <div>
                <p className="text-sm font-medium text-foreground">
                  Backend API
                </p>
                <p className="text-xs text-muted-foreground">
                  FastAPI backend service
                </p>
              </div>
              <Badge variant="success">
                <CheckCircle2 className="mr-1 h-3 w-3" />
                Connected
              </Badge>
            </div>
            <div className="flex items-center justify-between rounded-md border px-3 py-2.5">
              <div>
                <p className="text-sm font-medium text-foreground">
                  Database
                </p>
                <p className="text-xs text-muted-foreground">
                  PostgreSQL via Supabase
                </p>
              </div>
              <Badge variant="success">
                <CheckCircle2 className="mr-1 h-3 w-3" />
                Connected
              </Badge>
            </div>
            <div className="flex items-center justify-between rounded-md border px-3 py-2.5">
              <div>
                <p className="text-sm font-medium text-foreground">
                  AI Gateway
                </p>
                <p className="text-xs text-muted-foreground">
                  Vercel AI Gateway
                </p>
              </div>
              <Badge variant="muted">Not configured</Badge>
            </div>
            <div className="flex items-center justify-between rounded-md border px-3 py-2.5">
              <div>
                <p className="text-sm font-medium text-foreground">
                  Redis Cache
                </p>
                <p className="text-xs text-muted-foreground">
                  Upstash Redis
                </p>
              </div>
              <Badge variant="muted">Not configured</Badge>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

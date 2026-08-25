"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import {
  LayoutDashboard,
  Upload,
  GitBranch,
  Play,
  FileText,
  GraduationCap,
  Settings,
  ChevronDown,
  ChevronRight,
  FolderArchive,
  Briefcase,
  Ticket,
  Box,
  Wrench,
  FileEdit,
  Bot,
  FlaskConical,
  X,
} from "lucide-react";
import { cn } from "../utils/cn";

interface NavItem {
  label: string;
  href: string;
  icon: React.ElementType;
}

const primaryNav: NavItem[] = [
  { label: "Dashboard", href: "/", icon: LayoutDashboard },
  { label: "Uploads", href: "/uploads", icon: Upload },
  { label: "Data Mapping", href: "/data-mapping", icon: GitBranch },
  { label: "Operations", href: "/operations", icon: Play },
  { label: "Reports", href: "/reports", icon: FileText },
  { label: "Training Twin", href: "/training", icon: GraduationCap },
  { label: "Settings", href: "/settings", icon: Settings },
];

const legacyNav: NavItem[] = [
  { label: "Cases", href: "/cases", icon: Briefcase },
  { label: "Tickets", href: "/tickets", icon: Ticket },
  { label: "Inventory", href: "/inventory", icon: Box },
  { label: "Patches", href: "/patches", icon: Wrench },
  { label: "Change Requests", href: "/change-requests", icon: FileEdit },
  { label: "Agent Console", href: "/agent", icon: Bot },
  { label: "Ops Console", href: "/ops", icon: Play },
  { label: "Training Ops", href: "/training-ops", icon: GraduationCap },
  { label: "Labs", href: "/labs", icon: FlaskConical },
];

function NavLink({ item, pathname }: { item: NavItem; pathname: string }) {
  const isActive =
    item.href === "/"
      ? pathname === "/"
      : pathname.startsWith(item.href);
  const Icon = item.icon;

  return (
    <Link
      href={item.href}
      className={cn(
        "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
        isActive
          ? "bg-sidebar-accent text-sidebar-ring"
          : "text-sidebar-foreground/70 hover:bg-sidebar-accent/50 hover:text-sidebar-foreground"
      )}
    >
      <Icon className="h-4 w-4 shrink-0" />
      <span className="truncate">{item.label}</span>
    </Link>
  );
}

export function Sidebar({
  open,
  onClose,
}: {
  open: boolean;
  onClose: () => void;
}) {
  const pathname = usePathname();
  const [legacyExpanded, setLegacyExpanded] = useState(false);

  return (
    <>
      {/* Mobile overlay */}
      {open && (
        <div
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
          onClick={onClose}
        />
      )}

      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-50 flex w-sidebar min-w-sidebar flex-col bg-sidebar transition-transform duration-200 lg:translate-x-0 lg:z-30",
          open ? "translate-x-0" : "-translate-x-full"
        )}
      >
        {/* Brand header */}
        <div className="flex items-center justify-between border-b border-sidebar-accent px-4 py-5">
          <div className="flex items-center gap-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
              <Briefcase className="h-4 w-4" />
            </div>
            <div>
              <h2 className="text-sm font-bold text-sidebar-foreground">
                CourtOps
              </h2>
              <p className="text-[11px] text-sidebar-foreground/50">
                Analyst Agent
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="rounded-md p-1 text-sidebar-foreground/50 hover:text-sidebar-foreground lg:hidden"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Workspace badge */}
        <div className="px-4 pt-4 pb-2">
          <div className="rounded-md bg-sidebar-accent/60 px-3 py-2">
            <p className="text-[11px] font-medium uppercase tracking-wider text-sidebar-foreground/40">
              Workspace
            </p>
            <p className="mt-0.5 text-sm font-medium text-sidebar-foreground">
              Municipal Court Demo
            </p>
          </div>
        </div>

        {/* Navigation */}
        <nav className="sidebar-scroll flex-1 overflow-y-auto px-3 py-2">
          <div className="space-y-1">
            {primaryNav.map((item) => (
              <NavLink key={item.href} item={item} pathname={pathname} />
            ))}
          </div>

          {/* Legacy section */}
          <div className="mt-6 border-t border-sidebar-accent pt-4">
            <button
              onClick={() => setLegacyExpanded(!legacyExpanded)}
              className="mb-1 flex w-full items-center gap-2 rounded-md px-3 py-1.5 text-xs font-semibold uppercase tracking-wider text-sidebar-foreground/40 hover:text-sidebar-foreground/60"
            >
              <FolderArchive className="h-3.5 w-3.5" />
              <span>Legacy Demo</span>
              {legacyExpanded ? (
                <ChevronDown className="ml-auto h-3.5 w-3.5" />
              ) : (
                <ChevronRight className="ml-auto h-3.5 w-3.5" />
              )}
            </button>
            {legacyExpanded && (
              <div className="space-y-0.5">
                {legacyNav.map((item) => (
                  <NavLink key={item.href} item={item} pathname={pathname} />
                ))}
              </div>
            )}
          </div>
        </nav>

        {/* User section */}
        <div className="border-t border-sidebar-accent px-4 py-3">
          <div className="flex items-center gap-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/20 text-xs font-bold text-primary">
              DA
            </div>
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-medium text-sidebar-foreground">
                Demo Admin
              </p>
              <p className="truncate text-xs text-sidebar-foreground/50">
                admin@courtops.dev
              </p>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
}

"use client";

import { Menu, Bell, Search } from "lucide-react";
import { usePathname } from "next/navigation";

const pageTitles: Record<string, { title: string; description: string }> = {
  "/": { title: "Dashboard", description: "Overview of your court operations" },
  "/uploads": { title: "Uploads", description: "Import and manage data files" },
  "/data-mapping": {
    title: "Data Mapping",
    description: "Map source columns to target schema",
  },
  "/operations": {
    title: "Operations",
    description: "Run and monitor operational workflows",
  },
  "/reports": {
    title: "Reports",
    description: "Generated reports and analytics",
  },
  "/training": {
    title: "Training Twin",
    description: "Interactive learning and scenario training",
  },
  "/settings": {
    title: "Settings",
    description: "Workspace configuration and user management",
  },
};

export function Header({ onMenuClick }: { onMenuClick: () => void }) {
  const pathname = usePathname();

  const pageInfo = pageTitles[pathname] ?? {
    title: pathname
      .split("/")
      .pop()
      ?.replace(/-/g, " ")
      .replace(/\b\w/g, (c) => c.toUpperCase()) ?? "Page",
    description: "",
  };

  return (
    <header className="sticky top-0 z-20 flex items-center gap-4 border-b bg-card px-4 py-3 lg:px-6">
      <button
        onClick={onMenuClick}
        className="rounded-md p-1.5 text-muted-foreground hover:bg-muted hover:text-foreground lg:hidden"
      >
        <Menu className="h-5 w-5" />
        <span className="sr-only">Toggle navigation menu</span>
      </button>

      <div className="min-w-0 flex-1">
        <h1 className="text-lg font-semibold text-foreground">
          {pageInfo.title}
        </h1>
        {pageInfo.description && (
          <p className="text-sm text-muted-foreground">
            {pageInfo.description}
          </p>
        )}
      </div>

      <div className="flex items-center gap-2">
        <button className="rounded-md p-2 text-muted-foreground hover:bg-muted hover:text-foreground">
          <Search className="h-4 w-4" />
          <span className="sr-only">Search</span>
        </button>
        <button className="relative rounded-md p-2 text-muted-foreground hover:bg-muted hover:text-foreground">
          <Bell className="h-4 w-4" />
          <span className="sr-only">Notifications</span>
          <span className="absolute right-1.5 top-1.5 h-2 w-2 rounded-full bg-danger" />
        </button>
      </div>
    </header>
  );
}

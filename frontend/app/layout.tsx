import "./globals.css";
import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "CourtOps Analyst Agent",
  description: "Municipal Court Functional Analyst portfolio application",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-slate-50 text-slate-900">
        <div className="mx-auto flex min-h-screen max-w-6xl flex-col">
          <header className="border-b bg-white">
            <div className="flex items-center justify-between px-6 py-4">
              <div>
                <h1 className="text-xl font-semibold text-slate-900">
                  CourtOps Analyst Agent
                </h1>
                <p className="text-sm text-slate-600">
                  Municipal Court Operations &amp; Functional Analysis Demo
                </p>
              </div>
              <nav className="flex items-center gap-4 text-sm font-medium text-slate-700">
                <Link href="/" className="hover:text-primary">
                  Dashboard
                </Link>
                <Link href="/cases" className="hover:text-primary">
                  Cases
                </Link>
                <Link href="/tickets" className="hover:text-primary">
                  Tickets
                </Link>
                <Link href="/inventory" className="hover:text-primary">
                  Inventory
                </Link>
                <Link href="/patches" className="hover:text-primary">
                  Patches
                </Link>
                <Link href="/reports" className="hover:text-primary">
                  Reports
                </Link>
                <Link href="/change-requests" className="hover:text-primary">
                  Change Requests
                </Link>
                <Link href="/admin" className="hover:text-primary">
                  Admin
                </Link>
                <Link href="/mapping" className="hover:text-primary">
                  Job Mapping
                </Link>
                <Link href="/agent" className="hover:text-primary">
                  Agent Console
                </Link>
                <Link
                  href="/login"
                  className="rounded-md border border-slate-200 px-2 py-1 text-xs hover:border-primary hover:text-primary"
                >
                  Demo Login
                </Link>
              </nav>
            </div>
          </header>
          <main className="flex-1 px-6 py-6">{children}</main>
          <footer className="border-t bg-white px-6 py-4 text-xs text-slate-500">
            CourtOps Analyst Agent &mdash; Demonstration system only. No real
            court data.
          </footer>
        </div>
      </body>
    </html>
  );
}



"use client";

import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";

interface Ticket {
  id: number;
  title: string;
  description: string;
  category: string;
  priority: string;
  status: string;
  created_at: string;
  due_at?: string | null;
}

export default function TicketsPage() {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [creating, setCreating] = useState(false);
  const [newTitle, setNewTitle] = useState("");
  const [newDescription, setNewDescription] = useState("");
  const [newCategory, setNewCategory] = useState("application");
  const [newPriority, setNewPriority] = useState("medium");

  useEffect(() => {
    apiFetch<Ticket[]>("/tickets")
      .then(setTickets)
      .catch(() => {
        setError(
          "Could not load tickets. Ensure backend is running and you are logged in."
        );
      });
  }, []);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setCreating(true);
    try {
      const created = await apiFetch<Ticket>("/tickets", {
        method: "POST",
        body: JSON.stringify({
          title: newTitle,
          description: newDescription,
          category: newCategory,
          priority: newPriority,
        }),
      });
      setTickets((prev) => [created, ...prev]);
      setNewTitle("");
      setNewDescription("");
    } catch {
      setError(
        "Could not create ticket. Ensure backend is running and you are logged in."
      );
    } finally {
      setCreating(false);
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
        <div>
          <h2 className="text-lg font-semibold text-slate-900">
            Help Desk Tickets
          </h2>
          <p className="text-sm text-slate-600">
            Track application, hardware, and access issues with SLA monitoring
            and escalation.
          </p>
        </div>
        <form
          onSubmit={handleCreate}
          className="mt-2 flex max-w-md flex-col gap-2 rounded-md border bg-white p-3 text-xs"
        >
          <div className="font-semibold text-slate-800">New Ticket</div>
          <div className="flex flex-col gap-1">
            <input
              className="rounded-md border px-2 py-1"
              placeholder="Short title"
              value={newTitle}
              onChange={(e) => setNewTitle(e.target.value)}
              required
            />
            <textarea
              className="rounded-md border px-2 py-1"
              placeholder="Describe the issue"
              value={newDescription}
              onChange={(e) => setNewDescription(e.target.value)}
              rows={2}
            />
            <div className="flex gap-2">
              <select
                className="flex-1 rounded-md border px-2 py-1"
                value={newCategory}
                onChange={(e) => setNewCategory(e.target.value)}
              >
                <option value="application">Application</option>
                <option value="hardware">Hardware</option>
                <option value="access">Access</option>
              </select>
              <select
                className="flex-1 rounded-md border px-2 py-1"
                value={newPriority}
                onChange={(e) => setNewPriority(e.target.value)}
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="critical">Critical</option>
              </select>
            </div>
          </div>
          <button
            type="submit"
            disabled={creating}
            className="self-end rounded-md bg-primary px-3 py-1 text-xs font-medium text-white hover:bg-blue-700 disabled:opacity-60"
          >
            {creating ? "Creating..." : "Create"}
          </button>
        </form>
      </div>
      <div className="rounded-md border bg-white">
        <div className="border-b px-4 py-2 text-xs font-medium uppercase text-slate-500">
          Recent tickets
        </div>
        {error && (
          <div className="px-4 py-2 text-xs text-red-600">{error}</div>
        )}
        <div className="divide-y text-sm">
          {tickets.map((t) => (
            <div
              key={t.id}
              className="flex items-center justify-between px-4 py-3"
            >
              <div>
                <div className="font-medium text-slate-800">{t.title}</div>
                <div className="mt-1 text-xs text-slate-500">
                  Category: {t.category} • Priority: {t.priority} • Status:{" "}
                  {t.status}
                </div>
              </div>
              <div className="text-right text-xs text-slate-500">
                Created: {new Date(t.created_at).toLocaleString()}
                {t.due_at && (
                  <div>SLA due: {new Date(t.due_at).toLocaleString()}</div>
                )}
              </div>
            </div>
          ))}
          {tickets.length === 0 && !error && (
            <div className="px-4 py-3 text-xs text-slate-500">
              No tickets found. Use the API to create demo tickets or run the
              seed script.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}



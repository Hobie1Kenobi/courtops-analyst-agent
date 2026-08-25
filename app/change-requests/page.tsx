"use client";

import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";

interface ChangeRequest {
  id: number;
  title: string;
  requested_by: string;
  current_process: string;
  proposed_change: string;
  impact_users: string;
  impact_data: string;
  impact_security: string;
  status: string;
  created_at: string;
}

export default function ChangeRequestsPage() {
  const [items, setItems] = useState<ChangeRequest[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [generatingId, setGeneratingId] = useState<number | null>(null);

  useEffect(() => {
    apiFetch<ChangeRequest[]>("/change-requests")
      .then(setItems)
      .catch(() =>
        setError(
          "Could not load change requests. Ensure backend is running and you are logged in."
        )
      );
  }, []);

  async function handleGenerateDocs(id: number) {
    setGeneratingId(id);
    try {
      await apiFetch(`/change-requests/${id}/generate-docs`, {
        method: "POST",
      });
      alert(
        "Documentation generated under docs/generated/ on the backend. You can view the files in the repo."
      );
    } catch {
      setError(
        "Could not generate documentation. Ensure backend is running and you are logged in."
      );
    } finally {
      setGeneratingId(null);
    }
  }

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-lg font-semibold text-slate-900">
          Change Requests &amp; Requirements
        </h2>
        <p className="text-sm text-slate-600">
          Intake, analyze, and track requirements changes, along with
          auto-generated documentation.
        </p>
      </div>
      <section className="rounded-md border bg-white p-4">
        <h3 className="text-sm font-semibold text-slate-800">
          Existing Requests
        </h3>
        {error && <p className="mt-2 text-xs text-red-600">{error}</p>}
        {!error && (
          <ul className="mt-2 space-y-2 text-xs">
            {items.map((cr) => (
              <li
                key={cr.id}
                className="rounded-md border px-3 py-2 hover:bg-slate-50"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-semibold text-slate-800">
                      {cr.title}
                    </div>
                    <div className="text-slate-500">
                      Requested by {cr.requested_by} • Status: {cr.status}
                    </div>
                  </div>
                  <button
                    onClick={() => handleGenerateDocs(cr.id)}
                    disabled={generatingId === cr.id}
                    className="rounded-md bg-primary px-3 py-1 text-xs font-medium text-white hover:bg-blue-700 disabled:opacity-60"
                  >
                    {generatingId === cr.id ? "Generating..." : "Generate Docs"}
                  </button>
                </div>
              </li>
            ))}
            {items.length === 0 && !error && (
              <li className="text-slate-500">
                No change requests found. Seed data includes a few examples, or
                create new ones via the API.
              </li>
            )}
          </ul>
        )}
      </section>
    </div>
  );
}


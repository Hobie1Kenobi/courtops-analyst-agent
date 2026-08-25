"use client";

import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";

interface Patch {
  id: number;
  title: string;
  type: string;
  status: string;
  requested_date: string;
  scheduled_date?: string | null;
  deployed_date?: string | null;
  verified_date?: string | null;
}

export default function PatchesPage() {
  const [patches, setPatches] = useState<Patch[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiFetch<Patch[]>("/patches")
      .then(setPatches)
      .catch(() =>
        setError(
          "Could not load patches. Ensure backend is running and you are logged in."
        )
      );
  }, []);

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-lg font-semibold text-slate-900">
          Patches &amp; Upgrades
        </h2>
        <p className="text-sm text-slate-600">
          Manage application and device patches through the full lifecycle from
          request to verification.
        </p>
      </div>
      <section className="rounded-md border bg-white p-4">
        <h3 className="text-sm font-semibold text-slate-800">Recent Patches</h3>
        {error && <p className="mt-2 text-xs text-red-600">{error}</p>}
        {!error && (
          <table className="mt-3 w-full table-auto border-collapse text-xs">
            <thead>
              <tr className="border-b bg-slate-50">
                <th className="px-2 py-1 text-left font-semibold">Title</th>
                <th className="px-2 py-1 text-left font-semibold">Type</th>
                <th className="px-2 py-1 text-left font-semibold">Status</th>
                <th className="px-2 py-1 text-left font-semibold">
                  Requested
                </th>
                <th className="px-2 py-1 text-left font-semibold">
                  Scheduled
                </th>
                <th className="px-2 py-1 text-left font-semibold">Deployed</th>
                <th className="px-2 py-1 text-left font-semibold">
                  Verified
                </th>
              </tr>
            </thead>
            <tbody>
              {patches.map((p) => (
                <tr key={p.id} className="border-b last:border-0">
                  <td className="px-2 py-1">{p.title}</td>
                  <td className="px-2 py-1">{p.type}</td>
                  <td className="px-2 py-1">{p.status}</td>
                  <td className="px-2 py-1">
                    {new Date(p.requested_date).toLocaleDateString()}
                  </td>
                  <td className="px-2 py-1">
                    {p.scheduled_date
                      ? new Date(p.scheduled_date).toLocaleDateString()
                      : "-"}
                  </td>
                  <td className="px-2 py-1">
                    {p.deployed_date
                      ? new Date(p.deployed_date).toLocaleDateString()
                      : "-"}
                  </td>
                  <td className="px-2 py-1">
                    {p.verified_date
                      ? new Date(p.verified_date).toLocaleDateString()
                      : "-"}
                  </td>
                </tr>
              ))}
              {patches.length === 0 && !error && (
                <tr>
                  <td
                    colSpan={7}
                    className="px-2 py-2 text-center text-slate-500"
                  >
                    No patches found. Run the seed script to populate sample
                    patches.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        )}
      </section>
    </div>
  );
}



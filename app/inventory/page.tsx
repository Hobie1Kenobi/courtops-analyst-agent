"use client";

import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";

interface Device {
  id: number;
  asset_tag: string;
  type: string;
  location: string;
  assigned_user?: string | null;
  warranty_end?: string | null;
  last_patch_date?: string | null;
  status: string;
}

export default function InventoryPage() {
  const [devices, setDevices] = useState<Device[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiFetch<Device[]>("/inventory")
      .then(setDevices)
      .catch(() =>
        setError(
          "Could not load inventory. Ensure backend is running and you are logged in."
        )
      );
  }, []);

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-lg font-semibold text-slate-900">
          Hardware Inventory
        </h2>
        <p className="text-sm text-slate-600">
          Track devices, asset tags, locations, assigned users, warranties, and
          patch compliance.
        </p>
      </div>
      <section className="rounded-md border bg-white p-4">
        <h3 className="text-sm font-semibold text-slate-800">
          Inventory Snapshot
        </h3>
        {error && <p className="mt-2 text-xs text-red-600">{error}</p>}
        {!error && (
          <table className="mt-3 w-full table-auto border-collapse text-xs">
            <thead>
              <tr className="border-b bg-slate-50">
                <th className="px-2 py-1 text-left font-semibold">Asset Tag</th>
                <th className="px-2 py-1 text-left font-semibold">Type</th>
                <th className="px-2 py-1 text-left font-semibold">Location</th>
                <th className="px-2 py-1 text-left font-semibold">Assigned</th>
                <th className="px-2 py-1 text-left font-semibold">
                  Warranty End
                </th>
                <th className="px-2 py-1 text-left font-semibold">
                  Last Patch
                </th>
                <th className="px-2 py-1 text-left font-semibold">Status</th>
              </tr>
            </thead>
            <tbody>
              {devices.map((d) => (
                <tr key={d.id} className="border-b last:border-0">
                  <td className="px-2 py-1">{d.asset_tag}</td>
                  <td className="px-2 py-1">{d.type}</td>
                  <td className="px-2 py-1">{d.location}</td>
                  <td className="px-2 py-1">{d.assigned_user || "-"}</td>
                  <td className="px-2 py-1">
                    {d.warranty_end
                      ? new Date(d.warranty_end).toLocaleDateString()
                      : "-"}
                  </td>
                  <td className="px-2 py-1">
                    {d.last_patch_date
                      ? new Date(d.last_patch_date).toLocaleDateString()
                      : "-"}
                  </td>
                  <td className="px-2 py-1">{d.status}</td>
                </tr>
              ))}
              {devices.length === 0 && !error && (
                <tr>
                  <td
                    colSpan={7}
                    className="px-2 py-2 text-center text-slate-500"
                  >
                    No devices found. Run the seed script to populate sample
                    inventory.
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



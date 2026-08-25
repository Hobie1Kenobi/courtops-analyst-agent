export default function AdminPage() {
  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-lg font-semibold text-slate-900">Admin &amp; Security</h2>
        <p className="text-sm text-slate-600">
          Manage users, roles, and review key audit information for court operations.
        </p>
      </div>
      <section className="rounded-md border bg-white p-4">
        <h3 className="text-sm font-semibold text-slate-800">Roles &amp; Access</h3>
        <p className="mt-2 text-xs text-slate-600">
          Clerk, Analyst, IT Support, Supervisor, and Read-only roles are enforced via RBAC in the API.
          This screen will surface users, their roles, and recent audit events for transparency.
        </p>
      </section>
    </div>
  );
}


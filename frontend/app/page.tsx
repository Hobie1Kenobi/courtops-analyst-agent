export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <h2 className="text-lg font-semibold text-slate-900">Dashboard</h2>
      <p className="text-sm text-slate-600">
        High-level view of municipal court operations, help desk workload, inventory risk, and patch posture.
      </p>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <section className="rounded-md border bg-white p-4">
          <h3 className="text-sm font-semibold text-slate-800">
            Case Backlog &amp; Disposition
          </h3>
          <p className="mt-2 text-xs text-slate-600">
            Summary metrics on open vs disposed cases, average case age, and time-to-disposition.
          </p>
        </section>
        <section className="rounded-md border bg-white p-4">
          <h3 className="text-sm font-semibold text-slate-800">
            Help Desk &amp; SLA
          </h3>
          <p className="mt-2 text-xs text-slate-600">
            Ticket volume, SLA performance, and items currently escalated to supervisors.
          </p>
        </section>
        <section className="rounded-md border bg-white p-4">
          <h3 className="text-sm font-semibold text-slate-800">
            Inventory Compliance
          </h3>
          <p className="mt-2 text-xs text-slate-600">
            Devices with expiring warranties, missing patches, or out-of-compliance status.
          </p>
        </section>
        <section className="rounded-md border bg-white p-4">
          <h3 className="text-sm font-semibold text-slate-800">
            Patch &amp; Change Calendar
          </h3>
          <p className="mt-2 text-xs text-slate-600">
            Upcoming application and device patches, including verification reminders.
          </p>
        </section>
        <section className="rounded-md border bg-white p-4">
          <h3 className="text-sm font-semibold text-slate-800">
            Audit &amp; Security
          </h3>
          <p className="mt-2 text-xs text-slate-600">
            Snapshot of failed logins, off-hours exports, and bulk changes flagged for review.
          </p>
        </section>
        <section className="rounded-md border bg-white p-4">
          <h3 className="text-sm font-semibold text-slate-800">
            Change Requests
          </h3>
          <p className="mt-2 text-xs text-slate-600">
            Active requirements and change requests, with current review and approval status.
          </p>
        </section>
      </div>
    </div>
  );
}


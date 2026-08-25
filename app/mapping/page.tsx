export default function MappingPage() {
  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-lg font-semibold text-slate-900">
          Job Responsibilities Mapping
        </h2>
        <p className="text-sm text-slate-600">
          High-level view of how Municipal Court Functional Analyst responsibilities are supported by
          features in this system.
        </p>
      </div>
      <section className="rounded-md border bg-white p-4">
        <h3 className="text-sm font-semibold text-slate-800">
          Requirements Traceability Matrix
        </h3>
        <p className="mt-2 text-xs text-slate-600">
          The full matrix lives in `docs/requirements-traceability-matrix.md`. This page summarizes key
          duties and links them to modules such as Tickets, Cases, Inventory, Patches, Reports, and Change
          Requests, providing a narrative bridge for portfolio reviews.
        </p>
      </section>
    </div>
  );
}


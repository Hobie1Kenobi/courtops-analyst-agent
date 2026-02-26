"use client";

import { useState } from "react";
import {
  ArrowRight,
  CheckCircle2,
  AlertTriangle,
  Info,
  ChevronDown,
  FileSpreadsheet,
  Database,
  Eye,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "../../components/ui/card";
import { Badge } from "../../components/ui/badge";
import { Button } from "../../components/ui/button";

/* ------------------------------------------------------------------ */
/*  Mock mapping scenario: CSV -> cases table                          */
/* ------------------------------------------------------------------ */

interface SourceColumn {
  name: string;
  sampleValues: string[];
  type: string;
}

interface TargetField {
  name: string;
  label: string;
  required: boolean;
  dataType: string;
}

const sourceColumns: SourceColumn[] = [
  { name: "case_number", sampleValues: ["CR-2026-0451", "CR-2026-0452"], type: "string" },
  { name: "defendant_name", sampleValues: ["John Doe", "Jane Smith"], type: "string" },
  { name: "filing_date", sampleValues: ["2026-01-15", "2026-01-16"], type: "date" },
  { name: "charge_code", sampleValues: ["DUI-001", "SPD-042"], type: "string" },
  { name: "court_room", sampleValues: ["Room A", "Room B"], type: "string" },
  { name: "status", sampleValues: ["Open", "Pending"], type: "string" },
  { name: "fine_amount", sampleValues: ["250.00", "150.00"], type: "number" },
  { name: "assigned_judge", sampleValues: ["Hon. Martinez", "Hon. Lee"], type: "string" },
];

const targetFields: TargetField[] = [
  { name: "case_id", label: "Case ID", required: true, dataType: "string" },
  { name: "defendant", label: "Defendant Name", required: true, dataType: "string" },
  { name: "filed_date", label: "Filing Date", required: true, dataType: "date" },
  { name: "charge", label: "Charge Code", required: true, dataType: "string" },
  { name: "courtroom", label: "Courtroom", required: false, dataType: "string" },
  { name: "case_status", label: "Case Status", required: true, dataType: "string" },
  { name: "fine", label: "Fine Amount", required: false, dataType: "number" },
  { name: "judge", label: "Assigned Judge", required: false, dataType: "string" },
];

// Default auto-detected mappings
const defaultMappings: Record<string, string> = {
  case_id: "case_number",
  defendant: "defendant_name",
  filed_date: "filing_date",
  charge: "charge_code",
  courtroom: "court_room",
  case_status: "status",
  fine: "fine_amount",
  judge: "assigned_judge",
};

const previewRows = [
  ["CR-2026-0451", "John Doe", "2026-01-15", "DUI-001", "Room A", "Open", "$250.00", "Hon. Martinez"],
  ["CR-2026-0452", "Jane Smith", "2026-01-16", "SPD-042", "Room B", "Pending", "$150.00", "Hon. Lee"],
  ["CR-2026-0453", "Robert Chen", "2026-01-17", "TRF-018", "Room A", "Open", "$75.00", "Hon. Martinez"],
  ["CR-2026-0454", "Maria Garcia", "2026-01-18", "DUI-003", "Room C", "Disposed", "$500.00", "Hon. Park"],
  ["CR-2026-0455", "David Kim", "2026-01-19", "SPD-027", "Room B", "Open", "$200.00", "Hon. Lee"],
];

/* ------------------------------------------------------------------ */

export default function DataMappingPage() {
  const [mappings, setMappings] = useState<Record<string, string>>(defaultMappings);
  const [showPreview, setShowPreview] = useState(false);

  const mappedCount = Object.values(mappings).filter(Boolean).length;
  const requiredMapped = targetFields
    .filter((f) => f.required)
    .every((f) => mappings[f.name]);
  const totalRequired = targetFields.filter((f) => f.required).length;

  return (
    <div className="space-y-6">
      {/* Source file info bar */}
      <Card>
        <CardContent className="flex flex-wrap items-center gap-4 px-4 py-3">
          <div className="flex items-center gap-2">
            <FileSpreadsheet className="h-4 w-4 text-primary" />
            <span className="text-sm font-medium text-foreground">
              cases_export_feb2026.csv
            </span>
          </div>
          <Badge variant="muted">1,204 rows</Badge>
          <Badge variant="muted">8 columns</Badge>
          <div className="flex-1" />
          <Badge variant={requiredMapped ? "success" : "warning"}>
            {mappedCount}/{targetFields.length} mapped
          </Badge>
        </CardContent>
      </Card>

      {/* Mapping area */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Source Columns */}
        <Card>
          <CardHeader className="flex flex-row items-center gap-2">
            <FileSpreadsheet className="h-4 w-4 text-muted-foreground" />
            <CardTitle>Source Columns</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 p-4">
            {sourceColumns.map((col) => {
              const isMapped = Object.values(mappings).includes(col.name);
              return (
                <div
                  key={col.name}
                  className={`flex items-center justify-between rounded-md border px-3 py-2 transition-colors ${
                    isMapped
                      ? "border-success/30 bg-success/5"
                      : "border-border bg-card"
                  }`}
                >
                  <div>
                    <p className="text-sm font-medium text-foreground">
                      {col.name}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {col.sampleValues.join(", ")}
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant="muted">{col.type}</Badge>
                    {isMapped && (
                      <CheckCircle2 className="h-4 w-4 text-success" />
                    )}
                  </div>
                </div>
              );
            })}
          </CardContent>
        </Card>

        {/* Target Schema */}
        <Card>
          <CardHeader className="flex flex-row items-center gap-2">
            <Database className="h-4 w-4 text-muted-foreground" />
            <CardTitle>Target Schema: Cases</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 p-4">
            {targetFields.map((field) => {
              const currentMapping = mappings[field.name] || "";

              return (
                <div
                  key={field.name}
                  className="flex items-center gap-3 rounded-md border px-3 py-2"
                >
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                      <p className="text-sm font-medium text-foreground">
                        {field.label}
                      </p>
                      {field.required && (
                        <Badge variant="danger">Required</Badge>
                      )}
                    </div>
                    <p className="text-xs text-muted-foreground">
                      {field.name} ({field.dataType})
                    </p>
                  </div>

                  <ArrowRight className="h-4 w-4 shrink-0 text-muted-foreground" />

                  <div className="relative">
                    <select
                      value={currentMapping}
                      onChange={(e) =>
                        setMappings((prev) => ({
                          ...prev,
                          [field.name]: e.target.value,
                        }))
                      }
                      className="h-8 w-44 appearance-none rounded-md border bg-card px-3 pr-8 text-xs font-medium text-foreground focus:border-primary focus:outline-none focus:ring-1 focus:ring-ring"
                    >
                      <option value="">-- Select --</option>
                      {sourceColumns.map((sc) => (
                        <option key={sc.name} value={sc.name}>
                          {sc.name}
                        </option>
                      ))}
                    </select>
                    <ChevronDown className="pointer-events-none absolute right-2 top-1/2 h-3 w-3 -translate-y-1/2 text-muted-foreground" />
                  </div>
                </div>
              );
            })}
          </CardContent>
        </Card>
      </div>

      {/* Validation + Preview */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Validation Summary */}
        <Card>
          <CardHeader>
            <CardTitle>Validation Summary</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">Total Rows</span>
              <span className="font-semibold text-foreground">1,204</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">Valid Rows</span>
              <span className="font-semibold text-success">1,198</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">Warnings</span>
              <span className="font-semibold text-warning">4</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">Errors</span>
              <span className="font-semibold text-danger">2</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">Required Fields</span>
              <Badge variant={requiredMapped ? "success" : "warning"}>
                {requiredMapped
                  ? `${totalRequired}/${totalRequired} mapped`
                  : `Incomplete`}
              </Badge>
            </div>
          </CardContent>
        </Card>

        {/* Actions */}
        <Card className="lg:col-span-2">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>Preview & Import</CardTitle>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowPreview(!showPreview)}
            >
              <Eye className="mr-1 h-3 w-3" />
              {showPreview ? "Hide Preview" : "Show Preview"}
            </Button>
          </CardHeader>
          <CardContent>
            {showPreview ? (
              <div className="overflow-x-auto rounded-md border">
                <table className="w-full text-xs">
                  <thead>
                    <tr className="border-b bg-muted/40 text-left font-medium uppercase tracking-wider text-muted-foreground">
                      {targetFields.map((f) => (
                        <th key={f.name} className="px-3 py-2">
                          {f.label}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y">
                    {previewRows.map((row, i) => (
                      <tr key={i} className="hover:bg-muted/20">
                        {row.map((cell, j) => (
                          <td
                            key={j}
                            className="px-3 py-2 text-foreground whitespace-nowrap"
                          >
                            {cell}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="flex flex-col items-center gap-3 py-6 text-center">
                <Info className="h-6 w-6 text-muted-foreground" />
                <p className="text-sm text-muted-foreground">
                  Click &quot;Show Preview&quot; to see mapped data before importing
                </p>
              </div>
            )}

            <div className="mt-4 flex items-center justify-end gap-3">
              <Button variant="outline" size="md">
                Reset Mappings
              </Button>
              <Button
                variant="primary"
                size="md"
                disabled={!requiredMapped}
              >
                Import 1,204 Rows
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

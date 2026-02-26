"use client";

import {
  FileSpreadsheet,
  FileJson,
  FileArchive,
  FileText,
  CheckCircle2,
  Loader2,
  AlertTriangle,
  Clock,
  MoreHorizontal,
  ArrowRight,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "../../components/ui/card";
import { Badge } from "../../components/ui/badge";
import { Button } from "../../components/ui/button";
import { FileUpload } from "../../components/ui/file-upload";
import Link from "next/link";

/* ------------------------------------------------------------------ */
/*  Static mock data                                                   */
/* ------------------------------------------------------------------ */

type FileStatus = "imported" | "processing" | "pending" | "error";

const statusConfig: Record<
  FileStatus,
  { variant: "success" | "info" | "muted" | "danger"; icon: React.ElementType }
> = {
  imported: { variant: "success", icon: CheckCircle2 },
  processing: { variant: "info", icon: Loader2 },
  pending: { variant: "muted", icon: Clock },
  error: { variant: "danger", icon: AlertTriangle },
};

const fileIcon: Record<string, React.ElementType> = {
  csv: FileSpreadsheet,
  xlsx: FileSpreadsheet,
  json: FileJson,
  zip: FileArchive,
  pdf: FileText,
  docx: FileText,
  txt: FileText,
};

interface MockFile {
  id: number;
  name: string;
  type: string;
  size: string;
  status: FileStatus;
  rows: number | null;
  errors: number;
  uploadedAt: string;
  project: string;
}

const mockFiles: MockFile[] = [
  {
    id: 1,
    name: "cases_export_feb2026.csv",
    type: "csv",
    size: "2.4 MB",
    status: "imported",
    rows: 1204,
    errors: 0,
    uploadedAt: "Feb 26, 2026 09:14 AM",
    project: "FY2026 Operations",
  },
  {
    id: 2,
    name: "tickets_q1_2026.xlsx",
    type: "xlsx",
    size: "890 KB",
    status: "imported",
    rows: 547,
    errors: 3,
    uploadedAt: "Feb 25, 2026 03:22 PM",
    project: "FY2026 Operations",
  },
  {
    id: 3,
    name: "inventory_snapshot.json",
    type: "json",
    size: "156 KB",
    status: "processing",
    rows: null,
    errors: 0,
    uploadedAt: "Feb 26, 2026 10:01 AM",
    project: "FY2026 Operations",
  },
  {
    id: 4,
    name: "revenue_data_jan.csv",
    type: "csv",
    size: "1.1 MB",
    status: "pending",
    rows: null,
    errors: 0,
    uploadedAt: "Feb 26, 2026 10:15 AM",
    project: "FY2026 Operations",
  },
  {
    id: 5,
    name: "patch_history_backup.zip",
    type: "zip",
    size: "4.7 MB",
    status: "error",
    rows: null,
    errors: 1,
    uploadedAt: "Feb 24, 2026 11:30 AM",
    project: "FY2026 Operations",
  },
  {
    id: 6,
    name: "sla_policy_v3.pdf",
    type: "pdf",
    size: "320 KB",
    status: "imported",
    rows: null,
    errors: 0,
    uploadedAt: "Feb 23, 2026 02:05 PM",
    project: "FY2026 Operations",
  },
];

/* ------------------------------------------------------------------ */

export default function UploadsPage() {
  return (
    <div className="space-y-6">
      {/* Upload zone */}
      <FileUpload />

      {/* File listing */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Uploaded Files</CardTitle>
          <Badge variant="muted">{mockFiles.length} files</Badge>
        </CardHeader>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b bg-muted/40 text-left text-xs font-medium uppercase tracking-wider text-muted-foreground">
                  <th className="px-4 py-2.5">File</th>
                  <th className="px-4 py-2.5">Size</th>
                  <th className="px-4 py-2.5">Status</th>
                  <th className="px-4 py-2.5 hidden sm:table-cell">Rows</th>
                  <th className="px-4 py-2.5 hidden md:table-cell">Uploaded</th>
                  <th className="px-4 py-2.5 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {mockFiles.map((file) => {
                  const Icon = fileIcon[file.type] || FileText;
                  const statusCfg = statusConfig[file.status];
                  const StatusIcon = statusCfg.icon;

                  return (
                    <tr
                      key={file.id}
                      className="transition-colors hover:bg-muted/30"
                    >
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-3">
                          <Icon className="h-4 w-4 shrink-0 text-muted-foreground" />
                          <div className="min-w-0">
                            <p className="truncate font-medium text-foreground">
                              {file.name}
                            </p>
                            <p className="text-xs text-muted-foreground">
                              {file.project}
                            </p>
                          </div>
                        </div>
                      </td>
                      <td className="px-4 py-3 text-muted-foreground">
                        {file.size}
                      </td>
                      <td className="px-4 py-3">
                        <Badge variant={statusCfg.variant}>
                          <StatusIcon className="mr-1 h-3 w-3" />
                          {file.status.charAt(0).toUpperCase() +
                            file.status.slice(1)}
                        </Badge>
                      </td>
                      <td className="px-4 py-3 text-muted-foreground hidden sm:table-cell">
                        {file.rows !== null
                          ? file.rows.toLocaleString()
                          : "--"}
                        {file.errors > 0 && (
                          <span className="ml-1 text-danger">
                            ({file.errors} err)
                          </span>
                        )}
                      </td>
                      <td className="px-4 py-3 text-muted-foreground hidden md:table-cell">
                        {file.uploadedAt}
                      </td>
                      <td className="px-4 py-3 text-right">
                        <div className="flex items-center justify-end gap-1">
                          {file.status === "imported" && (
                            <Link href="/data-mapping">
                              <Button variant="ghost" size="sm">
                                Map
                                <ArrowRight className="ml-1 h-3 w-3" />
                              </Button>
                            </Link>
                          )}
                          <Button variant="ghost" size="icon">
                            <MoreHorizontal className="h-4 w-4" />
                            <span className="sr-only">More actions</span>
                          </Button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

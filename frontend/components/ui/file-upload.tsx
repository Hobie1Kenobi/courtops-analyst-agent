"use client";

import { useState, useCallback } from "react";
import { Upload, FileUp } from "lucide-react";
import { cn } from "../utils/cn";
import { Badge } from "./badge";

interface FileUploadProps {
  accept?: string[];
  onFilesSelected?: (files: File[]) => void;
  className?: string;
}

export function FileUpload({
  accept = [".csv", ".xlsx", ".json", ".zip", ".pdf", ".docx", ".txt"],
  onFilesSelected,
  className,
}: FileUploadProps) {
  const [isDragging, setIsDragging] = useState(false);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);
      const files = Array.from(e.dataTransfer.files);
      onFilesSelected?.(files);
    },
    [onFilesSelected]
  );

  const handleInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const files = e.target.files ? Array.from(e.target.files) : [];
      onFilesSelected?.(files);
    },
    [onFilesSelected]
  );

  return (
    <div
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      className={cn(
        "relative flex flex-col items-center justify-center rounded-lg border-2 border-dashed bg-card px-6 py-10 text-center transition-colors",
        isDragging
          ? "border-primary bg-primary/5"
          : "border-border hover:border-primary/50",
        className
      )}
    >
      <div className="mb-3 rounded-full bg-primary/10 p-3">
        {isDragging ? (
          <FileUp className="h-6 w-6 text-primary" />
        ) : (
          <Upload className="h-6 w-6 text-primary" />
        )}
      </div>

      <p className="text-sm font-medium text-foreground">
        {isDragging ? "Drop files here" : "Drag and drop files here"}
      </p>
      <p className="mt-1 text-xs text-muted-foreground">
        or click to browse from your computer
      </p>

      <div className="mt-3 flex flex-wrap justify-center gap-1.5">
        {accept.map((type) => (
          <Badge key={type} variant="muted">
            {type.replace(".", "").toUpperCase()}
          </Badge>
        ))}
      </div>

      <input
        type="file"
        multiple
        accept={accept.join(",")}
        onChange={handleInputChange}
        className="absolute inset-0 cursor-pointer opacity-0"
        aria-label="Upload files"
      />
    </div>
  );
}

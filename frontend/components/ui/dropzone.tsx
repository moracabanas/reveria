"use client";

import React, { useCallback, useState } from "react";
import { cn } from "@/lib/utils";

interface DropzoneProps {
  onFileSelect: (file: File) => void;
  accept?: string;
  disabled?: boolean;
  children?: React.ReactNode;
}

export function Dropzone({ onFileSelect, accept = ".csv", disabled, children }: DropzoneProps) {
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
      const file = e.dataTransfer.files[0];
      if (file && file.name.endsWith(".csv")) {
        onFileSelect(file);
      }
    },
    [onFileSelect]
  );

  const handleFileInput = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) onFileSelect(file);
    },
    [onFileSelect]
  );

  return (
    <div
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      className={cn(
        "border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors",
        isDragging ? "border-primary bg-primary/5" : "border-muted-foreground/25",
        disabled && "opacity-50 cursor-not-allowed"
      )}
    >
      <input
        type="file"
        accept={accept}
        onChange={handleFileInput}
        disabled={disabled}
        className="hidden"
        id="file-upload"
      />
      <label htmlFor="file-upload" className="cursor-pointer block">
        {children || (
          <>
            <p className="text-lg font-medium">Drop your CSV file here</p>
            <p className="text-sm text-muted-foreground mt-1">or click to browse</p>
          </>
        )}
      </label>
    </div>
  );
}

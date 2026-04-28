"use client";

import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Dropzone } from "@/components/ui/dropzone";
import { uploadFile } from "@/lib/api";
import { PredictionConfig, JobResponse } from "@/lib/types";

interface UploadProps {
  onUploadComplete?: (job: JobResponse, data: number[]) => void;
  config?: PredictionConfig;
}

export function UploadComponent({ onUploadComplete, config }: UploadProps) {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);

  const handleFileSelect = (selectedFile: File) => {
    if (!selectedFile.name.endsWith(".csv")) {
      setError("Please upload a CSV file");
      return;
    }
    setFile(selectedFile);
    setError(null);
  };

  const parseCSVFile = async (file: File): Promise<number[]> => {
    const text = await file.text();
    const lines = text.split("\n").filter((line) => line.trim());
    const values: number[] = [];

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      const parts = line.split(",");
      const firstValue = parts[1] || parts[0]; // Skip index column if present
      const num = parseFloat(firstValue);
      if (!isNaN(num)) {
        values.push(num);
      }
    }

    return values;
  };

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    setProgress(30);

    try {
      const result = await uploadFile(file, config);
      setProgress(100);
      const parsedData = await parseCSVFile(file);
      onUploadComplete?.(result, parsedData);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setUploading(false);
    }
  };

  return (
    <Card className="w-full max-w-2xl">
      <CardHeader>
        <CardTitle>Upload Time Series Data</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <Dropzone onFileSelect={handleFileSelect} disabled={uploading}>
          {file ? (
            <div>
              <p className="font-medium">{file.name}</p>
              <p className="text-sm text-muted-foreground">
                {(file.size / 1024).toFixed(1)} KB
              </p>
            </div>
          ) : (
            <>
              <p className="text-lg font-medium">Drop your CSV file here</p>
              <p className="text-sm text-muted-foreground mt-1">or click to browse</p>
            </>
          )}
        </Dropzone>

        {uploading && <Progress value={progress} className="w-full" />}

        {error && (
          <div className="text-sm text-destructive bg-destructive/10 p-3 rounded">
            {error}
          </div>
        )}

        <Button
          onClick={handleUpload}
          disabled={!file || uploading}
          className="w-full"
        >
          {uploading ? "Uploading..." : "Upload and Predict"}
        </Button>
      </CardContent>
    </Card>
  );
}

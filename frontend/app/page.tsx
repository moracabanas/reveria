"use client";

import { useState, useCallback } from "react";
import { UploadComponent } from "@/components/upload";
import { Chart } from "@/components/chart";
import { useJobPolling } from "@/hooks/useJobPolling";
import { JobResponse } from "@/lib/types";

export default function Home() {
  const [jobId, setJobId] = useState<string | null>(null);
  const [originalData, setOriginalData] = useState<number[]>([]);

  const { data, status, error, isPolling } = useJobPolling(jobId, originalData);

  const handleUploadComplete = useCallback((job: JobResponse, parsedData: number[]) => {
    setJobId(job.job_id);
    setOriginalData(parsedData);
  }, []);

  return (
    <main className="min-h-screen p-8">
      <div className="max-w-6xl mx-auto space-y-8">
        <h1 className="text-3xl font-bold">Reverso Signal Dashboard</h1>
        <UploadComponent onUploadComplete={handleUploadComplete} />
        <Chart
          data={data}
          isLoading={isPolling && status !== "completed"}
          error={error}
        />
      </div>
    </main>
  );
}

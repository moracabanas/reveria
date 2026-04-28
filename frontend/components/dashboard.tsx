"use client";

import React, { useState, useCallback, useRef } from "react";
import { UploadComponent } from "@/components/upload";
import { Chart } from "@/components/chart";
import { MetricsPanel } from "@/components/metrics";
import { ExportButtons } from "@/components/export";
import { ConfigPanel } from "@/components/config-panel";
import { useJobPolling } from "@/hooks/useJobPolling";
import { JobResponse, PredictionConfig } from "@/lib/types";

export function Dashboard() {
  const [jobId, setJobId] = useState<string | null>(null);
  const [originalData, setOriginalData] = useState<number[]>([]);
  const [config, setConfig] = useState<PredictionConfig>({
    context_size: 512,
    prediction_length: 96,
    frequency: "auto",
  });
  const chartContainerRef = useRef<HTMLDivElement>(null);

  const { data, status, error, isPolling } = useJobPolling(jobId, originalData);

  const handleUploadComplete = useCallback(
    (job: JobResponse, parsedData: number[]) => {
      setJobId(job.job_id);
      setOriginalData(parsedData);
    },
    []
  );

  const handleConfigChange = useCallback((newConfig: PredictionConfig) => {
    setConfig(newConfig);
  }, []);

  return (
    <div className="space-y-6">
      {/* Top section: Upload + Config side by side */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <UploadComponent
            onUploadComplete={handleUploadComplete}
            config={config}
          />
        </div>
        <div>
          <ConfigPanel config={config} onConfigChange={handleConfigChange} />
        </div>
      </div>

      {/* Metrics */}
      <MetricsPanel data={data} />

      {/* Chart + Export side by side */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="lg:col-span-3">
          <div ref={chartContainerRef}>
            <Chart
              data={data}
              isLoading={isPolling && status !== "completed"}
              error={error}
            />
          </div>
        </div>
        <div>
          <ExportButtons data={data} chartRef={chartContainerRef} />
        </div>
      </div>
    </div>
  );
}

"use client";

import React, { useState, useCallback, useRef, useMemo } from "react";
import { UploadComponent } from "@/components/upload";
import { Chart } from "@/components/chart";
import { MetricsPanel } from "@/components/metrics";
import { ExportButtons } from "@/components/export";
import { ConfigPanel } from "@/components/config-panel";
import { useJobPolling } from "@/hooks/useJobPolling";
import { buildChartDataWithWindow } from "@/lib/chart-data";
import { ChartData } from "@/lib/chart-types";
import { JobResponse, PredictionConfig } from "@/lib/types";

export function Dashboard() {
  const [jobId, setJobId] = useState<string | null>(null);
  const [originalData, setOriginalData] = useState<number[]>([]);
  const [config, setConfig] = useState<PredictionConfig>({
    context_size: 512,
    prediction_length: 96,
    frequency: "auto",
  });
  const [windowSize, setWindowSize] = useState<number | null>(null);
  const chartContainerRef = useRef<HTMLDivElement>(null);

  const { data: rawData, status, error, isPolling } = useJobPolling(jobId, originalData);

  const data = useMemo<ChartData | null>(() => {
    if (!rawData || !rawData.metadata || windowSize === null) return rawData;
    if (!rawData.metadata.original_length || rawData.metadata.original_length <= rawData.metadata.window_size) {
      return rawData;
    }
    const forecast = rawData.prediction.map((p) => p.value);
    return buildChartDataWithWindow(
      originalData,
      forecast,
      rawData.metadata,
      windowSize
    );
  }, [rawData, windowSize, originalData]);

  const handleUploadComplete = useCallback(
    (job: JobResponse, parsedData: number[]) => {
      setJobId(job.job_id);
      setOriginalData(parsedData);
      setWindowSize(null);
    },
    []
  );

  const handleConfigChange = useCallback((newConfig: PredictionConfig) => {
    setConfig(newConfig);
  }, []);

  const handleWindowSizeChange = useCallback((size: number) => {
    setWindowSize(size);
  }, []);

  return (
    <div className="space-y-6">
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

      <MetricsPanel data={data} />

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="lg:col-span-3">
          <div ref={chartContainerRef}>
            <Chart
              data={data}
              isLoading={isPolling && status !== "completed"}
              error={error}
              onWindowSizeChange={handleWindowSizeChange}
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

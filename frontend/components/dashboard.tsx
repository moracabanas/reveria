"use client";

import React, { useState, useCallback, useRef, useEffect } from "react";
import { UploadComponent } from "@/components/upload";
import { Chart } from "@/components/chart";
import { MetricsPanel } from "@/components/metrics";
import { ExportButtons } from "@/components/export";
import { ConfigPanel } from "@/components/config-panel";
import { SignalHistorySidebar } from "@/components/signal-history-sidebar";
import { useSignalHistory } from "@/contexts/signal-history-context";
import { useJobPolling } from "@/hooks/useJobPolling";
import { buildChartDataWithWindow } from "@/lib/chart-data";
import { ChartData } from "@/lib/chart-types";
import { JobResponse, PredictionConfig, HistoryEntry } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { History } from "lucide-react";

export function Dashboard() {
  const {
    state,
    activeChartData: contextChartData,
    activeOriginalData,
    addEntry,
    setActive,
    reapplyConfig,
  } = useSignalHistory();

  const [config, setConfig] = useState<PredictionConfig>({
    context_size: 512,
    prediction_length: 96,
    frequency: "auto",
  });
  const [windowSize, setWindowSize] = useState<number | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const chartContainerRef = useRef<HTMLDivElement>(null);

  const activeJobId = state.activeJobId;
  const { data: polledData, status, error, isPolling } = useJobPolling(
    activeJobId,
    activeOriginalData
  );

  const data: ChartData | null = React.useMemo(() => {
    const base = contextChartData || polledData;
    if (!base || !base.metadata || windowSize === null) return base;
    if (
      !base.metadata.original_length ||
      base.metadata.original_length <= base.metadata.window_size
    ) {
      return base;
    }
    const forecast = base.prediction.map((p) => p.value);
    return buildChartDataWithWindow(
      activeOriginalData,
      forecast,
      base.metadata,
      windowSize
    );
  }, [contextChartData, polledData, windowSize, activeOriginalData]);

  const handleUploadComplete = useCallback(
    (job: JobResponse, parsedData: number[], fileName?: string) => {
      const entry: HistoryEntry = {
        jobId: job.job_id,
        signalName: fileName || "Unnamed signal",
        uploadedAt: new Date().toISOString(),
        config: { ...config },
        status: "processing",
      };
      addEntry(entry);
      setActive(job.job_id);
      setWindowSize(null);
    },
    [addEntry, setActive, config]
  );

  const handleConfigChange = useCallback((newConfig: PredictionConfig) => {
    setConfig(newConfig);
  }, []);

  const handleReapply = useCallback(
    async (newConfig: PredictionConfig) => {
      if (activeJobId) {
        await reapplyConfig(activeJobId, newConfig);
        setConfig(newConfig);
      }
    },
    [activeJobId, reapplyConfig]
  );

  const handleWindowSizeChange = useCallback((size: number) => {
    setWindowSize(size);
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <Button
          variant="outline"
          onClick={() => setSidebarOpen(true)}
          className="gap-2"
        >
          <History className="h-4 w-4" />
          Signal History
          {state.entries.length > 0 && (
            <span className="ml-1 text-xs bg-primary text-primary-foreground rounded-full px-1.5 py-0.5">
              {state.entries.length}
            </span>
          )}
        </Button>
      </div>

      <SignalHistorySidebar
        open={sidebarOpen}
        onOpenChange={setSidebarOpen}
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <UploadComponent
            onUploadComplete={handleUploadComplete}
            config={config}
          />
        </div>
        <div>
          <ConfigPanel
            config={config}
            onConfigChange={handleConfigChange}
            onReapply={handleReapply}
            hasActiveSignal={!!activeJobId}
            isReapplying={state.isLoading}
          />
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

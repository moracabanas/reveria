"use client";

import React, { useEffect, useRef, useState, useCallback } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { renderChart, clearChart } from "@/lib/d3-chart";
import { ChartData, ViewMode } from "@/lib/chart-types";
import { Loader2 } from "lucide-react";

interface ChartProps {
  data: ChartData | null;
  isLoading?: boolean;
  error?: string | null;
  chartRef?: React.RefObject<HTMLDivElement | null>;
  onWindowSizeChange?: (size: number) => void;
}

export function Chart({ data, isLoading, error, chartRef: externalRef, onWindowSizeChange }: ChartProps) {
  const internalRef = useRef<HTMLDivElement>(null);
  const containerRef = externalRef || internalRef;
  const [viewMode, setViewMode] = useState<ViewMode>("both");
  const [dimensions, setDimensions] = useState({ width: 800, height: 400 });

  useEffect(() => {
    if (!containerRef.current) return;

    const observer = new ResizeObserver((entries) => {
      for (const entry of entries) {
        const { width } = entry.contentRect;
        setDimensions({ width, height: Math.max(300, width * 0.5) });
      }
    });

    observer.observe(containerRef.current);
    return () => observer.disconnect();
  }, [containerRef]);

  useEffect(() => {
    if (!containerRef.current || !data) return;

    const cleanup = renderChart(containerRef.current, data, {
      width: dimensions.width,
      height: dimensions.height,
      margin: { top: 20, right: 30, bottom: 40, left: 60 },
      viewMode,
    });

    return cleanup;
  }, [data, viewMode, dimensions, containerRef]);

  const handleViewModeChange = useCallback((mode: ViewMode) => {
    setViewMode(mode);
  }, []);

  if (isLoading) {
    return (
      <Card className="w-full">
        <CardContent className="flex items-center justify-center h-[400px]">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
          <p className="ml-2 text-muted-foreground">Running prediction...</p>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="w-full">
        <CardContent className="flex items-center justify-center h-[400px]">
          <p className="text-destructive">{error}</p>
        </CardContent>
      </Card>
    );
  }

  if (!data) {
    return (
      <Card className="w-full">
        <CardContent className="flex items-center justify-center h-[400px]">
          <p className="text-muted-foreground">Upload a CSV file to see the chart</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="w-full">
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>Time Series Forecast</CardTitle>
        <div className="flex items-center gap-4">
          {data?.metadata && data.metadata.original_length > data.metadata.window_size && (
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <span>Window:</span>
              <input
                type="range"
                min={Math.max(10, data.metadata.prediction_length * 2)}
                max={data.metadata.original_length}
                value={data.metadata.window_size}
                onChange={(e) => onWindowSizeChange?.(parseInt(e.target.value, 10))}
                className="w-24 h-1 bg-gray-200 rounded-lg appearance-none cursor-pointer"
              />
              <span>{data.metadata.window_size.toLocaleString()} pts</span>
            </div>
          )}
          <div className="flex gap-2">
            {(["both", "historical", "prediction"] as ViewMode[]).map((mode) => (
              <Button
                key={mode}
                variant={viewMode === mode ? "default" : "outline"}
                size="sm"
                onClick={() => handleViewModeChange(mode)}
              >
                {mode === "both" && "Both"}
                {mode === "historical" && "Historical"}
                {mode === "prediction" && "Prediction"}
              </Button>
            ))}
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div ref={containerRef} className="w-full" />
      </CardContent>
    </Card>
  );
}

"use client";

import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Clock, BarChart3, Activity, Layers } from "lucide-react";
import { ChartData } from "@/lib/chart-types";

interface MetricsPanelProps {
  data: ChartData | null;
}

export function MetricsPanel({ data }: MetricsPanelProps) {
  if (!data || !data.metadata) {
    return (
      <Card className="w-full">
        <CardContent className="flex items-center justify-center h-32">
          <p className="text-muted-foreground text-sm">
            Upload and predict to see metrics
          </p>
        </CardContent>
      </Card>
    );
  }

  const { metadata } = data;
  const actualValues = data.historical.map((d) => d.value);
  const predictedValues = data.prediction.map((d) => d.value);

  // Calculate MAE/MSE if we have overlapping data
  let mae: number | null = null;
  let mse: number | null = null;

  const overlapLength = Math.min(
    actualValues.length,
    predictedValues.length
  );
  if (overlapLength > 0) {
    const actualSlice = actualValues.slice(-overlapLength);
    const predSlice = predictedValues.slice(0, overlapLength);
    const errors = actualSlice.map((a, i) => a - predSlice[i]);
    mae = errors.reduce((sum, e) => sum + Math.abs(e), 0) / errors.length;
    mse = errors.reduce((sum, e) => sum + e * e, 0) / errors.length;
  }

  const metrics = [
    {
      label: "Computation Time",
      value: `${metadata.computation_time_ms} ms`,
      icon: Clock,
    },
    {
      label: "Window Size",
      value: `${metadata.window_size.toLocaleString()} pts`,
      icon: BarChart3,
    },
    {
      label: "Total Signal",
      value: `${metadata.original_length.toLocaleString()} pts`,
      icon: BarChart3,
    },
    {
      label: "Prediction Length",
      value: `${metadata.prediction_length} steps`,
      icon: Activity,
    },
    {
      label: "Context Size",
      value: `${metadata.context_size}`,
      icon: Layers,
    },
    ...(mae !== null
      ? [
          {
            label: "MAE",
            value: mae.toFixed(4),
            icon: Activity,
          },
          {
            label: "MSE",
            value: mse?.toFixed(4) || "0",
            icon: Activity,
          },
        ]
      : []),
  ];

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="text-lg">Metrics</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {metrics.map((metric) => (
            <div key={metric.label} className="space-y-1">
              <div className="flex items-center gap-2 text-muted-foreground">
                <metric.icon className="h-4 w-4" />
                <span className="text-xs">{metric.label}</span>
              </div>
              <p className="text-lg font-semibold">{metric.value}</p>
            </div>
          ))}
        </div>
        <div className="mt-4 pt-4 border-t text-xs text-muted-foreground">
          Model: {metadata.model_used} | Frequency: {metadata.frequency}
        </div>
      </CardContent>
    </Card>
  );
}

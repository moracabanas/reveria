"use client";

import React, { useState, useCallback } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { PredictionConfig } from "@/lib/types";

interface ConfigPanelProps {
  config: PredictionConfig;
  onConfigChange: (config: PredictionConfig) => void;
  onReapply?: (config: PredictionConfig) => void;
  hasActiveSignal?: boolean;
  isReapplying?: boolean;
}

const FREQUENCY_OPTIONS = ["auto", "H", "D", "W", "M", "Q", "Y"];

export function ConfigPanel({
  config,
  onConfigChange,
  onReapply,
  hasActiveSignal,
  isReapplying,
}: ConfigPanelProps) {
  const [localConfig, setLocalConfig] = useState<PredictionConfig>(config);

  const handleChange = useCallback(
    (field: keyof PredictionConfig, value: string | number) => {
      const updated = { ...localConfig, [field]: value };
      setLocalConfig(updated);
    },
    [localConfig]
  );

  const handleApply = useCallback(() => {
    if (hasActiveSignal && onReapply) {
      onReapply(localConfig);
    } else {
      onConfigChange(localConfig);
    }
  }, [localConfig, onConfigChange, onReapply, hasActiveSignal]);

  const handleReset = useCallback(() => {
    const defaults: PredictionConfig = {
      context_size: 512,
      prediction_length: 96,
      frequency: "auto",
    };
    setLocalConfig(defaults);
    onConfigChange(defaults);
  }, [onConfigChange]);

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="text-lg">Prediction Configuration</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="context-size">Context Size</Label>
            <Input
              id="context-size"
              type="number"
              min={32}
              value={localConfig.context_size || 512}
              onChange={(e) =>
                handleChange("context_size", parseInt(e.target.value, 10))
              }
            />
            <p className="text-xs text-muted-foreground">
              Historical steps to use (min: 32)
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="prediction-length">Prediction Length</Label>
            <Input
              id="prediction-length"
              type="number"
              min={1}
              value={localConfig.prediction_length || 96}
              onChange={(e) =>
                handleChange("prediction_length", parseInt(e.target.value, 10))
              }
            />
            <p className="text-xs text-muted-foreground">Steps to forecast (min: 1)</p>
          </div>
        </div>

        <div className="space-y-2">
          <Label htmlFor="frequency">Frequency</Label>
          <select
            id="frequency"
            value={localConfig.frequency || "auto"}
            onChange={(e) => handleChange("frequency", e.target.value)}
            className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors"
          >
            {FREQUENCY_OPTIONS.map((freq) => (
              <option key={freq} value={freq}>
                {freq === "auto" ? "Auto-detect" : freq}
              </option>
            ))}
          </select>
          <p className="text-xs text-muted-foreground">
            Time step frequency (H=hourly, D=daily, W=weekly, M=monthly)
          </p>
        </div>

        <div className="flex gap-2 pt-2">
          <Button
            onClick={handleApply}
            variant="default"
            className="flex-1"
            disabled={isReapplying}
          >
            {isReapplying
              ? "Running..."
              : hasActiveSignal
              ? "Apply Config"
              : "Apply"}
          </Button>
          <Button onClick={handleReset} variant="outline" className="flex-1">
            Reset
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

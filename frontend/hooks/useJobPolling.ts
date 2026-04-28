"use client";

import { useState, useEffect, useCallback } from "react";
import { getJobStatus, getJobResult } from "@/lib/api";
import { ChartData, DataPoint } from "@/lib/chart-types";

interface UseJobPollingReturn {
  data: ChartData | null;
  status: string;
  error: string | null;
  isPolling: boolean;
}

export function useJobPolling(jobId: string | null, originalData: number[]): UseJobPollingReturn {
  const [data, setData] = useState<ChartData | null>(null);
  const [status, setStatus] = useState<string>("");
  const [error, setError] = useState<string | null>(null);
  const [isPolling, setIsPolling] = useState(false);

  const poll = useCallback(async () => {
    if (!jobId) return;

    try {
      const statusRes = await getJobStatus(jobId);
      setStatus(statusRes.status);

      if (statusRes.status === "completed") {
        const result = await getJobResult(jobId);
        if (result.forecast && result.metadata) {
          // Build historical data from original CSV data
          const historical: DataPoint[] = originalData.map((value, i) => ({
            index: i,
            value,
          }));

          // Build prediction data
          const prediction: DataPoint[] = result.forecast.map((value, i) => ({
            index: result.metadata!.input_points + i,
            value,
          }));

          setData({
            historical,
            prediction,
            metadata: result.metadata,
          });
        }
        setIsPolling(false);
      } else if (statusRes.status === "failed") {
        setError("Prediction failed");
        setIsPolling(false);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Polling error");
    }
  }, [jobId, originalData]);

  useEffect(() => {
    if (!jobId) {
      setData(null);
      setStatus("");
      setError(null);
      setIsPolling(false);
      return;
    }

    setIsPolling(true);
    poll();

    const interval = setInterval(() => {
      if (status !== "completed" && status !== "failed") {
        poll();
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [jobId, status, poll]);

  return { data, status, error, isPolling };
}

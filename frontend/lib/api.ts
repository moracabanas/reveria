import { PredictionConfig, JobResponse, JobStatusResponse, JobResultResponse } from "@/lib/types";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

export async function uploadFile(
  file: File,
  config?: PredictionConfig
): Promise<JobResponse> {
  const formData = new FormData();
  formData.append("file", file);
  if (config?.context_size) formData.append("context_size", String(config.context_size));
  if (config?.prediction_length) formData.append("prediction_length", String(config.prediction_length));
  if (config?.frequency) formData.append("frequency", config.frequency);
  if (config?.column_index !== undefined) formData.append("column_index", String(config.column_index));
  if (config?.column_name) formData.append("column_name", config.column_name);

  const response = await fetch(`${BACKEND_URL}/predict/file`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Upload failed: ${error}`);
  }

  return response.json();
}

export async function getJobStatus(jobId: string): Promise<JobStatusResponse> {
  const response = await fetch(`${BACKEND_URL}/predict/status/${jobId}`);
  if (!response.ok) throw new Error("Failed to get job status");
  return response.json();
}

export async function getJobResult(jobId: string): Promise<JobResultResponse> {
  const response = await fetch(`${BACKEND_URL}/predict/result/${jobId}`);
  if (!response.ok) throw new Error("Failed to get job result");
  return response.json();
}

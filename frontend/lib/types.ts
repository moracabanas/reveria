export interface PredictionConfig {
  context_size?: number;
  prediction_length?: number;
  frequency?: string;
  column_index?: number;
  column_name?: string;
}

export interface JobResponse {
  job_id: string;
  status: string;
}

export interface JobStatusResponse {
  job_id: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface PredictionMetadata {
  computation_time_ms: number;
  model_used: string;
  input_points: number;
  prediction_length: number;
  context_size: number;
  frequency: string;
}

export interface JobResultResponse {
  job_id: string;
  status: string;
  forecast: number[] | null;
  metadata: PredictionMetadata | null;
}

export type JobStatus = "pending" | "processing" | "completed" | "failed";

export interface JobSummaryResponse {
  job_id: string;
  status: string;
  created_at: string;
  updated_at: string;
  signal_name: string | null;
  config: PredictionConfig | null;
}

export interface OriginalDataResponse {
  job_id: string;
  signal_name: string | null;
  data: number[];
}

export interface ReapplyRequest {
  context_size: number;
  prediction_length: number;
  frequency: string;
}

export interface HistoryEntry {
  jobId: string;
  signalName: string;
  uploadedAt: string;
  config: PredictionConfig;
  status: JobStatus;
}

export interface DataPoint {
  index: number;
  value: number;
}

export interface ChartData {
  historical: DataPoint[];
  prediction: DataPoint[];
  metadata: {
    computation_time_ms: number;
    model_used: string;
    input_points: number;
    prediction_length: number;
    context_size: number;
    frequency: string;
    original_length: number;
    window_size: number;
  } | null;
}

export type ViewMode = "both" | "historical" | "prediction";

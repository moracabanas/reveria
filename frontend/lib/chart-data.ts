import { ChartData, DataPoint } from "@/lib/chart-types";
import { PredictionMetadata } from "@/lib/types";

/**
 * Build ChartData from original CSV data, forecast, and metadata.
 *
 * Historical data is sliced to a context window:
 *   window_size = max(context_size, 10 × prediction_length)
 *
 * This ensures the user sees enough history for context while keeping
 * the visualization focused on the relevant region.
 */
export function buildChartData(
  originalData: number[],
  forecast: number[],
  metadata: PredictionMetadata
): ChartData {
  const inputPoints = metadata.input_points;
  const predictionLength = metadata.prediction_length;
  const contextSize = metadata.context_size;

  const defaultWindowSize = Math.max(contextSize, predictionLength * 10);
  const windowSize = Math.min(defaultWindowSize, originalData.length);
  const startIndex = originalData.length - windowSize;

  const historical: DataPoint[] = originalData
    .slice(startIndex)
    .map((value, i) => ({
      index: startIndex + i,
      value,
    }));

  const lastHistoricalIndex = historical[historical.length - 1]?.index ?? startIndex - 1;
  const prediction: DataPoint[] = forecast.map((value, i) => ({
    index: lastHistoricalIndex + 1 + i,
    value,
  }));

  return {
    historical,
    prediction,
    metadata: {
      ...metadata,
      original_length: originalData.length,
      window_size: windowSize,
    } as PredictionMetadata & { original_length: number; window_size: number },
  };
}

/**
 * Build ChartData with a custom historical window size.
 * Used by the slider control to let users adjust how much history they see.
 */
export function buildChartDataWithWindow(
  originalData: number[],
  forecast: number[],
  metadata: PredictionMetadata,
  windowSize: number
): ChartData {
  const clampedWindow = Math.min(Math.max(windowSize, 10), originalData.length);
  const startIndex = originalData.length - clampedWindow;

  const historical: DataPoint[] = originalData
    .slice(startIndex)
    .map((value, i) => ({
      index: startIndex + i,
      value,
    }));

  const lastHistoricalIndex = historical[historical.length - 1]?.index ?? startIndex - 1;
  const prediction: DataPoint[] = forecast.map((value, i) => ({
    index: lastHistoricalIndex + 1 + i,
    value,
  }));

  return {
    historical,
    prediction,
    metadata: {
      ...metadata,
      original_length: originalData.length,
      window_size: clampedWindow,
    } as PredictionMetadata & { original_length: number; window_size: number },
  };
}

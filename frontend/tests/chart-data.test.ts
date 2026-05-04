import { describe, it, expect } from "vitest";
import { buildChartData, buildChartDataWithWindow } from "@/lib/chart-data";

const baseMetadata = {
  computation_time_ms: 100,
  model_used: "test",
  input_points: 5,
  prediction_length: 3,
  context_size: 10,
  frequency: "1min",
};

describe("buildChartData", () => {
  it("slices historical data to window size when data exceeds window", () => {
    const originalData = Array.from({ length: 100 }, (_, i) => i + 1);
    const forecast = [101, 102, 103];
    const metadata = { ...baseMetadata, input_points: 50, context_size: 10, prediction_length: 3 };
    const result = buildChartData(originalData, forecast, metadata);

    const expectedWindow = Math.max(10, 3 * 10);
    expect(result.historical.length).toBe(expectedWindow);
    expect(result.historical[0]).toEqual({ index: 70, value: 71 });
    expect(result.historical[result.historical.length - 1]).toEqual({ index: 99, value: 100 });
  });

  it("uses 10× prediction_length as default window when greater than context_size", () => {
    const originalData = Array.from({ length: 200 }, (_, i) => i + 1);
    const forecast = [201, 202, 203];
    const metadata = { ...baseMetadata, context_size: 5, prediction_length: 10, input_points: 100 };
    const result = buildChartData(originalData, forecast, metadata);

    expect(result.historical.length).toBe(100);
    expect(result.metadata.window_size).toBe(100);
  });

  it("uses context_size as window when greater than 10× prediction_length", () => {
    const originalData = Array.from({ length: 200 }, (_, i) => i + 1);
    const forecast = [201, 202, 203];
    const metadata = { ...baseMetadata, context_size: 150, prediction_length: 5, input_points: 100 };
    const result = buildChartData(originalData, forecast, metadata);

    expect(result.historical.length).toBe(150);
    expect(result.metadata.window_size).toBe(150);
  });

  it("starts prediction indices at input_points", () => {
    const originalData = [1, 2, 3, 4, 5];
    const forecast = [6, 7, 8];
    const result = buildChartData(originalData, forecast, baseMetadata);

    expect(result.prediction).toEqual([
      { index: 5, value: 6 },
      { index: 6, value: 7 },
      { index: 7, value: 8 },
    ]);
  });

  it("uses contiguous indices for historical and prediction", () => {
    const originalData = Array.from({ length: 50 }, (_, i) => i + 1);
    const forecast = [51, 52, 53];
    const result = buildChartData(originalData, forecast, baseMetadata);

    const lastHistorical = result.historical[result.historical.length - 1];
    const firstPrediction = result.prediction[0];

    expect(lastHistorical.index).toBe(49);
    expect(firstPrediction.index).toBe(lastHistorical.index + 1);
  });

  it("handles input_points greater than data length", () => {
    const originalData = [1, 2, 3];
    const forecast = [4, 5, 6];
    const metadata = { ...baseMetadata, input_points: 10 };
    const result = buildChartData(originalData, forecast, metadata);

    expect(result.historical).toEqual([
      { index: 0, value: 1 },
      { index: 1, value: 2 },
      { index: 2, value: 3 },
    ]);
  });

  it("includes original_length and window_size in metadata", () => {
    const originalData = Array.from({ length: 100 }, (_, i) => i + 1);
    const forecast = [101, 102, 103];
    const metadata = { ...baseMetadata, input_points: 50, context_size: 10, prediction_length: 3 };
    const result = buildChartData(originalData, forecast, metadata);

    expect(result.metadata.original_length).toBe(100);
    expect(result.metadata.window_size).toBe(30);
  });
});

describe("buildChartDataWithWindow", () => {
  it("uses custom window size", () => {
    const originalData = Array.from({ length: 100 }, (_, i) => i + 1);
    const forecast = [101, 102, 103];
    const result = buildChartDataWithWindow(originalData, forecast, baseMetadata, 20);

    expect(result.historical.length).toBe(20);
    expect(result.metadata.window_size).toBe(20);
  });

  it("clamps window size to minimum of 10", () => {
    const originalData = Array.from({ length: 100 }, (_, i) => i + 1);
    const forecast = [101, 102, 103];
    const result = buildChartDataWithWindow(originalData, forecast, baseMetadata, 5);

    expect(result.historical.length).toBe(10);
  });

  it("clamps window size to data length", () => {
    const originalData = [1, 2, 3];
    const forecast = [4, 5, 6];
    const result = buildChartDataWithWindow(originalData, forecast, baseMetadata, 100);

    expect(result.historical.length).toBe(3);
  });
});

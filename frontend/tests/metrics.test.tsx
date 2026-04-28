import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MetricsPanel } from '@/components/metrics';

describe('MetricsPanel', () => {
  const mockData = {
    historical: [
      { index: 0, value: 1.0 },
      { index: 1, value: 1.5 },
      { index: 2, value: 2.0 },
    ],
    prediction: [
      { index: 3, value: 2.5 },
      { index: 4, value: 3.0 },
    ],
    metadata: {
      computation_time_ms: 1500,
      model_used: 'reverso',
      input_points: 50000,
      prediction_length: 100,
      context_size: 512,
      frequency: '1min',
    },
  };

  it('shows placeholder when no data', () => {
    render(<MetricsPanel data={null} />);
    expect(screen.getByText(/upload and predict to see metrics/i)).toBeInTheDocument();
  });

  it('shows placeholder when data has no metadata', () => {
    render(<MetricsPanel data={{ historical: [], prediction: [], metadata: null }} />);
    expect(screen.getByText(/upload and predict to see metrics/i)).toBeInTheDocument();
  });

  it('displays computation time', () => {
    render(<MetricsPanel data={mockData} />);
    expect(screen.getByText(/1500 ms/i)).toBeInTheDocument();
  });

  it('displays signal length', () => {
    render(<MetricsPanel data={mockData} />);
    expect(screen.getByText(/50,000/i)).toBeInTheDocument();
  });

  it('displays prediction length', () => {
    render(<MetricsPanel data={mockData} />);
    expect(screen.getByText(/100/i)).toBeInTheDocument();
  });

  it('displays context size', () => {
    render(<MetricsPanel data={mockData} />);
    expect(screen.getByText(/512/i)).toBeInTheDocument();
  });

  it('displays frequency', () => {
    render(<MetricsPanel data={mockData} />);
    expect(screen.getByText(/1min/i)).toBeInTheDocument();
  });

  it('displays model name in footer', () => {
    render(<MetricsPanel data={mockData} />);
    expect(screen.getByText(/reverso/i)).toBeInTheDocument();
  });

  it('calculates MAE when historical and prediction overlap', () => {
    // Create data where we can calculate MAE
    const dataWithOverlap = {
      historical: [
        { index: 0, value: 1.0 },
        { index: 1, value: 2.0 },
        { index: 2, value: 3.0 },
      ],
      prediction: [
        { index: 0, value: 1.1 }, // error = 0.1
        { index: 1, value: 2.1 }, // error = 0.1
      ],
      metadata: mockData.metadata,
    };

    render(<MetricsPanel data={dataWithOverlap} />);
    expect(screen.getByText(/MAE/i)).toBeInTheDocument();
  });

  it('calculates MSE when historical and prediction overlap', () => {
    const dataWithOverlap = {
      historical: [
        { index: 0, value: 1.0 },
        { index: 1, value: 2.0 },
        { index: 2, value: 3.0 },
      ],
      prediction: [
        { index: 0, value: 1.1 },
        { index: 1, value: 2.1 },
      ],
      metadata: mockData.metadata,
    };

    render(<MetricsPanel data={dataWithOverlap} />);
    expect(screen.getByText(/MSE/i)).toBeInTheDocument();
  });

  it('does not display MAE/MSE when no prediction data', () => {
    // Empty prediction array means no overlap possible
    render(<MetricsPanel data={{ ...mockData, prediction: [] }} />);
    expect(screen.queryByText(/MAE/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/MSE/i)).not.toBeInTheDocument();
  });
});

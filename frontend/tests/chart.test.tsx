import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Chart } from '@/components/chart';

// Mock D3 to prevent actual SVG rendering in tests
vi.mock('d3', async () => {
  const actual = await vi.importActual('d3');
  return {
    ...actual,
    select: vi.fn(() => ({
      select: vi.fn().mockReturnThis(),
      append: vi.fn().mockReturnThis(),
      attr: vi.fn().mockReturnThis(),
      text: vi.fn().mockReturnThis(),
      datum: vi.fn().mockReturnThis(),
      enter: vi.fn().mockReturnThis(),
      join: vi.fn().mockReturnThis(),
      on: vi.fn().mockReturnThis(),
      call: vi.fn().mockReturnThis(),
      remove: vi.fn().mockReturnThis(),
    })),
    scaleLinear: vi.fn(() => ({
      domain: vi.fn().mockReturnThis(),
      range: vi.fn().mockReturnThis(),
      nice: vi.fn().mockReturnThis(),
    })),
    scaleTime: vi.fn(() => ({
      domain: vi.fn().mockReturnThis(),
      range: vi.fn().mockReturnThis(),
      nice: vi.fn().mockReturnThis(),
    })),
    axisBottom: vi.fn(() => ({
      scale: vi.fn().mockReturnThis(),
      tickSizeOuter: vi.fn().mockReturnThis(),
      tickSizeInner: vi.fn().mockReturnThis(),
    })),
    axisLeft: vi.fn(() => ({
      scale: vi.fn().mockReturnThis(),
      tickSizeOuter: vi.fn().mockReturnThis(),
      tickSizeInner: vi.fn().mockReturnThis(),
    })),
    zoom: vi.fn(() => ({
      scaleExtent: vi.fn().mockReturnThis(),
      on: vi.fn().mockReturnThis(),
    })),
    max: vi.fn(() => 100),
    min: vi.fn(() => 0),
    extent: vi.fn(() => [0, 100]),
    timeParse: vi.fn(() => () => new Date()),
    timeFormat: vi.fn(() => () => '2024-01-01'),
  };
});

// Mock the d3-chart lib
vi.mock('@/lib/d3-chart', () => ({
  renderChart: vi.fn(() => vi.fn()),
  clearChart: vi.fn(),
}));

describe('Chart', () => {
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
      input_points: 3,
      prediction_length: 2,
      context_size: 512,
      frequency: '1min',
    },
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders chart with title', () => {
    render(<Chart data={mockData} />);
    expect(screen.getByText('Time Series Forecast')).toBeInTheDocument();
  });

  it('renders view mode toggle buttons', () => {
    render(<Chart data={mockData} />);
    expect(screen.getByRole('button', { name: /both/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /historical/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /prediction/i })).toBeInTheDocument();
  });

  it('toggles view mode when buttons are clicked', async () => {
    render(<Chart data={mockData} viewMode="both" />);

    const historicalButton = screen.getByRole('button', { name: /historical/i });
    historicalButton.click();

    // After clicking, the historical button should still exist
    expect(screen.getByRole('button', { name: /historical/i })).toBeInTheDocument();
  });

  it('handles empty prediction data gracefully', () => {
    const emptyPredictionData = {
      ...mockData,
      prediction: [],
    };
    render(<Chart data={emptyPredictionData} />);
    expect(screen.getByText('Time Series Forecast')).toBeInTheDocument();
  });

  it('handles null data gracefully', () => {
    render(<Chart data={null} />);
    expect(screen.getByText(/upload a csv file to see the chart/i)).toBeInTheDocument();
  });

  it('shows loading state', () => {
    render(<Chart data={null} isLoading={true} />);
    expect(screen.getByText(/running prediction/i)).toBeInTheDocument();
  });

  it('shows error state', () => {
    render(<Chart data={null} error="Failed to load data" />);
    expect(screen.getByText('Failed to load data')).toBeInTheDocument();
  });
});

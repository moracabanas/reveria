import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { ExportButtons } from '@/components/export';

// Mock export utilities
const mockDownloadCSV = vi.fn();
const mockDownloadChartAsPNG = vi.fn();
const mockDownloadChartAsSVG = vi.fn();

vi.mock('@/lib/export-utils', () => ({
  downloadCSV: (...args: unknown[]) => mockDownloadCSV(...args),
  downloadChartAsPNG: (...args: unknown[]) => mockDownloadChartAsPNG(...args),
  downloadChartAsSVG: (...args: unknown[]) => mockDownloadChartAsSVG(...args),
}));

describe('ExportButtons', () => {
  const mockData = {
    historical: [{ index: 0, value: 1.0 }],
    prediction: [{ index: 1, value: 2.0 }],
    metadata: {
      computation_time_ms: 1500,
      model_used: 'reverso',
      input_points: 100,
      prediction_length: 50,
      context_size: 512,
      frequency: '1min',
    },
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders CSV, PNG, and SVG export buttons', () => {
    render(<ExportButtons data={mockData} />);
    expect(screen.getByText(/download csv/i)).toBeInTheDocument();
    expect(screen.getByText(/download png/i)).toBeInTheDocument();
    expect(screen.getByText(/download svg/i)).toBeInTheDocument();
  });

  it('downloads CSV when button is clicked', () => {
    render(<ExportButtons data={mockData} />);
    fireEvent.click(screen.getByText(/download csv/i));
    expect(mockDownloadCSV).toHaveBeenCalledWith(mockData);
  });

  it('triggers PNG download when button is clicked', () => {
    const mockSVG = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    const mockChartRef = {
      current: {
        querySelector: vi.fn(() => mockSVG),
      },
    };

    render(<ExportButtons data={mockData} chartRef={mockChartRef as React.RefObject<HTMLDivElement>} />);
    fireEvent.click(screen.getByText(/download png/i));
    expect(mockDownloadChartAsPNG).toHaveBeenCalled();
  });

  it('triggers SVG download when button is clicked', () => {
    const mockSVG = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    const mockChartRef = {
      current: {
        querySelector: vi.fn(() => mockSVG),
      },
    };

    render(<ExportButtons data={mockData} chartRef={mockChartRef as React.RefObject<HTMLDivElement>} />);
    fireEvent.click(screen.getByText(/download svg/i));
    expect(mockDownloadChartAsSVG).toHaveBeenCalled();
  });

  it('disables all buttons when data is null', () => {
    render(<ExportButtons data={null} />);
    expect(screen.getByText(/download csv/i)).toBeDisabled();
    expect(screen.getByText(/download png/i)).toBeDisabled();
    expect(screen.getByText(/download svg/i)).toBeDisabled();
  });

  it('disables CSV button when data is null', () => {
    render(<ExportButtons data={null} />);
    expect(screen.getByText(/download csv/i)).toBeDisabled();
  });

  it('enables CSV button when data is present', () => {
    render(<ExportButtons data={mockData} />);
    expect(screen.getByText(/download csv/i)).not.toBeDisabled();
  });
});

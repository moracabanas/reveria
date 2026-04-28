import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { UploadComponent } from '@/components/upload';

// Mock the API module at the top level
vi.mock('@/lib/api', () => {
  return {
    uploadFile: vi.fn().mockName('uploadFile'),
  };
});

// Get reference to the mocked function
import { uploadFile } from '@/lib/api';

vi.mock('@/components/ui/dropzone', () => ({
  Dropzone: ({ children, onFileSelect, disabled }: { children: React.ReactNode; onFileSelect: (file: File) => void; disabled?: boolean }) => (
    <div data-testid="dropzone">
      <input
        type="file"
        accept=".csv"
        data-testid="file-input"
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file && file.name.endsWith('.csv')) {
            onFileSelect(file);
          }
        }}
        disabled={disabled}
      />
      {children}
    </div>
  ),
}));

describe('UploadComponent', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders upload card with title', () => {
    render(<UploadComponent />);
    expect(screen.getByText('Upload Time Series Data')).toBeInTheDocument();
  });

  it('shows dropzone with default text', () => {
    render(<UploadComponent />);
    expect(screen.getByText(/drop your csv file here/i)).toBeInTheDocument();
    expect(screen.getByText(/or click to browse/i)).toBeInTheDocument();
  });

  it('upload button is disabled when no file selected', () => {
    render(<UploadComponent />);
    const button = screen.getByRole('button', { name: /upload and predict/i });
    expect(button).toBeDisabled();
  });

  it('upload button is enabled after CSV file selection', async () => {
    render(<UploadComponent />);

    const input = screen.getByTestId('file-input');
    await userEvent.upload(input, new File(['value\n1\n2'], 'test.csv', { type: 'text/csv' }));

    const button = screen.getByRole('button', { name: /upload and predict/i });
    expect(button).not.toBeDisabled();
  });

  it('displays selected filename after upload', async () => {
    render(<UploadComponent />);

    const input = screen.getByTestId('file-input');
    await userEvent.upload(input, new File(['timestamp,value\n2024-01-01,1.0'], 'myfile.csv', { type: 'text/csv' }));

    expect(screen.getByText('myfile.csv')).toBeInTheDocument();
  });

  it('shows error message on upload failure', async () => {
    vi.mocked(uploadFile).mockRejectedValue(new Error('Upload failed'));

    render(<UploadComponent />);

    const input = screen.getByTestId('file-input');
    await userEvent.upload(input, new File(['timestamp,value\n2024-01-01,1.0'], 'test.csv', { type: 'text/csv' }));

    const button = screen.getByRole('button', { name: /upload and predict/i });
    await userEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText(/upload failed/i)).toBeInTheDocument();
    });
  });

  it('calls onUploadComplete after successful upload', async () => {
    const mockOnUploadComplete = vi.fn();
    vi.mocked(uploadFile).mockResolvedValue({ job_id: 'test-job-123', status: 'completed' });

    render(<UploadComponent onUploadComplete={mockOnUploadComplete} />);

    const input = screen.getByTestId('file-input');
    // Create file with proper content - the component calls file.text()
    const csvContent = 'timestamp,value\n2024-01-01,1.0\n2024-01-02,2.0';
    const testFile = new File([csvContent], 'test.csv', { type: 'text/csv' });

    // Mock the text() method since jsdom File doesn't have it
    const mockText = vi.fn().mockResolvedValue(csvContent);
    Object.defineProperty(testFile, 'text', { value: mockText, writable: true });

    await userEvent.upload(input, testFile);

    const button = screen.getByRole('button', { name: /upload and predict/i });
    await userEvent.click(button);

    await waitFor(() => {
      expect(mockOnUploadComplete).toHaveBeenCalled();
    }, { timeout: 3000 });
  });
});

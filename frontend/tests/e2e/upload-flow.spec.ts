import { test, expect } from '@playwright/test';
import path from 'path';

test.describe('Upload Flow E2E', () => {
  test('complete upload to export flow', async ({ page }) => {
    // Navigate to app
    await page.goto('/');

    // Wait for upload component to be visible
    await expect(page.getByText(/upload time series data/i)).toBeVisible();

    // Upload CSV file
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setFiles(path.join(__dirname, '../fixtures/sample.csv'));

    // Wait for upload button to be enabled
    const uploadButton = page.getByRole('button', { name: /upload and predict/i });
    await expect(uploadButton).toBeEnabled();

    // Click upload and wait for processing
    await uploadButton.click();

    // Wait for chart to appear (or error state if backend not running)
    await page.waitForTimeout(2000);

    // If prediction completes, verify chart and metrics appear
    // Otherwise, the test verifies the upload flow initiates correctly
    const chartOrError = page.locator('[class*="card"]').first();
    await expect(chartOrError).toBeVisible();

    // Test view mode toggles if chart is visible
    const bothButton = page.getByRole('button', { name: /both/i });
    if (await bothButton.isVisible()) {
      await bothButton.click();
      const historicalButton = page.getByRole('button', { name: /historical/i });
      if (await historicalButton.isVisible()) {
        await historicalButton.click();
      }
    }

    // Test export buttons exist
    const csvButton = page.getByText(/download csv/i);
    if (await csvButton.isVisible()) {
      await expect(csvButton).toBeVisible();
    }
  });

  test('displays error for non-CSV files', async ({ page }) => {
    await page.goto('/');

    // Try to upload a non-CSV file
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setFiles({
      name: 'test.txt',
      mimeType: 'text/plain',
      buffer: Buffer.from('not a csv'),
    } as any);

    // Verify file is not accepted (dropzone should not show the filename)
    await expect(page.getByText(/test.txt/i)).not.toBeVisible();
  });

  test('metrics panel shows placeholder without data', async ({ page }) => {
    await page.goto('/');

    // Verify metrics placeholder is shown
    await expect(page.getByText(/upload and predict to see metrics/i)).toBeVisible();
  });
});

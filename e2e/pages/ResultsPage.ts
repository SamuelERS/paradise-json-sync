/**
 * ResultsPage Page Object Model
 * Modelo de página para la página de resultados
 *
 * Encapsulates all interactions with results and downloads
 * Encapsula todas las interacciones con resultados y descargas
 */

import { Page, Locator, expect } from '@playwright/test';

export class ResultsPage {
  readonly page: Page;
  readonly progressBar: Locator;
  readonly progressText: Locator;
  readonly statusMessage: Locator;
  readonly downloadExcelButton: Locator;
  readonly downloadPdfButton: Locator;
  readonly downloadCsvButton: Locator;
  readonly errorList: Locator;
  readonly errorItems: Locator;
  readonly successMessage: Locator;
  readonly resultsContainer: Locator;

  // Selectors / Selectores
  private readonly selectors = {
    progressBar: '[data-testid="progress-bar"]',
    progressText: '[data-testid="progress-text"]',
    progressFill: '[data-testid="progress-fill"]',
    statusMessage: '[data-testid="status-message"]',
    downloadExcel: '[data-testid="download-excel"]',
    downloadPdf: '[data-testid="download-pdf"]',
    downloadCsv: '[data-testid="download-csv"]',
    errorList: '[data-testid="error-list"]',
    errorItem: '[data-testid="error-item"]',
    successMessage: '[data-testid="success-message"]',
    resultsContainer: '[data-testid="results-container"]',
  };

  constructor(page: Page) {
    this.page = page;
    this.progressBar = page.locator(this.selectors.progressBar);
    this.progressText = page.locator(this.selectors.progressText);
    this.statusMessage = page.locator(this.selectors.statusMessage);
    this.downloadExcelButton = page.locator(this.selectors.downloadExcel);
    this.downloadPdfButton = page.locator(this.selectors.downloadPdf);
    this.downloadCsvButton = page.locator(this.selectors.downloadCsv);
    this.errorList = page.locator(this.selectors.errorList);
    this.errorItems = page.locator(this.selectors.errorItem);
    this.successMessage = page.locator(this.selectors.successMessage);
    this.resultsContainer = page.locator(this.selectors.resultsContainer);
  }

  /**
   * Wait for processing to complete
   * Esperar a que el procesamiento se complete
   * @param timeout - Maximum wait time in ms / Tiempo máximo de espera en ms
   */
  async waitForCompletion(timeout: number = 60000): Promise<void> {
    // Wait for progress to reach 100% or success message
    // Esperar a que el progreso llegue a 100% o mensaje de éxito
    await expect(this.successMessage).toBeVisible({ timeout });
  }

  /**
   * Get current progress percentage
   * Obtener porcentaje de progreso actual
   */
  async getProgress(): Promise<number> {
    const text = await this.progressText.textContent();
    if (!text) return 0;

    // Extract number from text like "75%" or "75"
    // Extraer número de texto como "75%" o "75"
    const match = text.match(/(\d+)/);
    return match ? parseInt(match[1], 10) : 0;
  }

  /**
   * Get progress bar width percentage
   * Obtener porcentaje de ancho de la barra de progreso
   */
  async getProgressBarWidth(): Promise<number> {
    const fill = this.page.locator(this.selectors.progressFill);
    const style = await fill.getAttribute('style');
    if (!style) return 0;

    const match = style.match(/width:\s*(\d+)%/);
    return match ? parseInt(match[1], 10) : 0;
  }

  /**
   * Download Excel file
   * Descargar archivo Excel
   * @returns Promise with download info / Promesa con info de descarga
   */
  async downloadExcel(): Promise<{ filename: string; path: string }> {
    await expect(this.downloadExcelButton).toBeEnabled();

    // Start waiting for download before clicking
    // Empezar a esperar descarga antes de hacer clic
    const downloadPromise = this.page.waitForEvent('download');
    await this.downloadExcelButton.click();
    const download = await downloadPromise;

    const filename = download.suggestedFilename();
    const downloadPath = await download.path();

    return {
      filename,
      path: downloadPath || '',
    };
  }

  /**
   * Download PDF file
   * Descargar archivo PDF
   * @returns Promise with download info / Promesa con info de descarga
   */
  async downloadPdf(): Promise<{ filename: string; path: string }> {
    await expect(this.downloadPdfButton).toBeEnabled();

    const downloadPromise = this.page.waitForEvent('download');
    await this.downloadPdfButton.click();
    const download = await downloadPromise;

    const filename = download.suggestedFilename();
    const downloadPath = await download.path();

    return {
      filename,
      path: downloadPath || '',
    };
  }

  /**
   * Download CSV file
   * Descargar archivo CSV
   * @returns Promise with download info / Promesa con info de descarga
   */
  async downloadCsv(): Promise<{ filename: string; path: string }> {
    await expect(this.downloadCsvButton).toBeEnabled();

    const downloadPromise = this.page.waitForEvent('download');
    await this.downloadCsvButton.click();
    const download = await downloadPromise;

    const filename = download.suggestedFilename();
    const downloadPath = await download.path();

    return {
      filename,
      path: downloadPath || '',
    };
  }

  /**
   * Get count of errors
   * Obtener cantidad de errores
   */
  async getErrorCount(): Promise<number> {
    if (!(await this.errorList.isVisible())) return 0;
    return await this.errorItems.count();
  }

  /**
   * Get error messages
   * Obtener mensajes de error
   */
  async getErrors(): Promise<string[]> {
    if (!(await this.errorList.isVisible())) return [];

    const items = await this.errorItems.all();
    const errors: string[] = [];
    for (const item of items) {
      const text = await item.textContent();
      if (text) errors.push(text.trim());
    }
    return errors;
  }

  /**
   * Check if download buttons are enabled
   * Verificar si los botones de descarga están habilitados
   */
  async areDownloadsEnabled(): Promise<boolean> {
    const excelEnabled = await this.downloadExcelButton.isEnabled();
    const pdfEnabled = await this.downloadPdfButton.isEnabled();
    return excelEnabled && pdfEnabled;
  }

  /**
   * Get status message text
   * Obtener texto del mensaje de estado
   */
  async getStatusMessage(): Promise<string> {
    return (await this.statusMessage.textContent()) || '';
  }

  /**
   * Check if processing is in progress
   * Verificar si el procesamiento está en progreso
   */
  async isProcessing(): Promise<boolean> {
    const progress = await this.getProgress();
    return progress > 0 && progress < 100;
  }

  /**
   * Check if processing completed successfully
   * Verificar si el procesamiento se completó exitosamente
   */
  async isCompleted(): Promise<boolean> {
    return await this.successMessage.isVisible();
  }

  /**
   * Wait for progress to change
   * Esperar a que el progreso cambie
   */
  async waitForProgressChange(currentProgress: number): Promise<number> {
    let newProgress = currentProgress;
    let attempts = 0;
    const maxAttempts = 50;

    while (newProgress === currentProgress && attempts < maxAttempts) {
      await this.page.waitForTimeout(100);
      newProgress = await this.getProgress();
      attempts++;
    }

    return newProgress;
  }
}

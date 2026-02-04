/**
 * HomePage Page Object Model
 * Modelo de página para la página principal
 *
 * Encapsulates all interactions with the home page
 * Encapsula todas las interacciones con la página principal
 */

import { Page, Locator, expect } from '@playwright/test';

export class HomePage {
  readonly page: Page;
  readonly title: Locator;
  readonly dropzone: Locator;
  readonly fileList: Locator;
  readonly fileItems: Locator;
  readonly processButton: Locator;
  readonly uploadSection: Locator;

  // Selectors / Selectores
  private readonly selectors = {
    title: 'h1',
    dropzone: '[data-testid="dropzone"]',
    fileList: '[data-testid="file-list"]',
    fileItem: '[data-testid="file-item"]',
    processButton: '[data-testid="process-button"]',
    uploadSection: '[data-testid="upload-section"]',
  };

  constructor(page: Page) {
    this.page = page;
    this.title = page.locator(this.selectors.title);
    this.dropzone = page.locator(this.selectors.dropzone);
    this.fileList = page.locator(this.selectors.fileList);
    this.fileItems = page.locator(this.selectors.fileItem);
    this.processButton = page.locator(this.selectors.processButton);
    this.uploadSection = page.locator(this.selectors.uploadSection);
  }

  /**
   * Navigate to home page
   * Navegar a la página principal
   */
  async goto(): Promise<void> {
    await this.page.goto('/');
  }

  /**
   * Get page title text
   * Obtener el texto del título de la página
   */
  async getTitle(): Promise<string> {
    return await this.title.textContent() || '';
  }

  /**
   * Check if dropzone is visible
   * Verificar si la zona de arrastrar está visible
   */
  async isDropzoneVisible(): Promise<boolean> {
    return await this.dropzone.isVisible();
  }

  /**
   * Get count of uploaded files
   * Obtener cantidad de archivos subidos
   */
  async getFileCount(): Promise<number> {
    return await this.fileItems.count();
  }

  /**
   * Check if a specific file is in the list
   * Verificar si un archivo específico está en la lista
   */
  async hasFile(filename: string): Promise<boolean> {
    const fileItem = this.page.locator(
      `${this.selectors.fileItem}:has-text("${filename}")`
    );
    return await fileItem.isVisible();
  }

  /**
   * Check if process button is enabled
   * Verificar si el botón de procesar está habilitado
   */
  async isProcessButtonEnabled(): Promise<boolean> {
    return await this.processButton.isEnabled();
  }

  /**
   * Wait for page to be ready
   * Esperar a que la página esté lista
   */
  async waitForReady(): Promise<void> {
    await this.page.waitForLoadState('networkidle');
    await expect(this.uploadSection).toBeVisible();
  }

  /**
   * Get file list items
   * Obtener elementos de la lista de archivos
   */
  async getFileNames(): Promise<string[]> {
    const items = await this.fileItems.all();
    const names: string[] = [];
    for (const item of items) {
      const text = await item.textContent();
      if (text) names.push(text.trim());
    }
    return names;
  }
}

/**
 * UploadPage Page Object Model
 * Modelo de página para la funcionalidad de carga de archivos
 *
 * Encapsulates all upload-related interactions
 * Encapsula todas las interacciones relacionadas con la carga
 */

import { Page, Locator, expect } from '@playwright/test';
import path from 'path';

export class UploadPage {
  readonly page: Page;
  readonly dropzone: Locator;
  readonly fileInput: Locator;
  readonly fileList: Locator;
  readonly fileItems: Locator;
  readonly processButton: Locator;
  readonly errorMessage: Locator;
  readonly removeButtons: Locator;

  // Selectors / Selectores
  private readonly selectors = {
    dropzone: '[data-testid="dropzone"]',
    fileInput: 'input[type="file"]',
    fileList: '[data-testid="file-list"]',
    fileItem: '[data-testid="file-item"]',
    processButton: '[data-testid="process-button"]',
    errorMessage: '[data-testid="error-message"]',
    removeButton: '[data-testid="remove-file"]',
    fileName: '[data-testid="file-name"]',
  };

  constructor(page: Page) {
    this.page = page;
    this.dropzone = page.locator(this.selectors.dropzone);
    this.fileInput = page.locator(this.selectors.fileInput);
    this.fileList = page.locator(this.selectors.fileList);
    this.fileItems = page.locator(this.selectors.fileItem);
    this.processButton = page.locator(this.selectors.processButton);
    this.errorMessage = page.locator(this.selectors.errorMessage);
    this.removeButtons = page.locator(this.selectors.removeButton);
  }

  /**
   * Upload a single file
   * Subir un solo archivo
   * @param filePath - Path to the file / Ruta al archivo
   */
  async uploadFile(filePath: string): Promise<void> {
    // Playwright handles file input even if hidden
    // Playwright maneja input de archivos incluso si está oculto
    const absolutePath = path.isAbsolute(filePath)
      ? filePath
      : path.join(__dirname, '..', filePath);

    await this.fileInput.setInputFiles(absolutePath);

    // Wait for file to appear in list
    // Esperar a que el archivo aparezca en la lista
    const filename = path.basename(filePath);
    await expect(
      this.page.locator(`${this.selectors.fileItem}:has-text("${filename}")`)
    ).toBeVisible({ timeout: 5000 });
  }

  /**
   * Upload multiple files
   * Subir múltiples archivos
   * @param filePaths - Array of file paths / Array de rutas de archivos
   */
  async uploadMultipleFiles(filePaths: string[]): Promise<void> {
    const absolutePaths = filePaths.map((fp) =>
      path.isAbsolute(fp) ? fp : path.join(__dirname, '..', fp)
    );

    await this.fileInput.setInputFiles(absolutePaths);

    // Wait for all files to appear
    // Esperar a que todos los archivos aparezcan
    for (const fp of filePaths) {
      const filename = path.basename(fp);
      await expect(
        this.page.locator(`${this.selectors.fileItem}:has-text("${filename}")`)
      ).toBeVisible({ timeout: 5000 });
    }
  }

  /**
   * Get list of uploaded files
   * Obtener lista de archivos subidos
   */
  async getUploadedFiles(): Promise<string[]> {
    const items = await this.fileItems.all();
    const files: string[] = [];
    for (const item of items) {
      const nameElement = item.locator(this.selectors.fileName);
      const text = await nameElement.textContent();
      if (text) files.push(text.trim());
    }
    return files;
  }

  /**
   * Remove a file from the list by name
   * Eliminar un archivo de la lista por nombre
   * @param filename - Name of file to remove / Nombre del archivo a eliminar
   */
  async removeFile(filename: string): Promise<void> {
    const fileItem = this.page.locator(
      `${this.selectors.fileItem}:has-text("${filename}")`
    );
    const removeButton = fileItem.locator(this.selectors.removeButton);
    await removeButton.click();

    // Wait for file to be removed
    // Esperar a que el archivo sea eliminado
    await expect(fileItem).not.toBeVisible({ timeout: 5000 });
  }

  /**
   * Click process button to start processing
   * Click en botón de procesar para iniciar procesamiento
   */
  async clickProcess(): Promise<void> {
    await expect(this.processButton).toBeEnabled();
    await this.processButton.click();
  }

  /**
   * Check if error message is displayed
   * Verificar si se muestra mensaje de error
   */
  async hasError(): Promise<boolean> {
    return await this.errorMessage.isVisible();
  }

  /**
   * Get error message text
   * Obtener texto del mensaje de error
   */
  async getErrorMessage(): Promise<string> {
    if (await this.errorMessage.isVisible()) {
      return (await this.errorMessage.textContent()) || '';
    }
    return '';
  }

  /**
   * Clear all uploaded files
   * Limpiar todos los archivos subidos
   */
  async clearAllFiles(): Promise<void> {
    const buttons = await this.removeButtons.all();
    for (const button of buttons) {
      await button.click();
    }
    await expect(this.fileItems).toHaveCount(0);
  }

  /**
   * Get count of uploaded files
   * Obtener cantidad de archivos subidos
   */
  async getFileCount(): Promise<number> {
    return await this.fileItems.count();
  }

  /**
   * Check if dropzone accepts drag and drop
   * Verificar si la zona acepta arrastrar y soltar
   */
  async isDragDropEnabled(): Promise<boolean> {
    const dropzoneClasses = await this.dropzone.getAttribute('class');
    return !dropzoneClasses?.includes('disabled');
  }
}

/**
 * Download Tests / Tests de Descarga
 *
 * E2E tests for file download functionality
 * Tests E2E para la funcionalidad de descarga de archivos
 */

import { test, expect } from '@playwright/test';
import { HomePage, UploadPage, ResultsPage } from '../pages';
import { getTestDataPath, verifyDownloadedFile } from '../utils/helpers';
import path from 'path';

test.describe('File Download / Descarga de Archivos', () => {
  let homePage: HomePage;
  let uploadPage: UploadPage;
  let resultsPage: ResultsPage;

  test.beforeEach(async ({ page }) => {
    homePage = new HomePage(page);
    uploadPage = new UploadPage(page);
    resultsPage = new ResultsPage(page);

    // Navigate to home, upload file, and process
    // Navegar al inicio, subir archivo y procesar
    await homePage.goto();
    const jsonFilePath = getTestDataPath('sample-invoice.json');
    await uploadPage.uploadFile(jsonFilePath);
    await uploadPage.clickProcess();
    await resultsPage.waitForCompletion(60000);
  });

  test('Download Excel generates .xlsx file / Descargar Excel genera archivo .xlsx', async ({ page }) => {
    // Act: Download Excel file
    // Actuar: Descargar archivo Excel
    const { filename, path: downloadPath } = await resultsPage.downloadExcel();

    // Assert: File is generated with correct extension
    // Verificar: Archivo se genera con extensión correcta
    expect(filename).toMatch(/\.xlsx$/i);
    expect(downloadPath).toBeTruthy();

    // Verify file exists and has content
    // Verificar que el archivo existe y tiene contenido
    const isValid = await verifyDownloadedFile(downloadPath, '.xlsx');
    expect(isValid).toBe(true);
  });

  test('Download PDF generates .pdf file / Descargar PDF genera archivo .pdf', async ({ page }) => {
    // Act: Download PDF file
    // Actuar: Descargar archivo PDF
    const { filename, path: downloadPath } = await resultsPage.downloadPdf();

    // Assert: File is generated with correct extension
    // Verificar: Archivo se genera con extensión correcta
    expect(filename).toMatch(/\.pdf$/i);
    expect(downloadPath).toBeTruthy();

    // Verify file exists and has content
    // Verificar que el archivo existe y tiene contenido
    const isValid = await verifyDownloadedFile(downloadPath, '.pdf');
    expect(isValid).toBe(true);
  });

  test('Download CSV generates .csv file / Descargar CSV genera archivo .csv', async ({ page }) => {
    // Act: Download CSV file
    // Actuar: Descargar archivo CSV
    const { filename, path: downloadPath } = await resultsPage.downloadCsv();

    // Assert: File is generated with correct extension
    // Verificar: Archivo se genera con extensión correcta
    expect(filename).toMatch(/\.csv$/i);
    expect(downloadPath).toBeTruthy();

    // Verify file exists and has content
    // Verificar que el archivo existe y tiene contenido
    const isValid = await verifyDownloadedFile(downloadPath, '.csv');
    expect(isValid).toBe(true);
  });

  test('Download buttons enabled after completion / Botones descarga habilitados después de completar', async ({ page }) => {
    // Assert: Download buttons are enabled after processing
    // Verificar: Botones de descarga habilitados después de procesar
    const areEnabled = await resultsPage.areDownloadsEnabled();
    expect(areEnabled).toBe(true);
  });

  test('Multiple downloads possible / Múltiples descargas posibles', async ({ page }) => {
    // Act: Download both Excel and PDF
    // Actuar: Descargar tanto Excel como PDF
    const excelDownload = await resultsPage.downloadExcel();
    const pdfDownload = await resultsPage.downloadPdf();

    // Assert: Both files downloaded successfully
    // Verificar: Ambos archivos descargados exitosamente
    expect(excelDownload.filename).toMatch(/\.xlsx$/i);
    expect(pdfDownload.filename).toMatch(/\.pdf$/i);
  });

  test('Downloaded Excel has expected filename pattern / Excel descargado tiene patrón de nombre esperado', async ({ page }) => {
    // Act: Download Excel
    // Actuar: Descargar Excel
    const { filename } = await resultsPage.downloadExcel();

    // Assert: Filename follows expected pattern (e.g., includes date or identifier)
    // Verificar: Nombre de archivo sigue patrón esperado (ej: incluye fecha o identificador)
    expect(filename).toBeTruthy();
    expect(filename.length).toBeGreaterThan(5); // Has meaningful name

    // Common patterns: consolidated_YYYYMMDD.xlsx, export_123456.xlsx, etc.
    // Patrones comunes: consolidado_YYYYMMDD.xlsx, export_123456.xlsx, etc.
    const hasValidPattern = /\.(xlsx)$/i.test(filename);
    expect(hasValidPattern).toBe(true);
  });

  test('Downloaded PDF has expected filename pattern / PDF descargado tiene patrón de nombre esperado', async ({ page }) => {
    // Act: Download PDF
    // Actuar: Descargar PDF
    const { filename } = await resultsPage.downloadPdf();

    // Assert: Filename follows expected pattern
    // Verificar: Nombre de archivo sigue patrón esperado
    expect(filename).toBeTruthy();
    expect(filename.length).toBeGreaterThan(5);

    const hasValidPattern = /\.(pdf)$/i.test(filename);
    expect(hasValidPattern).toBe(true);
  });
});

test.describe('Download Buttons Disabled Before Completion / Botones Descarga Deshabilitados Antes de Completar', () => {
  let homePage: HomePage;
  let uploadPage: UploadPage;
  let resultsPage: ResultsPage;

  test.beforeEach(async ({ page }) => {
    homePage = new HomePage(page);
    uploadPage = new UploadPage(page);
    resultsPage = new ResultsPage(page);

    // Navigate to home and upload file
    // Navegar al inicio y subir archivo
    await homePage.goto();
    const jsonFilePath = getTestDataPath('sample-invoice.json');
    await uploadPage.uploadFile(jsonFilePath);
  });

  test('Download buttons disabled before processing starts / Botones descarga deshabilitados antes de iniciar procesamiento', async ({ page }) => {
    // Assert: Download buttons should not be accessible before processing
    // Verificar: Botones de descarga no deben ser accesibles antes de procesar

    // Download buttons may not exist or be disabled before processing
    // Los botones de descarga pueden no existir o estar deshabilitados antes de procesar
    const excelButtonExists = await resultsPage.downloadExcelButton.isVisible().catch(() => false);

    if (excelButtonExists) {
      const isEnabled = await resultsPage.downloadExcelButton.isEnabled().catch(() => false);
      expect(isEnabled).toBe(false);
    }
  });

  test('Download buttons disabled during processing / Botones descarga deshabilitados durante procesamiento', async ({ page }) => {
    // Act: Start processing but don't wait for completion
    // Actuar: Iniciar procesamiento pero no esperar a completar
    await uploadPage.clickProcess();

    // Wait for progress bar to appear (processing started)
    // Esperar a que aparezca la barra de progreso (procesamiento iniciado)
    await expect(resultsPage.progressBar).toBeVisible({ timeout: 5000 });

    // Check if download buttons are disabled while processing
    // Verificar si los botones de descarga están deshabilitados mientras procesa
    const areEnabled = await resultsPage.areDownloadsEnabled().catch(() => false);

    // During processing, downloads should be disabled
    // Durante procesamiento, descargas deben estar deshabilitadas
    // Note: This test might be flaky if processing completes very quickly
    // Nota: Este test puede ser inestable si el procesamiento completa muy rápido
    expect(areEnabled).toBe(false);
  });
});

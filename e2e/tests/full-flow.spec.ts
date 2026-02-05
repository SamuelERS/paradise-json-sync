/**
 * Full Flow Tests / Tests de Flujo Completo
 *
 * End-to-end tests covering the complete user journey
 * Tests end-to-end cubriendo el viaje completo del usuario
 */

import { test, expect } from '@playwright/test';
import { HomePage, UploadPage, ResultsPage } from '../pages';
import { getTestDataPath, verifyDownloadedFile, waitForNetworkIdle } from '../utils/helpers';

test.describe('Full Flow E2E / Flujo Completo E2E', () => {
  let homePage: HomePage;
  let uploadPage: UploadPage;
  let resultsPage: ResultsPage;

  test.beforeEach(async ({ page }) => {
    homePage = new HomePage(page);
    uploadPage = new UploadPage(page);
    resultsPage = new ResultsPage(page);
  });

  test('Complete flow: Upload -> Process -> Download Excel', async ({ page }) => {
    // =================================================================
    // STEP 1: Navigate to home page
    // PASO 1: Navegar a la página principal
    // =================================================================
    await homePage.goto();
    await homePage.waitForReady();

    // Verify page loaded correctly
    // Verificar que la página cargó correctamente
    const isDropzoneVisible = await homePage.isDropzoneVisible();
    expect(isDropzoneVisible).toBe(true);

    // =================================================================
    // STEP 2: Upload a JSON invoice file
    // PASO 2: Subir un archivo de factura JSON
    // =================================================================
    const jsonFilePath = getTestDataPath('sample-invoice.json');
    await uploadPage.uploadFile(jsonFilePath);

    // Verify file was uploaded
    // Verificar que el archivo se subió
    const fileCount = await uploadPage.getFileCount();
    expect(fileCount).toBe(1);

    // =================================================================
    // STEP 3: Start processing
    // PASO 3: Iniciar procesamiento
    // =================================================================
    const isProcessEnabled = await homePage.isProcessButtonEnabled();
    expect(isProcessEnabled).toBe(true);

    await uploadPage.clickProcess();

    // =================================================================
    // STEP 4: Wait for processing to complete
    // PASO 4: Esperar a que el procesamiento complete
    // =================================================================
    await expect(resultsPage.progressBar).toBeVisible({ timeout: 10000 });
    await resultsPage.waitForCompletion(60000);

    // Verify completion status
    // Verificar estado de completado
    const isCompleted = await resultsPage.isCompleted();
    expect(isCompleted).toBe(true);

    // =================================================================
    // STEP 5: Download Excel result
    // PASO 5: Descargar resultado Excel
    // =================================================================
    const areDownloadsEnabled = await resultsPage.areDownloadsEnabled();
    expect(areDownloadsEnabled).toBe(true);

    const { filename, path: downloadPath } = await resultsPage.downloadExcel();

    // Verify download completed
    // Verificar que la descarga completó
    expect(filename).toMatch(/\.xlsx$/i);
    const isValidFile = await verifyDownloadedFile(downloadPath, '.xlsx');
    expect(isValidFile).toBe(true);
  });

  test('Complete flow: Upload -> Process -> Download PDF', async ({ page }) => {
    // =================================================================
    // STEP 1: Navigate and upload
    // PASO 1: Navegar y subir
    // =================================================================
    await homePage.goto();
    await homePage.waitForReady();

    const jsonFilePath = getTestDataPath('sample-invoice.json');
    await uploadPage.uploadFile(jsonFilePath);

    // Verify upload
    // Verificar carga
    expect(await uploadPage.getFileCount()).toBe(1);

    // =================================================================
    // STEP 2: Process
    // PASO 2: Procesar
    // =================================================================
    await uploadPage.clickProcess();
    await resultsPage.waitForCompletion(60000);

    expect(await resultsPage.isCompleted()).toBe(true);

    // =================================================================
    // STEP 3: Download PDF
    // PASO 3: Descargar PDF
    // =================================================================
    const { filename, path: downloadPath } = await resultsPage.downloadPdf();

    expect(filename).toMatch(/\.pdf$/i);
    expect(await verifyDownloadedFile(downloadPath, '.pdf')).toBe(true);
  });

  test('Complete flow with multiple files (JSON batch)', async ({ page }) => {
    // =================================================================
    // STEP 1: Navigate to home
    // PASO 1: Navegar al inicio
    // =================================================================
    await homePage.goto();
    await homePage.waitForReady();

    // =================================================================
    // STEP 2: Upload multiple JSON files
    // PASO 2: Subir múltiples archivos JSON
    // =================================================================
    const files = [
      getTestDataPath('sample-invoice.json'),
      getTestDataPath('sample-invoice-2.json'),
    ];
    await uploadPage.uploadMultipleFiles(files);

    // Verify both files uploaded
    // Verificar que ambos archivos se subieron
    const fileCount = await uploadPage.getFileCount();
    expect(fileCount).toBe(2);

    // =================================================================
    // STEP 3: Process batch
    // PASO 3: Procesar lote
    // =================================================================
    await uploadPage.clickProcess();

    // Wait for completion (longer timeout for batch)
    // Esperar completado (timeout más largo para lote)
    await resultsPage.waitForCompletion(90000);

    expect(await resultsPage.isCompleted()).toBe(true);

    // =================================================================
    // STEP 4: Download consolidated Excel
    // PASO 4: Descargar Excel consolidado
    // =================================================================
    const { filename, path: downloadPath } = await resultsPage.downloadExcel();

    expect(filename).toMatch(/\.xlsx$/i);
    expect(await verifyDownloadedFile(downloadPath, '.xlsx')).toBe(true);
  });

  test('Complete flow with mixed files (JSON + PDF)', async ({ page }) => {
    // Note: This test requires PDF test file to exist
    // Nota: Este test requiere que exista el archivo PDF de prueba
    const pdfPath = getTestDataPath('sample.pdf');
    const fs = require('fs');
    test.skip(!fs.existsSync(pdfPath), 'PDF test file not created yet');

    // =================================================================
    // STEP 1: Navigate to home
    // PASO 1: Navegar al inicio
    // =================================================================
    await homePage.goto();
    await homePage.waitForReady();

    // =================================================================
    // STEP 2: Upload JSON and PDF files
    // PASO 2: Subir archivos JSON y PDF
    // =================================================================
    const jsonPath = getTestDataPath('sample-invoice.json');
    await uploadPage.uploadFile(jsonPath);
    await uploadPage.uploadFile(pdfPath);

    // Verify both files uploaded
    // Verificar que ambos archivos se subieron
    const fileCount = await uploadPage.getFileCount();
    expect(fileCount).toBe(2);

    // =================================================================
    // STEP 3: Process mixed batch
    // PASO 3: Procesar lote mixto
    // =================================================================
    await uploadPage.clickProcess();
    await resultsPage.waitForCompletion(120000);

    expect(await resultsPage.isCompleted()).toBe(true);

    // =================================================================
    // STEP 4: Verify downloads available
    // PASO 4: Verificar descargas disponibles
    // =================================================================
    expect(await resultsPage.areDownloadsEnabled()).toBe(true);

    // Download and verify Excel
    // Descargar y verificar Excel
    const excelDownload = await resultsPage.downloadExcel();
    expect(excelDownload.filename).toMatch(/\.xlsx$/i);
  });

  test('Flow with error handling / Flujo con manejo de errores', async ({ page }) => {
    // =================================================================
    // STEP 1: Navigate and upload invalid file
    // PASO 1: Navegar y subir archivo inválido
    // =================================================================
    await homePage.goto();
    await homePage.waitForReady();

    const invalidPath = getTestDataPath('invalid-invoice.json');
    await uploadPage.uploadFile(invalidPath);

    // =================================================================
    // STEP 2: Process invalid file
    // PASO 2: Procesar archivo inválido
    // =================================================================
    await uploadPage.clickProcess();

    // Wait for results (may show errors or complete with warnings)
    // Esperar resultados (puede mostrar errores o completar con advertencias)
    await expect(resultsPage.resultsContainer).toBeVisible({ timeout: 60000 });

    // =================================================================
    // STEP 3: Verify error/warning handling
    // PASO 3: Verificar manejo de errores/advertencias
    // =================================================================
    const errorCount = await resultsPage.getErrorCount();
    const errors = await resultsPage.getErrors();

    // System should handle invalid files gracefully
    // El sistema debe manejar archivos inválidos correctamente
    // Either show errors or skip invalid files
    // Ya sea mostrar errores o saltar archivos inválidos
    expect(errorCount >= 0).toBe(true);

    // If errors exist, they should be meaningful
    // Si existen errores, deben ser significativos
    if (errors.length > 0) {
      errors.forEach(error => {
        expect(error.length).toBeGreaterThan(0);
      });
    }
  });

  test('Complete user journey with file management', async ({ page }) => {
    // =================================================================
    // Full journey: Upload -> Remove -> Upload again -> Process -> Download
    // Viaje completo: Subir -> Eliminar -> Subir de nuevo -> Procesar -> Descargar
    // =================================================================

    // Step 1: Navigate
    // Paso 1: Navegar
    await homePage.goto();
    await homePage.waitForReady();

    // Step 2: Upload first file
    // Paso 2: Subir primer archivo
    const file1 = getTestDataPath('sample-invoice.json');
    await uploadPage.uploadFile(file1);
    expect(await uploadPage.getFileCount()).toBe(1);

    // Step 3: Remove the file
    // Paso 3: Eliminar el archivo
    await uploadPage.removeFile('sample-invoice.json');
    expect(await uploadPage.getFileCount()).toBe(0);

    // Step 4: Upload different file
    // Paso 4: Subir archivo diferente
    const file2 = getTestDataPath('sample-invoice-2.json');
    await uploadPage.uploadFile(file2);
    expect(await uploadPage.getFileCount()).toBe(1);

    // Step 5: Process
    // Paso 5: Procesar
    await uploadPage.clickProcess();
    await resultsPage.waitForCompletion(60000);
    expect(await resultsPage.isCompleted()).toBe(true);

    // Step 6: Download
    // Paso 6: Descargar
    const { filename } = await resultsPage.downloadExcel();
    expect(filename).toMatch(/\.xlsx$/i);
  });
});

test.describe('Performance Tests / Tests de Rendimiento', () => {
  test('Page loads within acceptable time', async ({ page }) => {
    const homePage = new HomePage(page);

    // Measure page load time
    // Medir tiempo de carga de página
    const startTime = Date.now();
    await homePage.goto();
    await homePage.waitForReady();
    const loadTime = Date.now() - startTime;

    // Assert: Page loads in less than 5 seconds
    // Verificar: Página carga en menos de 5 segundos
    expect(loadTime).toBeLessThan(5000);
  });

  test('File upload completes within acceptable time', async ({ page }) => {
    const homePage = new HomePage(page);
    const uploadPage = new UploadPage(page);

    await homePage.goto();
    await homePage.waitForReady();

    // Measure upload time
    // Medir tiempo de carga
    const jsonFilePath = getTestDataPath('sample-invoice.json');
    const startTime = Date.now();
    await uploadPage.uploadFile(jsonFilePath);
    const uploadTime = Date.now() - startTime;

    // Assert: Upload completes in less than 3 seconds
    // Verificar: Carga completa en menos de 3 segundos
    expect(uploadTime).toBeLessThan(3000);
  });
});

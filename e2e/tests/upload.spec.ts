/**
 * Upload Tests / Tests de Carga de Archivos
 *
 * E2E tests for file upload functionality
 * Tests E2E para la funcionalidad de carga de archivos
 */

import { test, expect } from '@playwright/test';
import { HomePage, UploadPage } from '../pages';
import { getTestDataPath, cleanupTempFiles, createTempFile } from '../utils/helpers';

test.describe('File Upload / Carga de Archivos', () => {
  let homePage: HomePage;
  let uploadPage: UploadPage;

  test.beforeEach(async ({ page }) => {
    homePage = new HomePage(page);
    uploadPage = new UploadPage(page);
    await homePage.goto();
  });

  test.afterAll(() => {
    cleanupTempFiles();
  });

  test('User can upload a JSON file / Usuario puede subir archivo JSON', async ({ page }) => {
    // Arrange: Get test file path
    // Preparar: Obtener ruta del archivo de prueba
    const jsonFilePath = getTestDataPath('sample-invoice.json');

    // Act: Upload the file
    // Actuar: Subir el archivo
    await uploadPage.uploadFile(jsonFilePath);

    // Assert: File appears in the list
    // Verificar: El archivo aparece en la lista
    const fileCount = await uploadPage.getFileCount();
    expect(fileCount).toBe(1);

    const hasFile = await homePage.hasFile('sample-invoice.json');
    expect(hasFile).toBe(true);
  });

  test('User can upload a PDF file / Usuario puede subir archivo PDF', async ({ page }) => {
    // Arrange: Create a minimal test PDF path (would exist in real implementation)
    // Preparar: Crear ruta de PDF de prueba mínimo
    const pdfFilePath = getTestDataPath('sample.pdf');

    // Skip if PDF doesn't exist (for initial setup)
    // Saltar si el PDF no existe (para configuración inicial)
    test.skip(!require('fs').existsSync(pdfFilePath), 'PDF test file not created yet');

    // Act: Upload the file
    // Actuar: Subir el archivo
    await uploadPage.uploadFile(pdfFilePath);

    // Assert: File appears in the list
    // Verificar: El archivo aparece en la lista
    const fileCount = await uploadPage.getFileCount();
    expect(fileCount).toBe(1);

    const hasFile = await homePage.hasFile('sample.pdf');
    expect(hasFile).toBe(true);
  });

  test('User can upload multiple files / Usuario puede subir múltiples archivos', async ({ page }) => {
    // Arrange: Get test file paths
    // Preparar: Obtener rutas de archivos de prueba
    const files = [
      getTestDataPath('sample-invoice.json'),
      getTestDataPath('sample-invoice-2.json'),
    ];

    // Act: Upload multiple files
    // Actuar: Subir múltiples archivos
    await uploadPage.uploadMultipleFiles(files);

    // Assert: Both files appear in the list
    // Verificar: Ambos archivos aparecen en la lista
    const fileCount = await uploadPage.getFileCount();
    expect(fileCount).toBe(2);

    const hasFile1 = await homePage.hasFile('sample-invoice.json');
    const hasFile2 = await homePage.hasFile('sample-invoice-2.json');
    expect(hasFile1).toBe(true);
    expect(hasFile2).toBe(true);
  });

  test('Invalid file shows error / Archivo inválido muestra error', async ({ page }) => {
    // Arrange: Create an invalid file (wrong extension)
    // Preparar: Crear un archivo inválido (extensión incorrecta)
    const invalidFilePath = await createTempFile(
      'This is not a valid invoice file',
      'invalid.txt'
    );

    // Act: Try to upload invalid file
    // Actuar: Intentar subir archivo inválido
    await uploadPage.uploadFile(invalidFilePath);

    // Assert: Error message is shown
    // Verificar: Se muestra mensaje de error
    const hasError = await uploadPage.hasError();
    expect(hasError).toBe(true);

    const errorMessage = await uploadPage.getErrorMessage();
    expect(errorMessage).toBeTruthy();
  });

  test('User can remove file from list / Usuario puede eliminar archivo de la lista', async ({ page }) => {
    // Arrange: Upload a file first
    // Preparar: Subir un archivo primero
    const jsonFilePath = getTestDataPath('sample-invoice.json');
    await uploadPage.uploadFile(jsonFilePath);

    // Verify file is in list
    // Verificar que el archivo está en la lista
    let fileCount = await uploadPage.getFileCount();
    expect(fileCount).toBe(1);

    // Act: Remove the file
    // Actuar: Eliminar el archivo
    await uploadPage.removeFile('sample-invoice.json');

    // Assert: File is removed from the list
    // Verificar: El archivo se elimina de la lista
    fileCount = await uploadPage.getFileCount();
    expect(fileCount).toBe(0);
  });

  test('Dropzone is visible and interactive / Dropzone es visible e interactivo', async ({ page }) => {
    // Assert: Dropzone is visible
    // Verificar: Dropzone es visible
    const isVisible = await homePage.isDropzoneVisible();
    expect(isVisible).toBe(true);

    // Assert: Drag and drop is enabled
    // Verificar: Arrastrar y soltar está habilitado
    const isEnabled = await uploadPage.isDragDropEnabled();
    expect(isEnabled).toBe(true);
  });

  test('Process button is disabled without files / Botón procesar deshabilitado sin archivos', async ({ page }) => {
    // Assert: Process button is disabled when no files uploaded
    // Verificar: Botón procesar está deshabilitado cuando no hay archivos
    const isEnabled = await homePage.isProcessButtonEnabled();
    expect(isEnabled).toBe(false);
  });

  test('Process button is enabled with files / Botón procesar habilitado con archivos', async ({ page }) => {
    // Arrange: Upload a file
    // Preparar: Subir un archivo
    const jsonFilePath = getTestDataPath('sample-invoice.json');
    await uploadPage.uploadFile(jsonFilePath);

    // Assert: Process button is enabled
    // Verificar: Botón procesar está habilitado
    const isEnabled = await homePage.isProcessButtonEnabled();
    expect(isEnabled).toBe(true);
  });

  test('Clear all files / Limpiar todos los archivos', async ({ page }) => {
    // Arrange: Upload multiple files
    // Preparar: Subir múltiples archivos
    const files = [
      getTestDataPath('sample-invoice.json'),
      getTestDataPath('sample-invoice-2.json'),
    ];
    await uploadPage.uploadMultipleFiles(files);

    // Verify files are uploaded
    // Verificar que los archivos están subidos
    let fileCount = await uploadPage.getFileCount();
    expect(fileCount).toBe(2);

    // Act: Clear all files
    // Actuar: Limpiar todos los archivos
    await uploadPage.clearAllFiles();

    // Assert: All files are removed
    // Verificar: Todos los archivos se eliminaron
    fileCount = await uploadPage.getFileCount();
    expect(fileCount).toBe(0);
  });
});

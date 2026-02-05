/**
 * E2E Test Helpers / Utilidades para Tests E2E
 *
 * Common utilities and helper functions for E2E tests
 * Funciones utilitarias comunes para tests E2E
 */

import { Page, expect, BrowserContext } from '@playwright/test';
import path from 'path';
import fs from 'fs';

/**
 * Test data directory path
 * Ruta al directorio de datos de prueba
 */
export const TEST_DATA_DIR = path.join(__dirname, '..', 'fixtures', 'test-data');

/**
 * Get path to a test data file
 * Obtener ruta a un archivo de datos de prueba
 */
export function getTestDataPath(filename: string): string {
  return path.join(TEST_DATA_DIR, filename);
}

/**
 * Wait for API response
 * Esperar respuesta de API
 */
export async function waitForApiResponse(
  page: Page,
  urlPattern: string | RegExp,
  timeout: number = 30000
): Promise<void> {
  await page.waitForResponse(
    (response) => {
      if (typeof urlPattern === 'string') {
        return response.url().includes(urlPattern);
      }
      return urlPattern.test(response.url());
    },
    { timeout }
  );
}

/**
 * Wait for network to be idle
 * Esperar a que la red esté inactiva
 */
export async function waitForNetworkIdle(
  page: Page,
  timeout: number = 5000
): Promise<void> {
  await page.waitForLoadState('networkidle', { timeout });
}

/**
 * Generate unique test ID
 * Generar ID único para tests
 */
export function generateTestId(): string {
  return `test-${Date.now()}-${Math.random().toString(36).substring(7)}`;
}

/**
 * Create temporary test file
 * Crear archivo temporal de prueba
 */
export async function createTempFile(
  content: string,
  filename: string
): Promise<string> {
  const tempDir = path.join(__dirname, '..', 'temp');
  if (!fs.existsSync(tempDir)) {
    fs.mkdirSync(tempDir, { recursive: true });
  }
  const filePath = path.join(tempDir, filename);
  fs.writeFileSync(filePath, content);
  return filePath;
}

/**
 * Clean up temporary files
 * Limpiar archivos temporales
 */
export function cleanupTempFiles(): void {
  const tempDir = path.join(__dirname, '..', 'temp');
  if (fs.existsSync(tempDir)) {
    fs.rmSync(tempDir, { recursive: true, force: true });
  }
}

/**
 * Verify downloaded file exists and has content
 * Verificar que el archivo descargado existe y tiene contenido
 */
export async function verifyDownloadedFile(
  downloadPath: string,
  expectedExtension: string
): Promise<boolean> {
  if (!fs.existsSync(downloadPath)) {
    return false;
  }

  const stats = fs.statSync(downloadPath);
  if (stats.size === 0) {
    return false;
  }

  const ext = path.extname(downloadPath);
  return ext === expectedExtension;
}

/**
 * Take a screenshot for debugging
 * Tomar captura de pantalla para depuración
 */
export async function takeDebugScreenshot(
  page: Page,
  name: string
): Promise<void> {
  const screenshotsDir = path.join(__dirname, '..', 'screenshots');
  if (!fs.existsSync(screenshotsDir)) {
    fs.mkdirSync(screenshotsDir, { recursive: true });
  }
  await page.screenshot({
    path: path.join(screenshotsDir, `${name}-${Date.now()}.png`),
    fullPage: true,
  });
}

/**
 * Mock API responses for offline testing
 * Simular respuestas de API para pruebas offline
 */
export async function mockApiResponses(
  page: Page,
  mocks: Array<{
    url: string | RegExp;
    status?: number;
    body: unknown;
  }>
): Promise<void> {
  for (const mock of mocks) {
    await page.route(mock.url, (route) => {
      route.fulfill({
        status: mock.status || 200,
        contentType: 'application/json',
        body: JSON.stringify(mock.body),
      });
    });
  }
}

/**
 * Clear all mock routes
 * Limpiar todas las rutas simuladas
 */
export async function clearMocks(page: Page): Promise<void> {
  await page.unrouteAll();
}

/**
 * Wait for element and verify text
 * Esperar elemento y verificar texto
 */
export async function waitForText(
  page: Page,
  selector: string,
  text: string,
  timeout: number = 10000
): Promise<void> {
  const element = page.locator(selector);
  await expect(element).toContainText(text, { timeout });
}

/**
 * Retry an action with exponential backoff
 * Reintentar una acción con backoff exponencial
 */
export async function retryWithBackoff<T>(
  action: () => Promise<T>,
  maxRetries: number = 3,
  initialDelay: number = 1000
): Promise<T> {
  let lastError: Error | undefined;

  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      return await action();
    } catch (error) {
      lastError = error as Error;
      if (attempt < maxRetries - 1) {
        const delay = initialDelay * Math.pow(2, attempt);
        await new Promise((resolve) => setTimeout(resolve, delay));
      }
    }
  }

  throw lastError;
}

/**
 * Validate JSON structure
 * Validar estructura JSON
 */
export function validateJsonStructure(
  data: unknown,
  requiredFields: string[]
): boolean {
  if (typeof data !== 'object' || data === null) {
    return false;
  }

  const obj = data as Record<string, unknown>;
  return requiredFields.every((field) => field in obj);
}

/**
 * Storage utilities for browser context
 * Utilidades de almacenamiento para contexto de navegador
 */
export const storage = {
  async setItem(context: BrowserContext, key: string, value: string): Promise<void> {
    await context.addInitScript(
      ({ key, value }) => {
        localStorage.setItem(key, value);
      },
      { key, value }
    );
  },

  async clear(context: BrowserContext): Promise<void> {
    await context.addInitScript(() => {
      localStorage.clear();
    });
  },
};

/**
 * Polling helper for async operations
 * Helper de polling para operaciones asíncronas
 */
export async function pollUntil<T>(
  condition: () => Promise<T>,
  predicate: (value: T) => boolean,
  options: {
    timeout?: number;
    interval?: number;
  } = {}
): Promise<T> {
  const { timeout = 30000, interval = 500 } = options;
  const startTime = Date.now();

  while (Date.now() - startTime < timeout) {
    const value = await condition();
    if (predicate(value)) {
      return value;
    }
    await new Promise((resolve) => setTimeout(resolve, interval));
  }

  throw new Error(`Polling timeout after ${timeout}ms`);
}

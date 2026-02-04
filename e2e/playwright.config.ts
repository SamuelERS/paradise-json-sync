/**
 * Playwright Configuration
 * Configuración de Playwright para tests E2E
 *
 * Paradise JSON Sync - E2E Testing Infrastructure
 */

import { defineConfig, devices } from '@playwright/test';

/**
 * Read environment variables
 * Variables de entorno para configuración
 * @see https://playwright.dev/docs/test-configuration
 */
export default defineConfig({
  // Test directory / Directorio de tests
  testDir: './tests',

  // Run tests in parallel / Ejecutar tests en paralelo
  fullyParallel: true,

  // Fail the build on CI if you accidentally left test.only in the source code
  // Fallar en CI si se deja test.only en el código
  forbidOnly: !!process.env.CI,

  // Retry configuration / Configuración de reintentos
  // 2 retries on CI, 0 on local / 2 reintentos en CI, 0 en local
  retries: process.env.CI ? 2 : 0,

  // Opt out of parallel tests on CI / Deshabilitar paralelismo en CI
  workers: process.env.CI ? 1 : undefined,

  // Reporter configuration / Configuración de reportes
  reporter: [
    ['list'],
    ['html', { outputFolder: 'playwright-report' }],
    ...(process.env.CI ? [['github' as const]] : []),
  ],

  // Global timeout / Timeout global
  timeout: 30000,

  // Expect timeout / Timeout para assertions
  expect: {
    timeout: 5000,
  },

  // Shared settings for all projects / Configuración compartida
  use: {
    // Base URL from environment or default
    // URL base desde variable de entorno o por defecto
    baseURL: process.env.BASE_URL || 'http://localhost:5173',

    // Collect trace when retrying the failed test
    // Recolectar trace al reintentar test fallido
    trace: 'on-first-retry',

    // Take screenshot on failure / Captura de pantalla al fallar
    screenshot: 'only-on-failure',

    // Record video on retry / Grabar video al reintentar
    video: 'on-first-retry',

    // Action timeout / Timeout para acciones
    actionTimeout: 10000,

    // Navigation timeout / Timeout para navegación
    navigationTimeout: 15000,
  },

  // Configure projects for major browsers
  // Configurar proyectos para navegadores principales
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    // Webkit is optional, uncomment to enable
    // Webkit es opcional, descomentar para habilitar
    // {
    //   name: 'webkit',
    //   use: { ...devices['Desktop Safari'] },
    // },

    // Mobile viewports / Viewports móviles
    {
      name: 'mobile-chrome',
      use: { ...devices['Pixel 5'] },
    },
  ],

  // Run local dev server before starting the tests
  // Ejecutar servidor de desarrollo antes de los tests
  // Uncomment when frontend is ready / Descomentar cuando el frontend esté listo
  // webServer: [
  //   {
  //     command: 'cd ../frontend && npm run dev',
  //     url: 'http://localhost:5173',
  //     reuseExistingServer: !process.env.CI,
  //     timeout: 120 * 1000,
  //   },
  //   {
  //     command: 'cd ../backend && uvicorn app.main:app --reload --port 8000',
  //     url: 'http://localhost:8000/health',
  //     reuseExistingServer: !process.env.CI,
  //     timeout: 120 * 1000,
  //   },
  // ],
});

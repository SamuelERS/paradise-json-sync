/**
 * Vitest Configuration / Configuración de Vitest
 *
 * Configuration for frontend unit and integration tests.
 * Configuración para tests unitarios y de integración del frontend.
 */

import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    // Test environment / Entorno de tests
    environment: 'jsdom',

    // Globals (describe, it, expect)
    globals: true,

    // Setup files / Archivos de configuración
    setupFiles: ['./tests/setup.ts'],

    // Include patterns / Patrones de inclusión
    include: [
      'tests/**/*.{test,spec}.{js,jsx,ts,tsx}',
      'src/**/*.{test,spec}.{js,jsx,ts,tsx}',
    ],

    // Exclude patterns / Patrones de exclusión
    exclude: ['node_modules', 'dist'],

    // Coverage configuration / Configuración de cobertura
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html', 'lcov'],
      reportsDirectory: './coverage',
      exclude: [
        'node_modules',
        'tests',
        '**/*.d.ts',
        '**/*.config.{js,ts}',
        '**/index.{js,ts,jsx,tsx}',
      ],
    },

    // Test timeout / Timeout de tests
    testTimeout: 10000,

    // Reporter configuration / Configuración de reportes
    reporters: ['default', 'html'],

    // Output directory for reports / Directorio de salida para reportes
    outputFile: {
      html: './test-results/index.html',
    },
  },
});

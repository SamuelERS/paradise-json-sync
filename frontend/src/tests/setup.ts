/**
 * Test Setup / Configuración de Tests
 *
 * EN: Global setup file for Vitest tests with testing-library matchers.
 * ES: Archivo de configuración global para tests de Vitest con matchers de testing-library.
 */
import '@testing-library/jest-dom';
import { afterEach, vi } from 'vitest';
import { cleanup } from '@testing-library/react';

// EN: Clean up after each test | ES: Limpieza después de cada test
afterEach(() => {
  cleanup();
});

// EN: Mock window.URL.createObjectURL | ES: Mock de window.URL.createObjectURL
Object.defineProperty(window.URL, 'createObjectURL', {
  writable: true,
  value: vi.fn(() => 'blob:mock-url'),
});

Object.defineProperty(window.URL, 'revokeObjectURL', {
  writable: true,
  value: vi.fn(),
});

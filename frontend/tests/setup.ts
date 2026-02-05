/**
 * Test Setup / Configuración de Tests
 *
 * Global setup for all frontend tests.
 * Configuración global para todos los tests del frontend.
 */

import '@testing-library/jest-dom';

// Mock window.matchMedia for tests that use media queries
// Mock de window.matchMedia para tests que usan media queries
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: (query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: () => {},
    removeListener: () => {},
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => false,
  }),
});

// Mock IntersectionObserver for tests
// Mock de IntersectionObserver para tests
class MockIntersectionObserver {
  observe = () => {};
  disconnect = () => {};
  unobserve = () => {};
}

Object.defineProperty(window, 'IntersectionObserver', {
  writable: true,
  value: MockIntersectionObserver,
});

// Mock ResizeObserver for tests
// Mock de ResizeObserver para tests
class MockResizeObserver {
  observe = () => {};
  disconnect = () => {};
  unobserve = () => {};
}

Object.defineProperty(window, 'ResizeObserver', {
  writable: true,
  value: MockResizeObserver,
});

// Clean up after each test
// Limpiar después de cada test
afterEach(() => {
  // Clean up any DOM elements created during tests
  // Limpiar cualquier elemento DOM creado durante tests
  document.body.innerHTML = '';
});

// Global test utilities
// Utilidades globales de test
export const testUtils = {
  /**
   * Wait for a condition to be true
   * Esperar a que una condición sea verdadera
   */
  waitFor: async (
    condition: () => boolean,
    timeout = 5000,
    interval = 100
  ): Promise<void> => {
    const startTime = Date.now();
    while (!condition() && Date.now() - startTime < timeout) {
      await new Promise((resolve) => setTimeout(resolve, interval));
    }
    if (!condition()) {
      throw new Error(`Condition not met within ${timeout}ms`);
    }
  },

  /**
   * Create a mock file for testing
   * Crear un archivo mock para testing
   */
  createMockFile: (
    name: string,
    type: string,
    content: string = ''
  ): File => {
    return new File([content], name, { type });
  },
};

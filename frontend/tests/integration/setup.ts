/**
 * MSW Integration Test Setup / Configuración de Tests de Integración con MSW
 *
 * Setup Mock Service Worker for frontend integration tests.
 * Configurar Mock Service Worker para tests de integración del frontend.
 */

import { setupServer } from 'msw/node';
import { handlers } from './handlers';

/**
 * MSW Server instance
 * Instancia del servidor MSW
 *
 * This server intercepts network requests and returns mock responses.
 * Este servidor intercepta peticiones de red y retorna respuestas mock.
 */
export const server = setupServer(...handlers);

/**
 * Setup and teardown for tests
 * Configuración y limpieza para tests
 *
 * Use these hooks in your test files:
 * Usar estos hooks en tus archivos de test:
 *
 * beforeAll(() => server.listen())
 * afterEach(() => server.resetHandlers())
 * afterAll(() => server.close())
 */

/**
 * Start the MSW server before all tests
 * Iniciar el servidor MSW antes de todos los tests
 */
export const startServer = (): void => {
  server.listen({ onUnhandledRequest: 'warn' });
};

/**
 * Reset handlers after each test
 * Resetear handlers después de cada test
 */
export const resetHandlers = (): void => {
  server.resetHandlers();
};

/**
 * Close the server after all tests
 * Cerrar el servidor después de todos los tests
 */
export const closeServer = (): void => {
  server.close();
};

/**
 * Helper to add runtime handlers for specific tests
 * Helper para agregar handlers en tiempo de ejecución para tests específicos
 *
 * @param additionalHandlers - Array of additional handlers
 */
export const useHandlers = (...additionalHandlers: Parameters<typeof server.use>): void => {
  server.use(...additionalHandlers);
};

/**
 * Export the server for direct access when needed
 * Exportar el servidor para acceso directo cuando sea necesario
 */
export { server };

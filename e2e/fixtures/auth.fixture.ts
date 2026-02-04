/**
 * Authentication Fixture / Fixture de Autenticación
 *
 * Handles authentication state for E2E tests
 * Maneja el estado de autenticación para tests E2E
 *
 * Note: This fixture is prepared for when authentication is implemented
 * Nota: Este fixture está preparado para cuando se implemente autenticación
 */

import { test as base, BrowserContext, Page } from '@playwright/test';

/**
 * Authentication state type
 * Tipo de estado de autenticación
 */
interface AuthState {
  isAuthenticated: boolean;
  user?: {
    id: string;
    email: string;
    name: string;
    role: string;
  };
  token?: string;
}

/**
 * Test fixtures type extension
 * Extensión de tipo de fixtures de test
 */
type AuthFixtures = {
  authenticatedPage: Page;
  authContext: BrowserContext;
  authState: AuthState;
};

/**
 * Default auth state for tests
 * Estado de autenticación por defecto para tests
 */
const defaultAuthState: AuthState = {
  isAuthenticated: false,
};

/**
 * Mock authenticated state
 * Estado autenticado simulado
 */
const mockAuthenticatedState: AuthState = {
  isAuthenticated: true,
  user: {
    id: 'test-user-001',
    email: 'test@example.com',
    name: 'Test User',
    role: 'admin',
  },
  token: 'mock-jwt-token-for-testing',
};

/**
 * Extended test with auth fixtures
 * Test extendido con fixtures de autenticación
 */
export const test = base.extend<AuthFixtures>({
  /**
   * Auth state fixture
   * Fixture de estado de autenticación
   */
  authState: async ({}, use) => {
    // For now, use mock state - replace with real auth when implemented
    // Por ahora, usar estado mock - reemplazar con auth real cuando se implemente
    await use(mockAuthenticatedState);
  },

  /**
   * Authenticated browser context
   * Contexto de navegador autenticado
   */
  authContext: async ({ browser, authState }, use) => {
    const context = await browser.newContext();

    // Set authentication storage state if authenticated
    // Establecer estado de almacenamiento de autenticación si está autenticado
    if (authState.isAuthenticated && authState.token) {
      await context.addInitScript(
        (state) => {
          localStorage.setItem('auth_token', state.token || '');
          localStorage.setItem('auth_user', JSON.stringify(state.user));
          localStorage.setItem('is_authenticated', 'true');
        },
        authState
      );
    }

    await use(context);
    await context.close();
  },

  /**
   * Authenticated page
   * Página autenticada
   */
  authenticatedPage: async ({ authContext }, use) => {
    const page = await authContext.newPage();
    await use(page);
    await page.close();
  },
});

/**
 * Helper to simulate login
 * Helper para simular login
 */
export async function simulateLogin(
  page: Page,
  credentials?: { email: string; password: string }
): Promise<void> {
  const email = credentials?.email || 'test@example.com';
  const password = credentials?.password || 'testpassword123';

  // Navigate to login page
  // Navegar a página de login
  await page.goto('/login');

  // Fill credentials
  // Llenar credenciales
  await page.fill('[data-testid="email-input"]', email);
  await page.fill('[data-testid="password-input"]', password);

  // Submit
  // Enviar
  await page.click('[data-testid="login-button"]');

  // Wait for redirect to home
  // Esperar redirección a inicio
  await page.waitForURL('/');
}

/**
 * Helper to simulate logout
 * Helper para simular logout
 */
export async function simulateLogout(page: Page): Promise<void> {
  // Click logout button or navigate to logout
  // Click en botón de logout o navegar a logout
  await page.click('[data-testid="logout-button"]');

  // Wait for redirect to login
  // Esperar redirección a login
  await page.waitForURL('/login');
}

/**
 * Helper to check if user is authenticated
 * Helper para verificar si el usuario está autenticado
 */
export async function isAuthenticated(page: Page): Promise<boolean> {
  const token = await page.evaluate(() => localStorage.getItem('auth_token'));
  return token !== null && token !== '';
}

/**
 * Export expect from base test
 * Exportar expect del test base
 */
export { expect } from '@playwright/test';

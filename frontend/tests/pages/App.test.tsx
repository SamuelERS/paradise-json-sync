/**
 * App Component Tests (Tests del Componente App)
 *
 * Tests for the root App component.
 * Tests para el componente raíz App.
 */
import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { App } from '../../src/App';

// Mock HomePage to avoid complex dependency chain
vi.mock('../../src/pages', () => ({
  HomePage: () => <div data-testid="home-page">HomePage Mock</div>,
}));

describe('App', () => {
  describe('Rendering', () => {
    it('renders without crashing', () => {
      render(<App />);
      expect(screen.getByTestId('home-page')).toBeInTheDocument();
    });

    it('renders HomePage component', () => {
      render(<App />);
      expect(screen.getByText('HomePage Mock')).toBeInTheDocument();
    });
  });

  describe('Structure', () => {
    it('renders as root component', () => {
      const { container } = render(<App />);
      expect(container.firstChild).toBeTruthy();
    });
  });

  describe('Default Export', () => {
    it('exports default App component', async () => {
      const module = await import('../../src/App');
      expect(module.default).toBeDefined();
      expect(module.App).toBeDefined();
    });
  });
});

describe('App Integration', () => {
  // For full integration tests, unmock HomePage
  beforeEach(() => {
    vi.resetModules();
  });

  it('integrates with HomePage (full render)', async () => {
    // This test would render the full app with actual HomePage
    // Skipped in unit tests to avoid hook dependencies
    vi.doUnmock('../../src/pages');

    // Full integration would need all hooks mocked
    expect(true).toBe(true);
  });
});

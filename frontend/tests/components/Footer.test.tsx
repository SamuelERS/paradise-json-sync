/**
 * Footer Component Tests (Tests del Componente Footer)
 *
 * Tests for the Footer layout component.
 * Tests para el componente de layout Footer.
 */
import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { Footer } from '../../src/components/layout/Footer';

describe('Footer', () => {
  describe('Rendering', () => {
    it('renders footer element', () => {
      render(<Footer />);

      const footer = screen.getByRole('contentinfo');
      expect(footer).toBeInTheDocument();
    });

    it('renders current year in copyright', () => {
      render(<Footer />);

      const currentYear = new Date().getFullYear();
      expect(screen.getByText(new RegExp(`${currentYear}`))).toBeInTheDocument();
    });

    it('renders Paradise JSON Sync text', () => {
      render(<Footer />);

      expect(screen.getByText(/Paradise JSON Sync/)).toBeInTheDocument();
    });

    it('renders version number', () => {
      render(<Footer />);

      expect(screen.getByText('v0.1.0')).toBeInTheDocument();
    });
  });

  describe('Navigation Links', () => {
    it('renders help link', () => {
      render(<Footer />);

      const helpLink = screen.getByRole('link', { name: /ayuda/i });
      expect(helpLink).toBeInTheDocument();
      expect(helpLink).toHaveAttribute('href', '#help');
    });

    it('renders documentation link', () => {
      render(<Footer />);

      const docsLink = screen.getByRole('link', { name: /documentación/i });
      expect(docsLink).toBeInTheDocument();
      expect(docsLink).toHaveAttribute('href', '#docs');
    });
  });

  describe('Dynamic Year', () => {
    it('displays a 4-digit year in copyright', () => {
      render(<Footer />);

      // Check that a 4-digit year is present (202x or 203x)
      const copyrightText = screen.getByText(/Paradise JSON Sync/);
      expect(copyrightText.textContent).toMatch(/\d{4}/);
    });

    it('year is reasonable (between 2020 and 2100)', () => {
      render(<Footer />);

      const copyrightText = screen.getByText(/Paradise JSON Sync/).textContent || '';
      const yearMatch = copyrightText.match(/(\d{4})/);
      expect(yearMatch).not.toBeNull();

      const year = parseInt(yearMatch![1], 10);
      expect(year).toBeGreaterThanOrEqual(2020);
      expect(year).toBeLessThanOrEqual(2100);
    });
  });

  describe('Styling', () => {
    it('has gray background', () => {
      render(<Footer />);

      const footer = screen.getByRole('contentinfo');
      expect(footer.className).toContain('bg-gray-50');
    });

    it('has top border', () => {
      render(<Footer />);

      const footer = screen.getByRole('contentinfo');
      expect(footer.className).toContain('border-t');
    });
  });
});

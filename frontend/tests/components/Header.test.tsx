/**
 * Header Component Tests (Tests del Componente Header)
 *
 * Tests for the Header layout component.
 * Tests para el componente de layout Header.
 */
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { Header } from '../../src/components/layout/Header';

describe('Header', () => {
  describe('Rendering', () => {
    it('renders header element', () => {
      render(<Header />);

      const header = screen.getByRole('banner');
      expect(header).toBeInTheDocument();
    });

    it('renders default title', () => {
      render(<Header />);

      expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('Paradise JSON Sync');
    });

    it('renders version number', () => {
      render(<Header />);

      expect(screen.getByText('v0.1.0')).toBeInTheDocument();
    });

    it('renders logo icon', () => {
      render(<Header />);

      const svg = document.querySelector('svg');
      expect(svg).toBeInTheDocument();
    });
  });

  describe('Custom Title', () => {
    it('renders custom title when provided', () => {
      render(<Header title="Custom App Name" />);

      expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('Custom App Name');
    });

    it('uses default title when not provided', () => {
      render(<Header />);

      expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('Paradise JSON Sync');
    });

    it('handles empty string title', () => {
      render(<Header title="" />);

      const heading = screen.getByRole('heading', { level: 1 });
      expect(heading).toHaveTextContent('');
    });
  });

  describe('Structure', () => {
    it('contains navigation element', () => {
      render(<Header />);

      const nav = screen.getByRole('navigation');
      expect(nav).toBeInTheDocument();
    });

    it('heading is level 1', () => {
      render(<Header />);

      const heading = screen.getByRole('heading', { level: 1 });
      expect(heading.tagName).toBe('H1');
    });
  });

  describe('Styling', () => {
    it('is fixed positioned', () => {
      render(<Header />);

      const header = screen.getByRole('banner');
      expect(header.className).toContain('fixed');
    });

    it('has white background', () => {
      render(<Header />);

      const header = screen.getByRole('banner');
      expect(header.className).toContain('bg-white');
    });

    it('has bottom border', () => {
      render(<Header />);

      const header = screen.getByRole('banner');
      expect(header.className).toContain('border-b');
    });

    it('has high z-index', () => {
      render(<Header />);

      const header = screen.getByRole('banner');
      expect(header.className).toContain('z-50');
    });
  });

  describe('Accessibility', () => {
    it('has proper heading hierarchy', () => {
      render(<Header />);

      const headings = screen.getAllByRole('heading');
      expect(headings.length).toBe(1);
      expect(headings[0].tagName).toBe('H1');
    });
  });
});

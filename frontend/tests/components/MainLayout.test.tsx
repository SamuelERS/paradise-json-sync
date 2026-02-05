/**
 * MainLayout Component Tests (Tests del Componente MainLayout)
 *
 * Tests for the MainLayout component that combines Header, Footer, and Container.
 * Tests para el componente MainLayout que combina Header, Footer y Container.
 */
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { MainLayout } from '../../src/components/layout/MainLayout';

describe('MainLayout', () => {
  describe('Rendering', () => {
    it('renders children content', () => {
      render(
        <MainLayout>
          <div data-testid="page-content">Page Content</div>
        </MainLayout>
      );

      expect(screen.getByTestId('page-content')).toBeInTheDocument();
      expect(screen.getByText('Page Content')).toBeInTheDocument();
    });

    it('renders Header component', () => {
      render(
        <MainLayout>
          <div>Content</div>
        </MainLayout>
      );

      expect(screen.getByRole('banner')).toBeInTheDocument();
    });

    it('renders Footer component', () => {
      render(
        <MainLayout>
          <div>Content</div>
        </MainLayout>
      );

      expect(screen.getByRole('contentinfo')).toBeInTheDocument();
    });

    it('renders main element', () => {
      render(
        <MainLayout>
          <div>Content</div>
        </MainLayout>
      );

      expect(screen.getByRole('main')).toBeInTheDocument();
    });
  });

  describe('Structure', () => {
    it('has header, main, and footer in correct order', () => {
      const { container } = render(
        <MainLayout>
          <div>Content</div>
        </MainLayout>
      );

      const wrapper = container.firstChild as HTMLElement;
      const children = wrapper.children;

      // header, main, footer
      expect(children[0].tagName).toBe('HEADER');
      expect(children[1].tagName).toBe('MAIN');
      expect(children[2].tagName).toBe('FOOTER');
    });

    it('children are wrapped in Container', () => {
      render(
        <MainLayout>
          <span data-testid="test-child">Test</span>
        </MainLayout>
      );

      const main = screen.getByRole('main');
      const container = main.querySelector('.max-w-5xl');
      expect(container).toBeInTheDocument();
    });
  });

  describe('Styling', () => {
    it('wrapper has min-h-screen', () => {
      const { container } = render(
        <MainLayout>
          <div>Content</div>
        </MainLayout>
      );

      const wrapper = container.firstChild as HTMLElement;
      expect(wrapper.className).toContain('min-h-screen');
    });

    it('wrapper uses flexbox column', () => {
      const { container } = render(
        <MainLayout>
          <div>Content</div>
        </MainLayout>
      );

      const wrapper = container.firstChild as HTMLElement;
      expect(wrapper.className).toContain('flex');
      expect(wrapper.className).toContain('flex-col');
    });

    it('main has flex-1 for growth', () => {
      render(
        <MainLayout>
          <div>Content</div>
        </MainLayout>
      );

      const main = screen.getByRole('main');
      expect(main.className).toContain('flex-1');
    });

    it('has gray background', () => {
      const { container } = render(
        <MainLayout>
          <div>Content</div>
        </MainLayout>
      );

      const wrapper = container.firstChild as HTMLElement;
      expect(wrapper.className).toContain('bg-gray-50');
    });

    it('main has top padding for fixed header', () => {
      render(
        <MainLayout>
          <div>Content</div>
        </MainLayout>
      );

      const main = screen.getByRole('main');
      expect(main.className).toContain('pt-20');
    });
  });

  describe('Integration', () => {
    it('displays app title from Header', () => {
      render(
        <MainLayout>
          <div>Content</div>
        </MainLayout>
      );

      expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('Paradise JSON Sync');
    });

    it('displays footer links', () => {
      render(
        <MainLayout>
          <div>Content</div>
        </MainLayout>
      );

      expect(screen.getByRole('link', { name: /ayuda/i })).toBeInTheDocument();
      expect(screen.getByRole('link', { name: /documentación/i })).toBeInTheDocument();
    });

    it('renders complex children', () => {
      render(
        <MainLayout>
          <div>
            <h2>Section Title</h2>
            <p>Paragraph text</p>
            <button>Action Button</button>
          </div>
        </MainLayout>
      );

      expect(screen.getByText('Section Title')).toBeInTheDocument();
      expect(screen.getByText('Paragraph text')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: 'Action Button' })).toBeInTheDocument();
    });
  });
});

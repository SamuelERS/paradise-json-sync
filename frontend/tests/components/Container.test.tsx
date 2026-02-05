/**
 * Container Component Tests (Tests del Componente Container)
 *
 * Tests for the Container layout component.
 * Tests para el componente de layout Container.
 */
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { Container } from '../../src/components/layout/Container';

describe('Container', () => {
  describe('Rendering', () => {
    it('renders children correctly', () => {
      render(
        <Container>
          <span data-testid="child">Test content</span>
        </Container>
      );

      expect(screen.getByTestId('child')).toBeInTheDocument();
      expect(screen.getByText('Test content')).toBeInTheDocument();
    });

    it('renders with default lg size', () => {
      const { container } = render(
        <Container>Content</Container>
      );

      const div = container.firstChild as HTMLElement;
      expect(div.className).toContain('max-w-5xl');
    });
  });

  describe('Size Variants', () => {
    it('renders with sm size', () => {
      const { container } = render(
        <Container size="sm">Content</Container>
      );

      const div = container.firstChild as HTMLElement;
      expect(div.className).toContain('max-w-2xl');
    });

    it('renders with md size', () => {
      const { container } = render(
        <Container size="md">Content</Container>
      );

      const div = container.firstChild as HTMLElement;
      expect(div.className).toContain('max-w-3xl');
    });

    it('renders with lg size', () => {
      const { container } = render(
        <Container size="lg">Content</Container>
      );

      const div = container.firstChild as HTMLElement;
      expect(div.className).toContain('max-w-5xl');
    });

    it('renders with xl size', () => {
      const { container } = render(
        <Container size="xl">Content</Container>
      );

      const div = container.firstChild as HTMLElement;
      expect(div.className).toContain('max-w-7xl');
    });
  });

  describe('Custom className', () => {
    it('applies additional className', () => {
      const { container } = render(
        <Container className="custom-class">Content</Container>
      );

      const div = container.firstChild as HTMLElement;
      expect(div.className).toContain('custom-class');
    });

    it('combines size and custom className', () => {
      const { container } = render(
        <Container size="sm" className="my-custom">Content</Container>
      );

      const div = container.firstChild as HTMLElement;
      expect(div.className).toContain('max-w-2xl');
      expect(div.className).toContain('my-custom');
    });
  });

  describe('Base Styles', () => {
    it('includes centering styles', () => {
      const { container } = render(
        <Container>Content</Container>
      );

      const div = container.firstChild as HTMLElement;
      expect(div.className).toContain('mx-auto');
    });

    it('includes responsive padding', () => {
      const { container } = render(
        <Container>Content</Container>
      );

      const div = container.firstChild as HTMLElement;
      expect(div.className).toContain('px-4');
      expect(div.className).toContain('sm:px-6');
      expect(div.className).toContain('lg:px-8');
    });
  });
});

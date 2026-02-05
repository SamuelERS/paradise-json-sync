/**
 * Layout Components Tests (Tests de Componentes de Layout)
 */
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { Header } from '../../src/components/layout/Header';
import { Footer } from '../../src/components/layout/Footer';
import { Container } from '../../src/components/layout/Container';
import { MainLayout } from '../../src/components/layout/MainLayout';

describe('Header', () => {
  it('renders with default title', () => {
    render(<Header />);
    expect(screen.getByText('Paradise JSON Sync')).toBeInTheDocument();
  });

  it('renders with custom title', () => {
    render(<Header title="Custom Title" />);
    expect(screen.getByText('Custom Title')).toBeInTheDocument();
  });

  it('displays version number', () => {
    render(<Header />);
    expect(screen.getByText('v0.1.0')).toBeInTheDocument();
  });
});

describe('Footer', () => {
  it('renders copyright text', () => {
    render(<Footer />);
    expect(screen.getByText(/Paradise JSON Sync/)).toBeInTheDocument();
  });

  it('renders help link', () => {
    render(<Footer />);
    expect(screen.getByText('Ayuda')).toBeInTheDocument();
  });

  it('renders documentation link', () => {
    render(<Footer />);
    expect(screen.getByText('Documentación')).toBeInTheDocument();
  });

  it('displays version', () => {
    render(<Footer />);
    expect(screen.getByText('v0.1.0')).toBeInTheDocument();
  });
});

describe('Container', () => {
  it('renders children', () => {
    render(<Container>Container content</Container>);
    expect(screen.getByText('Container content')).toBeInTheDocument();
  });

  it('applies default large size', () => {
    const { container } = render(<Container>Content</Container>);
    expect(container.firstChild).toHaveClass('max-w-5xl');
  });

  it('applies small size', () => {
    const { container } = render(<Container size="sm">Content</Container>);
    expect(container.firstChild).toHaveClass('max-w-2xl');
  });

  it('applies medium size', () => {
    const { container } = render(<Container size="md">Content</Container>);
    expect(container.firstChild).toHaveClass('max-w-3xl');
  });

  it('applies xl size', () => {
    const { container } = render(<Container size="xl">Content</Container>);
    expect(container.firstChild).toHaveClass('max-w-7xl');
  });

  it('applies custom className', () => {
    const { container } = render(<Container className="py-8">Content</Container>);
    expect(container.firstChild).toHaveClass('py-8');
  });
});

describe('MainLayout', () => {
  it('renders children in main area', () => {
    render(<MainLayout>Main content</MainLayout>);
    expect(screen.getByText('Main content')).toBeInTheDocument();
  });

  it('includes Header component', () => {
    render(<MainLayout>Content</MainLayout>);
    expect(screen.getByText('Paradise JSON Sync')).toBeInTheDocument();
  });

  it('includes Footer component', () => {
    render(<MainLayout>Content</MainLayout>);
    expect(screen.getByText('Ayuda')).toBeInTheDocument();
  });
});

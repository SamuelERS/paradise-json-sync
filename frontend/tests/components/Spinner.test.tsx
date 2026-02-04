/**
 * Spinner Component Tests (Tests del Componente Spinner)
 */
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { Spinner } from '../../src/components/common/Spinner';

describe('Spinner', () => {
  it('renders with default medium size', () => {
    render(<Spinner />);
    const spinner = screen.getByLabelText('Loading');
    expect(spinner).toHaveClass('w-6', 'h-6');
  });

  it('renders with small size', () => {
    render(<Spinner size="sm" />);
    const spinner = screen.getByLabelText('Loading');
    expect(spinner).toHaveClass('w-4', 'h-4');
  });

  it('renders with large size', () => {
    render(<Spinner size="lg" />);
    const spinner = screen.getByLabelText('Loading');
    expect(spinner).toHaveClass('w-8', 'h-8');
  });

  it('applies custom className', () => {
    render(<Spinner className="text-red-500" />);
    const spinner = screen.getByLabelText('Loading');
    expect(spinner).toHaveClass('text-red-500');
  });

  it('has animate-spin class for animation', () => {
    render(<Spinner />);
    const spinner = screen.getByLabelText('Loading');
    expect(spinner).toHaveClass('animate-spin');
  });
});

/**
 * ProgressBar Component Tests (Tests del Componente Barra de Progreso)
 */
import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { ProgressBar } from '../../src/components/common/ProgressBar';

describe('ProgressBar', () => {
  it('renders with correct progress width', () => {
    render(<ProgressBar progress={50} />);
    const progressBar = screen.getByRole('progressbar');
    expect(progressBar).toHaveStyle({ width: '50%' });
  });

  it('clamps progress to 0-100 range', () => {
    const { rerender } = render(<ProgressBar progress={-10} />);
    expect(screen.getByRole('progressbar')).toHaveStyle({ width: '0%' });

    rerender(<ProgressBar progress={150} />);
    expect(screen.getByRole('progressbar')).toHaveStyle({ width: '100%' });
  });

  it('shows percentage when showPercentage is true', () => {
    render(<ProgressBar progress={75} showPercentage />);
    expect(screen.getByText('75%')).toBeInTheDocument();
  });

  it('does not show percentage by default', () => {
    render(<ProgressBar progress={75} />);
    expect(screen.queryByText('75%')).not.toBeInTheDocument();
  });

  it('applies correct status colors', () => {
    const { rerender } = render(<ProgressBar progress={50} status="loading" />);
    expect(screen.getByRole('progressbar')).toHaveClass('bg-primary');

    rerender(<ProgressBar progress={100} status="success" />);
    expect(screen.getByRole('progressbar')).toHaveClass('bg-green-500');

    rerender(<ProgressBar progress={50} status="error" />);
    expect(screen.getByRole('progressbar')).toHaveClass('bg-red-500');
  });

  it('has correct aria attributes', () => {
    render(<ProgressBar progress={60} />);
    const progressBar = screen.getByRole('progressbar');
    expect(progressBar).toHaveAttribute('aria-valuenow', '60');
    expect(progressBar).toHaveAttribute('aria-valuemin', '0');
    expect(progressBar).toHaveAttribute('aria-valuemax', '100');
  });
});

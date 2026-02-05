/**
 * DownloadButton Component Tests (Tests del Componente Botón de Descarga)
 */
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { DownloadButton } from '../../src/components/results/DownloadButton';

describe('DownloadButton', () => {
  it('renders Excel button with correct label', () => {
    render(<DownloadButton type="excel" onClick={vi.fn()} />);
    expect(screen.getByText('Descargar Excel')).toBeInTheDocument();
  });

  it('renders PDF button with correct label', () => {
    render(<DownloadButton type="pdf" onClick={vi.fn()} />);
    expect(screen.getByText('Descargar PDF')).toBeInTheDocument();
  });

  it('applies Excel button styling', () => {
    render(<DownloadButton type="excel" onClick={vi.fn()} />);
    const button = screen.getByRole('button');
    expect(button).toHaveClass('bg-green-600');
  });

  it('applies PDF button styling', () => {
    render(<DownloadButton type="pdf" onClick={vi.fn()} />);
    const button = screen.getByRole('button');
    expect(button).toHaveClass('bg-red-600');
  });

  it('calls onClick when clicked', () => {
    const handleClick = vi.fn();
    render(<DownloadButton type="excel" onClick={handleClick} />);
    fireEvent.click(screen.getByRole('button'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('is disabled when disabled prop is true', () => {
    render(<DownloadButton type="excel" onClick={vi.fn()} disabled />);
    expect(screen.getByRole('button')).toBeDisabled();
  });

  it('is not disabled by default', () => {
    render(<DownloadButton type="excel" onClick={vi.fn()} />);
    expect(screen.getByRole('button')).not.toBeDisabled();
  });
});

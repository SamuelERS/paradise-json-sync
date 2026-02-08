/**
 * ModeToggle Component Tests
 */
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { ModeToggle } from '../../../src/components/purchases/ModeToggle';

describe('ModeToggle', () => {
  it('renders both tabs', () => {
    render(<ModeToggle activeMode="ventas" onModeChange={vi.fn()} />);
    expect(screen.getByText('Facturas Emitidas')).toBeInTheDocument();
    expect(screen.getByText('Facturas Recibidas')).toBeInTheDocument();
  });

  it('applies active styling to ventas tab when ventas is active', () => {
    render(<ModeToggle activeMode="ventas" onModeChange={vi.fn()} />);
    const ventasTab = screen.getByText('Facturas Emitidas');
    const comprasTab = screen.getByText('Facturas Recibidas');
    expect(ventasTab).toHaveClass('bg-blue-600', 'text-white');
    expect(comprasTab).not.toHaveClass('bg-green-700');
  });

  it('applies active styling to compras tab when compras is active', () => {
    render(<ModeToggle activeMode="compras" onModeChange={vi.fn()} />);
    const ventasTab = screen.getByText('Facturas Emitidas');
    const comprasTab = screen.getByText('Facturas Recibidas');
    expect(comprasTab).toHaveClass('bg-green-700', 'text-white');
    expect(ventasTab).not.toHaveClass('bg-blue-600');
  });

  it('calls onModeChange with "compras" when compras tab is clicked', () => {
    const handleChange = vi.fn();
    render(<ModeToggle activeMode="ventas" onModeChange={handleChange} />);
    fireEvent.click(screen.getByText('Facturas Recibidas'));
    expect(handleChange).toHaveBeenCalledWith('compras');
  });

  it('calls onModeChange with "ventas" when ventas tab is clicked', () => {
    const handleChange = vi.fn();
    render(<ModeToggle activeMode="compras" onModeChange={handleChange} />);
    fireEvent.click(screen.getByText('Facturas Emitidas'));
    expect(handleChange).toHaveBeenCalledWith('ventas');
  });
});

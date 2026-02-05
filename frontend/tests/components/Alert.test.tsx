/**
 * Alert Component Tests (Tests del Componente Alerta)
 */
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { Alert } from '../../src/components/common/Alert';

describe('Alert', () => {
  it('renders message correctly', () => {
    render(<Alert type="info" message="Test message" />);
    expect(screen.getByText('Test message')).toBeInTheDocument();
  });

  it('renders title when provided', () => {
    render(<Alert type="info" title="Test Title" message="Test message" />);
    expect(screen.getByText('Test Title')).toBeInTheDocument();
  });

  it('applies info styles', () => {
    render(<Alert type="info" message="Info message" />);
    const alert = screen.getByRole('alert');
    expect(alert).toHaveClass('bg-blue-50', 'border-blue-200');
  });

  it('applies success styles', () => {
    render(<Alert type="success" message="Success message" />);
    const alert = screen.getByRole('alert');
    expect(alert).toHaveClass('bg-green-50', 'border-green-200');
  });

  it('applies warning styles', () => {
    render(<Alert type="warning" message="Warning message" />);
    const alert = screen.getByRole('alert');
    expect(alert).toHaveClass('bg-yellow-50', 'border-yellow-200');
  });

  it('applies error styles', () => {
    render(<Alert type="error" message="Error message" />);
    const alert = screen.getByRole('alert');
    expect(alert).toHaveClass('bg-red-50', 'border-red-200');
  });

  it('shows close button when onClose is provided', () => {
    render(<Alert type="info" message="Test" onClose={vi.fn()} />);
    expect(screen.getByRole('button', { name: 'Cerrar alerta' })).toBeInTheDocument();
  });

  it('does not show close button when onClose is not provided', () => {
    render(<Alert type="info" message="Test" />);
    expect(screen.queryByRole('button')).not.toBeInTheDocument();
  });

  it('calls onClose when close button is clicked', () => {
    const handleClose = vi.fn();
    render(<Alert type="info" message="Test" onClose={handleClose} />);
    fireEvent.click(screen.getByRole('button', { name: 'Cerrar alerta' }));
    expect(handleClose).toHaveBeenCalledTimes(1);
  });
});

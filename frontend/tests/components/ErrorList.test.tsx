/**
 * ErrorList Component Tests (Tests del Componente Lista de Errores)
 */
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { ErrorList } from '../../src/components/results/ErrorList';
import type { FileError } from '../../src/types';

const mockErrors: FileError[] = [
  { fileName: 'error1.json', message: 'Invalid JSON format' },
  { fileName: 'error2.json', message: 'Missing required field' },
  { fileName: 'error3.json', message: 'Parse error', line: 42 },
  { fileName: 'error4.json', message: 'Schema validation failed' },
  { fileName: 'error5.json', message: 'Encoding issue' },
];

describe('ErrorList', () => {
  it('renders nothing when errors array is empty', () => {
    const { container } = render(<ErrorList errors={[]} />);
    expect(container.firstChild).toBeNull();
  });

  it('displays error count', () => {
    render(<ErrorList errors={mockErrors} />);
    expect(screen.getByText('Errores encontrados (5)')).toBeInTheDocument();
  });

  it('shows first 3 errors by default', () => {
    render(<ErrorList errors={mockErrors} />);
    expect(screen.getByText('error1.json')).toBeInTheDocument();
    expect(screen.getByText('error2.json')).toBeInTheDocument();
    expect(screen.getByText('error3.json')).toBeInTheDocument();
    expect(screen.queryByText('error4.json')).not.toBeInTheDocument();
  });

  it('shows expand button when more than 3 errors', () => {
    render(<ErrorList errors={mockErrors} />);
    expect(screen.getByText('Ver 2 errores más')).toBeInTheDocument();
  });

  it('does not show expand button when 3 or fewer errors', () => {
    render(<ErrorList errors={mockErrors.slice(0, 3)} />);
    expect(screen.queryByText(/Ver .* errores más/)).not.toBeInTheDocument();
  });

  it('expands to show all errors when expand button clicked', () => {
    render(<ErrorList errors={mockErrors} />);
    fireEvent.click(screen.getByText('Ver 2 errores más'));
    expect(screen.getByText('error4.json')).toBeInTheDocument();
    expect(screen.getByText('error5.json')).toBeInTheDocument();
  });

  it('shows collapse button after expanding', () => {
    render(<ErrorList errors={mockErrors} />);
    fireEvent.click(screen.getByText('Ver 2 errores más'));
    expect(screen.getByText('Ver menos')).toBeInTheDocument();
  });

  it('collapses when collapse button clicked', () => {
    render(<ErrorList errors={mockErrors} />);
    fireEvent.click(screen.getByText('Ver 2 errores más'));
    fireEvent.click(screen.getByText('Ver menos'));
    expect(screen.queryByText('error4.json')).not.toBeInTheDocument();
  });

  it('displays error messages', () => {
    render(<ErrorList errors={mockErrors.slice(0, 1)} />);
    expect(screen.getByText('Invalid JSON format')).toBeInTheDocument();
  });

  it('displays line number when provided', () => {
    render(<ErrorList errors={[mockErrors[2]]} />);
    expect(screen.getByText('Línea: 42')).toBeInTheDocument();
  });

  it('does not display line number when not provided', () => {
    render(<ErrorList errors={[mockErrors[0]]} />);
    expect(screen.queryByText(/Línea:/)).not.toBeInTheDocument();
  });
});

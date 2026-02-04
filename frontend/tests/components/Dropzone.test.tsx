/**
 * Dropzone Component Tests (Tests del Componente Zona de Arrastre)
 */
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { Dropzone } from '../../src/components/upload/Dropzone';

describe('Dropzone', () => {
  it('renders dropzone with instructions', () => {
    render(<Dropzone onFilesSelected={vi.fn()} />);
    expect(screen.getByText('Arrastra archivos aquí')).toBeInTheDocument();
    expect(screen.getByText(/haz clic para seleccionar/)).toBeInTheDocument();
  });

  it('shows accepted file types', () => {
    render(<Dropzone onFilesSelected={vi.fn()} />);
    expect(screen.getByText('JSON')).toBeInTheDocument();
    expect(screen.getByText('PDF')).toBeInTheDocument();
  });

  it('shows max files limit', () => {
    render(<Dropzone onFilesSelected={vi.fn()} maxFiles={10} />);
    expect(screen.getByText('Max: 10 archivos')).toBeInTheDocument();
  });

  it('is disabled when disabled prop is true', () => {
    render(<Dropzone onFilesSelected={vi.fn()} disabled />);
    const dropzone = screen.getByText('Arrastra archivos aquí').closest('div');
    expect(dropzone?.parentElement).toHaveClass('cursor-not-allowed');
  });

  it('calls onFilesSelected when files are dropped', async () => {
    const handleFilesSelected = vi.fn();
    render(<Dropzone onFilesSelected={handleFilesSelected} />);
    const input = document.querySelector('input[type="file"]') as HTMLInputElement;
    const file = new File(['{}'], 'test.json', { type: 'application/json' });
    Object.defineProperty(input, 'files', { value: [file] });
    fireEvent.change(input);
    await new Promise((resolve) => setTimeout(resolve, 100));
    expect(handleFilesSelected).toHaveBeenCalled();
  });
});

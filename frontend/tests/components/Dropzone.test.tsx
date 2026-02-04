/**
 * Dropzone Component Tests (Tests del Componente Zona de Arrastre)
 */
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

  it('renders with disabled styling when disabled prop is true', () => {
    const { container } = render(<Dropzone onFilesSelected={vi.fn()} disabled />);
    const dropzoneDiv = container.querySelector('.border-dashed');
    expect(dropzoneDiv).toHaveClass('border-gray-200', 'bg-gray-50');
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

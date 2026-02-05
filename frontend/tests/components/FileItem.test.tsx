/**
 * FileItem Component Tests (Tests del Componente Ítem de Archivo)
 */
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { FileItem } from '../../src/components/upload/FileItem';
import type { FileInfo } from '../../src/types';

const createMockFile = (overrides: Partial<FileInfo> = {}): FileInfo => ({
  id: '1',
  file: new File(['{}'], 'test.json', { type: 'application/json' }),
  name: 'test.json',
  size: 1024,
  type: 'json',
  status: 'pending',
  ...overrides,
});

describe('FileItem', () => {
  it('renders file name', () => {
    render(<FileItem file={createMockFile()} onRemove={vi.fn()} />);
    expect(screen.getByText('test.json')).toBeInTheDocument();
  });

  it('renders file size in KB', () => {
    render(<FileItem file={createMockFile({ size: 2048 })} onRemove={vi.fn()} />);
    expect(screen.getByText('2.0 KB')).toBeInTheDocument();
  });

  it('renders file size in MB for large files', () => {
    render(<FileItem file={createMockFile({ size: 1048576 })} onRemove={vi.fn()} />);
    expect(screen.getByText('1.0 MB')).toBeInTheDocument();
  });

  it('renders file size in bytes for small files', () => {
    render(<FileItem file={createMockFile({ size: 500 })} onRemove={vi.fn()} />);
    expect(screen.getByText('500 B')).toBeInTheDocument();
  });

  it('shows pending status', () => {
    render(<FileItem file={createMockFile({ status: 'pending' })} onRemove={vi.fn()} />);
    expect(screen.getByText('Pendiente')).toBeInTheDocument();
  });

  it('shows uploading status', () => {
    render(<FileItem file={createMockFile({ status: 'uploading' })} onRemove={vi.fn()} />);
    expect(screen.getByText('Subiendo')).toBeInTheDocument();
  });

  it('shows success status', () => {
    render(<FileItem file={createMockFile({ status: 'success' })} onRemove={vi.fn()} />);
    expect(screen.getByText('Completado')).toBeInTheDocument();
  });

  it('shows error status', () => {
    render(<FileItem file={createMockFile({ status: 'error' })} onRemove={vi.fn()} />);
    expect(screen.getByText('Error')).toBeInTheDocument();
  });

  it('shows remove button when not uploading', () => {
    render(<FileItem file={createMockFile({ status: 'pending' })} onRemove={vi.fn()} />);
    expect(screen.getByRole('button', { name: /Eliminar archivo/i })).toBeInTheDocument();
  });

  it('hides remove button when uploading', () => {
    render(<FileItem file={createMockFile({ status: 'uploading' })} onRemove={vi.fn()} />);
    expect(screen.queryByRole('button', { name: /Eliminar archivo/i })).not.toBeInTheDocument();
  });

  it('calls onRemove when remove button clicked', () => {
    const handleRemove = vi.fn();
    render(<FileItem file={createMockFile()} onRemove={handleRemove} />);
    fireEvent.click(screen.getByRole('button', { name: /Eliminar archivo/i }));
    expect(handleRemove).toHaveBeenCalledTimes(1);
  });

  it('renders JSON file with green icon', () => {
    const { container } = render(
      <FileItem file={createMockFile({ type: 'json' })} onRemove={vi.fn()} />
    );
    expect(container.querySelector('.bg-green-100')).toBeInTheDocument();
  });

  it('renders PDF file with red icon', () => {
    const { container } = render(
      <FileItem file={createMockFile({ type: 'pdf', name: 'test.pdf' })} onRemove={vi.fn()} />
    );
    expect(container.querySelector('.bg-red-100')).toBeInTheDocument();
  });
});

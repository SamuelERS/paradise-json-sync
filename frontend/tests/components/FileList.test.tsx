/**
 * FileList Component Tests (Tests del Componente Lista de Archivos)
 */
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { FileList } from '../../src/components/upload/FileList';
import type { FileInfo } from '../../src/types';

const mockFiles: FileInfo[] = [
  {
    id: '1',
    file: new File(['{}'], 'test1.json', { type: 'application/json' }),
    name: 'test1.json',
    size: 1024,
    type: 'json',
    status: 'pending',
  },
  {
    id: '2',
    file: new File(['%PDF'], 'test2.pdf', { type: 'application/pdf' }),
    name: 'test2.pdf',
    size: 2048,
    type: 'pdf',
    status: 'success',
  },
];

describe('FileList', () => {
  it('renders nothing when files array is empty', () => {
    const { container } = render(<FileList files={[]} onRemove={vi.fn()} />);
    expect(container.firstChild).toBeNull();
  });

  it('renders file count correctly', () => {
    render(<FileList files={mockFiles} onRemove={vi.fn()} />);
    expect(screen.getByText('Archivos seleccionados (2)')).toBeInTheDocument();
  });

  it('renders file type counts', () => {
    render(<FileList files={mockFiles} onRemove={vi.fn()} />);
    expect(screen.getByText('1 JSON')).toBeInTheDocument();
    expect(screen.getByText('1 PDF')).toBeInTheDocument();
  });

  it('renders all files in the list', () => {
    render(<FileList files={mockFiles} onRemove={vi.fn()} />);
    expect(screen.getByText('test1.json')).toBeInTheDocument();
    expect(screen.getByText('test2.pdf')).toBeInTheDocument();
  });

  it('calls onRemove with correct index when remove button clicked', () => {
    const handleRemove = vi.fn();
    render(<FileList files={mockFiles} onRemove={handleRemove} />);
    const removeButtons = screen.getAllByRole('button', { name: 'Eliminar archivo' });
    fireEvent.click(removeButtons[0]);
    expect(handleRemove).toHaveBeenCalledWith(0);
  });
});

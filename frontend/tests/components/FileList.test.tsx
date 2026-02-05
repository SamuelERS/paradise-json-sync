/**
 * FileList Component Tests (Tests del Componente Lista de Archivos)
 */
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
    // Button aria-label includes filename: "Eliminar archivo test1.json"
    const removeButtons = screen.getAllByRole('button', { name: /Eliminar archivo/i });
    fireEvent.click(removeButtons[0]);
    expect(handleRemove).toHaveBeenCalledWith(0);
  });
});

describe('FileList - Large Lists (Virtualization)', () => {
  // Helper to create many mock files
  const createManyFiles = (count: number): FileInfo[] => {
    return Array.from({ length: count }, (_, i) => ({
      id: `file-${i}`,
      file: new File(['{}'], `test${i}.json`, { type: 'application/json' }),
      name: `test${i}.json`,
      size: 1024 + i,
      type: i % 3 === 0 ? 'pdf' : 'json' as 'pdf' | 'json',
      status: 'pending' as const,
    }));
  };

  it('renders 100 files without crashing', () => {
    const files = createManyFiles(100);
    const { container } = render(<FileList files={files} onRemove={vi.fn()} />);
    expect(container).toBeTruthy();
    expect(screen.getByText('Archivos seleccionados (100)')).toBeInTheDocument();
  });

  it('renders 500 files without crashing', () => {
    const files = createManyFiles(500);
    const { container } = render(<FileList files={files} onRemove={vi.fn()} />);
    expect(container).toBeTruthy();
    expect(screen.getByText('Archivos seleccionados (500)')).toBeInTheDocument();
  });

  it('shows correct file type counts for large lists', () => {
    const files = createManyFiles(300);
    render(<FileList files={files} onRemove={vi.fn()} />);

    // With i % 3 === 0 being PDF, we expect 100 PDFs and 200 JSONs
    expect(screen.getByText('200 JSON')).toBeInTheDocument();
    expect(screen.getByText('100 PDF')).toBeInTheDocument();
  });

  it('uses virtualization for lists over 50 files', () => {
    const files = createManyFiles(100);
    const { container } = render(<FileList files={files} onRemove={vi.fn()} />);

    // With virtualization, not all 100 items should be in the DOM
    // The virtualizer only renders visible items + overscan
    const fileItems = container.querySelectorAll('[class*="rounded-lg"]');

    // Should have significantly fewer DOM elements than files
    // With virtualization: ~10-15 visible + 5 overscan on each side = ~20-25 max
    // Without: would be 100
    expect(fileItems.length).toBeLessThan(50);
  });

  it('renders without virtualization for lists under 50 files', () => {
    const files = createManyFiles(30);
    const { container } = render(<FileList files={files} onRemove={vi.fn()} />);

    // Without virtualization, all items should be in DOM
    // Each FileItem has the file name visible
    expect(screen.getByText('test0.json')).toBeInTheDocument();
    expect(screen.getByText('test29.json')).toBeInTheDocument();
  });

  it('maintains scroll container with max height', () => {
    const files = createManyFiles(200);
    const { container } = render(<FileList files={files} onRemove={vi.fn()} />);

    const scrollContainer = container.querySelector('.max-h-64');
    expect(scrollContainer).toBeTruthy();
  });
});

/**
 * FormatSelector Component Tests
 */
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { FormatSelector } from '../../../src/components/purchases/FormatSelector';

describe('FormatSelector', () => {
  it('renders four format options', () => {
    render(<FormatSelector value="xlsx" onChange={vi.fn()} />);
    expect(screen.getByText('Excel')).toBeInTheDocument();
    expect(screen.getByText('CSV')).toBeInTheDocument();
    expect(screen.getByText('PDF')).toBeInTheDocument();
    expect(screen.getByText('JSON')).toBeInTheDocument();
  });

  it('highlights xlsx as selected by default', () => {
    render(<FormatSelector value="xlsx" onChange={vi.fn()} />);
    const excelButton = screen.getByText('Excel').closest('button');
    expect(excelButton).toHaveClass('border-green-700', 'bg-green-50');
  });

  it('calls onChange with correct format when clicked', () => {
    const handleChange = vi.fn();
    render(<FormatSelector value="xlsx" onChange={handleChange} />);
    fireEvent.click(screen.getByText('CSV'));
    expect(handleChange).toHaveBeenCalledWith('csv');
  });

  it('highlights the selected format', () => {
    render(<FormatSelector value="pdf" onChange={vi.fn()} />);
    const pdfButton = screen.getByText('PDF').closest('button');
    expect(pdfButton).toHaveClass('border-green-700', 'bg-green-50');
    const excelButton = screen.getByText('Excel').closest('button');
    expect(excelButton).not.toHaveClass('border-green-700');
  });

  it('renders the heading', () => {
    render(<FormatSelector value="xlsx" onChange={vi.fn()} />);
    expect(screen.getByText('Formato de salida')).toBeInTheDocument();
  });
});

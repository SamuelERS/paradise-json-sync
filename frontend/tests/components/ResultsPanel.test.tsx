/**
 * ResultsPanel Component Tests (Tests del Componente Panel de Resultados)
 */
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { ResultsPanel } from '../../src/components/results/ResultsPanel';
import type { ProcessResults } from '../../src/types';

const mockResults: ProcessResults = {
  totalFiles: 5,
  successCount: 4,
  errorCount: 1,
  errors: [
    { fileName: 'error.json', message: 'Invalid JSON format' },
  ],
  outputUrl: '/download/result.xlsx',
  duration: 1500,
};

const defaultProps = {
  onDownloadExcel: vi.fn(),
  onDownloadPdf: vi.fn(),
  onReset: vi.fn(),
};

describe('ResultsPanel', () => {
  it('renders nothing when status is pending', () => {
    const { container } = render(
      <ResultsPanel status="pending" {...defaultProps} />
    );
    expect(container.firstChild).toBeNull();
  });

  it('renders nothing when status is processing', () => {
    const { container } = render(
      <ResultsPanel status="processing" {...defaultProps} />
    );
    expect(container.firstChild).toBeNull();
  });

  it('shows success message when completed without errors', () => {
    const results: ProcessResults = {
      ...mockResults,
      errorCount: 0,
      errors: [],
    };
    render(<ResultsPanel status="completed" results={results} {...defaultProps} />);
    expect(screen.getByText('Procesamiento completado')).toBeInTheDocument();
  });

  it('shows warning message when completed with errors', () => {
    render(<ResultsPanel status="completed" results={mockResults} {...defaultProps} />);
    expect(screen.getByText('Procesamiento con errores')).toBeInTheDocument();
  });

  it('displays file counts', () => {
    render(<ResultsPanel status="completed" results={mockResults} {...defaultProps} />);
    expect(screen.getByText('5 archivos procesados')).toBeInTheDocument();
    expect(screen.getByText('4 exitosos')).toBeInTheDocument();
    expect(screen.getByText('1 con errores')).toBeInTheDocument();
  });

  it('shows download buttons when there are successful files', () => {
    render(<ResultsPanel status="completed" results={mockResults} {...defaultProps} />);
    expect(screen.getByText('Descargar Excel')).toBeInTheDocument();
    expect(screen.getByText('Descargar PDF')).toBeInTheDocument();
  });

  it('calls download handlers when buttons clicked', () => {
    const onDownloadExcel = vi.fn();
    const onDownloadPdf = vi.fn();
    render(
      <ResultsPanel
        status="completed"
        results={mockResults}
        onDownloadExcel={onDownloadExcel}
        onDownloadPdf={onDownloadPdf}
        onReset={vi.fn()}
      />
    );
    fireEvent.click(screen.getByText('Descargar Excel'));
    expect(onDownloadExcel).toHaveBeenCalled();
    fireEvent.click(screen.getByText('Descargar PDF'));
    expect(onDownloadPdf).toHaveBeenCalled();
  });

  it('calls onReset when reset button clicked', () => {
    const onReset = vi.fn();
    render(
      <ResultsPanel
        status="completed"
        results={mockResults}
        {...defaultProps}
        onReset={onReset}
      />
    );
    fireEvent.click(screen.getByText('Procesar más archivos'));
    expect(onReset).toHaveBeenCalled();
  });

  it('shows error list when there are errors', () => {
    render(<ResultsPanel status="completed" results={mockResults} {...defaultProps} />);
    expect(screen.getByText('error.json')).toBeInTheDocument();
    expect(screen.getByText('Invalid JSON format')).toBeInTheDocument();
  });
});

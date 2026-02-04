/**
 * UploadProgress Component Tests (Tests del Componente Progreso de Carga)
 */
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { UploadProgress } from '../../src/components/upload/UploadProgress';

describe('UploadProgress', () => {
  const defaultProps = {
    totalFiles: 10,
    processedFiles: 5,
    progress: 50,
  };

  it('renders with default uploading status', () => {
    render(<UploadProgress {...defaultProps} />);
    expect(screen.getByText('Subiendo archivos...')).toBeInTheDocument();
  });

  it('displays processing status message', () => {
    render(<UploadProgress {...defaultProps} status="processing" />);
    expect(screen.getByText('Procesando datos...')).toBeInTheDocument();
  });

  it('displays completed status message', () => {
    render(<UploadProgress {...defaultProps} status="completed" progress={100} />);
    expect(screen.getByText('Procesamiento completado')).toBeInTheDocument();
  });

  it('displays error status message', () => {
    render(<UploadProgress {...defaultProps} status="error" />);
    expect(screen.getByText('Error en el procesamiento')).toBeInTheDocument();
  });

  it('shows file count progress', () => {
    render(<UploadProgress {...defaultProps} />);
    expect(screen.getByText('5 de 10 archivos')).toBeInTheDocument();
  });

  it('shows current file name when provided and not completed', () => {
    render(<UploadProgress {...defaultProps} currentFile="test.json" />);
    expect(screen.getByText('test.json')).toBeInTheDocument();
  });

  it('does not show current file when completed', () => {
    render(
      <UploadProgress
        {...defaultProps}
        status="completed"
        currentFile="test.json"
        progress={100}
      />
    );
    expect(screen.queryByText('test.json')).not.toBeInTheDocument();
  });

  it('shows spinner when uploading', () => {
    render(<UploadProgress {...defaultProps} status="uploading" />);
    expect(screen.getByLabelText('Loading')).toBeInTheDocument();
  });

  it('shows spinner when processing', () => {
    render(<UploadProgress {...defaultProps} status="processing" />);
    expect(screen.getByLabelText('Loading')).toBeInTheDocument();
  });

  it('shows success icon when completed', () => {
    const { container } = render(
      <UploadProgress {...defaultProps} status="completed" progress={100} />
    );
    expect(container.querySelector('.bg-green-100')).toBeInTheDocument();
  });

  it('shows error icon when error', () => {
    const { container } = render(<UploadProgress {...defaultProps} status="error" />);
    expect(container.querySelector('.bg-red-100')).toBeInTheDocument();
  });
});

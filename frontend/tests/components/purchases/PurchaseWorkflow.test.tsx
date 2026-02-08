/**
 * PurchaseWorkflow Component Tests
 */
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';

// Mock the hook
const mockReset = vi.fn();
const mockSetUploadData = vi.fn();
const mockStartProcessing = vi.fn();
const mockDownloadResult = vi.fn();
const mockClearError = vi.fn();

let mockWorkflowState = {
  step: 'upload' as 'upload' | 'configure' | 'processing' | 'done',
  uploadData: null as { upload_id: string; file_count: number; json_count: number; pdf_count: number; files: Array<{ filename: string; type: string; path: string }> } | null,
  jobId: null as string | null,
  status: null as { job_id: string; status: string; progress: number; current_step: string; result?: { invoice_count: number; error_count: number; errors: Array<{ file: string; reason: string }>; output_path: string } } | null,
  isUploading: false,
  isProcessing: false,
  uploadProgress: 0,
  processingProgress: 0,
  error: null as string | null,
  uploadFiles: vi.fn(),
  setUploadData: mockSetUploadData,
  startProcessing: mockStartProcessing,
  downloadResult: mockDownloadResult,
  reset: mockReset,
  clearError: mockClearError,
};

vi.mock('../../../src/hooks/usePurchaseWorkflow', () => ({
  usePurchaseWorkflow: () => mockWorkflowState,
}));

vi.mock('../../../src/services/purchaseService', () => ({
  uploadPurchaseFiles: vi.fn(),
  startPurchaseProcessing: vi.fn(),
  getPurchaseStatus: vi.fn(),
  triggerPurchaseDownload: vi.fn(),
}));

import { PurchaseWorkflow } from '../../../src/components/purchases/PurchaseWorkflow';

describe('PurchaseWorkflow', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockWorkflowState = {
      step: 'upload',
      uploadData: null,
      jobId: null,
      status: null,
      isUploading: false,
      isProcessing: false,
      uploadProgress: 0,
      processingProgress: 0,
      error: null,
      uploadFiles: vi.fn(),
      setUploadData: mockSetUploadData,
      startProcessing: mockStartProcessing,
      downloadResult: mockDownloadResult,
      reset: mockReset,
      clearError: mockClearError,
    };
  });

  it('starts at upload step', () => {
    render(<PurchaseWorkflow />);
    expect(screen.getByText('Cargar Facturas de Compra')).toBeInTheDocument();
  });

  it('shows configuration after upload', () => {
    mockWorkflowState.step = 'configure';
    mockWorkflowState.uploadData = {
      upload_id: 'test-123',
      file_count: 3,
      json_count: 2,
      pdf_count: 1,
      files: [],
    };

    render(<PurchaseWorkflow />);
    expect(screen.getByText('Configuración de Exportación')).toBeInTheDocument();
    expect(screen.getByText(/3 archivos cargados/)).toBeInTheDocument();
    expect(screen.getByText('Procesar Facturas')).toBeInTheDocument();
  });

  it('shows column configurator in configure step', () => {
    mockWorkflowState.step = 'configure';
    mockWorkflowState.uploadData = {
      upload_id: 'test-123',
      file_count: 1,
      json_count: 1,
      pdf_count: 0,
      files: [],
    };

    render(<PurchaseWorkflow />);
    expect(screen.getByText('Perfil de columnas')).toBeInTheDocument();
    expect(screen.getByText('Formato de salida')).toBeInTheDocument();
  });

  it('shows progress bar during processing', () => {
    mockWorkflowState.step = 'processing';
    mockWorkflowState.isProcessing = true;
    mockWorkflowState.processingProgress = 45;
    mockWorkflowState.status = {
      job_id: 'job-1',
      status: 'processing',
      progress: 45,
      current_step: 'Extrayendo datos...',
    };

    render(<PurchaseWorkflow />);
    expect(screen.getByText('Procesando Facturas')).toBeInTheDocument();
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
    expect(screen.getByText('Extrayendo datos...')).toBeInTheDocument();
  });

  it('shows results when done', () => {
    mockWorkflowState.step = 'done';
    mockWorkflowState.status = {
      job_id: 'job-1',
      status: 'completed',
      progress: 100,
      current_step: 'completed',
      result: {
        invoice_count: 5,
        error_count: 0,
        errors: [],
        output_path: '/output/result.xlsx',
      },
    };

    render(<PurchaseWorkflow />);
    expect(screen.getByText('Procesamiento Completado')).toBeInTheDocument();
    expect(screen.getByText(/5 facturas procesadas/)).toBeInTheDocument();
    expect(screen.getByText('Descargar Resultado')).toBeInTheDocument();
    expect(screen.getByText('Procesar más archivos')).toBeInTheDocument();
  });

  it('shows errors in done step when there are errors', () => {
    mockWorkflowState.step = 'done';
    mockWorkflowState.status = {
      job_id: 'job-1',
      status: 'completed',
      progress: 100,
      current_step: 'completed',
      result: {
        invoice_count: 3,
        error_count: 1,
        errors: [{ file: 'bad.json', reason: 'Formato inválido' }],
        output_path: '/output/result.xlsx',
      },
    };

    render(<PurchaseWorkflow />);
    expect(screen.getByText('bad.json')).toBeInTheDocument();
    expect(screen.getByText('Formato inválido')).toBeInTheDocument();
  });

  it('calls reset when "Procesar más archivos" is clicked', () => {
    mockWorkflowState.step = 'done';
    mockWorkflowState.status = {
      job_id: 'job-1',
      status: 'completed',
      progress: 100,
      current_step: 'completed',
      result: {
        invoice_count: 5,
        error_count: 0,
        errors: [],
        output_path: '/output/result.xlsx',
      },
    };

    render(<PurchaseWorkflow />);
    fireEvent.click(screen.getByText('Procesar más archivos'));
    expect(mockReset).toHaveBeenCalled();
  });

  it('calls downloadResult when download button is clicked', () => {
    mockWorkflowState.step = 'done';
    mockWorkflowState.status = {
      job_id: 'job-1',
      status: 'completed',
      progress: 100,
      current_step: 'completed',
      result: {
        invoice_count: 5,
        error_count: 0,
        errors: [],
        output_path: '/output/result.xlsx',
      },
    };

    render(<PurchaseWorkflow />);
    fireEvent.click(screen.getByText('Descargar Resultado'));
    expect(mockDownloadResult).toHaveBeenCalled();
  });

  it('shows error alert when error exists', () => {
    mockWorkflowState.error = 'Error de conexión';

    render(<PurchaseWorkflow />);
    expect(screen.getByText('Error de conexión')).toBeInTheDocument();
  });

  it('shows additional options in configure step', () => {
    mockWorkflowState.step = 'configure';
    mockWorkflowState.uploadData = {
      upload_id: 'test-123',
      file_count: 1,
      json_count: 1,
      pdf_count: 0,
      files: [],
    };

    render(<PurchaseWorkflow />);
    expect(screen.getByText('Incluir hoja resumen')).toBeInTheDocument();
    expect(screen.getByText('Incluir detalle de items')).toBeInTheDocument();
  });
});

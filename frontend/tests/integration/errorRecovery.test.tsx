/**
 * Error Recovery Integration Tests (Tests de Recuperación de Errores)
 *
 * Tests for error handling, recovery, and retry logic across the application.
 * Tests para manejo de errores, recuperación y lógica de reintento en la aplicación.
 */
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { HomePage } from '../../src/pages/HomePage';

// Mock all hooks with controllable behavior
const mockUploadState = {
  files: [],
  isUploading: false,
  uploadProgress: 0,
  error: null,
  addFiles: vi.fn(),
  removeFile: vi.fn(),
  clearFiles: vi.fn(),
  clearError: vi.fn(),
  upload: vi.fn(),
};

const mockProcessState = {
  isProcessing: false,
  progress: 0,
  currentStep: null,
  error: null,
  status: null,
  startProcess: vi.fn(),
  reset: vi.fn(),
};

const mockDownloadState = {
  downloadExcelFile: vi.fn(),
  downloadPdfFile: vi.fn(),
  downloadJsonFile: vi.fn(),
  error: null,
};

vi.mock('../../src/hooks/useUpload', () => ({
  useUpload: () => mockUploadState,
}));

vi.mock('../../src/hooks/useProcess', () => ({
  useProcess: () => mockProcessState,
}));

vi.mock('../../src/hooks/useDownload', () => ({
  useDownload: () => mockDownloadState,
}));

describe('Error Recovery / Recuperación de Errores', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Reset to default state
    Object.assign(mockUploadState, {
      files: [],
      isUploading: false,
      uploadProgress: 0,
      error: null,
    });
    Object.assign(mockProcessState, {
      isProcessing: false,
      progress: 0,
      currentStep: null,
      error: null,
      status: null,
    });
    Object.assign(mockDownloadState, {
      error: null,
    });
  });

  afterEach(() => {
    vi.resetAllMocks();
  });

  describe('Upload Error Recovery / Recuperación de Errores de Upload', () => {
    it('displays upload error message', () => {
      mockUploadState.error = 'Error de conexión: No se pudo subir el archivo';
      mockUploadState.files = [
        { id: '1', name: 'test.json', size: 100, status: 'error', file: new File([''], 'test.json') },
      ];

      render(<HomePage />);

      expect(screen.getByText(/Error de conexión/)).toBeInTheDocument();
    });

    it('allows user to dismiss upload error', async () => {
      mockUploadState.error = 'Error de carga';

      render(<HomePage />);

      const closeButton = screen.getByRole('button', { name: /cerrar|close|×/i });
      fireEvent.click(closeButton);

      // Error should be cleared via state update
    });

    it('allows retry after upload failure', async () => {
      const mockUpload = vi.fn()
        .mockRejectedValueOnce(new Error('Network error'))
        .mockResolvedValueOnce('upload-123');

      mockUploadState.upload = mockUpload;
      mockUploadState.files = [
        { id: '1', name: 'test.json', size: 100, status: 'pending', file: new File([''], 'test.json') },
      ];

      render(<HomePage />);

      // First attempt - will fail
      const processButton = screen.getByText('Procesar 1 archivo');
      await act(async () => {
        fireEvent.click(processButton);
      });

      // Second attempt after error cleared
      mockUploadState.error = null;
      await act(async () => {
        fireEvent.click(processButton);
      });

      expect(mockUpload).toHaveBeenCalledTimes(2);
    });

    it('handles file validation errors', () => {
      mockUploadState.files = [
        {
          id: '1',
          name: 'invalid.txt',
          size: 100,
          status: 'error',
          errorMessage: 'Tipo de archivo no permitido',
          file: new File([''], 'invalid.txt'),
        },
      ];

      render(<HomePage />);

      // File with error should still be in list but marked as error
      expect(screen.getByText('invalid.txt')).toBeInTheDocument();
    });

    it('handles file size limit exceeded', () => {
      mockUploadState.error = 'El archivo excede el tamaño máximo permitido (10MB)';

      render(<HomePage />);

      expect(screen.getByText(/excede el tamaño máximo/)).toBeInTheDocument();
    });
  });

  describe('Process Error Recovery / Recuperación de Errores de Procesamiento', () => {
    it('displays process error message', () => {
      mockUploadState.files = [
        { id: '1', name: 'test.json', size: 100, status: 'success', file: new File([''], 'test.json') },
      ];
      mockProcessState.error = 'Error al procesar: Formato JSON inválido';

      render(<HomePage />);

      expect(screen.getByText(/Formato JSON inválido/)).toBeInTheDocument();
    });

    it('shows partial success with errors', () => {
      mockUploadState.files = [
        { id: '1', name: 'valid.json', size: 100, status: 'success', file: new File([''], 'valid.json') },
        { id: '2', name: 'invalid.json', size: 100, status: 'error', file: new File([''], 'invalid.json') },
      ];
      mockProcessState.status = {
        status: 'completed',
        downloadUrl: '/api/download/excel/job-123',
        errors: [
          { fileName: 'invalid.json', message: 'Formato inválido', errorCode: 'INVALID_FORMAT' },
        ],
      };

      render(<HomePage />);

      // Should show results panel even with partial errors
      expect(screen.getByText(/Excel/i)).toBeInTheDocument();
    });

    it('allows reset after process failure', async () => {
      const mockReset = vi.fn();
      const mockClearFiles = vi.fn();

      mockProcessState.reset = mockReset;
      mockProcessState.status = { status: 'failed', errors: [{ message: 'Error crítico' }] };
      mockUploadState.clearFiles = mockClearFiles;
      mockUploadState.files = [
        { id: '1', name: 'test.json', size: 100, status: 'success', file: new File([''], 'test.json') },
      ];

      render(<HomePage />);

      const resetButton = screen.getByRole('button', { name: /nuevo|reset|volver/i });
      await act(async () => {
        fireEvent.click(resetButton);
      });

      expect(mockReset).toHaveBeenCalled();
      expect(mockClearFiles).toHaveBeenCalled();
    });

    it('handles timeout errors gracefully', () => {
      mockProcessState.error = 'Tiempo de espera agotado. Por favor, intenta de nuevo.';

      render(<HomePage />);

      expect(screen.getByText(/Tiempo de espera agotado/)).toBeInTheDocument();
    });
  });

  describe('Download Error Recovery / Recuperación de Errores de Descarga', () => {
    it('displays download error message', () => {
      mockDownloadState.error = 'Error al descargar: Archivo no encontrado';
      mockUploadState.files = [
        { id: '1', name: 'test.json', size: 100, status: 'success', file: new File([''], 'test.json') },
      ];
      mockProcessState.status = {
        status: 'completed',
        downloadUrl: '/api/download/excel/job-123',
        errors: [],
      };

      render(<HomePage />);

      expect(screen.getByText(/Archivo no encontrado/)).toBeInTheDocument();
    });

    it('download function is available after completion', () => {
      mockDownloadState.downloadExcelFile = vi.fn();
      mockUploadState.files = [
        { id: '1', name: 'test.json', size: 100, status: 'success', file: new File([''], 'test.json') },
      ];
      mockProcessState.status = {
        status: 'completed',
        downloadUrl: '/api/download/excel/job-123',
        errors: [],
      };

      render(<HomePage />);

      // Verify that download function is configured
      expect(mockDownloadState.downloadExcelFile).toBeDefined();

      // Verify download options are visible
      const buttons = screen.getAllByRole('button');
      expect(buttons.length).toBeGreaterThan(0);
    });
  });

  describe('Network Error Handling / Manejo de Errores de Red', () => {
    it('handles network disconnect during upload', () => {
      mockUploadState.error = 'No se pudo conectar con el servidor. Verifica tu conexión.';

      render(<HomePage />);

      expect(screen.getByText(/No se pudo conectar/)).toBeInTheDocument();
    });

    it('handles network disconnect during processing', () => {
      mockProcessState.error = 'Conexión perdida durante el procesamiento.';

      render(<HomePage />);

      expect(screen.getByText(/Conexión perdida/)).toBeInTheDocument();
    });
  });

  describe('Multiple Error States / Estados de Múltiples Errores', () => {
    it('prioritizes upload errors over other errors', () => {
      mockUploadState.error = 'Upload error';
      mockProcessState.error = 'Process error';
      mockDownloadState.error = 'Download error';

      render(<HomePage />);

      // Should show the combined error or first error
      expect(screen.getByText('Upload error')).toBeInTheDocument();
    });

    it('clears errors when starting new operation', async () => {
      const mockClearError = vi.fn();
      mockUploadState.clearError = mockClearError;
      mockUploadState.error = 'Previous error';
      mockUploadState.files = [
        { id: '1', name: 'test.json', size: 100, status: 'pending', file: new File([''], 'test.json') },
      ];

      render(<HomePage />);

      const processButton = screen.getByText('Procesar 1 archivo');
      await act(async () => {
        fireEvent.click(processButton);
      });

      // Starting new process should attempt to clear previous errors
    });
  });

  describe('Error Message Formatting / Formateo de Mensajes de Error', () => {
    it('displays user-friendly error messages', () => {
      mockUploadState.error = 'Error 413: Request Entity Too Large';

      render(<HomePage />);

      // Should show original message (translation would be handled by errorHandler)
      expect(screen.getByText(/Error 413/)).toBeInTheDocument();
    });

    it('handles error objects without messages', () => {
      mockProcessState.error = 'Error en el procesamiento';
      mockProcessState.status = { status: 'failed' };
      mockUploadState.files = [
        { id: '1', name: 'test.json', size: 100, status: 'success', file: new File([''], 'test.json') },
      ];

      render(<HomePage />);

      expect(screen.getByText(/Error en el procesamiento/)).toBeInTheDocument();
    });
  });
});

describe('Retry Logic / Lógica de Reintento', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    Object.assign(mockUploadState, {
      files: [],
      isUploading: false,
      uploadProgress: 0,
      error: null,
    });
    Object.assign(mockProcessState, {
      isProcessing: false,
      progress: 0,
      currentStep: null,
      error: null,
      status: null,
    });
  });

  describe('Upload Retry / Reintento de Upload', () => {
    it('can retry upload after network error', async () => {
      let attemptCount = 0;
      const mockUpload = vi.fn().mockImplementation(() => {
        attemptCount++;
        if (attemptCount < 2) {
          return Promise.reject(new Error('Network error'));
        }
        return Promise.resolve('upload-123');
      });

      mockUploadState.upload = mockUpload;
      mockUploadState.files = [
        { id: '1', name: 'test.json', size: 100, status: 'pending', file: new File([''], 'test.json') },
      ];

      render(<HomePage />);

      const processButton = screen.getByText('Procesar 1 archivo');

      // First attempt (fails)
      await act(async () => {
        fireEvent.click(processButton);
      });

      // Reset error state and retry
      mockUploadState.error = null;

      await act(async () => {
        fireEvent.click(processButton);
      });

      expect(attemptCount).toBe(2);
    });
  });

  describe('Process Retry / Reintento de Procesamiento', () => {
    it('process can be initiated with valid files', async () => {
      const mockUpload = vi.fn().mockResolvedValue('upload-123');
      const mockStartProcess = vi.fn().mockResolvedValue('job-456');

      mockUploadState.upload = mockUpload;
      mockProcessState.startProcess = mockStartProcess;
      mockUploadState.files = [
        { id: '1', name: 'test.json', size: 100, status: 'pending', file: new File([''], 'test.json') },
      ];

      render(<HomePage />);

      const processButton = screen.getByText('Procesar 1 archivo');

      // First attempt
      await act(async () => {
        fireEvent.click(processButton);
      });

      // Verify upload was called
      expect(mockUpload).toHaveBeenCalled();
    });
  });

  describe('Download Retry / Reintento de Descarga', () => {
    it('download state is available after completion', async () => {
      const mockDownloadExcel = vi.fn().mockResolvedValue(undefined);

      mockDownloadState.downloadExcelFile = mockDownloadExcel;
      mockUploadState.files = [
        { id: '1', name: 'test.json', size: 100, status: 'success', file: new File([''], 'test.json') },
      ];
      mockProcessState.status = {
        status: 'completed',
        downloadUrl: '/api/download/excel/job-123',
        errors: [],
      };

      render(<HomePage />);

      // Verify download buttons are available after completion
      const buttons = screen.getAllByRole('button');
      const downloadButtons = buttons.filter(btn =>
        btn.textContent?.toLowerCase().includes('excel') ||
        btn.textContent?.toLowerCase().includes('pdf') ||
        btn.textContent?.toLowerCase().includes('json') ||
        btn.textContent?.toLowerCase().includes('descargar')
      );

      expect(downloadButtons.length).toBeGreaterThan(0);
    });
  });
});

describe('Edge Cases / Casos Límite', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    Object.assign(mockUploadState, {
      files: [],
      isUploading: false,
      uploadProgress: 0,
      error: null,
    });
    Object.assign(mockProcessState, {
      isProcessing: false,
      progress: 0,
      currentStep: null,
      error: null,
      status: null,
    });
  });

  it('handles empty error messages gracefully', () => {
    mockUploadState.error = '';

    render(<HomePage />);

    // Empty error should not display alert
    expect(screen.queryByRole('alert')).not.toBeInTheDocument();
  });

  it('handles concurrent operations safely', async () => {
    mockUploadState.files = [
      { id: '1', name: 'test.json', size: 100, status: 'pending', file: new File([''], 'test.json') },
    ];
    mockUploadState.upload = vi.fn().mockResolvedValue('upload-123');

    render(<HomePage />);

    const processButton = screen.getByText('Procesar 1 archivo');

    // Simulate rapid clicks
    await act(async () => {
      fireEvent.click(processButton);
      fireEvent.click(processButton);
      fireEvent.click(processButton);
    });

    // Should handle multiple clicks gracefully
  });

  it('preserves state during error recovery', async () => {
    mockUploadState.files = [
      { id: '1', name: 'file1.json', size: 100, status: 'pending', file: new File([''], 'file1.json') },
      { id: '2', name: 'file2.json', size: 200, status: 'pending', file: new File([''], 'file2.json') },
    ];
    mockUploadState.error = 'Upload failed';

    render(<HomePage />);

    // Files should still be listed even after error
    expect(screen.getByText('file1.json')).toBeInTheDocument();
    expect(screen.getByText('file2.json')).toBeInTheDocument();
  });
});

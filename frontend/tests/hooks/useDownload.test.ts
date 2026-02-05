/**
 * useDownload Hook Tests / Tests del Hook useDownload
 *
 * EN: Unit tests for the useDownload hook.
 * ES: Tests unitarios para el hook useDownload.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { useDownload } from '../../src/hooks/useDownload';

// EN: Mock downloadService | ES: Mock de downloadService
const mockDownloadExcel = vi.fn();
const mockDownloadPdf = vi.fn();
const mockTriggerDownload = vi.fn();

vi.mock('../../src/services/downloadService', () => ({
  downloadExcel: () => mockDownloadExcel(),
  downloadPdf: () => mockDownloadPdf(),
  triggerDownload: (blob: Blob, filename: string) => mockTriggerDownload(blob, filename),
}));

describe('useDownload Hook / Hook useDownload', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockDownloadExcel.mockResolvedValue(new Blob(['excel data']));
    mockDownloadPdf.mockResolvedValue(new Blob(['pdf data']));
  });

  describe('Initial State / Estado Inicial', () => {
    it('should have correct initial state / debe tener estado inicial correcto', () => {
      const { result } = renderHook(() => useDownload());

      expect(result.current.isDownloading).toBe(false);
      expect(result.current.downloadType).toBeNull();
      expect(result.current.error).toBeNull();
    });
  });

  describe('downloadExcelFile / descargarArchivoExcel', () => {
    it('should download Excel file / debe descargar archivo Excel', async () => {
      const { result } = renderHook(() => useDownload());

      await act(async () => {
        await result.current.downloadExcelFile('job-123');
      });

      expect(mockDownloadExcel).toHaveBeenCalled();
      expect(mockTriggerDownload).toHaveBeenCalled();
    });

    it('should set downloadType to excel / debe establecer downloadType a excel', async () => {
      const { result } = renderHook(() => useDownload());

      act(() => {
        result.current.downloadExcelFile('job-123');
      });

      expect(result.current.downloadType).toBe('excel');
    });

    it('should use custom filename if provided / debe usar nombre personalizado si se provee', async () => {
      const { result } = renderHook(() => useDownload());

      await act(async () => {
        await result.current.downloadExcelFile('job-123', 'custom-name.xlsx');
      });

      expect(mockTriggerDownload).toHaveBeenCalledWith(
        expect.any(Blob),
        'custom-name.xlsx'
      );
    });

    it('should handle download error / debe manejar error de descarga', async () => {
      mockDownloadExcel.mockRejectedValue(new Error('Download failed'));

      const { result } = renderHook(() => useDownload());

      await act(async () => {
        try {
          await result.current.downloadExcelFile('job-123');
        } catch {
          // Expected error
        }
      });

      expect(result.current.error).toBeTruthy();
      expect(result.current.isDownloading).toBe(false);
    });
  });

  describe('downloadPdfFile / descargarArchivoPdf', () => {
    it('should download PDF file / debe descargar archivo PDF', async () => {
      const { result } = renderHook(() => useDownload());

      await act(async () => {
        await result.current.downloadPdfFile('job-123');
      });

      expect(mockDownloadPdf).toHaveBeenCalled();
      expect(mockTriggerDownload).toHaveBeenCalled();
    });

    it('should set downloadType to pdf / debe establecer downloadType a pdf', async () => {
      const { result } = renderHook(() => useDownload());

      act(() => {
        result.current.downloadPdfFile('job-123');
      });

      expect(result.current.downloadType).toBe('pdf');
    });
  });

  describe('clearError / limpiarError', () => {
    it('should clear error state / debe limpiar estado de error', async () => {
      mockDownloadExcel.mockRejectedValue(new Error('Test error'));

      const { result } = renderHook(() => useDownload());

      await act(async () => {
        try {
          await result.current.downloadExcelFile('job-123');
        } catch {
          // Expected
        }
      });

      act(() => {
        result.current.clearError();
      });

      expect(result.current.error).toBeNull();
    });
  });

  describe('reset / reiniciar', () => {
    it('should reset to initial state / debe reiniciar al estado inicial', () => {
      const { result } = renderHook(() => useDownload());

      act(() => {
        result.current.downloadExcelFile('job-123');
      });

      act(() => {
        result.current.reset();
      });

      expect(result.current.isDownloading).toBe(false);
      expect(result.current.downloadType).toBeNull();
      expect(result.current.error).toBeNull();
    });
  });
});

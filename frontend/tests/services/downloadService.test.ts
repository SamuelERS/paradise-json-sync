/**
 * Download Service Tests / Tests del Servicio de Descarga
 *
 * EN: Unit tests for the download service.
 * ES: Tests unitarios para el servicio de descarga.
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import {
  triggerDownload,
  getDownloadUrl,
  getFileMimeType,
} from '../../src/services/downloadService';
import { API_ENDPOINTS } from '../../src/config/constants';

describe('Download Service / Servicio de Descarga', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('triggerDownload / dispararDescarga', () => {
    it('should create and click download link / debe crear y hacer click en enlace de descarga', () => {
      // EN: Mock DOM methods | ES: Mock de métodos DOM
      const mockCreateObjectURL = vi.fn(() => 'blob:mock-url');
      const mockRevokeObjectURL = vi.fn();
      const mockAppendChild = vi.fn();
      const mockRemoveChild = vi.fn();
      const mockClick = vi.fn();

      Object.defineProperty(window.URL, 'createObjectURL', {
        value: mockCreateObjectURL,
        writable: true,
      });
      Object.defineProperty(window.URL, 'revokeObjectURL', {
        value: mockRevokeObjectURL,
        writable: true,
      });

      const mockLink = {
        href: '',
        download: '',
        click: mockClick,
      };

      vi.spyOn(document, 'createElement').mockReturnValue(mockLink as unknown as HTMLAnchorElement);
      vi.spyOn(document.body, 'appendChild').mockImplementation(mockAppendChild);
      vi.spyOn(document.body, 'removeChild').mockImplementation(mockRemoveChild);

      const blob = new Blob(['test'], { type: 'application/json' });
      triggerDownload(blob, 'test.xlsx');

      expect(mockCreateObjectURL).toHaveBeenCalledWith(blob);
      expect(mockClick).toHaveBeenCalled();
      expect(mockLink.download).toBe('test.xlsx');
      expect(mockRevokeObjectURL).toHaveBeenCalledWith('blob:mock-url');
    });

    it('should set correct filename / debe establecer nombre de archivo correcto', () => {
      const mockLink = {
        href: '',
        download: '',
        click: vi.fn(),
      };

      vi.spyOn(document, 'createElement').mockReturnValue(mockLink as unknown as HTMLAnchorElement);
      vi.spyOn(document.body, 'appendChild').mockImplementation(() => mockLink as unknown as HTMLAnchorElement);
      vi.spyOn(document.body, 'removeChild').mockImplementation(() => mockLink as unknown as HTMLAnchorElement);

      const blob = new Blob(['test']);
      triggerDownload(blob, 'custom-filename.pdf');

      expect(mockLink.download).toBe('custom-filename.pdf');
    });
  });

  describe('getDownloadUrl / obtenerUrlDeDescarga', () => {
    it('should return correct Excel URL / debe retornar URL de Excel correcta', () => {
      const url = getDownloadUrl('job-123', 'excel');

      expect(url).toBe(`${API_ENDPOINTS.DOWNLOAD_EXCEL}/job-123`);
    });

    it('should return correct PDF URL / debe retornar URL de PDF correcta', () => {
      const url = getDownloadUrl('job-456', 'pdf');

      expect(url).toBe(`${API_ENDPOINTS.DOWNLOAD_PDF}/job-456`);
    });

    it('should handle different jobIds / debe manejar diferentes jobIds', () => {
      const jobIds = ['abc-123', 'test-job', '12345'];

      jobIds.forEach((jobId) => {
        const excelUrl = getDownloadUrl(jobId, 'excel');
        const pdfUrl = getDownloadUrl(jobId, 'pdf');

        expect(excelUrl).toContain(jobId);
        expect(pdfUrl).toContain(jobId);
      });
    });
  });

  describe('getFileMimeType / obtenerTipoMimeDelArchivo', () => {
    it('should return correct MIME type for Excel / debe retornar tipo MIME correcto para Excel', () => {
      const mimeType = getFileMimeType('excel');

      expect(mimeType).toBe(
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      );
    });

    it('should return correct MIME type for PDF / debe retornar tipo MIME correcto para PDF', () => {
      const mimeType = getFileMimeType('pdf');

      expect(mimeType).toBe('application/pdf');
    });
  });
});

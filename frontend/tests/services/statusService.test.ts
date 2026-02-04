/**
 * Status Service Tests / Tests del Servicio de Estado
 *
 * EN: Unit tests for the status service.
 * ES: Tests unitarios para el servicio de estado.
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import {
  isTerminalStatus,
  getStatusDisplayName,
  StatusResponse,
} from '../../src/services/statusService';

describe('Status Service / Servicio de Estado', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
    vi.clearAllMocks();
  });

  describe('isTerminalStatus / esEstadoTerminal', () => {
    it('should return true for completed status / debe retornar true para estado completado', () => {
      const status: StatusResponse = {
        jobId: 'test-123',
        status: 'completed',
        progress: 100,
        currentStep: 'Completado',
        errors: [],
        downloadUrl: '/download/test-123',
      };

      expect(isTerminalStatus(status)).toBe(true);
    });

    it('should return true for failed status / debe retornar true para estado fallido', () => {
      const status: StatusResponse = {
        jobId: 'test-123',
        status: 'failed',
        progress: 50,
        currentStep: 'Error',
        errors: [{ fileName: 'test.json', errorCode: 'E001', message: 'Error' }],
      };

      expect(isTerminalStatus(status)).toBe(true);
    });

    it('should return false for pending status / debe retornar false para estado pendiente', () => {
      const status: StatusResponse = {
        jobId: 'test-123',
        status: 'pending',
        progress: 0,
        currentStep: 'Esperando',
        errors: [],
      };

      expect(isTerminalStatus(status)).toBe(false);
    });

    it('should return false for processing statuses / debe retornar false para estados de procesamiento', () => {
      const statuses: StatusResponse['status'][] = [
        'validating',
        'extracting',
        'consolidating',
        'generating',
      ];

      statuses.forEach((statusType) => {
        const status: StatusResponse = {
          jobId: 'test-123',
          status: statusType,
          progress: 50,
          currentStep: 'Procesando',
          errors: [],
        };

        expect(isTerminalStatus(status)).toBe(false);
      });
    });
  });

  describe('getStatusDisplayName / obtenerNombreDeVisualizaciónDelEstado', () => {
    it('should return correct name for pending / debe retornar nombre correcto para pendiente', () => {
      expect(getStatusDisplayName('pending')).toBe('Pendiente');
    });

    it('should return correct name for validating / debe retornar nombre correcto para validando', () => {
      expect(getStatusDisplayName('validating')).toBe('Validando archivos');
    });

    it('should return correct name for extracting / debe retornar nombre correcto para extrayendo', () => {
      expect(getStatusDisplayName('extracting')).toBe('Extrayendo datos');
    });

    it('should return correct name for consolidating / debe retornar nombre correcto para consolidando', () => {
      expect(getStatusDisplayName('consolidating')).toBe('Consolidando información');
    });

    it('should return correct name for generating / debe retornar nombre correcto para generando', () => {
      expect(getStatusDisplayName('generating')).toBe('Generando reportes');
    });

    it('should return correct name for completed / debe retornar nombre correcto para completado', () => {
      expect(getStatusDisplayName('completed')).toBe('Completado');
    });

    it('should return correct name for failed / debe retornar nombre correcto para fallido', () => {
      expect(getStatusDisplayName('failed')).toBe('Error');
    });
  });
});

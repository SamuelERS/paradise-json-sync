/**
 * useProcess Hook Tests / Tests del Hook useProcess
 *
 * EN: Unit tests for the useProcess hook.
 * ES: Tests unitarios para el hook useProcess.
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useProcess } from '../../src/hooks/useProcess';

// EN: Mock services | ES: Mock de servicios
vi.mock('../../src/services/processService', () => ({
  startProcess: vi.fn().mockResolvedValue({
    success: true,
    jobId: 'test-job',
    status: 'pending',
    message: 'Processing started',
  }),
  getDefaultOptions: vi.fn(() => ({
    generateExcel: true,
    generatePdf: false,
    sortBy: 'date',
  })),
}));

vi.mock('../../src/services/statusService', () => ({
  pollStatus: vi.fn(() => vi.fn()), // Returns stop function
}));

describe('useProcess Hook / Hook useProcess', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  describe('Initial State / Estado Inicial', () => {
    it('should have correct initial state / debe tener estado inicial correcto', () => {
      const { result } = renderHook(() => useProcess());

      expect(result.current.isProcessing).toBe(false);
      expect(result.current.progress).toBe(0);
      expect(result.current.currentStep).toBe('');
      expect(result.current.error).toBeNull();
      expect(result.current.status).toBeNull();
    });
  });

  describe('startProcess / iniciarProceso', () => {
    it('should set isProcessing to true when started / debe establecer isProcessing a true al iniciar', async () => {
      const { result } = renderHook(() => useProcess());

      await act(async () => {
        result.current.startProcess('test-job-123');
      });

      expect(result.current.isProcessing).toBe(true);
    });

    it('should set initial current step / debe establecer paso actual inicial', async () => {
      const { result } = renderHook(() => useProcess());

      await act(async () => {
        result.current.startProcess('test-job-123');
      });

      expect(result.current.currentStep).toBe('Iniciando procesamiento');
    });
  });

  describe('cancel / cancelar', () => {
    it('should stop processing when cancelled / debe detener procesamiento al cancelar', async () => {
      const { result } = renderHook(() => useProcess());

      await act(async () => {
        result.current.startProcess('test-job-123');
      });

      act(() => {
        result.current.cancel();
      });

      expect(result.current.isProcessing).toBe(false);
      expect(result.current.currentStep).toBe('Cancelado');
    });
  });

  describe('reset / reiniciar', () => {
    it('should reset to initial state / debe reiniciar al estado inicial', async () => {
      const { result } = renderHook(() => useProcess());

      await act(async () => {
        result.current.startProcess('test-job-123');
      });

      act(() => {
        result.current.reset();
      });

      expect(result.current.isProcessing).toBe(false);
      expect(result.current.progress).toBe(0);
      expect(result.current.currentStep).toBe('');
      expect(result.current.error).toBeNull();
    });
  });
});

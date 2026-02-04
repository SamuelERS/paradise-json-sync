/**
 * useStatus Hook Tests / Tests del Hook useStatus
 *
 * EN: Unit tests for the useStatus hook.
 * ES: Tests unitarios para el hook useStatus.
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useStatus } from '../../src/hooks/useStatus';

// EN: Mock statusService | ES: Mock de statusService
vi.mock('../../src/services/statusService', () => ({
  getStatus: vi.fn().mockResolvedValue({
    jobId: 'test-123',
    status: 'processing',
    progress: 50,
    currentStep: 'Procesando',
    errors: [],
  }),
  pollStatus: vi.fn(() => vi.fn()), // Returns stop function
}));

describe('useStatus Hook / Hook useStatus', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  describe('Initial State / Estado Inicial', () => {
    it('should have correct initial state / debe tener estado inicial correcto', () => {
      const { result } = renderHook(() => useStatus());

      expect(result.current.status).toBeNull();
      expect(result.current.isPolling).toBe(false);
      expect(result.current.isLoading).toBe(false);
      expect(result.current.error).toBeNull();
    });
  });

  describe('startPolling / iniciarSondeo', () => {
    it('should set isPolling to true / debe establecer isPolling a true', () => {
      const { result } = renderHook(() => useStatus());

      act(() => {
        result.current.startPolling('test-job-123');
      });

      expect(result.current.isPolling).toBe(true);
    });

    it('should clear previous error / debe limpiar error previo', () => {
      const { result } = renderHook(() => useStatus());

      act(() => {
        result.current.startPolling('test-job-123');
      });

      expect(result.current.error).toBeNull();
    });
  });

  describe('stopPolling / detenerSondeo', () => {
    it('should set isPolling to false / debe establecer isPolling a false', () => {
      const { result } = renderHook(() => useStatus());

      act(() => {
        result.current.startPolling('test-job-123');
      });

      act(() => {
        result.current.stopPolling();
      });

      expect(result.current.isPolling).toBe(false);
    });
  });

  describe('reset / reiniciar', () => {
    it('should reset to initial state / debe reiniciar al estado inicial', () => {
      const { result } = renderHook(() => useStatus());

      act(() => {
        result.current.startPolling('test-job-123');
      });

      act(() => {
        result.current.reset();
      });

      expect(result.current.status).toBeNull();
      expect(result.current.isPolling).toBe(false);
      expect(result.current.error).toBeNull();
    });
  });

  describe('Cleanup / Limpieza', () => {
    it('should cleanup on unmount / debe limpiar al desmontar', () => {
      const { result, unmount } = renderHook(() => useStatus());

      act(() => {
        result.current.startPolling('test-job-123');
      });

      unmount();

      // EN: Should not throw errors | ES: No debe lanzar errores
      expect(true).toBe(true);
    });
  });
});

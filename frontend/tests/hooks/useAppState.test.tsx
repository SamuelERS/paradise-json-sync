/**
 * useAppState Hook Tests / Tests del Hook useAppState
 *
 * EN: Unit tests for the useAppState hook.
 * ES: Tests unitarios para el hook useAppState.
 */
import { describe, it, expect } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import React, { ReactNode } from 'react';
import { useAppState } from '../../src/hooks/useAppState';
import { AppProvider } from '../../src/context/AppProvider';

// EN: Wrapper component for testing | ES: Componente wrapper para testing
const wrapper = ({ children }: { children: ReactNode }) => (
  <AppProvider>{children}</AppProvider>
);

describe('useAppState Hook / Hook useAppState', () => {
  describe('With Provider / Con Provider', () => {
    it('should return state and dispatch / debe retornar state y dispatch', () => {
      const { result } = renderHook(() => useAppState(), { wrapper });

      expect(result.current.state).toBeDefined();
      expect(result.current.dispatch).toBeDefined();
      expect(typeof result.current.dispatch).toBe('function');
    });

    it('should have initial state values / debe tener valores de estado inicial', () => {
      const { result } = renderHook(() => useAppState(), { wrapper });

      expect(result.current.state.status).toBe('idle');
      expect(result.current.state.jobId).toBeNull();
      expect(result.current.state.files).toEqual([]);
      expect(result.current.state.results).toBeNull();
      expect(result.current.state.errors).toEqual([]);
    });

    it('should update state with SET_STATUS / debe actualizar estado con SET_STATUS', () => {
      const { result } = renderHook(() => useAppState(), { wrapper });

      act(() => {
        result.current.dispatch({ type: 'SET_STATUS', payload: 'uploading' });
      });

      expect(result.current.state.status).toBe('uploading');
    });

    it('should update state with SET_JOB_ID / debe actualizar estado con SET_JOB_ID', () => {
      const { result } = renderHook(() => useAppState(), { wrapper });

      act(() => {
        result.current.dispatch({ type: 'SET_JOB_ID', payload: 'test-job-123' });
      });

      expect(result.current.state.jobId).toBe('test-job-123');
    });

    it('should update state with ADD_FILES / debe actualizar estado con ADD_FILES', () => {
      const { result } = renderHook(() => useAppState(), { wrapper });

      const mockFile = {
        id: 'file-1',
        name: 'test.json',
        size: 1024,
        type: 'application/json',
        file: new File([''], 'test.json'),
        status: 'pending' as const,
      };

      act(() => {
        result.current.dispatch({ type: 'ADD_FILES', payload: [mockFile] });
      });

      expect(result.current.state.files).toHaveLength(1);
      expect(result.current.state.files[0].name).toBe('test.json');
    });

    it('should update state with REMOVE_FILE / debe actualizar estado con REMOVE_FILE', () => {
      const { result } = renderHook(() => useAppState(), { wrapper });

      const mockFile = {
        id: 'file-1',
        name: 'test.json',
        size: 1024,
        type: 'application/json',
        file: new File([''], 'test.json'),
        status: 'pending' as const,
      };

      act(() => {
        result.current.dispatch({ type: 'ADD_FILES', payload: [mockFile] });
      });

      act(() => {
        result.current.dispatch({ type: 'REMOVE_FILE', payload: 'file-1' });
      });

      expect(result.current.state.files).toHaveLength(0);
    });

    it('should reset state with RESET / debe reiniciar estado con RESET', () => {
      const { result } = renderHook(() => useAppState(), { wrapper });

      act(() => {
        result.current.dispatch({ type: 'SET_STATUS', payload: 'processing' });
        result.current.dispatch({ type: 'SET_JOB_ID', payload: 'job-123' });
      });

      act(() => {
        result.current.dispatch({ type: 'RESET' });
      });

      expect(result.current.state.status).toBe('idle');
      expect(result.current.state.jobId).toBeNull();
    });
  });

  describe('Without Provider / Sin Provider', () => {
    it('should throw error when used outside provider / debe lanzar error fuera del provider', () => {
      expect(() => {
        renderHook(() => useAppState());
      }).toThrow('useAppState must be used within an AppProvider');
    });
  });
});

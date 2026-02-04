/**
 * App Context Tests / Tests del Contexto de Aplicación
 *
 * EN: Unit tests for the application context and reducer.
 * ES: Tests unitarios para el contexto y reducer de la aplicación.
 */
import { describe, it, expect } from 'vitest';
import React, { ReactNode } from 'react';
import { render, screen } from '@testing-library/react';
import { renderHook, act } from '@testing-library/react';
import { appReducer, initialState, AppState, AppAction } from '../../src/context/AppContext';
import { AppProvider } from '../../src/context/AppProvider';
import { useAppState } from '../../src/hooks/useAppState';

describe('AppContext / Contexto de Aplicación', () => {
  describe('appReducer / reducer de aplicación', () => {
    it('should return initial state for unknown action / debe retornar estado inicial para acción desconocida', () => {
      const state = appReducer(initialState, { type: 'UNKNOWN' } as unknown as AppAction);

      expect(state).toEqual(initialState);
    });

    describe('SET_STATUS', () => {
      it('should update status / debe actualizar estado', () => {
        const state = appReducer(initialState, {
          type: 'SET_STATUS',
          payload: 'uploading',
        });

        expect(state.status).toBe('uploading');
      });
    });

    describe('SET_JOB_ID', () => {
      it('should set job ID / debe establecer ID de trabajo', () => {
        const state = appReducer(initialState, {
          type: 'SET_JOB_ID',
          payload: 'job-123',
        });

        expect(state.jobId).toBe('job-123');
      });

      it('should clear job ID / debe limpiar ID de trabajo', () => {
        const stateWithJob: AppState = { ...initialState, jobId: 'job-123' };
        const state = appReducer(stateWithJob, {
          type: 'SET_JOB_ID',
          payload: null,
        });

        expect(state.jobId).toBeNull();
      });
    });

    describe('ADD_FILES', () => {
      it('should add files to state / debe agregar archivos al estado', () => {
        const mockFile = {
          id: 'file-1',
          name: 'test.json',
          size: 1024,
          type: 'application/json',
          file: new File([''], 'test.json'),
          status: 'pending' as const,
        };

        const state = appReducer(initialState, {
          type: 'ADD_FILES',
          payload: [mockFile],
        });

        expect(state.files).toHaveLength(1);
        expect(state.files[0].name).toBe('test.json');
      });
    });

    describe('REMOVE_FILE', () => {
      it('should remove file by ID / debe remover archivo por ID', () => {
        const stateWithFile: AppState = {
          ...initialState,
          files: [{
            id: 'file-1',
            name: 'test.json',
            size: 1024,
            type: 'application/json',
            file: new File([''], 'test.json'),
            status: 'pending',
          }],
        };

        const state = appReducer(stateWithFile, {
          type: 'REMOVE_FILE',
          payload: 'file-1',
        });

        expect(state.files).toHaveLength(0);
      });
    });

    describe('UPDATE_FILE', () => {
      it('should update file properties / debe actualizar propiedades del archivo', () => {
        const stateWithFile: AppState = {
          ...initialState,
          files: [{
            id: 'file-1',
            name: 'test.json',
            size: 1024,
            type: 'application/json',
            file: new File([''], 'test.json'),
            status: 'pending',
          }],
        };

        const state = appReducer(stateWithFile, {
          type: 'UPDATE_FILE',
          payload: { id: 'file-1', updates: { status: 'success' } },
        });

        expect(state.files[0].status).toBe('success');
      });
    });

    describe('CLEAR_FILES', () => {
      it('should clear all files / debe limpiar todos los archivos', () => {
        const stateWithFiles: AppState = {
          ...initialState,
          files: [
            {
              id: 'file-1',
              name: 'test1.json',
              size: 1024,
              type: 'application/json',
              file: new File([''], 'test1.json'),
              status: 'pending',
            },
            {
              id: 'file-2',
              name: 'test2.json',
              size: 1024,
              type: 'application/json',
              file: new File([''], 'test2.json'),
              status: 'pending',
            },
          ],
        };

        const state = appReducer(stateWithFiles, { type: 'CLEAR_FILES' });

        expect(state.files).toHaveLength(0);
      });
    });

    describe('SET_RESULTS', () => {
      it('should set process results / debe establecer resultados de proceso', () => {
        const results = {
          totalFiles: 5,
          processedFiles: 5,
          totalRecords: 100,
          totalAmount: 5000,
          downloadUrl: '/download/job-123',
          completedAt: '2025-02-04T10:30:00Z',
        };

        const state = appReducer(initialState, {
          type: 'SET_RESULTS',
          payload: results,
        });

        expect(state.results).toEqual(results);
      });
    });

    describe('ADD_ERROR', () => {
      it('should add error to list / debe agregar error a la lista', () => {
        const error = {
          fileName: 'test.json',
          errorCode: 'E001',
          message: 'Invalid format',
        };

        const state = appReducer(initialState, {
          type: 'ADD_ERROR',
          payload: error,
        });

        expect(state.errors).toHaveLength(1);
        expect(state.errors[0]).toEqual(error);
      });
    });

    describe('CLEAR_ERRORS', () => {
      it('should clear all errors / debe limpiar todos los errores', () => {
        const stateWithErrors: AppState = {
          ...initialState,
          errors: [
            { fileName: 'test.json', errorCode: 'E001', message: 'Error 1' },
            { fileName: 'test2.json', errorCode: 'E002', message: 'Error 2' },
          ],
        };

        const state = appReducer(stateWithErrors, { type: 'CLEAR_ERRORS' });

        expect(state.errors).toHaveLength(0);
      });
    });

    describe('RESET', () => {
      it('should reset to initial state / debe reiniciar al estado inicial', () => {
        const modifiedState: AppState = {
          status: 'processing',
          jobId: 'job-123',
          files: [{
            id: 'file-1',
            name: 'test.json',
            size: 1024,
            type: 'application/json',
            file: new File([''], 'test.json'),
            status: 'success',
          }],
          results: {
            totalFiles: 1,
            processedFiles: 1,
            totalRecords: 10,
            totalAmount: 100,
            downloadUrl: '/download',
            completedAt: '2025-02-04',
          },
          errors: [{ fileName: 'x', errorCode: 'E', message: 'err' }],
          lastStatus: null,
        };

        const state = appReducer(modifiedState, { type: 'RESET' });

        expect(state).toEqual(initialState);
      });
    });
  });

  describe('AppProvider / Proveedor de Aplicación', () => {
    it('should render children / debe renderizar hijos', () => {
      render(
        <AppProvider>
          <div data-testid="child">Child Content</div>
        </AppProvider>
      );

      expect(screen.getByTestId('child')).toBeInTheDocument();
    });

    it('should accept initial state override / debe aceptar sobrescritura de estado inicial', () => {
      const wrapper = ({ children }: { children: ReactNode }) => (
        <AppProvider initialStateOverride={{ jobId: 'preset-job' }}>
          {children}
        </AppProvider>
      );

      const { result } = renderHook(() => useAppState(), { wrapper });

      expect(result.current.state.jobId).toBe('preset-job');
    });
  });
});

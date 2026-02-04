/**
 * Error Handler Tests / Tests del Manejador de Errores
 *
 * EN: Unit tests for error handling utilities.
 * ES: Tests unitarios para utilidades de manejo de errores.
 */
import { describe, it, expect, vi } from 'vitest';
import axios, { AxiosError } from 'axios';
import {
  formatErrorMessage,
  isNetworkError,
  AppError,
} from '../../src/utils/errorHandler';

// EN: Helper to create real AxiosError | ES: Helper para crear AxiosError real
function createAxiosError(
  message: string,
  code?: string,
  response?: { data?: { message?: string }; status?: number }
): AxiosError {
  const error = new AxiosError(message, code);
  if (response) {
    error.response = {
      data: response.data || {},
      status: response.status || 500,
      statusText: 'Error',
      headers: {},
      config: {} as AxiosError['config'],
    } as AxiosError['response'];
  }
  return error;
}

describe('Error Handler / Manejador de Errores', () => {
  describe('AppError Class / Clase AppError', () => {
    it('should create error with message / debe crear error con mensaje', () => {
      const error = new AppError('Test error');

      expect(error.message).toBe('Test error');
      expect(error.name).toBe('AppError');
    });

    it('should create error with code / debe crear error con código', () => {
      const error = new AppError('Test error', 'TEST_ERROR');

      expect(error.code).toBe('TEST_ERROR');
    });

    it('should create error with status code / debe crear error con código de estado', () => {
      const error = new AppError('Not found', 'NOT_FOUND', 404);

      expect(error.statusCode).toBe(404);
    });

    it('should create error with details / debe crear error con detalles', () => {
      const details = { field: 'email', reason: 'invalid' };
      const error = new AppError('Validation error', 'VALIDATION', 400, details);

      expect(error.details).toEqual(details);
    });

    it('should have default code / debe tener código por defecto', () => {
      const error = new AppError('Test error');

      expect(error.code).toBe('UNKNOWN_ERROR');
    });
  });

  describe('formatErrorMessage / formatearMensajeDeError', () => {
    it('should format AppError / debe formatear AppError', () => {
      const error = new AppError('Custom error message');
      const message = formatErrorMessage(error);

      expect(message).toBe('Custom error message');
    });

    it('should format standard Error / debe formatear Error estándar', () => {
      const error = new Error('Standard error');
      const message = formatErrorMessage(error);

      expect(message).toBe('Standard error');
    });

    it('should format string error / debe formatear error de cadena', () => {
      const message = formatErrorMessage('String error');

      expect(message).toBe('String error');
    });

    it('should handle unknown error types / debe manejar tipos de error desconocidos', () => {
      const message = formatErrorMessage(null);

      expect(message).toBe('Ocurrió un error inesperado.');
    });

    it('should format AxiosError with response / debe formatear AxiosError con respuesta', () => {
      const axiosError = createAxiosError('Request failed', 'ERR_BAD_REQUEST', {
        data: { message: 'API Error Message' },
        status: 400,
      });

      const message = formatErrorMessage(axiosError);

      expect(message).toBe('API Error Message');
    });

    it('should handle AxiosError without response message / debe manejar AxiosError sin mensaje de respuesta', () => {
      const axiosError = createAxiosError('Network Error');

      const message = formatErrorMessage(axiosError);

      expect(message).toBe('Error de conexión. Verifica tu internet.');
    });
  });

  describe('isNetworkError / esErrorDeRed', () => {
    it('should detect network error from AxiosError / debe detectar error de red de AxiosError', () => {
      const axiosError = createAxiosError('Network Error', 'ERR_NETWORK');

      expect(isNetworkError(axiosError)).toBe(true);
    });

    it('should detect connection aborted / debe detectar conexión abortada', () => {
      const axiosError = createAxiosError('timeout', 'ECONNABORTED');

      expect(isNetworkError(axiosError)).toBe(true);
    });

    it('should detect from error message / debe detectar desde mensaje de error', () => {
      const error = new Error('Network connection failed');

      expect(isNetworkError(error)).toBe(true);
    });

    it('should detect offline error / debe detectar error offline', () => {
      const error = new Error('You are offline');

      expect(isNetworkError(error)).toBe(true);
    });

    it('should return false for non-network errors / debe retornar false para errores no de red', () => {
      const error = new Error('Something went wrong');

      expect(isNetworkError(error)).toBe(false);
    });

    it('should handle non-Error objects / debe manejar objetos no-Error', () => {
      expect(isNetworkError('string error')).toBe(false);
      expect(isNetworkError(null)).toBe(false);
      expect(isNetworkError(undefined)).toBe(false);
    });
  });
});

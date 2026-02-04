/**
 * Error Handler / Manejador de Errores
 *
 * EN: Centralized error handling utilities for API and application errors.
 * ES: Utilidades centralizadas de manejo de errores para errores de API y aplicación.
 */
import { AxiosError } from 'axios';

/**
 * API Error Interface / Interfaz de Error de API
 *
 * EN: Structure of error responses from the API.
 * ES: Estructura de respuestas de error de la API.
 */
export interface ApiErrorResponse {
  message: string;
  code?: string;
  details?: Record<string, unknown>;
}

/**
 * Application Error Class / Clase de Error de Aplicación
 *
 * EN: Custom error class for application-specific errors.
 * ES: Clase de error personalizada para errores específicos de la aplicación.
 */
export class AppError extends Error {
  public readonly code: string;
  public readonly statusCode?: number;
  public readonly details?: Record<string, unknown>;

  constructor(
    message: string,
    code: string = 'UNKNOWN_ERROR',
    statusCode?: number,
    details?: Record<string, unknown>
  ) {
    super(message);
    this.name = 'AppError';
    this.code = code;
    this.statusCode = statusCode;
    this.details = details;
  }
}

/**
 * Handle API Error / Manejar Error de API
 *
 * EN: Transforms an Axios error into an AppError and throws it.
 *     Never returns - always throws an AppError.
 * ES: Transforma un error de Axios en un AppError y lo lanza.
 *     Nunca retorna - siempre lanza un AppError.
 *
 * @param error - The Axios error to handle / El error de Axios a manejar
 * @throws AppError - Always throws an AppError / Siempre lanza un AppError
 */
export function handleApiError(error: AxiosError<ApiErrorResponse>): never {
  if (error.response) {
    const { status, data } = error.response;
    const message = data?.message || getHttpErrorMessage(status);
    const code = data?.code || `HTTP_${status}`;

    throw new AppError(message, code, status, data?.details);
  }

  if (error.request) {
    throw new AppError(
      'No se pudo conectar con el servidor. Por favor, verifica tu conexión.',
      'NETWORK_ERROR'
    );
  }

  throw new AppError(
    error.message || 'Ocurrió un error inesperado.',
    'REQUEST_ERROR'
  );
}

/**
 * Get HTTP Error Message / Obtener Mensaje de Error HTTP
 *
 * EN: Returns a user-friendly message for common HTTP status codes.
 * ES: Retorna un mensaje amigable para códigos de estado HTTP comunes.
 *
 * @param status - HTTP status code / Código de estado HTTP
 * @returns Human-readable error message / Mensaje de error legible
 */
function getHttpErrorMessage(status: number): string {
  const messages: Record<number, string> = {
    400: 'La solicitud contiene datos inválidos.',
    401: 'No tienes autorización para realizar esta acción.',
    403: 'No tienes permiso para acceder a este recurso.',
    404: 'El recurso solicitado no fue encontrado.',
    409: 'Conflicto con el estado actual del recurso.',
    413: 'El archivo es demasiado grande.',
    415: 'Tipo de archivo no soportado.',
    422: 'Los datos enviados no son válidos.',
    429: 'Demasiadas solicitudes. Por favor, espera un momento.',
    500: 'Error interno del servidor.',
    502: 'Error de comunicación con el servidor.',
    503: 'Servicio temporalmente no disponible.',
    504: 'Tiempo de espera agotado.',
  };

  return messages[status] || `Error del servidor (${status}).`;
}

/**
 * Format Error Message / Formatear Mensaje de Error
 *
 * EN: Extracts a user-friendly message from any error type.
 * ES: Extrae un mensaje amigable del usuario de cualquier tipo de error.
 *
 * @param error - Any error object / Cualquier objeto de error
 * @returns User-friendly error message / Mensaje de error amigable
 */
export function formatErrorMessage(error: unknown): string {
  if (error instanceof AppError) {
    return error.message;
  }

  if (error instanceof AxiosError) {
    if (error.response?.data?.message) {
      return error.response.data.message;
    }
    if (isNetworkError(error)) {
      return 'Error de conexión. Verifica tu internet.';
    }
    return error.message;
  }

  if (error instanceof Error) {
    return error.message;
  }

  if (typeof error === 'string') {
    return error;
  }

  return 'Ocurrió un error inesperado.';
}

/**
 * Is Network Error / Es Error de Red
 *
 * EN: Checks if an error is a network-related error.
 * ES: Verifica si un error es un error relacionado con la red.
 *
 * @param error - Any error object / Cualquier objeto de error
 * @returns True if it's a network error / Verdadero si es un error de red
 */
export function isNetworkError(error: unknown): boolean {
  if (error instanceof AxiosError) {
    return (
      error.code === 'ERR_NETWORK' ||
      error.code === 'ECONNABORTED' ||
      error.message === 'Network Error' ||
      !error.response
    );
  }

  if (error instanceof Error) {
    return (
      error.message.toLowerCase().includes('network') ||
      error.message.toLowerCase().includes('connection') ||
      error.message.toLowerCase().includes('offline')
    );
  }

  return false;
}

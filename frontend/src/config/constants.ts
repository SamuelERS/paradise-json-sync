/**
 * Application Constants / Constantes de la Aplicación
 *
 * EN: Central configuration constants for the frontend application.
 *     All API and file handling settings are defined here.
 * ES: Constantes de configuración central para la aplicación frontend.
 *     Todas las configuraciones de API y manejo de archivos se definen aquí.
 */

/**
 * API Base URL / URL Base de la API
 *
 * EN: The base URL for all API requests. Uses environment variable if available.
 *     Empty string uses Vite proxy in development.
 * ES: La URL base para todas las peticiones API. Usa variable de entorno si está disponible.
 *     String vacío usa proxy de Vite en desarrollo.
 */
export const API_BASE_URL: string =
  import.meta.env.VITE_API_URL || '';

/**
 * API Timeout / Tiempo de espera de la API
 *
 * EN: Maximum time in milliseconds to wait for API responses (30 seconds).
 * ES: Tiempo máximo en milisegundos para esperar respuestas de la API (30 segundos).
 */
export const API_TIMEOUT: number = 30000;

/**
 * Accepted File Types / Tipos de Archivo Aceptados
 *
 * EN: List of file extensions that can be uploaded to the system.
 * ES: Lista de extensiones de archivo que pueden subirse al sistema.
 */
export const ACCEPTED_FILE_TYPES: readonly string[] = ['.json', '.pdf'] as const;

/**
 * Maximum File Size / Tamaño Máximo de Archivo
 *
 * EN: Maximum file size in bytes (50MB).
 * ES: Tamaño máximo de archivo en bytes (50MB).
 */
export const MAX_FILE_SIZE: number = 50 * 1024 * 1024;

/**
 * Polling Interval / Intervalo de Sondeo
 *
 * EN: Time in milliseconds between status polling requests (2 seconds).
 * ES: Tiempo en milisegundos entre peticiones de sondeo de estado (2 segundos).
 */
export const POLLING_INTERVAL: number = 2000;

/**
 * API Endpoints / Endpoints de la API
 *
 * EN: All API endpoint paths used by the frontend services.
 * ES: Todas las rutas de endpoints de la API usadas por los servicios del frontend.
 */
export const API_ENDPOINTS = {
  UPLOAD: '/api/upload',
  PROCESS: '/api/process',
  STATUS: '/api/status',
  DOWNLOAD_EXCEL: '/api/download/excel',
  DOWNLOAD_PDF: '/api/download/pdf',
  DOWNLOAD_JSON: '/api/download/json',
} as const;

/**
 * Application Status / Estados de la Aplicación
 *
 * EN: Possible states of the application workflow.
 * ES: Estados posibles del flujo de trabajo de la aplicación.
 */
export const APP_STATUS = {
  IDLE: 'idle',
  UPLOADING: 'uploading',
  PROCESSING: 'processing',
  COMPLETED: 'completed',
  ERROR: 'error',
} as const;

/**
 * Process Status / Estados de Proceso
 *
 * EN: Possible states of the processing job.
 * ES: Estados posibles del trabajo de procesamiento.
 */
export const PROCESS_STATUS = {
  PENDING: 'pending',
  VALIDATING: 'validating',
  EXTRACTING: 'extracting',
  CONSOLIDATING: 'consolidating',
  GENERATING: 'generating',
  COMPLETED: 'completed',
  FAILED: 'failed',
} as const;

/**
 * Type Exports / Exportación de Tipos
 */
export type AppStatusType = (typeof APP_STATUS)[keyof typeof APP_STATUS];
export type ProcessStatusType = (typeof PROCESS_STATUS)[keyof typeof PROCESS_STATUS];

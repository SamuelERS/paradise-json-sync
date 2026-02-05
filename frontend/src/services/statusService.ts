/**
 * Status Service / Servicio de Estado
 *
 * EN: Service for checking and polling job processing status.
 * ES: Servicio para verificar y sondear el estado del procesamiento de trabajos.
 */
import api from './api';
import { API_ENDPOINTS, POLLING_INTERVAL } from '../config/constants';

/**
 * File Error Interface / Interfaz de Error de Archivo
 *
 * EN: Structure for file-specific errors during processing.
 * ES: Estructura para errores específicos de archivo durante el procesamiento.
 */
export interface FileError {
  fileName: string;
  errorCode: string;
  message: string;
  line?: number;
}

/**
 * Backend Status Response / Respuesta del Backend de Estado
 *
 * EN: Actual response structure from the backend status endpoint.
 * ES: Estructura de respuesta real del endpoint de estado del backend.
 */
interface BackendStatusResponse {
  success: boolean;
  data: {
    job_id: string;
    status: string;
    progress: number;
    current_step: string | null;
    result: {
      total_invoices?: number;
      total_amount?: number;
      output_file?: string;
      output_path?: string;
    } | null;
    error: string | null;
    started_at: string;
    completed_at: string | null;
    failed_at: string | null;
  };
}

/**
 * Status Response Interface / Interfaz de Respuesta de Estado
 *
 * EN: Normalized response structure for the frontend.
 * ES: Estructura de respuesta normalizada para el frontend.
 */
export interface StatusResponse {
  jobId: string;
  status: 'pending' | 'validating' | 'extracting' | 'consolidating' | 'generating' | 'completed' | 'failed' | 'processing';
  progress: number;
  currentStep: string;
  errors: FileError[];
  downloadUrl?: string;
  completedAt?: string;
}

/**
 * Stop Polling Function Type / Tipo de Función para Detener Sondeo
 *
 * EN: Function type returned by pollStatus to stop polling.
 * ES: Tipo de función retornado por pollStatus para detener el sondeo.
 */
export type StopPolling = () => void;

/**
 * Status Callback Type / Tipo de Callback de Estado
 *
 * EN: Function type for status update callbacks.
 * ES: Tipo de función para callbacks de actualización de estado.
 */
export type StatusCallback = (status: StatusResponse) => void;

/**
 * Error Callback Type / Tipo de Callback de Error
 *
 * EN: Function type for error callbacks during polling.
 * ES: Tipo de función para callbacks de error durante el sondeo.
 */
export type ErrorCallback = (error: Error) => void;

/**
 * Normalize Backend Status / Normalizar Estado del Backend
 *
 * EN: Converts backend status string to frontend status type.
 * ES: Convierte el string de estado del backend al tipo del frontend.
 */
function normalizeStatus(backendStatus: string): StatusResponse['status'] {
  const statusMap: Record<string, StatusResponse['status']> = {
    pending: 'pending',
    validating: 'validating',
    extracting: 'extracting',
    consolidating: 'consolidating',
    generating: 'generating',
    processing: 'processing',
    completed: 'completed',
    failed: 'failed',
  };
  return statusMap[backendStatus] || 'processing';
}

/**
 * Get Status / Obtener Estado
 *
 * EN: Retrieves the current status of a processing job.
 * ES: Obtiene el estado actual de un trabajo de procesamiento.
 *
 * @param jobId - Job identifier / Identificador del trabajo
 * @returns Promise with status response / Promesa con respuesta de estado
 * @throws Error if status request fails / Error si falla la petición de estado
 */
export async function getStatus(jobId: string): Promise<StatusResponse> {
  const response = await api.get<BackendStatusResponse>(
    `${API_ENDPOINTS.STATUS}/${jobId}`
  );

  // Validar que la respuesta tiene la estructura esperada
  if (!response.data?.data) {
    throw new Error('Formato de respuesta de estado inválido');
  }

  const backendData = response.data.data;

  // EN: Transform backend response to frontend format
  // ES: Transformar respuesta del backend al formato del frontend
  return {
    jobId: backendData.job_id,
    status: normalizeStatus(backendData.status),
    progress: backendData.progress,
    currentStep: backendData.current_step || '',
    errors: backendData.error
      ? [{ fileName: '', errorCode: 'ERROR', message: backendData.error }]
      : [],
    downloadUrl: backendData.result?.output_path
      ? `/api/download/excel/${backendData.job_id}`
      : undefined,
    completedAt: backendData.completed_at || undefined,
  };
}

/**
 * Maximum consecutive errors before stopping polling
 * Máximo de errores consecutivos antes de detener el sondeo
 */
const MAX_CONSECUTIVE_ERRORS = 5;

/**
 * Maximum polling time in milliseconds (1 hour)
 * Tiempo máximo de sondeo en milisegundos (1 hora)
 */
const MAX_POLLING_TIME_MS = 60 * 60 * 1000;

/**
 * Poll Status / Sondear Estado
 *
 * EN: Starts polling for job status at regular intervals.
 *     Returns a function to stop the polling.
 *     Stops automatically after MAX_CONSECUTIVE_ERRORS errors.
 * ES: Inicia el sondeo del estado del trabajo a intervalos regulares.
 *     Retorna una función para detener el sondeo.
 *     Se detiene automáticamente después de MAX_CONSECUTIVE_ERRORS errores.
 *
 * @param jobId - Job identifier / Identificador del trabajo
 * @param callback - Function called with each status update / Función llamada con cada actualización
 * @param onError - Optional error callback / Callback de error opcional
 * @param interval - Polling interval in ms / Intervalo de sondeo en ms
 * @returns Function to stop polling / Función para detener el sondeo
 */
export function pollStatus(
  jobId: string,
  callback: StatusCallback,
  onError?: ErrorCallback,
  interval: number = POLLING_INTERVAL
): StopPolling {
  let isPolling = true;
  let timeoutId: ReturnType<typeof setTimeout> | null = null;
  let consecutiveErrors = 0;
  const startTime = Date.now();

  const stopPolling = (): void => {
    isPolling = false;
    if (timeoutId) {
      clearTimeout(timeoutId);
      timeoutId = null;
    }
  };

  const poll = async (): Promise<void> => {
    if (!isPolling) return;

    // EN: Check maximum polling time
    // ES: Verificar tiempo máximo de sondeo
    if (Date.now() - startTime > MAX_POLLING_TIME_MS) {
      stopPolling();
      if (onError) {
        onError(new Error('Timeout: el procesamiento excedió el tiempo máximo de 1 hora'));
      }
      return;
    }

    try {
      const status = await getStatus(jobId);
      consecutiveErrors = 0; // Reset on success

      callback(status);

      // EN: Stop polling if job is completed or failed
      // ES: Detener sondeo si el trabajo está completado o falló
      if (status.status === 'completed' || status.status === 'failed') {
        stopPolling();
        return;
      }

      // EN: Schedule next poll
      // ES: Programar siguiente sondeo
      if (isPolling) {
        timeoutId = setTimeout(poll, interval);
      }
    } catch (error) {
      consecutiveErrors++;

      // EN: Stop polling after too many consecutive errors
      // ES: Detener sondeo después de demasiados errores consecutivos
      if (consecutiveErrors >= MAX_CONSECUTIVE_ERRORS) {
        stopPolling();
        if (onError && error instanceof Error) {
          onError(
            new Error(
              `Error de conexión: no se pudo obtener el estado después de ${MAX_CONSECUTIVE_ERRORS} intentos. ${error.message}`
            )
          );
        }
        return;
      }

      // EN: Continue polling, will stop after max errors
      // ES: Continuar sondeo, se detendrá después del máximo de errores
      if (isPolling) {
        timeoutId = setTimeout(poll, interval);
      }
    }
  };

  // EN: Start initial poll
  // ES: Iniciar sondeo inicial
  poll();

  // EN: Return stop function
  // ES: Retornar función de detención
  return stopPolling;
}

/**
 * Is Terminal Status / Es Estado Terminal
 *
 * EN: Checks if a status is a terminal state (completed or failed).
 * ES: Verifica si un estado es un estado terminal (completado o fallido).
 *
 * @param status - Status to check / Estado a verificar
 * @returns True if terminal / Verdadero si es terminal
 */
export function isTerminalStatus(status: StatusResponse): boolean {
  return status.status === 'completed' || status.status === 'failed';
}

/**
 * Get Status Display Name / Obtener Nombre de Visualización del Estado
 *
 * EN: Returns a human-readable name for the status.
 * ES: Retorna un nombre legible para el estado.
 *
 * @param status - Status code / Código de estado
 * @returns Display name / Nombre de visualización
 */
export function getStatusDisplayName(status: StatusResponse['status']): string {
  const names: Record<StatusResponse['status'], string> = {
    pending: 'Pendiente',
    validating: 'Validando archivos',
    extracting: 'Extrayendo datos',
    consolidating: 'Consolidando información',
    generating: 'Generando reportes',
    processing: 'Procesando',
    completed: 'Completado',
    failed: 'Error',
  };
  return names[status] || status;
}

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
 * Status Response Interface / Interfaz de Respuesta de Estado
 *
 * EN: Response structure from the status endpoint.
 * ES: Estructura de respuesta del endpoint de estado.
 */
export interface StatusResponse {
  jobId: string;
  status: 'pending' | 'validating' | 'extracting' | 'consolidating' | 'generating' | 'completed' | 'failed';
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
  const response = await api.get<StatusResponse>(
    `${API_ENDPOINTS.STATUS}/${jobId}`
  );
  return response.data;
}

/**
 * Poll Status / Sondear Estado
 *
 * EN: Starts polling for job status at regular intervals.
 *     Returns a function to stop the polling.
 * ES: Inicia el sondeo del estado del trabajo a intervalos regulares.
 *     Retorna una función para detener el sondeo.
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

  const poll = async (): Promise<void> => {
    if (!isPolling) return;

    try {
      const status = await getStatus(jobId);
      callback(status);

      // EN: Stop polling if job is completed or failed
      // ES: Detener sondeo si el trabajo está completado o falló
      if (status.status === 'completed' || status.status === 'failed') {
        isPolling = false;
        return;
      }

      // EN: Schedule next poll
      // ES: Programar siguiente sondeo
      if (isPolling) {
        timeoutId = setTimeout(poll, interval);
      }
    } catch (error) {
      if (onError && error instanceof Error) {
        onError(error);
      }
      // EN: Continue polling even on error
      // ES: Continuar sondeo incluso en error
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
  return (): void => {
    isPolling = false;
    if (timeoutId) {
      clearTimeout(timeoutId);
      timeoutId = null;
    }
  };
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
    completed: 'Completado',
    failed: 'Error',
  };
  return names[status] || status;
}

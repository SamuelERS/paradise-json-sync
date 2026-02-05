/**
 * useStatus Hook / Hook useStatus
 *
 * EN: Custom hook for polling and managing job status.
 * ES: Hook personalizado para sondear y manejar el estado del trabajo.
 */
import { useState, useCallback, useRef, useEffect } from 'react';
import {
  getStatus,
  pollStatus,
  StatusResponse,
  StopPolling,
} from '../services/statusService';
import { formatErrorMessage } from '../utils/errorHandler';
import { POLLING_INTERVAL } from '../config/constants';

/**
 * Status State Interface / Interfaz de Estado de Status
 *
 * EN: Internal state structure for the status hook.
 * ES: Estructura de estado interno para el hook de estado.
 */
interface StatusState {
  status: StatusResponse | null;
  isPolling: boolean;
  isLoading: boolean;
  error: string | null;
}

/**
 * Status Hook Return Type / Tipo de Retorno del Hook de Estado
 *
 * EN: Return type for the useStatus hook.
 * ES: Tipo de retorno para el hook useStatus.
 */
export interface UseStatusReturn {
  /** EN: Current status response | ES: Respuesta de estado actual */
  status: StatusResponse | null;
  /** EN: Whether polling is active | ES: Si el sondeo está activo */
  isPolling: boolean;
  /** EN: Whether loading initial status | ES: Si está cargando estado inicial */
  isLoading: boolean;
  /** EN: Error message if any | ES: Mensaje de error si existe */
  error: string | null;
  /** EN: Fetch status once | ES: Obtener estado una vez */
  fetchStatus: (jobId: string) => Promise<StatusResponse>;
  /** EN: Start polling for status | ES: Iniciar sondeo de estado */
  startPolling: (jobId: string, interval?: number) => void;
  /** EN: Stop polling | ES: Detener sondeo */
  stopPolling: () => void;
  /** EN: Reset state | ES: Reiniciar estado */
  reset: () => void;
}

/**
 * Initial State / Estado Inicial
 */
const initialState: StatusState = {
  status: null,
  isPolling: false,
  isLoading: false,
  error: null,
};

/**
 * useStatus Hook / Hook useStatus
 *
 * EN: Hook for managing job status polling and retrieval.
 *     Supports both one-time fetch and continuous polling.
 * ES: Hook para manejar el sondeo y recuperación del estado del trabajo.
 *     Soporta tanto obtención única como sondeo continuo.
 *
 * @returns Status state and operations / Estado y operaciones de estado
 *
 * @example
 * const { status, startPolling, stopPolling } = useStatus();
 *
 * // Start polling
 * startPolling(jobId);
 *
 * // Check status
 * if (status?.status === 'completed') {
 *   stopPolling();
 * }
 */
export function useStatus(): UseStatusReturn {
  const [state, setState] = useState<StatusState>(initialState);
  const stopPollingRef = useRef<StopPolling | null>(null);
  const isMountedRef = useRef(true);

  /**
   * Cleanup on unmount / Limpieza al desmontar
   */
  useEffect(() => {
    isMountedRef.current = true;
    return () => {
      isMountedRef.current = false;
      if (stopPollingRef.current) {
        stopPollingRef.current();
      }
    };
  }, []);

  /**
   * Handle Status Update / Manejar Actualización de Estado
   *
   * EN: Updates state with new status response.
   * ES: Actualiza estado con nueva respuesta de estado.
   */
  const handleStatusUpdate = useCallback((status: StatusResponse): void => {
    if (!isMountedRef.current) return;

    setState((prev) => ({
      ...prev,
      status,
      error: null,
    }));

    // EN: Stop polling if terminal status
    // ES: Detener sondeo si es estado terminal
    if (status.status === 'completed' || status.status === 'failed') {
      if (stopPollingRef.current) {
        stopPollingRef.current();
        stopPollingRef.current = null;
      }
      setState((prev) => ({ ...prev, isPolling: false }));
    }
  }, []);

  /**
   * Handle Error / Manejar Error
   *
   * EN: Handles errors during status operations.
   * ES: Maneja errores durante operaciones de estado.
   */
  const handleError = useCallback((error: Error): void => {
    if (!isMountedRef.current) return;

    setState((prev) => ({
      ...prev,
      error: formatErrorMessage(error),
    }));
  }, []);

  /**
   * Fetch Status / Obtener Estado
   *
   * EN: Fetches the status once without polling.
   * ES: Obtiene el estado una vez sin sondeo.
   */
  const fetchStatus = useCallback(async (jobId: string): Promise<StatusResponse> => {
    setState((prev) => ({ ...prev, isLoading: true, error: null }));

    try {
      const status = await getStatus(jobId);
      if (isMountedRef.current) {
        setState((prev) => ({
          ...prev,
          status,
          isLoading: false,
        }));
      }
      return status;
    } catch (error) {
      if (isMountedRef.current) {
        setState((prev) => ({
          ...prev,
          isLoading: false,
          error: formatErrorMessage(error),
        }));
      }
      throw error;
    }
  }, []);

  /**
   * Start Polling / Iniciar Sondeo
   *
   * EN: Starts polling for status updates at the specified interval.
   * ES: Inicia el sondeo de actualizaciones de estado al intervalo especificado.
   */
  const startPolling = useCallback(
    (jobId: string, interval: number = POLLING_INTERVAL): void => {
      // EN: Stop any existing polling
      // ES: Detener cualquier sondeo existente
      if (stopPollingRef.current) {
        stopPollingRef.current();
      }

      setState((prev) => ({
        ...prev,
        isPolling: true,
        error: null,
      }));

      stopPollingRef.current = pollStatus(
        jobId,
        handleStatusUpdate,
        handleError,
        interval
      );
    },
    [handleStatusUpdate, handleError]
  );

  /**
   * Stop Polling / Detener Sondeo
   *
   * EN: Stops the current polling operation.
   * ES: Detiene la operación de sondeo actual.
   */
  const stopPolling = useCallback((): void => {
    if (stopPollingRef.current) {
      stopPollingRef.current();
      stopPollingRef.current = null;
    }
    setState((prev) => ({ ...prev, isPolling: false }));
  }, []);

  /**
   * Reset / Reiniciar
   *
   * EN: Resets the hook state to initial values.
   * ES: Reinicia el estado del hook a valores iniciales.
   */
  const reset = useCallback((): void => {
    if (stopPollingRef.current) {
      stopPollingRef.current();
      stopPollingRef.current = null;
    }
    setState(initialState);
  }, []);

  return {
    status: state.status,
    isPolling: state.isPolling,
    isLoading: state.isLoading,
    error: state.error,
    fetchStatus,
    startPolling,
    stopPolling,
    reset,
  };
}

export default useStatus;

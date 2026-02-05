/**
 * useProcess Hook / Hook useProcess
 *
 * EN: Custom hook for managing file processing state and operations.
 * ES: Hook personalizado para manejar el estado y operaciones de procesamiento.
 */
import { useState, useCallback, useRef } from 'react';
import {
  startProcess as startProcessService,
  ProcessOptions,
  getDefaultOptions,
} from '../services/processService';
import {
  pollStatus,
  StatusResponse,
  StopPolling,
} from '../services/statusService';
import { formatErrorMessage } from '../utils/errorHandler';

/**
 * Process State Interface / Interfaz de Estado de Proceso
 *
 * EN: Internal state structure for the process hook.
 * ES: Estructura de estado interno para el hook de proceso.
 */
interface ProcessState {
  isProcessing: boolean;
  progress: number;
  currentStep: string;
  error: string | null;
  status: StatusResponse | null;
}

/**
 * Process Hook Return Type / Tipo de Retorno del Hook de Proceso
 *
 * EN: Return type for the useProcess hook.
 * ES: Tipo de retorno para el hook useProcess.
 */
export interface UseProcessReturn {
  /** EN: Whether processing is in progress | ES: Si el procesamiento está en progreso */
  isProcessing: boolean;
  /** EN: Processing progress (0-100) | ES: Progreso de procesamiento (0-100) */
  progress: number;
  /** EN: Current processing step | ES: Paso de procesamiento actual */
  currentStep: string;
  /** EN: Error message if any | ES: Mensaje de error si existe */
  error: string | null;
  /** EN: Full status response | ES: Respuesta de estado completa */
  status: StatusResponse | null;
  /** EN: Start processing, returns real job_id | ES: Iniciar procesamiento, retorna job_id real */
  startProcess: (uploadId: string, options?: ProcessOptions) => Promise<string>;
  /** EN: Cancel processing | ES: Cancelar procesamiento */
  cancel: () => void;
  /** EN: Reset state | ES: Reiniciar estado */
  reset: () => void;
}

/**
 * Initial State / Estado Inicial
 */
const initialState: ProcessState = {
  isProcessing: false,
  progress: 0,
  currentStep: '',
  error: null,
  status: null,
};

/**
 * useProcess Hook / Hook useProcess
 *
 * EN: Hook for managing file processing workflow.
 *     Starts processing and polls for status updates.
 * ES: Hook para manejar el flujo de trabajo de procesamiento de archivos.
 *     Inicia procesamiento y sondea actualizaciones de estado.
 *
 * @returns Process state and operations / Estado y operaciones de proceso
 *
 * @example
 * const { isProcessing, progress, startProcess, cancel } = useProcess();
 *
 * // Start processing
 * await startProcess(jobId, { generateExcel: true });
 *
 * // Cancel if needed
 * cancel();
 */
export function useProcess(): UseProcessReturn {
  const [state, setState] = useState<ProcessState>(initialState);
  const stopPollingRef = useRef<StopPolling | null>(null);

  /**
   * Handle Status Update / Manejar Actualización de Estado
   *
   * EN: Updates state based on status response.
   * ES: Actualiza estado basado en respuesta de estado.
   */
  const handleStatusUpdate = useCallback((status: StatusResponse): void => {
    setState((prev) => ({
      ...prev,
      status,
      progress: status.progress,
      currentStep: status.currentStep,
      isProcessing: status.status !== 'completed' && status.status !== 'failed',
      error: status.status === 'failed'
        ? status.errors.map((e) => e.message).join(', ') || 'Error en el procesamiento'
        : null,
    }));
  }, []);

  /**
   * Handle Polling Error / Manejar Error de Sondeo
   *
   * EN: Handles errors during status polling. Sets isProcessing to false
   *     so the UI can recover from errors.
   * ES: Maneja errores durante el sondeo de estado. Pone isProcessing en false
   *     para que la UI pueda recuperarse de errores.
   */
  const handlePollingError = useCallback((error: Error): void => {
    setState((prev) => ({
      ...prev,
      isProcessing: false,
      error: formatErrorMessage(error),
    }));
  }, []);

  /**
   * Start Process / Iniciar Proceso
   *
   * EN: Starts the processing job and begins status polling.
   *     Returns the real job_id from the backend.
   * ES: Inicia el trabajo de procesamiento y comienza el sondeo de estado.
   *     Retorna el job_id real del backend.
   */
  const startProcess = useCallback(
    async (uploadId: string, options?: ProcessOptions): Promise<string> => {
      // EN: Cancel any existing polling
      // ES: Cancelar cualquier sondeo existente
      if (stopPollingRef.current) {
        stopPollingRef.current();
        stopPollingRef.current = null;
      }

      setState({
        isProcessing: true,
        progress: 0,
        currentStep: 'Iniciando procesamiento',
        error: null,
        status: null,
      });

      try {
        const processOptions = options || getDefaultOptions();
        // EN: Capture the response to get the real job_id
        // ES: Capturar la respuesta para obtener el job_id real
        const processResponse = await startProcessService(uploadId, processOptions);
        const realJobId = processResponse.jobId;

        // EN: Start polling for status updates using the REAL job_id
        // ES: Iniciar sondeo de actualizaciones de estado usando el job_id REAL
        stopPollingRef.current = pollStatus(
          realJobId,
          handleStatusUpdate,
          handlePollingError
        );

        return realJobId;
      } catch (error) {
        setState((prev) => ({
          ...prev,
          isProcessing: false,
          error: formatErrorMessage(error),
        }));
        throw error;
      }
    },
    [handleStatusUpdate, handlePollingError]
  );

  /**
   * Cancel / Cancelar
   *
   * EN: Cancels the current processing (stops polling).
   * ES: Cancela el procesamiento actual (detiene sondeo).
   */
  const cancel = useCallback((): void => {
    if (stopPollingRef.current) {
      stopPollingRef.current();
      stopPollingRef.current = null;
    }

    setState((prev) => ({
      ...prev,
      isProcessing: false,
      currentStep: 'Cancelado',
    }));
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
    isProcessing: state.isProcessing,
    progress: state.progress,
    currentStep: state.currentStep,
    error: state.error,
    status: state.status,
    startProcess,
    cancel,
    reset,
  };
}

export default useProcess;

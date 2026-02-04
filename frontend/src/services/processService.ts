/**
 * Process Service / Servicio de Proceso
 *
 * EN: Service for handling file processing operations.
 * ES: Servicio para manejar operaciones de procesamiento de archivos.
 */
import api from './api';
import { API_ENDPOINTS } from '../config/constants';

/**
 * Process Options Interface / Interfaz de Opciones de Proceso
 *
 * EN: Configuration options for the processing job.
 * ES: Opciones de configuración para el trabajo de procesamiento.
 */
export interface ProcessOptions {
  /** EN: Generate Excel output | ES: Generar salida Excel */
  generateExcel: boolean;
  /** EN: Generate PDF output | ES: Generar salida PDF */
  generatePdf: boolean;
  /** EN: Sort field for results | ES: Campo de ordenamiento para resultados */
  sortBy: 'date' | 'amount' | 'provider' | 'none';
}

/**
 * Process Response Interface / Interfaz de Respuesta de Proceso
 *
 * EN: Response structure from the process endpoint.
 * ES: Estructura de respuesta del endpoint de proceso.
 */
export interface ProcessResponse {
  success: boolean;
  jobId: string;
  status: string;
  message: string;
  estimatedTime?: number;
}

/**
 * Process Request Interface / Interfaz de Petición de Proceso
 *
 * EN: Request structure for the process endpoint.
 * ES: Estructura de petición para el endpoint de proceso.
 */
interface ProcessRequest {
  jobId: string;
  options: ProcessOptions;
}

/**
 * Start Process / Iniciar Proceso
 *
 * EN: Starts the processing job for uploaded files.
 * ES: Inicia el trabajo de procesamiento para archivos cargados.
 *
 * @param jobId - Job identifier from upload / Identificador del trabajo de carga
 * @param options - Processing options / Opciones de procesamiento
 * @returns Promise with process response / Promesa con respuesta de proceso
 * @throws Error if process fails to start / Error si falla al iniciar proceso
 */
export async function startProcess(
  jobId: string,
  options: ProcessOptions = getDefaultOptions()
): Promise<ProcessResponse> {
  const request: ProcessRequest = {
    jobId,
    options,
  };

  const response = await api.post<ProcessResponse>(
    API_ENDPOINTS.PROCESS,
    request
  );

  return response.data;
}

/**
 * Get Default Options / Obtener Opciones por Defecto
 *
 * EN: Returns the default processing options.
 * ES: Retorna las opciones de procesamiento por defecto.
 *
 * @returns Default process options / Opciones de proceso por defecto
 */
export function getDefaultOptions(): ProcessOptions {
  return {
    generateExcel: true,
    generatePdf: false,
    sortBy: 'date',
  };
}

/**
 * Validate Process Options / Validar Opciones de Proceso
 *
 * EN: Validates that process options are valid.
 * ES: Valida que las opciones de proceso sean válidas.
 *
 * @param options - Options to validate / Opciones a validar
 * @returns True if valid / Verdadero si son válidas
 */
export function validateProcessOptions(options: ProcessOptions): boolean {
  const validSortOptions = ['date', 'amount', 'provider', 'none'];

  if (typeof options.generateExcel !== 'boolean') {
    return false;
  }

  if (typeof options.generatePdf !== 'boolean') {
    return false;
  }

  if (!validSortOptions.includes(options.sortBy)) {
    return false;
  }

  // EN: At least one output format should be selected
  // ES: Al menos un formato de salida debe estar seleccionado
  if (!options.generateExcel && !options.generatePdf) {
    return false;
  }

  return true;
}

/**
 * Merge Process Options / Combinar Opciones de Proceso
 *
 * EN: Merges partial options with defaults.
 * ES: Combina opciones parciales con valores por defecto.
 *
 * @param partial - Partial options / Opciones parciales
 * @returns Complete options / Opciones completas
 */
export function mergeProcessOptions(
  partial: Partial<ProcessOptions>
): ProcessOptions {
  return {
    ...getDefaultOptions(),
    ...partial,
  };
}

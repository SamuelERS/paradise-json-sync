/**
 * Upload Service / Servicio de Carga
 *
 * EN: Service for handling file uploads to the backend API.
 * ES: Servicio para manejar cargas de archivos al API del backend.
 */
import { formDataApi } from './api';
import { API_ENDPOINTS, ACCEPTED_FILE_TYPES } from '../config/constants';
import { validateFiles, ValidationResult } from '../utils/fileUtils';

/**
 * File Detail Interface / Interfaz de Detalle de Archivo
 *
 * EN: Detailed information about an uploaded file.
 * ES: Información detallada sobre un archivo cargado.
 */
export interface FileDetail {
  name: string;
  size: number;
  type: string;
  status: 'accepted' | 'rejected';
  message?: string;
}

/**
 * Upload Response Interface / Interfaz de Respuesta de Carga
 *
 * EN: Response structure from the upload endpoint.
 * ES: Estructura de respuesta del endpoint de carga.
 */
export interface UploadResponse {
  success: boolean;
  jobId: string;
  filesReceived: number;
  filesDetail: FileDetail[];
  message: string;
}

/**
 * Upload Progress Callback / Callback de Progreso de Carga
 *
 * EN: Function type for upload progress updates.
 * ES: Tipo de función para actualizaciones de progreso de carga.
 */
export type UploadProgressCallback = (progress: number) => void;

/**
 * Upload Files / Cargar Archivos
 *
 * EN: Uploads multiple files to the backend API.
 *     Validates files before upload and reports progress.
 * ES: Carga múltiples archivos al API del backend.
 *     Valida archivos antes de cargar y reporta progreso.
 *
 * @param files - Array of files to upload / Array de archivos a cargar
 * @param onProgress - Optional progress callback / Callback de progreso opcional
 * @returns Promise with upload response / Promesa con respuesta de carga
 * @throws Error if validation fails or upload fails / Error si falla validación o carga
 */
export async function uploadFiles(
  files: File[],
  onProgress?: UploadProgressCallback
): Promise<UploadResponse> {
  // EN: Validate files before upload
  // ES: Validar archivos antes de cargar
  const validation = validateFilesForUpload(files);
  if (!validation.isValid) {
    throw new Error(validation.errors.join('\n'));
  }

  // EN: Create FormData with files
  // ES: Crear FormData con archivos
  const formData = new FormData();
  files.forEach((file) => {
    formData.append('files', file);
  });

  // EN: Upload with progress tracking
  // ES: Cargar con seguimiento de progreso
  const response = await formDataApi.post<UploadResponse>(
    API_ENDPOINTS.UPLOAD,
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const progress = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          onProgress(progress);
        }
      },
    }
  );

  return response.data;
}

/**
 * Validate Files For Upload / Validar Archivos para Carga
 *
 * EN: Validates files using the utility function.
 * ES: Valida archivos usando la función utilitaria.
 *
 * @param files - Files to validate / Archivos a validar
 * @returns Validation result / Resultado de validación
 */
export function validateFilesForUpload(files: File[]): ValidationResult {
  return validateFiles(files);
}

/**
 * Get Accepted Types / Obtener Tipos Aceptados
 *
 * EN: Returns the list of accepted file types.
 * ES: Retorna la lista de tipos de archivo aceptados.
 *
 * @returns Array of accepted extensions / Array de extensiones aceptadas
 */
export function getAcceptedTypes(): readonly string[] {
  return ACCEPTED_FILE_TYPES;
}

/**
 * Create Upload Form Data / Crear FormData para Carga
 *
 * EN: Creates a FormData object from files.
 * ES: Crea un objeto FormData a partir de archivos.
 *
 * @param files - Files to include / Archivos a incluir
 * @returns FormData object / Objeto FormData
 */
export function createUploadFormData(files: File[]): FormData {
  const formData = new FormData();
  files.forEach((file) => {
    formData.append('files', file);
  });
  return formData;
}

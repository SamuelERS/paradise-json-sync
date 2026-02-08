/**
 * Purchase Service / Servicio de Compras
 *
 * API service for the purchases module.
 * Servicio de API para el módulo de compras.
 */
import api, { formDataApi } from './api';
import { API_ENDPOINTS } from '../config/constants';
import type {
  PurchaseUploadResponse,
  PurchaseProcessOptions,
  PurchaseStatusResponse,
  PurchaseFormatInfo,
  PurchaseColumnInfo,
} from '../types';
import { triggerDownload } from './downloadService';

/**
 * Upload Purchase Files / Cargar Archivos de Compras
 *
 * Uploads purchase invoice files (JSON/PDF) to the backend.
 */
export async function uploadPurchaseFiles(
  files: File[],
  onProgress?: (progress: number) => void
): Promise<PurchaseUploadResponse> {
  const formData = new FormData();
  files.forEach((file) => {
    formData.append('files', file);
  });

  const response = await formDataApi.post<PurchaseUploadResponse>(
    API_ENDPOINTS.PURCHASES_UPLOAD,
    formData,
    {
      headers: { 'Content-Type': 'multipart/form-data' },
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
 * Start Purchase Processing / Iniciar Procesamiento de Compras
 *
 * Starts processing uploaded purchase files with specified options.
 */
export async function startPurchaseProcessing(
  options: PurchaseProcessOptions
): Promise<{ job_id: string }> {
  const response = await api.post<{ job_id: string }>(
    API_ENDPOINTS.PURCHASES_PROCESS,
    options
  );
  return response.data;
}

/**
 * Get Purchase Status / Obtener Estado de Compras
 *
 * Polls the processing status for a given job.
 */
export async function getPurchaseStatus(
  jobId: string
): Promise<PurchaseStatusResponse> {
  const response = await api.get<PurchaseStatusResponse>(
    `${API_ENDPOINTS.PURCHASES_STATUS}/${jobId}`
  );
  return response.data;
}

/**
 * Download Purchase Result / Descargar Resultado de Compras
 *
 * Downloads the processed result file as a blob.
 */
export async function downloadPurchaseResult(jobId: string): Promise<Blob> {
  const response = await api.get(
    `${API_ENDPOINTS.PURCHASES_DOWNLOAD}/${jobId}`,
    { responseType: 'blob' }
  );
  return response.data;
}

/**
 * Trigger Purchase Download / Disparar Descarga de Compras
 *
 * Downloads and saves the result file in the browser.
 */
export async function triggerPurchaseDownload(
  jobId: string,
  filename: string
): Promise<void> {
  const blob = await downloadPurchaseResult(jobId);
  triggerDownload(blob, filename);
}

/**
 * Get Purchase Formats / Obtener Formatos de Compras
 *
 * Retrieves available output formats.
 */
export async function getPurchaseFormats(): Promise<PurchaseFormatInfo[]> {
  const response = await api.get<PurchaseFormatInfo[]>(
    API_ENDPOINTS.PURCHASES_FORMATS
  );
  return response.data;
}

/**
 * Get Purchase Columns / Obtener Columnas de Compras
 *
 * Retrieves available column definitions.
 */
export async function getPurchaseColumns(): Promise<PurchaseColumnInfo[]> {
  const response = await api.get<PurchaseColumnInfo[]>(
    API_ENDPOINTS.PURCHASES_COLUMNS
  );
  return response.data;
}

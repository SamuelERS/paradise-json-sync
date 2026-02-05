/**
 * Download Service / Servicio de Descarga
 *
 * EN: Service for downloading processed files from the backend.
 * ES: Servicio para descargar archivos procesados del backend.
 */
import api from './api';
import { API_ENDPOINTS } from '../config/constants';

/**
 * Download Type / Tipo de Descarga
 *
 * EN: Available download formats.
 * ES: Formatos de descarga disponibles.
 */
export type DownloadType = 'excel' | 'pdf';

/**
 * Download Excel / Descargar Excel
 *
 * EN: Downloads the Excel file for a completed job.
 * ES: Descarga el archivo Excel para un trabajo completado.
 *
 * @param jobId - Job identifier / Identificador del trabajo
 * @returns Promise with file Blob / Promesa con Blob del archivo
 * @throws Error if download fails / Error si falla la descarga
 */
export async function downloadExcel(jobId: string): Promise<Blob> {
  const response = await api.get(
    `${API_ENDPOINTS.DOWNLOAD_EXCEL}/${jobId}`,
    {
      responseType: 'blob',
    }
  );
  return response.data;
}

/**
 * Download PDF / Descargar PDF
 *
 * EN: Downloads the PDF file for a completed job.
 * ES: Descarga el archivo PDF para un trabajo completado.
 *
 * @param jobId - Job identifier / Identificador del trabajo
 * @returns Promise with file Blob / Promesa con Blob del archivo
 * @throws Error if download fails / Error si falla la descarga
 */
export async function downloadPdf(jobId: string): Promise<Blob> {
  const response = await api.get(
    `${API_ENDPOINTS.DOWNLOAD_PDF}/${jobId}`,
    {
      responseType: 'blob',
    }
  );
  return response.data;
}

/**
 * Trigger Download / Disparar Descarga
 *
 * EN: Triggers a file download in the browser.
 *     Creates a temporary link element and clicks it.
 * ES: Dispara una descarga de archivo en el navegador.
 *     Crea un elemento de enlace temporal y lo hace click.
 *
 * @param blob - File blob to download / Blob del archivo a descargar
 * @param filename - Name for the downloaded file / Nombre para el archivo descargado
 */
export function triggerDownload(blob: Blob, filename: string): void {
  // EN: Create object URL for the blob
  // ES: Crear URL de objeto para el blob
  const url = window.URL.createObjectURL(blob);

  // EN: Create temporary link element
  // ES: Crear elemento de enlace temporal
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;

  // EN: Append to body, click, and remove
  // ES: Agregar al body, hacer click, y remover
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);

  // EN: Revoke object URL to free memory
  // ES: Revocar URL de objeto para liberar memoria
  window.URL.revokeObjectURL(url);
}

/**
 * Download File / Descargar Archivo
 *
 * EN: Downloads and triggers save of a file based on type.
 * ES: Descarga y dispara el guardado de un archivo basado en tipo.
 *
 * @param jobId - Job identifier / Identificador del trabajo
 * @param type - Download type (excel or pdf) / Tipo de descarga (excel o pdf)
 * @param customFilename - Optional custom filename / Nombre de archivo personalizado opcional
 */
export async function downloadFile(
  jobId: string,
  type: DownloadType,
  customFilename?: string
): Promise<void> {
  const blob = type === 'excel'
    ? await downloadExcel(jobId)
    : await downloadPdf(jobId);

  const extension = type === 'excel' ? 'xlsx' : 'pdf';
  const filename = customFilename || `consolidado_${jobId}.${extension}`;

  triggerDownload(blob, filename);
}

/**
 * Get Download URL / Obtener URL de Descarga
 *
 * EN: Constructs the download URL for a file.
 * ES: Construye la URL de descarga para un archivo.
 *
 * @param jobId - Job identifier / Identificador del trabajo
 * @param type - Download type / Tipo de descarga
 * @returns Download URL / URL de descarga
 */
export function getDownloadUrl(jobId: string, type: DownloadType): string {
  const endpoint = type === 'excel'
    ? API_ENDPOINTS.DOWNLOAD_EXCEL
    : API_ENDPOINTS.DOWNLOAD_PDF;
  return `${endpoint}/${jobId}`;
}

/**
 * Get File MIME Type / Obtener Tipo MIME del Archivo
 *
 * EN: Returns the MIME type for a download type.
 * ES: Retorna el tipo MIME para un tipo de descarga.
 *
 * @param type - Download type / Tipo de descarga
 * @returns MIME type string / Cadena de tipo MIME
 */
export function getFileMimeType(type: DownloadType): string {
  return type === 'excel'
    ? 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    : 'application/pdf';
}

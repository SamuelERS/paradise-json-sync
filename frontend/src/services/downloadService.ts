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
export type DownloadType = 'excel' | 'pdf' | 'json';

/**
 * Validate Download Response / Validar Respuesta de Descarga
 *
 * EN: Checks that the response blob is a valid file and not a JSON error.
 *     When responseType is 'blob', error JSON responses become blobs too.
 * ES: Verifica que el blob de respuesta sea un archivo válido y no un error JSON.
 */
async function validateDownloadBlob(blob: Blob, expectedType: string): Promise<Blob> {
  // If the response is JSON when we expected a file, it's likely an error
  if (blob.type === 'application/json' && expectedType !== 'application/json') {
    const text = await blob.text();
    try {
      const errorData = JSON.parse(text) as { message?: string; error?: string };
      throw new Error(errorData.message || errorData.error || 'Error en la descarga del archivo');
    } catch (e) {
      if (e instanceof SyntaxError) {
        throw new Error('Respuesta inesperada del servidor');
      }
      throw e;
    }
  }
  return blob;
}

/**
 * Download Excel / Descargar Excel
 */
export async function downloadExcel(jobId: string): Promise<Blob> {
  const response = await api.get(
    `${API_ENDPOINTS.DOWNLOAD_EXCEL}/${jobId}`,
    { responseType: 'blob' }
  );
  return validateDownloadBlob(response.data, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
}

/**
 * Download PDF / Descargar PDF
 */
export async function downloadPdf(jobId: string): Promise<Blob> {
  const response = await api.get(
    `${API_ENDPOINTS.DOWNLOAD_PDF}/${jobId}`,
    { responseType: 'blob' }
  );
  return validateDownloadBlob(response.data, 'application/pdf');
}

/**
 * Download JSON / Descargar JSON
 */
export async function downloadJson(jobId: string): Promise<Blob> {
  const response = await api.get(
    `${API_ENDPOINTS.DOWNLOAD_JSON}/${jobId}`,
    { responseType: 'blob' }
  );
  return validateDownloadBlob(response.data, 'application/json');
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

  try {
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
  } finally {
    // EN: Always revoke object URL to free memory
    // ES: Siempre revocar URL de objeto para liberar memoria
    window.URL.revokeObjectURL(url);
  }
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
  let blob: Blob;
  let extension: string;

  switch (type) {
    case 'excel':
      blob = await downloadExcel(jobId);
      extension = 'xlsx';
      break;
    case 'pdf':
      blob = await downloadPdf(jobId);
      extension = 'pdf';
      break;
    case 'json':
      blob = await downloadJson(jobId);
      extension = 'json';
      break;
  }

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
  let endpoint: string;
  switch (type) {
    case 'excel':
      endpoint = API_ENDPOINTS.DOWNLOAD_EXCEL;
      break;
    case 'pdf':
      endpoint = API_ENDPOINTS.DOWNLOAD_PDF;
      break;
    case 'json':
      endpoint = API_ENDPOINTS.DOWNLOAD_JSON;
      break;
  }
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
  switch (type) {
    case 'excel':
      return 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';
    case 'pdf':
      return 'application/pdf';
    case 'json':
      return 'application/json';
  }
}

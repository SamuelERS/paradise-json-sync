/**
 * Services Module Exports / Exportaciones del Módulo de Servicios
 *
 * EN: Re-exports all service functions and types.
 * ES: Re-exporta todas las funciones y tipos de servicios.
 */

// API Client / Cliente de API
export { default as api, formDataApi, getApiBaseUrl, getApiTimeout } from './api';

// Upload Service / Servicio de Carga
export {
  uploadFiles,
  validateFilesForUpload,
  getAcceptedTypes,
  createUploadFormData,
} from './uploadService';
export type {
  UploadResponse,
  FileDetail,
  UploadProgressCallback,
} from './uploadService';

// Process Service / Servicio de Proceso
export {
  startProcess,
  getDefaultOptions,
  validateProcessOptions,
  mergeProcessOptions,
} from './processService';
export type { ProcessOptions, ProcessResponse } from './processService';

// Status Service / Servicio de Estado
export {
  getStatus,
  pollStatus,
  isTerminalStatus,
  getStatusDisplayName,
} from './statusService';
export type {
  StatusResponse,
  FileError,
  StopPolling,
  StatusCallback,
  ErrorCallback,
} from './statusService';

// Download Service / Servicio de Descarga
export {
  downloadExcel,
  downloadPdf,
  triggerDownload,
  downloadFile,
  getDownloadUrl,
  getFileMimeType,
} from './downloadService';
export type { DownloadType } from './downloadService';

/**
 * Utils Module Exports / Exportaciones del Módulo de Utilidades
 *
 * EN: Re-exports all utility functions and types.
 * ES: Re-exporta todas las funciones utilitarias y tipos.
 */

// Error Handler / Manejador de Errores
export {
  handleApiError,
  formatErrorMessage,
  isNetworkError,
  AppError,
} from './errorHandler';
export type { ApiErrorResponse } from './errorHandler';

// File Utils / Utilidades de Archivos
export {
  formatFileSize,
  getFileExtension,
  isValidFileType,
  isValidFileSize,
  validateFile,
  validateFiles,
  generateFileId,
  createFileInfo,
  getAcceptedMimeTypes,
} from './fileUtils';
export type { FileInfo, ValidationResult } from './fileUtils';

// Formatters / Formateadores
export {
  formatDate,
  formatDateTime,
  formatCurrency,
  formatPercentage,
  formatNumber,
  formatDuration,
  truncateText,
} from './formatters';

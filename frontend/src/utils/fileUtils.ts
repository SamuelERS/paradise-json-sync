/**
 * File Utilities / Utilidades de Archivos
 *
 * EN: Helper functions for file operations, validation, and formatting.
 * ES: Funciones auxiliares para operaciones de archivo, validación y formateo.
 */
import { ACCEPTED_FILE_TYPES, MAX_FILE_SIZE } from '../config/constants';

/**
 * File Info Interface / Interfaz de Información de Archivo
 *
 * EN: Structure containing file metadata for UI display.
 * ES: Estructura con metadatos del archivo para mostrar en la UI.
 */
export interface FileInfo {
  id: string;
  name: string;
  size: number;
  type: string;
  file: File;
  status: 'pending' | 'uploading' | 'success' | 'error';
  errorMessage?: string;
}

/**
 * Validation Result Interface / Interfaz de Resultado de Validación
 *
 * EN: Result of file validation with error details.
 * ES: Resultado de la validación de archivo con detalles de error.
 */
export interface ValidationResult {
  isValid: boolean;
  errors: string[];
}

/**
 * Format File Size / Formatear Tamaño de Archivo
 *
 * EN: Converts bytes to human-readable format (KB, MB, GB).
 * ES: Convierte bytes a formato legible (KB, MB, GB).
 *
 * @param bytes - Size in bytes / Tamaño en bytes
 * @returns Formatted string / Cadena formateada
 *
 * @example
 * formatFileSize(1024) // "1.00 KB"
 * formatFileSize(1048576) // "1.00 MB"
 */
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes';

  const units = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const k = 1024;
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  const size = bytes / Math.pow(k, i);

  return `${size.toFixed(2)} ${units[i]}`;
}

/**
 * Get File Extension / Obtener Extensión de Archivo
 *
 * EN: Extracts the file extension from a filename (lowercase, with dot).
 * ES: Extrae la extensión del archivo de un nombre de archivo (minúsculas, con punto).
 *
 * @param filename - Name of the file / Nombre del archivo
 * @returns File extension with dot / Extensión del archivo con punto
 *
 * @example
 * getFileExtension("document.pdf") // ".pdf"
 * getFileExtension("data.JSON") // ".json"
 */
export function getFileExtension(filename: string): string {
  const lastDot = filename.lastIndexOf('.');
  if (lastDot === -1) return '';
  return filename.slice(lastDot).toLowerCase();
}

/**
 * Is Valid File Type / Es Tipo de Archivo Válido
 *
 * EN: Checks if a file has an accepted extension.
 * ES: Verifica si un archivo tiene una extensión aceptada.
 *
 * @param file - File to validate / Archivo a validar
 * @param accepted - List of accepted extensions / Lista de extensiones aceptadas
 * @returns True if valid / Verdadero si es válido
 */
export function isValidFileType(
  file: File,
  accepted: readonly string[] = ACCEPTED_FILE_TYPES
): boolean {
  const extension = getFileExtension(file.name);
  return accepted.includes(extension);
}

/**
 * Is Valid File Size / Es Tamaño de Archivo Válido
 *
 * EN: Checks if a file size is within the allowed limit.
 * ES: Verifica si el tamaño del archivo está dentro del límite permitido.
 *
 * @param file - File to validate / Archivo a validar
 * @param maxSize - Maximum size in bytes / Tamaño máximo en bytes
 * @returns True if valid / Verdadero si es válido
 */
export function isValidFileSize(
  file: File,
  maxSize: number = MAX_FILE_SIZE
): boolean {
  return file.size <= maxSize;
}

/**
 * Validate File / Validar Archivo
 *
 * EN: Performs complete validation on a file (type and size).
 * ES: Realiza validación completa en un archivo (tipo y tamaño).
 *
 * @param file - File to validate / Archivo a validar
 * @returns Validation result / Resultado de validación
 */
export function validateFile(file: File): ValidationResult {
  const errors: string[] = [];

  if (!isValidFileType(file)) {
    errors.push(
      `Tipo de archivo no permitido: ${getFileExtension(file.name) || 'sin extensión'}. ` +
      `Tipos aceptados: ${ACCEPTED_FILE_TYPES.join(', ')}`
    );
  }

  if (!isValidFileSize(file)) {
    errors.push(
      `Archivo muy grande: ${formatFileSize(file.size)}. ` +
      `Máximo permitido: ${formatFileSize(MAX_FILE_SIZE)}`
    );
  }

  return {
    isValid: errors.length === 0,
    errors,
  };
}

/**
 * Validate Files / Validar Archivos
 *
 * EN: Validates multiple files and returns combined results.
 * ES: Valida múltiples archivos y retorna resultados combinados.
 *
 * @param files - Array of files to validate / Array de archivos a validar
 * @returns Validation result / Resultado de validación
 */
export function validateFiles(files: File[]): ValidationResult {
  const allErrors: string[] = [];

  files.forEach((file) => {
    const result = validateFile(file);
    if (!result.isValid) {
      allErrors.push(`${file.name}: ${result.errors.join(', ')}`);
    }
  });

  return {
    isValid: allErrors.length === 0,
    errors: allErrors,
  };
}

/**
 * Generate File ID / Generar ID de Archivo
 *
 * EN: Generates a unique identifier for a file.
 * ES: Genera un identificador único para un archivo.
 *
 * @returns Unique file ID / ID único de archivo
 */
export function generateFileId(): string {
  return `file-${Date.now()}-${Math.random().toString(36).substring(2, 11)}`;
}

/**
 * Create File Info / Crear Info de Archivo
 *
 * EN: Creates a FileInfo object from a File.
 * ES: Crea un objeto FileInfo a partir de un File.
 *
 * @param file - File to convert / Archivo a convertir
 * @returns FileInfo object / Objeto FileInfo
 */
export function createFileInfo(file: File): FileInfo {
  return {
    id: generateFileId(),
    name: file.name,
    size: file.size,
    type: file.type || getFileExtension(file.name),
    file,
    status: 'pending',
  };
}

/**
 * Get Accepted MIME Types / Obtener Tipos MIME Aceptados
 *
 * EN: Returns the MIME types for accepted file extensions.
 * ES: Retorna los tipos MIME para las extensiones de archivo aceptadas.
 *
 * @returns Object with extension to MIME type mapping / Objeto con mapeo de extensión a tipo MIME
 */
export function getAcceptedMimeTypes(): Record<string, string[]> {
  return {
    '.json': ['application/json'],
    '.pdf': ['application/pdf'],
  };
}

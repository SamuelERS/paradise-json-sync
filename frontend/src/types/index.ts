/**
 * Shared Types (Tipos Compartidos)
 *
 * Common type definitions used across the application.
 * Definiciones de tipos comunes usados en toda la aplicación.
 */

/** File information interface / Interfaz de información de archivo */
export interface FileInfo {
  /** Original file object / Objeto de archivo original */
  file: File;
  /** Unique identifier / Identificador único */
  id: string;
  /** File name / Nombre del archivo */
  name: string;
  /** File size in bytes / Tamaño del archivo en bytes */
  size: number;
  /** File type (json/pdf) / Tipo de archivo */
  type: 'json' | 'pdf';
  /** Upload/process status / Estado de carga/proceso */
  status: 'pending' | 'uploading' | 'success' | 'error';
  /** Error message if any / Mensaje de error si existe */
  errorMessage?: string;
}

/** File processing error / Error de procesamiento de archivo */
export interface FileError {
  /** File name / Nombre del archivo */
  fileName: string;
  /** Error message / Mensaje de error */
  message: string;
  /** Error code / Código de error */
  code?: string;
  /** Line number if applicable / Número de línea si aplica */
  line?: number;
}

/** Processing results / Resultados del procesamiento */
export interface ProcessResults {
  /** Total files processed / Total de archivos procesados */
  totalFiles: number;
  /** Successfully processed / Procesados exitosamente */
  successCount: number;
  /** Failed to process / Fallidos al procesar */
  errorCount: number;
  /** List of errors / Lista de errores */
  errors: FileError[];
  /** Output file URL / URL del archivo de salida */
  outputUrl?: string;
  /** Processing duration in ms / Duración del procesamiento en ms */
  duration?: number;
}

/** Application state / Estado de la aplicación */
export type AppStatus =
  | 'idle'
  | 'files_selected'
  | 'uploading'
  | 'processing'
  | 'completed'
  | 'error';

/** Purchase column definition / Definición de columna de compras */
export interface ColumnDef {
  id: string;
  label: string;
  category: string;
}

/** Purchase upload response / Respuesta de carga de compras */
export interface PurchaseUploadResponse {
  upload_id: string;
  file_count: number;
  json_count: number;
  pdf_count: number;
  files: Array<{ filename: string; type: string; path: string }>;
}

/** Purchase process options / Opciones de procesamiento de compras */
export interface PurchaseProcessOptions {
  upload_id: string;
  output_format: string;
  column_profile: string;
  custom_columns?: string[];
  options?: {
    include_summary?: boolean;
    include_items_sheet?: boolean;
    include_raw_data?: boolean;
  };
}

/** Purchase status response / Respuesta de estado de compras */
export interface PurchaseStatusResponse {
  job_id: string;
  status: string;
  progress: number;
  current_step: string;
  result?: {
    invoice_count: number;
    error_count: number;
    errors: Array<{ file: string; reason: string }>;
    output_path: string;
  };
}

/** Purchase format info / Info de formato de compras */
export interface PurchaseFormatInfo {
  id: string;
  label: string;
  extension: string;
}

/** Purchase column info / Info de columna de compras */
export interface PurchaseColumnInfo {
  id: string;
  label: string;
  category: string;
}

/**
 * useUpload Hook / Hook useUpload
 *
 * EN: Custom hook for managing file upload state and operations.
 * ES: Hook personalizado para manejar el estado y operaciones de carga de archivos.
 */
import { useState, useCallback, useRef, useEffect } from 'react';
import { uploadFiles as uploadFilesService } from '../services/uploadService';
import { FileInfo, createFileInfo, validateFile } from '../utils/fileUtils';
import { formatErrorMessage } from '../utils/errorHandler';

/**
 * Upload State Interface / Interfaz de Estado de Carga
 *
 * EN: Internal state structure for the upload hook.
 * ES: Estructura de estado interno para el hook de carga.
 */
interface UploadState {
  files: FileInfo[];
  isUploading: boolean;
  uploadProgress: number;
  error: string | null;
}

/**
 * Upload Hook Return Type / Tipo de Retorno del Hook de Carga
 *
 * EN: Return type for the useUpload hook.
 * ES: Tipo de retorno para el hook useUpload.
 */
export interface UseUploadReturn {
  /** EN: List of files to upload | ES: Lista de archivos a cargar */
  files: FileInfo[];
  /** EN: Whether upload is in progress | ES: Si la carga está en progreso */
  isUploading: boolean;
  /** EN: Upload progress (0-100) | ES: Progreso de carga (0-100) */
  uploadProgress: number;
  /** EN: Error message if any | ES: Mensaje de error si existe */
  error: string | null;
  /** EN: Add files to the list | ES: Agregar archivos a la lista */
  addFiles: (newFiles: File[]) => void;
  /** EN: Remove a file by ID | ES: Remover un archivo por ID */
  removeFile: (id: string) => void;
  /** EN: Clear all files | ES: Limpiar todos los archivos */
  clearFiles: () => void;
  /** EN: Clear error | ES: Limpiar error */
  clearError: () => void;
  /** EN: Upload all files | ES: Cargar todos los archivos */
  upload: () => Promise<string>;
}

/**
 * Initial State / Estado Inicial
 */
const initialState: UploadState = {
  files: [],
  isUploading: false,
  uploadProgress: 0,
  error: null,
};

/**
 * useUpload Hook / Hook useUpload
 *
 * EN: Hook for managing file upload workflow.
 *     Handles file selection, validation, upload progress, and errors.
 * ES: Hook para manejar el flujo de trabajo de carga de archivos.
 *     Maneja selección de archivos, validación, progreso de carga y errores.
 *
 * @returns Upload state and operations / Estado y operaciones de carga
 *
 * @example
 * const { files, addFiles, upload, isUploading } = useUpload();
 *
 * // Add files from input
 * addFiles(event.target.files);
 *
 * // Upload and get jobId
 * const jobId = await upload();
 */
export function useUpload(): UseUploadReturn {
  const [state, setState] = useState<UploadState>(initialState);

  // Ref to store current files - avoids stale closure in upload callback
  // Ref para almacenar archivos actuales - evita closure obsoleto en callback de upload
  const filesRef = useRef<FileInfo[]>([]);

  // Keep ref in sync with state
  // Mantener ref sincronizado con el estado
  useEffect(() => {
    filesRef.current = state.files;
  }, [state.files]);

  /**
   * Add Files / Agregar Archivos
   *
   * EN: Adds new files to the upload list after validation.
   * ES: Agrega nuevos archivos a la lista de carga después de validación.
   */
  const addFiles = useCallback((newFiles: File[]): void => {
    const fileInfos: FileInfo[] = [];

    for (const file of newFiles) {
      const validation = validateFile(file);
      const fileInfo = createFileInfo(file);

      if (!validation.isValid) {
        fileInfo.status = 'error';
        fileInfo.errorMessage = validation.errors.join(', ');
      }

      fileInfos.push(fileInfo);
    }

    setState((prev) => ({
      ...prev,
      files: [...prev.files, ...fileInfos],
      error: null,
    }));
  }, []);

  /**
   * Remove File / Remover Archivo
   *
   * EN: Removes a file from the upload list by ID.
   * ES: Remueve un archivo de la lista de carga por ID.
   */
  const removeFile = useCallback((id: string): void => {
    setState((prev) => ({
      ...prev,
      files: prev.files.filter((f) => f.id !== id),
    }));
  }, []);

  /**
   * Clear Files / Limpiar Archivos
   *
   * EN: Clears all files from the upload list.
   * ES: Limpia todos los archivos de la lista de carga.
   */
  const clearFiles = useCallback((): void => {
    setState((prev) => ({
      ...prev,
      files: [],
      uploadProgress: 0,
      error: null,
    }));
  }, []);

  /**
   * Clear Error / Limpiar Error
   *
   * EN: Clears the error state.
   * ES: Limpia el estado de error.
   */
  const clearError = useCallback((): void => {
    setState((prev) => ({
      ...prev,
      error: null,
    }));
  }, []);

  /**
   * Upload / Cargar
   *
   * EN: Uploads all valid files and returns the job ID.
   * ES: Carga todos los archivos válidos y retorna el ID del trabajo.
   */
  const upload = useCallback(async (): Promise<string> => {
    // EN: Capture current files from ref to avoid stale closure
    // ES: Capturar archivos actuales del ref para evitar closure obsoleto
    const currentFiles = filesRef.current;

    // EN: Filter valid files only
    // ES: Filtrar solo archivos válidos
    const validFiles = currentFiles.filter((f) => f.status !== 'error');

    if (validFiles.length === 0) {
      const errorMsg = 'No hay archivos válidos para cargar';
      setState((prev) => ({ ...prev, error: errorMsg }));
      throw new Error(errorMsg);
    }

    setState((prev) => ({
      ...prev,
      isUploading: true,
      uploadProgress: 0,
      error: null,
    }));

    try {
      // EN: Mark files as uploading
      // ES: Marcar archivos como cargando
      setState((prev) => ({
        ...prev,
        files: prev.files.map((f) =>
          f.status !== 'error' ? { ...f, status: 'uploading' as const } : f
        ),
      }));

      const filesToUpload = validFiles.map((f) => f.file);
      const response = await uploadFilesService(filesToUpload, (progress) => {
        setState((prev) => ({ ...prev, uploadProgress: progress }));
      });

      // EN: Mark files as success
      // ES: Marcar archivos como exitosos
      setState((prev) => ({
        ...prev,
        isUploading: false,
        uploadProgress: 100,
        files: prev.files.map((f) =>
          f.status === 'uploading' ? { ...f, status: 'success' as const } : f
        ),
      }));

      return response.jobId;
    } catch (error) {
      const errorMsg = formatErrorMessage(error);
      setState((prev) => ({
        ...prev,
        isUploading: false,
        error: errorMsg,
        files: prev.files.map((f) =>
          f.status === 'uploading'
            ? { ...f, status: 'error' as const, errorMessage: errorMsg }
            : f
        ),
      }));
      throw error;
    }
  }, []);

  return {
    files: state.files,
    isUploading: state.isUploading,
    uploadProgress: state.uploadProgress,
    error: state.error,
    addFiles,
    removeFile,
    clearFiles,
    clearError,
    upload,
  };
}

export default useUpload;

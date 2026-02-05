/**
 * useDownload Hook / Hook useDownload
 *
 * EN: Custom hook for managing file download operations.
 * ES: Hook personalizado para manejar operaciones de descarga de archivos.
 */
import { useState, useCallback } from 'react';
import {
  downloadExcel,
  downloadPdf,
  downloadJson,
  triggerDownload,
  DownloadType,
} from '../services/downloadService';
import { formatErrorMessage } from '../utils/errorHandler';

/**
 * Download State Interface / Interfaz de Estado de Descarga
 *
 * EN: Internal state structure for the download hook.
 * ES: Estructura de estado interno para el hook de descarga.
 */
interface DownloadState {
  isDownloading: boolean;
  downloadType: DownloadType | null;
  error: string | null;
}

/**
 * Download Hook Return Type / Tipo de Retorno del Hook de Descarga
 *
 * EN: Return type for the useDownload hook.
 * ES: Tipo de retorno para el hook useDownload.
 */
export interface UseDownloadReturn {
  /** EN: Whether download is in progress | ES: Si la descarga está en progreso */
  isDownloading: boolean;
  /** EN: Type of current download | ES: Tipo de descarga actual */
  downloadType: DownloadType | null;
  /** EN: Error message if any | ES: Mensaje de error si existe */
  error: string | null;
  /** EN: Download Excel file | ES: Descargar archivo Excel */
  downloadExcelFile: (jobId: string, filename?: string) => Promise<void>;
  /** EN: Download PDF file | ES: Descargar archivo PDF */
  downloadPdfFile: (jobId: string, filename?: string) => Promise<void>;
  /** EN: Download JSON file | ES: Descargar archivo JSON */
  downloadJsonFile: (jobId: string, filename?: string) => Promise<void>;
  /** EN: Clear error | ES: Limpiar error */
  clearError: () => void;
  /** EN: Reset state | ES: Reiniciar estado */
  reset: () => void;
}

/**
 * Initial State / Estado Inicial
 */
const initialState: DownloadState = {
  isDownloading: false,
  downloadType: null,
  error: null,
};

/**
 * useDownload Hook / Hook useDownload
 *
 * EN: Hook for managing file download workflow.
 *     Handles Excel and PDF downloads with error management.
 * ES: Hook para manejar el flujo de trabajo de descarga de archivos.
 *     Maneja descargas de Excel y PDF con manejo de errores.
 *
 * @returns Download state and operations / Estado y operaciones de descarga
 *
 * @example
 * const { isDownloading, downloadExcelFile, downloadPdfFile } = useDownload();
 *
 * // Download Excel
 * await downloadExcelFile(jobId);
 *
 * // Download PDF with custom filename
 * await downloadPdfFile(jobId, 'my-report.pdf');
 */
export function useDownload(): UseDownloadReturn {
  const [state, setState] = useState<DownloadState>(initialState);

  /**
   * Download Excel File / Descargar Archivo Excel
   *
   * EN: Downloads the Excel file for a completed job.
   * ES: Descarga el archivo Excel para un trabajo completado.
   */
  const downloadExcelFile = useCallback(
    async (jobId: string, filename?: string): Promise<void> => {
      setState({
        isDownloading: true,
        downloadType: 'excel',
        error: null,
      });

      try {
        const blob = await downloadExcel(jobId);
        const downloadFilename = filename || `consolidado_${jobId}.xlsx`;
        triggerDownload(blob, downloadFilename);

        setState((prev) => ({
          ...prev,
          isDownloading: false,
        }));
      } catch (error) {
        setState({
          isDownloading: false,
          downloadType: 'excel',
          error: formatErrorMessage(error),
        });
        throw error;
      }
    },
    []
  );

  /**
   * Download PDF File / Descargar Archivo PDF
   *
   * EN: Downloads the PDF file for a completed job.
   * ES: Descarga el archivo PDF para un trabajo completado.
   */
  const downloadPdfFile = useCallback(
    async (jobId: string, filename?: string): Promise<void> => {
      setState({
        isDownloading: true,
        downloadType: 'pdf',
        error: null,
      });

      try {
        const blob = await downloadPdf(jobId);
        const downloadFilename = filename || `consolidado_${jobId}.pdf`;
        triggerDownload(blob, downloadFilename);

        setState((prev) => ({
          ...prev,
          isDownloading: false,
        }));
      } catch (error) {
        setState({
          isDownloading: false,
          downloadType: 'pdf',
          error: formatErrorMessage(error),
        });
        throw error;
      }
    },
    []
  );

  /**
   * Download JSON File / Descargar Archivo JSON
   *
   * EN: Downloads the consolidated JSON file for a completed job.
   * ES: Descarga el archivo JSON consolidado para un trabajo completado.
   */
  const downloadJsonFile = useCallback(
    async (jobId: string, filename?: string): Promise<void> => {
      setState({
        isDownloading: true,
        downloadType: 'json',
        error: null,
      });

      try {
        const blob = await downloadJson(jobId);
        const downloadFilename = filename || `consolidado_${jobId}.json`;
        triggerDownload(blob, downloadFilename);

        setState((prev) => ({
          ...prev,
          isDownloading: false,
        }));
      } catch (error) {
        setState({
          isDownloading: false,
          downloadType: 'json',
          error: formatErrorMessage(error),
        });
        throw error;
      }
    },
    []
  );

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
   * Reset / Reiniciar
   *
   * EN: Resets the hook state to initial values.
   * ES: Reinicia el estado del hook a valores iniciales.
   */
  const reset = useCallback((): void => {
    setState(initialState);
  }, []);

  return {
    isDownloading: state.isDownloading,
    downloadType: state.downloadType,
    error: state.error,
    downloadExcelFile,
    downloadPdfFile,
    downloadJsonFile,
    clearError,
    reset,
  };
}

export default useDownload;

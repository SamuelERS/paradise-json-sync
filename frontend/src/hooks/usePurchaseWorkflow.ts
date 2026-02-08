/**
 * usePurchaseWorkflow Hook / Hook de Flujo de Compras
 *
 * Orchestrates the full purchase workflow:
 * upload → configure → processing → done.
 */
import { useState, useCallback, useRef, useEffect } from 'react';
import type {
  PurchaseUploadResponse,
  PurchaseProcessOptions,
  PurchaseStatusResponse,
} from '../types';
import {
  uploadPurchaseFiles,
  startPurchaseProcessing,
  getPurchaseStatus,
  triggerPurchaseDownload,
} from '../services/purchaseService';
import { POLLING_INTERVAL } from '../config/constants';

export type PurchaseStep = 'upload' | 'configure' | 'processing' | 'done';

export interface UsePurchaseWorkflowReturn {
  step: PurchaseStep;
  uploadData: PurchaseUploadResponse | null;
  jobId: string | null;
  status: PurchaseStatusResponse | null;
  isUploading: boolean;
  isProcessing: boolean;
  uploadProgress: number;
  processingProgress: number;
  error: string | null;

  uploadFiles: (files: File[]) => Promise<void>;
  setUploadData: (data: PurchaseUploadResponse) => void;
  startProcessing: (options: PurchaseProcessOptions) => Promise<void>;
  downloadResult: () => Promise<void>;
  reset: () => void;
  clearError: () => void;
}

export function usePurchaseWorkflow(): UsePurchaseWorkflowReturn {
  const [step, setStep] = useState<PurchaseStep>('upload');
  const [uploadData, setUploadDataState] = useState<PurchaseUploadResponse | null>(null);
  const [jobId, setJobId] = useState<string | null>(null);
  const [status, setStatus] = useState<PurchaseStatusResponse | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [processingProgress, setProcessingProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const pollingRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const mountedRef = useRef(true);

  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
      if (pollingRef.current) {
        clearInterval(pollingRef.current);
      }
    };
  }, []);

  const stopPolling = useCallback(() => {
    if (pollingRef.current) {
      clearInterval(pollingRef.current);
      pollingRef.current = null;
    }
  }, []);

  const startPolling = useCallback((id: string) => {
    stopPolling();
    pollingRef.current = setInterval(async () => {
      if (!mountedRef.current) {
        stopPolling();
        return;
      }
      try {
        const statusResult = await getPurchaseStatus(id);
        if (!mountedRef.current) return;
        setStatus(statusResult);
        setProcessingProgress(statusResult.progress);

        if (statusResult.status === 'completed') {
          stopPolling();
          setIsProcessing(false);
          setStep('done');
        } else if (statusResult.status === 'failed') {
          stopPolling();
          setIsProcessing(false);
          const errorMsg = statusResult.result?.errors
            ?.map((e) => `${e.file}: ${e.reason}`)
            .join('; ') || 'Error en el procesamiento';
          setError(errorMsg);
        }
      } catch (err) {
        if (!mountedRef.current) return;
        stopPolling();
        setIsProcessing(false);
        setError(err instanceof Error ? err.message : 'Error al consultar estado');
      }
    }, POLLING_INTERVAL);
  }, [stopPolling]);

  const uploadFiles = useCallback(async (files: File[]) => {
    setIsUploading(true);
    setError(null);
    setUploadProgress(0);
    try {
      const result = await uploadPurchaseFiles(files, (p) => {
        if (mountedRef.current) setUploadProgress(p);
      });
      if (!mountedRef.current) return;
      setUploadDataState(result);
      setStep('configure');
    } catch (err) {
      if (!mountedRef.current) return;
      setError(err instanceof Error ? err.message : 'Error al subir archivos');
    } finally {
      if (mountedRef.current) setIsUploading(false);
    }
  }, []);

  const setUploadData = useCallback((data: PurchaseUploadResponse) => {
    setUploadDataState(data);
    setStep('configure');
  }, []);

  const startProcessing = useCallback(async (options: PurchaseProcessOptions) => {
    setIsProcessing(true);
    setError(null);
    setProcessingProgress(0);
    setStep('processing');
    try {
      const result = await startPurchaseProcessing(options);
      if (!mountedRef.current) return;
      setJobId(result.job_id);
      startPolling(result.job_id);
    } catch (err) {
      if (!mountedRef.current) return;
      setIsProcessing(false);
      setStep('configure');
      setError(err instanceof Error ? err.message : 'Error al iniciar procesamiento');
    }
  }, [startPolling]);

  const downloadResult = useCallback(async () => {
    if (!jobId) return;
    try {
      await triggerPurchaseDownload(jobId, `compras_${jobId}.xlsx`);
    } catch (err) {
      if (!mountedRef.current) return;
      setError(err instanceof Error ? err.message : 'Error al descargar resultado');
    }
  }, [jobId]);

  const reset = useCallback(() => {
    stopPolling();
    setStep('upload');
    setUploadDataState(null);
    setJobId(null);
    setStatus(null);
    setIsUploading(false);
    setIsProcessing(false);
    setUploadProgress(0);
    setProcessingProgress(0);
    setError(null);
  }, [stopPolling]);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    step,
    uploadData,
    jobId,
    status,
    isUploading,
    isProcessing,
    uploadProgress,
    processingProgress,
    error,
    uploadFiles,
    setUploadData,
    startProcessing,
    downloadResult,
    reset,
    clearError,
  };
}

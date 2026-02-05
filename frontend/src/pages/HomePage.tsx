/**
 * HomePage Component (Componente Página Principal)
 *
 * Main page with file upload and processing workflow.
 * Página principal con carga de archivos y flujo de procesamiento.
 */
import { useState, useCallback, useEffect, useMemo } from 'react';
import type { ProcessResults, AppStatus } from '../types';
import { MainLayout } from '../components/layout';
import { Card, Button, Alert } from '../components/common';
import { Dropzone, FileList, UploadProgress } from '../components/upload';
import { ResultsPanel } from '../components/results';
import { useDownload } from '../hooks/useDownload';
import { useUpload } from '../hooks/useUpload';
import { useProcess } from '../hooks/useProcess';

export function HomePage() {
  const [appStatus, setAppStatus] = useState<AppStatus>('idle');
  const [results, setResults] = useState<ProcessResults | undefined>();
  const [error, setError] = useState<string | null>(null);
  const [jobId, setJobId] = useState<string | null>(null);

  // Hooks for real backend operations
  const {
    files,
    isUploading,
    uploadProgress,
    error: uploadError,
    addFiles,
    removeFile,
    clearFiles,
    clearError: clearUploadError,
    upload,
  } = useUpload();

  const {
    isProcessing,
    progress: processProgress,
    currentStep,
    error: processError,
    status: processStatus,
    startProcess,
    reset: resetProcess,
  } = useProcess();

  const {
    downloadExcelFile,
    downloadPdfFile,
    downloadJsonFile,
    error: downloadError,
  } = useDownload();

  // Combine progress from upload and process phases (memoized)
  const totalProgress = useMemo(() => {
    if (isUploading) return uploadProgress * 0.3; // Upload is 30% of total
    if (isProcessing) return 30 + processProgress * 0.7; // Process is 70% of total
    return 0;
  }, [isUploading, isProcessing, uploadProgress, processProgress]);

  // Update app status based on hook states
  useEffect(() => {
    if (isUploading) {
      setAppStatus('uploading');
    } else if (isProcessing) {
      setAppStatus('processing');
    } else if (processStatus?.status === 'completed') {
      setAppStatus('completed');
      const errorCount = processStatus.errors?.length || 0;
      setResults({
        totalFiles: files.length,
        successCount: files.length - errorCount,
        errorCount,
        errors: processStatus.errors?.map((e) => ({
          fileName: e.fileName,
          message: e.message,
          code: e.errorCode,
          line: e.line,
        })) || [],
        outputUrl: processStatus.downloadUrl || (jobId ? `/api/download/excel/${jobId}` : undefined),
      });
    } else if (processStatus?.status === 'failed') {
      setAppStatus('error');
      setError(processStatus.errors?.map((e) => e.message).join(', ') || 'Error en el procesamiento');
    }
  }, [isUploading, isProcessing, processStatus, files.length, jobId]);

  // Consolidate errors
  useEffect(() => {
    const combinedError = uploadError || processError || downloadError;
    if (combinedError) {
      setError(combinedError);
    }
  }, [uploadError, processError, downloadError]);

  const handleFilesSelected = useCallback(
    (newFiles: File[]) => {
      addFiles(newFiles);
      setAppStatus('files_selected');
      setError(null);
    },
    [addFiles]
  );

  const handleRemoveFile = useCallback(
    (index: number) => {
      const fileToRemove = files[index];
      if (fileToRemove) {
        removeFile(fileToRemove.id);
        if (files.length <= 1) {
          setAppStatus('idle');
        }
      }
    },
    [files, removeFile]
  );

  const handleProcess = useCallback(async () => {
    if (files.length === 0) return;
    setError(null);
    setResults(undefined);

    try {
      // Step 1: Upload files to backend (returns upload_id)
      const uploadId = await upload();

      // Step 2: Start processing - returns the REAL job_id from backend
      const realJobId = await startProcess(uploadId);
      setJobId(realJobId);
    } catch (err) {
      setAppStatus('error');
      setError(err instanceof Error ? err.message : 'Error durante el procesamiento');
    }
  }, [files.length, upload, startProcess]);

  const handleDownloadExcel = useCallback(async () => {
    if (!jobId) {
      setError('No hay resultados para descargar.');
      return;
    }
    try {
      await downloadExcelFile(jobId, `consolidado_${jobId}.xlsx`);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Error desconocido';
      console.error('Error descargando Excel:', errorMsg);
      setError(`Error al descargar el archivo Excel: ${errorMsg}`);
    }
  }, [jobId, downloadExcelFile]);

  const handleDownloadPdf = useCallback(async () => {
    if (!jobId) {
      setError('No hay resultados para descargar.');
      return;
    }
    try {
      await downloadPdfFile(jobId, `consolidado_${jobId}.pdf`);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Error desconocido';
      console.error('Error descargando PDF:', errorMsg);
      setError(`Error al descargar el archivo PDF: ${errorMsg}`);
    }
  }, [jobId, downloadPdfFile]);

  const handleDownloadJson = useCallback(async () => {
    if (!jobId) {
      setError('No hay resultados para descargar.');
      return;
    }
    try {
      await downloadJsonFile(jobId, `consolidado_${jobId}.json`);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Error desconocido';
      console.error('Error descargando JSON:', errorMsg);
      setError(`Error al descargar el archivo JSON: ${errorMsg}`);
    }
  }, [jobId, downloadJsonFile]);

  const handleReset = useCallback(() => {
    setAppStatus('idle');
    clearFiles();
    resetProcess();
    setResults(undefined);
    setError(null);
    setJobId(null);
    clearUploadError();
  }, [clearFiles, resetProcess, clearUploadError]);

  const isBusy = isUploading || isProcessing;

  // Convert FileInfo from useUpload to the format expected by FileList (memoized)
  const filesForDisplay = useMemo(() => files.map((f) => ({
    ...f,
    type: (f.name?.toLowerCase().endsWith('.json')) ? 'json' as const : 'pdf' as const,
  })), [files]);

  return (
    <MainLayout>
      <div className="py-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            Paradise JSON Sync
          </h1>
          <p className="text-gray-600 mt-2">
            Consolida archivos JSON y PDF de facturación en un solo documento
          </p>
        </div>
        <div className="space-y-6">
          {error && (
            <Alert
              type="error"
              title="Error"
              message={error}
              onClose={() => setError(null)}
            />
          )}
          {!isBusy && appStatus !== 'completed' && (
            <Card>
              <div className="space-y-6">
                <Dropzone
                  onFilesSelected={handleFilesSelected}
                  disabled={isBusy}
                />
                <FileList files={filesForDisplay} onRemove={handleRemoveFile} />
                {files.length > 0 && (
                  <div className="flex justify-center pt-4">
                    <Button
                      variant="primary"
                      size="lg"
                      onClick={handleProcess}
                      disabled={isBusy}
                    >
                      Procesar {files.length} archivo{files.length !== 1 ? 's' : ''}
                    </Button>
                  </div>
                )}
              </div>
            </Card>
          )}
          {isBusy && (
            <UploadProgress
              totalFiles={files.length}
              processedFiles={files.filter((f) => f.status === 'success').length}
              currentFile={currentStep || (isUploading ? 'Subiendo archivos...' : 'Procesando...')}
              progress={totalProgress}
              status={isUploading ? 'uploading' : 'processing'}
            />
          )}
          {(appStatus === 'completed' || appStatus === 'error') && (
            <ResultsPanel
              status={appStatus === 'error' ? 'error' : 'completed'}
              results={results}
              onDownloadExcel={handleDownloadExcel}
              onDownloadPdf={handleDownloadPdf}
              onDownloadJson={handleDownloadJson}
              onReset={handleReset}
            />
          )}
        </div>
      </div>
    </MainLayout>
  );
}

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
import type { DownloadType } from '../services/downloadService';

/**
 * Step Display Names / Nombres de Pasos para Mostrar
 *
 * Maps backend step keys to user-friendly Spanish labels.
 */
const STEP_LABELS: Record<string, string> = {
  'Iniciando procesamiento': 'Iniciando procesamiento...',
  'validating': 'Validando archivos...',
  'extracting': 'Extrayendo datos...',
  'consolidating': 'Consolidando información...',
  'generating': 'Generando reporte...',
  'processing': 'Procesando...',
};

export function HomePage() {
  const [appStatus, setAppStatus] = useState<AppStatus>('idle');
  const [results, setResults] = useState<ProcessResults | undefined>();
  const [error, setError] = useState<string | null>(null);
  const [jobId, setJobId] = useState<string | null>(null);

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
    isDownloading,
    downloadType,
    downloadExcelFile,
    downloadPdfFile,
    downloadJsonFile,
    error: downloadError,
  } = useDownload();

  // Combine progress from upload and process phases
  const totalProgress = useMemo(() => {
    if (isUploading) return uploadProgress * 0.3;
    if (isProcessing) return 30 + processProgress * 0.7;
    return 0;
  }, [isUploading, isProcessing, uploadProgress, processProgress]);

  // User-friendly step label
  const stepLabel = useMemo(() => {
    if (isUploading) return 'Subiendo archivos...';
    if (!currentStep) return 'Procesando...';
    return STEP_LABELS[currentStep] || currentStep;
  }, [isUploading, currentStep]);

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
      const uploadId = await upload();
      const realJobId = await startProcess(uploadId);
      setJobId(realJobId);
    } catch (err) {
      setAppStatus('error');
      if (err instanceof Error) {
        // Distinguish upload vs process errors for the user
        const isUploadPhase = !jobId;
        setError(
          isUploadPhase
            ? `No se pudieron subir los archivos: ${err.message}`
            : `Error al procesar los archivos: ${err.message}`
        );
      } else {
        setError('Error inesperado durante el procesamiento');
      }
    }
  }, [files.length, upload, startProcess, jobId]);

  // Unified download handler
  const handleDownload = useCallback(async (type: DownloadType) => {
    if (!jobId) {
      setError('No hay resultados para descargar.');
      return;
    }
    const downloaders = {
      excel: downloadExcelFile,
      pdf: downloadPdfFile,
      json: downloadJsonFile,
    };
    const extensions = { excel: 'xlsx', pdf: 'pdf', json: 'json' };
    try {
      await downloaders[type](jobId, `consolidado_${jobId}.${extensions[type]}`);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Error desconocido';
      setError(`Error al descargar el archivo ${type.toUpperCase()}: ${errorMsg}`);
    }
  }, [jobId, downloadExcelFile, downloadPdfFile, downloadJsonFile]);

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
                <FileList files={files} onRemove={handleRemoveFile} />
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
              currentFile={stepLabel}
              progress={totalProgress}
              status={isUploading ? 'uploading' : 'processing'}
            />
          )}
          {(appStatus === 'completed' || appStatus === 'error') && (
            <ResultsPanel
              status={appStatus === 'error' ? 'error' : 'completed'}
              results={results}
              isDownloading={isDownloading}
              downloadType={downloadType}
              onDownloadExcel={() => handleDownload('excel')}
              onDownloadPdf={() => handleDownload('pdf')}
              onDownloadJson={() => handleDownload('json')}
              onReset={handleReset}
            />
          )}
        </div>
      </div>
    </MainLayout>
  );
}

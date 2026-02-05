/**
 * HomePage Component (Componente Página Principal)
 *
 * Main page with file upload and processing workflow.
 * Página principal con carga de archivos y flujo de procesamiento.
 */
import { useState, useCallback } from 'react';
import type { FileInfo, ProcessResults, AppStatus } from '../types';
import { MainLayout } from '../components/layout';
import { Card, Button, Alert } from '../components/common';
import { Dropzone, FileList, UploadProgress } from '../components/upload';
import { ResultsPanel } from '../components/results';

function generateFileId(): string {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
}

function getFileType(file: File): 'json' | 'pdf' {
  return file.name.toLowerCase().endsWith('.json') ? 'json' : 'pdf';
}

export function HomePage() {
  const [status, setStatus] = useState<AppStatus>('idle');
  const [files, setFiles] = useState<FileInfo[]>([]);
  const [progress, setProgress] = useState(0);
  const [currentFile, setCurrentFile] = useState('');
  const [results, setResults] = useState<ProcessResults | undefined>();
  const [error, setError] = useState<string | null>(null);

  const handleFilesSelected = useCallback((newFiles: File[]) => {
    const fileInfos: FileInfo[] = newFiles.map((file) => ({
      file,
      id: generateFileId(),
      name: file.name,
      size: file.size,
      type: getFileType(file),
      status: 'pending',
    }));
    setFiles((prev) => [...prev, ...fileInfos]);
    setStatus('files_selected');
    setError(null);
  }, []);

  const handleRemoveFile = useCallback((index: number) => {
    setFiles((prev) => {
      const newFiles = prev.filter((_, i) => i !== index);
      if (newFiles.length === 0) {
        setStatus('idle');
      }
      return newFiles;
    });
  }, []);

  const handleProcess = useCallback(async () => {
    if (files.length === 0) return;
    setStatus('uploading');
    setProgress(0);
    setResults(undefined);
    try {
      for (let i = 0; i < files.length; i++) {
        setCurrentFile(files[i].name);
        setFiles((prev) =>
          prev.map((f, idx) => (idx === i ? { ...f, status: 'uploading' } : f))
        );
        await new Promise((resolve) => setTimeout(resolve, 500));
        setProgress(((i + 1) / files.length) * 50);
        setFiles((prev) =>
          prev.map((f, idx) => (idx === i ? { ...f, status: 'success' } : f))
        );
      }
      setStatus('processing');
      setCurrentFile('Consolidando datos...');
      await new Promise((resolve) => setTimeout(resolve, 1000));
      setProgress(100);
      setResults({
        totalFiles: files.length,
        successCount: files.length,
        errorCount: 0,
        errors: [],
        outputUrl: '/download/result.xlsx',
        duration: 1500,
      });
      setStatus('completed');
    } catch {
      setStatus('error');
      setError('Ocurrió un error durante el procesamiento.');
    }
  }, [files]);

  const handleDownloadExcel = useCallback(() => {
    console.log('Downloading Excel...');
  }, []);

  const handleDownloadPdf = useCallback(() => {
    console.log('Downloading PDF...');
  }, []);

  const handleReset = useCallback(() => {
    setStatus('idle');
    setFiles([]);
    setProgress(0);
    setCurrentFile('');
    setResults(undefined);
    setError(null);
  }, []);

  const isProcessing = status === 'uploading' || status === 'processing';

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
          {!isProcessing && status !== 'completed' && (
            <Card>
              <div className="space-y-6">
                <Dropzone
                  onFilesSelected={handleFilesSelected}
                  disabled={isProcessing}
                />
                <FileList files={files} onRemove={handleRemoveFile} />
                {files.length > 0 && (
                  <div className="flex justify-center pt-4">
                    <Button
                      variant="primary"
                      size="lg"
                      onClick={handleProcess}
                      disabled={isProcessing}
                    >
                      Procesar {files.length} archivo{files.length !== 1 ? 's' : ''}
                    </Button>
                  </div>
                )}
              </div>
            </Card>
          )}
          {isProcessing && (
            <UploadProgress
              totalFiles={files.length}
              processedFiles={files.filter((f) => f.status === 'success').length}
              currentFile={currentFile}
              progress={progress}
              status={status === 'uploading' ? 'uploading' : 'processing'}
            />
          )}
          {(status === 'completed' || status === 'error') && (
            <ResultsPanel
              status={status === 'error' ? 'error' : 'completed'}
              results={results}
              onDownloadExcel={handleDownloadExcel}
              onDownloadPdf={handleDownloadPdf}
              onReset={handleReset}
            />
          )}
        </div>
      </div>
    </MainLayout>
  );
}

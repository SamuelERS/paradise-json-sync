/**
 * PurchaseUpload Component / Componente Carga de Compras
 *
 * Reuses Dropzone for uploading purchase invoice files.
 * Points to /api/purchases/upload.
 */
import { useState, useCallback } from 'react';
import { Dropzone } from '../upload/Dropzone';
import { FileList } from '../upload/FileList';
import { Button } from '../common/Button';
import { Alert } from '../common/Alert';
import type { FileInfo, PurchaseUploadResponse } from '../../types';
import { uploadPurchaseFiles } from '../../services/purchaseService';
import { ProgressBar } from '../common/ProgressBar';

interface PurchaseUploadProps {
  onUploaded: (uploadData: PurchaseUploadResponse) => void;
}

let nextFileId = 0;

export function PurchaseUpload({ onUploaded }: PurchaseUploadProps) {
  const [files, setFiles] = useState<FileInfo[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const handleFilesSelected = useCallback((newFiles: File[]) => {
    setError(null);
    const mapped: FileInfo[] = newFiles.map((file) => ({
      file,
      id: `purchase-file-${nextFileId++}`,
      name: file.name,
      size: file.size,
      type: file.name.endsWith('.pdf') ? 'pdf' : 'json',
      status: 'pending',
    }));
    setFiles((prev) => [...prev, ...mapped]);
  }, []);

  const handleRemove = useCallback((index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  }, []);

  const handleUpload = useCallback(async () => {
    if (files.length === 0) return;
    setIsUploading(true);
    setError(null);
    setUploadProgress(0);

    try {
      const rawFiles = files.map((f) => f.file);
      const result = await uploadPurchaseFiles(rawFiles, setUploadProgress);
      onUploaded(result);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al subir archivos';
      setError(message);
    } finally {
      setIsUploading(false);
    }
  }, [files, onUploaded]);

  const jsonCount = files.filter((f) => f.type === 'json').length;
  const pdfCount = files.filter((f) => f.type === 'pdf').length;

  return (
    <div className="space-y-4">
      {error && (
        <Alert
          type="error"
          title="Error de carga"
          message={error}
          onClose={() => setError(null)}
        />
      )}

      {!isUploading && (
        <>
          <Dropzone
            onFilesSelected={handleFilesSelected}
            acceptedTypes={['.json', '.pdf']}
            disabled={isUploading}
          />

          {files.length > 0 && (
            <>
              <div className="text-sm text-gray-600">
                {files.length} archivo{files.length !== 1 ? 's' : ''} seleccionado{files.length !== 1 ? 's' : ''}
                {jsonCount > 0 && ` (${jsonCount} JSON`}
                {pdfCount > 0 && `${jsonCount > 0 ? ', ' : ' ('}${pdfCount} PDF`}
                {(jsonCount > 0 || pdfCount > 0) && ')'}
              </div>
              <FileList files={files} onRemove={handleRemove} />
              <div className="flex justify-center pt-2">
                <Button
                  variant="primary"
                  size="lg"
                  onClick={handleUpload}
                  disabled={isUploading}
                  className="bg-green-700 hover:bg-green-800 focus:ring-green-600"
                >
                  Continuar
                </Button>
              </div>
            </>
          )}
        </>
      )}

      {isUploading && (
        <div className="text-center space-y-3 py-4">
          <p className="text-sm text-gray-600">Subiendo archivos de compra...</p>
          <ProgressBar
            progress={uploadProgress}
            status="loading"
            showPercentage
          />
        </div>
      )}
    </div>
  );
}

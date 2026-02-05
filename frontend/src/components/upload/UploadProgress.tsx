/**
 * UploadProgress Component (Componente Progreso de Carga)
 *
 * Shows progress of file upload/processing.
 * Muestra el progreso de carga/procesamiento de archivos.
 */
import { ProgressBar } from '../common/ProgressBar';
import { Spinner } from '../common/Spinner';

interface UploadProgressProps {
  /** Total number of files / Número total de archivos */
  totalFiles: number;
  /** Number of processed files / Número de archivos procesados */
  processedFiles: number;
  /** Current file being processed / Archivo actual siendo procesado */
  currentFile?: string;
  /** Progress percentage / Porcentaje de progreso */
  progress: number;
  /** Processing status / Estado del procesamiento */
  status?: 'uploading' | 'processing' | 'completed' | 'error';
}

const statusMessages = {
  uploading: 'Subiendo archivos...',
  processing: 'Procesando datos...',
  completed: 'Procesamiento completado',
  error: 'Error en el procesamiento',
};

export function UploadProgress({
  totalFiles,
  processedFiles,
  currentFile,
  progress,
  status = 'uploading',
}: UploadProgressProps) {
  const progressStatus = status === 'error' ? 'error' : status === 'completed' ? 'success' : 'loading';

  return (
    <div className="w-full bg-white border border-gray-200 rounded-xl p-6">
      <div className="flex items-center gap-3 mb-4">
        {status !== 'completed' && status !== 'error' && <Spinner size="sm" />}
        {status === 'completed' && (
          <div className="w-6 h-6 bg-green-100 rounded-full flex items-center justify-center">
            <svg className="w-4 h-4 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
        )}
        {status === 'error' && (
          <div className="w-6 h-6 bg-red-100 rounded-full flex items-center justify-center">
            <svg className="w-4 h-4 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
        )}
        <span className="text-sm font-medium text-gray-700">{statusMessages[status]}</span>
      </div>
      <ProgressBar progress={progress} status={progressStatus} showPercentage />
      <div className="flex items-center justify-between mt-3 text-sm text-gray-500">
        <span>
          {processedFiles} de {totalFiles} archivos
        </span>
        {currentFile && status !== 'completed' && (
          <span className="truncate max-w-[200px]">{currentFile}</span>
        )}
      </div>
    </div>
  );
}

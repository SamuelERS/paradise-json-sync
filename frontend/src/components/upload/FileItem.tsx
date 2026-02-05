/**
 * FileItem Component (Componente Ítem de Archivo)
 *
 * Single file item in the upload list.
 * Elemento individual de archivo en la lista de carga.
 */
import type { FileInfo } from '../../types';

interface FileItemProps {
  /** File information / Información del archivo */
  file: FileInfo;
  /** Remove handler / Manejador de eliminación */
  onRemove: () => void;
}

const statusColors = {
  pending: 'bg-gray-100 text-gray-600',
  uploading: 'bg-blue-100 text-blue-600',
  success: 'bg-green-100 text-green-600',
  error: 'bg-red-100 text-red-600',
};

const statusLabels = {
  pending: 'Pendiente',
  uploading: 'Subiendo',
  success: 'Completado',
  error: 'Error',
};

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export function FileItem({ file, onRemove }: FileItemProps) {
  const isJson = file.type === 'json';

  return (
    <div className="flex items-center gap-3 p-3 bg-white border border-gray-200 rounded-lg">
      <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${isJson ? 'bg-green-100' : 'bg-red-100'}`}>
        {isJson ? (
          <svg className="w-5 h-5 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
          </svg>
        ) : (
          <svg className="w-5 h-5 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
          </svg>
        )}
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-gray-900 truncate">{file.name}</p>
        <p className="text-xs text-gray-500">{formatFileSize(file.size)}</p>
      </div>
      <span className={`px-2 py-1 text-xs font-medium rounded-full ${statusColors[file.status]}`}>
        {statusLabels[file.status]}
      </span>
      {file.status !== 'uploading' && (
        <button
          onClick={onRemove}
          className="p-1 text-gray-400 hover:text-red-500 transition-colors"
          aria-label="Eliminar archivo"
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      )}
    </div>
  );
}

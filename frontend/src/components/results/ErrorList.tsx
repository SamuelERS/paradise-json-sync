/**
 * ErrorList Component (Componente Lista de Errores)
 *
 * Displays processing errors.
 * Muestra los errores de procesamiento.
 */
import { useState } from 'react';
import type { FileError } from '../../types';

interface ErrorListProps {
  /** List of errors / Lista de errores */
  errors: FileError[];
}

export function ErrorList({ errors }: ErrorListProps) {
  const [expanded, setExpanded] = useState(false);

  if (errors.length === 0) {
    return null;
  }

  const displayedErrors = expanded ? errors : errors.slice(0, 3);
  const hasMore = errors.length > 3;

  return (
    <div className="w-full">
      <div className="flex items-center gap-2 mb-3">
        <svg
          className="w-5 h-5 text-red-500"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
          />
        </svg>
        <h4 className="text-sm font-medium text-red-700">
          Errores encontrados ({errors.length})
        </h4>
      </div>
      <div className="space-y-2">
        {displayedErrors.map((error, index) => (
          <div
            key={index}
            className="bg-red-50 border border-red-200 rounded-lg p-3"
          >
            <p className="text-sm font-medium text-red-800">{error.fileName}</p>
            <p className="text-sm text-red-600 mt-1">{error.message}</p>
            {error.line && (
              <p className="text-xs text-red-500 mt-1">Línea: {error.line}</p>
            )}
          </div>
        ))}
      </div>
      {hasMore && (
        <button
          onClick={() => setExpanded(!expanded)}
          className="mt-2 text-sm text-red-600 hover:text-red-800 font-medium"
        >
          {expanded ? 'Ver menos' : `Ver ${errors.length - 3} errores más`}
        </button>
      )}
    </div>
  );
}

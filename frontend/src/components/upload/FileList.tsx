/**
 * FileList Component (Componente Lista de Archivos)
 *
 * Displays list of selected files.
 * Muestra la lista de archivos seleccionados.
 */
import React from 'react';
import type { FileInfo } from '../../types';
import { FileItem } from './FileItem';

interface FileListProps {
  /** List of files / Lista de archivos */
  files: FileInfo[];
  /** Remove file handler / Manejador de eliminación de archivo */
  onRemove: (index: number) => void;
}

export function FileList({ files, onRemove }: FileListProps) {
  if (files.length === 0) {
    return null;
  }

  const jsonCount = files.filter((f) => f.type === 'json').length;
  const pdfCount = files.filter((f) => f.type === 'pdf').length;

  return (
    <div className="w-full">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-medium text-gray-700">
          Archivos seleccionados ({files.length})
        </h3>
        <div className="flex items-center gap-3 text-xs text-gray-500">
          {jsonCount > 0 && (
            <span className="flex items-center gap-1">
              <span className="w-2 h-2 bg-green-400 rounded-full" />
              {jsonCount} JSON
            </span>
          )}
          {pdfCount > 0 && (
            <span className="flex items-center gap-1">
              <span className="w-2 h-2 bg-red-400 rounded-full" />
              {pdfCount} PDF
            </span>
          )}
        </div>
      </div>
      <div className="space-y-2 max-h-64 overflow-y-auto">
        {files.map((file, index) => (
          <FileItem
            key={file.id}
            file={file}
            onRemove={() => onRemove(index)}
          />
        ))}
      </div>
    </div>
  );
}

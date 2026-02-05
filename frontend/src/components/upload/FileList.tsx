/**
 * FileList Component (Componente Lista de Archivos)
 *
 * Displays list of selected files with virtualization for large lists.
 * Muestra la lista de archivos seleccionados con virtualización para listas grandes.
 */
import { useRef, useMemo } from 'react';
import { useVirtualizer } from '@tanstack/react-virtual';
import type { FileInfo } from '../../types';
import { FileItem } from './FileItem';

interface FileListProps {
  /** List of files / Lista de archivos */
  files: FileInfo[];
  /** Remove file handler / Manejador de eliminación de archivo */
  onRemove: (_index: number) => void;
}

/**
 * Threshold for enabling virtualization.
 * Below this, render normally for simplicity.
 */
const VIRTUALIZATION_THRESHOLD = 50;
const ITEM_HEIGHT = 56; // Height of each FileItem in pixels

export function FileList({ files, onRemove }: FileListProps) {
  const parentRef = useRef<HTMLDivElement>(null);

  // Memoize counts to avoid recalculating on every render
  const { jsonCount, pdfCount } = useMemo(() => ({
    jsonCount: files.filter((f) => f.type === 'json').length,
    pdfCount: files.filter((f) => f.type === 'pdf').length,
  }), [files]);

  // Virtualization for large lists
  const virtualizer = useVirtualizer({
    count: files.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => ITEM_HEIGHT,
    overscan: 5, // Render 5 extra items above/below viewport
  });

  if (files.length === 0) {
    return null;
  }

  const useVirtualization = files.length > VIRTUALIZATION_THRESHOLD;

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

      {useVirtualization ? (
        // Virtualized list for large file counts (>50)
        <div
          ref={parentRef}
          className="max-h-64 overflow-y-auto"
          style={{ contain: 'strict' }}
        >
          <div
            style={{
              height: `${virtualizer.getTotalSize()}px`,
              width: '100%',
              position: 'relative',
            }}
          >
            {virtualizer.getVirtualItems().map((virtualItem) => {
              const file = files[virtualItem.index];
              return (
                <div
                  key={file.id}
                  style={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    width: '100%',
                    height: `${virtualItem.size}px`,
                    transform: `translateY(${virtualItem.start}px)`,
                  }}
                >
                  <FileItem
                    file={file}
                    onRemove={() => onRemove(virtualItem.index)}
                  />
                </div>
              );
            })}
          </div>
        </div>
      ) : (
        // Simple list for small file counts (<=50)
        <div className="space-y-2 max-h-64 overflow-y-auto">
          {files.map((file, index) => (
            <FileItem
              key={file.id}
              file={file}
              onRemove={() => onRemove(index)}
            />
          ))}
        </div>
      )}
    </div>
  );
}

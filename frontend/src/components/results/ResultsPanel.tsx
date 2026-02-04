/**
 * ResultsPanel Component (Componente Panel de Resultados)
 *
 * Displays processing results and download options.
 * Muestra los resultados del procesamiento y opciones de descarga.
 */
import React from 'react';
import type { ProcessResults } from '../../types';
import { Button } from '../common/Button';
import { Card } from '../common/Card';
import { DownloadButton } from './DownloadButton';
import { ErrorList } from './ErrorList';

interface ResultsPanelProps {
  /** Processing status / Estado del procesamiento */
  status: 'pending' | 'processing' | 'completed' | 'error';
  /** Processing results / Resultados del procesamiento */
  results?: ProcessResults;
  /** Download Excel handler / Manejador de descarga Excel */
  onDownloadExcel: () => void;
  /** Download PDF handler / Manejador de descarga PDF */
  onDownloadPdf: () => void;
  /** Reset handler / Manejador de reinicio */
  onReset: () => void;
}

export function ResultsPanel({
  status,
  results,
  onDownloadExcel,
  onDownloadPdf,
  onReset,
}: ResultsPanelProps) {
  if (status === 'pending' || status === 'processing') {
    return null;
  }

  const isSuccess = status === 'completed' && results && results.errorCount === 0;
  const hasPartialSuccess = status === 'completed' && results && results.successCount > 0;

  return (
    <Card className="w-full">
      <div className="flex flex-col gap-6">
        <div className="flex items-start gap-4">
          <div
            className={`w-12 h-12 rounded-full flex items-center justify-center ${
              isSuccess ? 'bg-green-100' : 'bg-yellow-100'
            }`}
          >
            {isSuccess ? (
              <svg className="w-6 h-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            ) : (
              <svg className="w-6 h-6 text-yellow-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            )}
          </div>
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-gray-900">
              {isSuccess ? 'Procesamiento completado' : 'Procesamiento con errores'}
            </h3>
            {results && (
              <div className="flex items-center gap-4 mt-2 text-sm text-gray-600">
                <span>{results.totalFiles} archivos procesados</span>
                <span className="text-green-600">{results.successCount} exitosos</span>
                {results.errorCount > 0 && (
                  <span className="text-red-600">{results.errorCount} con errores</span>
                )}
              </div>
            )}
          </div>
        </div>
        {results && results.errors.length > 0 && <ErrorList errors={results.errors} />}
        {hasPartialSuccess && (
          <div className="flex flex-wrap gap-3 pt-4 border-t border-gray-100">
            <DownloadButton type="excel" onClick={onDownloadExcel} />
            <DownloadButton type="pdf" onClick={onDownloadPdf} />
            <Button variant="secondary" onClick={onReset}>
              Procesar más archivos
            </Button>
          </div>
        )}
        {!hasPartialSuccess && (
          <div className="pt-4 border-t border-gray-100">
            <Button variant="primary" onClick={onReset}>
              Intentar de nuevo
            </Button>
          </div>
        )}
      </div>
    </Card>
  );
}

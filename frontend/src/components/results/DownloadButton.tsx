/**
 * DownloadButton Component (Componente Botón de Descarga)
 *
 * Styled button for downloading processed files.
 * Botón estilizado para descargar archivos procesados.
 */
import React from 'react';

interface DownloadButtonProps {
  /** Download type / Tipo de descarga */
  type: 'excel' | 'pdf';
  /** Disabled state / Estado deshabilitado */
  disabled?: boolean;
  /** Click handler / Manejador de click */
  onClick: () => void;
}

const typeConfig = {
  excel: {
    icon: 'M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
    label: 'Descargar Excel',
    bg: 'bg-green-600 hover:bg-green-700',
    ring: 'focus:ring-green-500',
  },
  pdf: {
    icon: 'M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z',
    label: 'Descargar PDF',
    bg: 'bg-red-600 hover:bg-red-700',
    ring: 'focus:ring-red-500',
  },
};

export function DownloadButton({ type, disabled = false, onClick }: DownloadButtonProps) {
  const config = typeConfig[type];

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`
        inline-flex items-center gap-2 px-4 py-2
        text-white font-medium rounded-lg
        transition-colors duration-200
        focus:outline-none focus:ring-2 focus:ring-offset-2
        disabled:opacity-50 disabled:cursor-not-allowed
        ${config.bg} ${config.ring}
      `}
    >
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={config.icon} />
      </svg>
      {config.label}
    </button>
  );
}

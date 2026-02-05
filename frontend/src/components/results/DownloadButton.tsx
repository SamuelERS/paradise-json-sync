/**
 * DownloadButton Component (Componente Botón de Descarga)
 *
 * Styled button for downloading processed files with loading state.
 * Botón estilizado para descargar archivos procesados con estado de carga.
 */

interface DownloadButtonProps {
  /** Download type / Tipo de descarga */
  type: 'excel' | 'pdf' | 'json';
  /** Disabled state / Estado deshabilitado */
  disabled?: boolean;
  /** Loading state / Estado de carga */
  isLoading?: boolean;
  /** Click handler / Manejador de click */
  onClick: () => void;
}

const typeConfig = {
  excel: {
    icon: 'M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
    label: 'Descargar Excel',
    loadingLabel: 'Descargando...',
    bg: 'bg-green-600 hover:bg-green-700',
    ring: 'focus:ring-green-500',
  },
  pdf: {
    icon: 'M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z',
    label: 'Descargar PDF',
    loadingLabel: 'Descargando...',
    bg: 'bg-red-600 hover:bg-red-700',
    ring: 'focus:ring-red-500',
  },
  json: {
    icon: 'M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4',
    label: 'Descargar JSON',
    loadingLabel: 'Descargando...',
    bg: 'bg-blue-600 hover:bg-blue-700',
    ring: 'focus:ring-blue-500',
  },
};

export function DownloadButton({ type, disabled = false, isLoading = false, onClick }: DownloadButtonProps) {
  const config = typeConfig[type];

  return (
    <button
      onClick={onClick}
      disabled={disabled || isLoading}
      className={`
        inline-flex items-center gap-2 px-4 py-2
        text-white font-medium rounded-lg
        transition-colors duration-200
        focus:outline-none focus:ring-2 focus:ring-offset-2
        disabled:opacity-50 disabled:cursor-not-allowed
        ${config.bg} ${config.ring}
      `}
    >
      {isLoading ? (
        <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
        </svg>
      ) : (
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={config.icon} />
        </svg>
      )}
      {isLoading ? config.loadingLabel : config.label}
    </button>
  );
}

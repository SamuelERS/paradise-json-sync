/**
 * ProgressBar Component (Componente Barra de Progreso)
 *
 * Visual progress indicator with multiple states.
 * Indicador visual de progreso con múltiples estados.
 */

interface ProgressBarProps {
  /** Progress percentage (0-100) / Porcentaje de progreso */
  progress: number;
  /** Current status / Estado actual */
  status?: 'idle' | 'loading' | 'success' | 'error';
  /** Show percentage text / Mostrar texto de porcentaje */
  showPercentage?: boolean;
  /** Additional CSS classes / Clases CSS adicionales */
  className?: string;
}

const statusColors = {
  idle: 'bg-gray-400',
  loading: 'bg-primary',
  success: 'bg-green-500',
  error: 'bg-red-500',
};

export function ProgressBar({
  progress,
  status = 'idle',
  showPercentage = false,
  className = '',
}: ProgressBarProps) {
  const clampedProgress = Math.min(100, Math.max(0, progress));

  return (
    <div className={`w-full ${className}`}>
      <div className="flex items-center gap-2">
        <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
          <div
            className={`h-full transition-all duration-300 ease-out ${statusColors[status]}`}
            style={{ width: `${clampedProgress}%` }}
            role="progressbar"
            aria-valuenow={clampedProgress}
            aria-valuemin={0}
            aria-valuemax={100}
          />
        </div>
        {showPercentage && (
          <span className="text-sm text-gray-600 min-w-[3rem] text-right">
            {Math.round(clampedProgress)}%
          </span>
        )}
      </div>
    </div>
  );
}

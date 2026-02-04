/**
 * Alert Component (Componente de Alerta)
 *
 * Displays messages to users with different severity levels.
 * Muestra mensajes a usuarios con diferentes niveles de severidad.
 */
import React from 'react';

interface AlertProps {
  /** Alert type / Tipo de alerta */
  type: 'info' | 'success' | 'warning' | 'error';
  /** Alert title / Título de la alerta */
  title?: string;
  /** Alert message / Mensaje de la alerta */
  message: string;
  /** Close handler / Manejador de cierre */
  onClose?: () => void;
  /** Additional CSS classes / Clases CSS adicionales */
  className?: string;
}

const typeStyles = {
  info: {
    bg: 'bg-blue-50 border-blue-200',
    text: 'text-blue-800',
    icon: 'text-blue-500',
  },
  success: {
    bg: 'bg-green-50 border-green-200',
    text: 'text-green-800',
    icon: 'text-green-500',
  },
  warning: {
    bg: 'bg-yellow-50 border-yellow-200',
    text: 'text-yellow-800',
    icon: 'text-yellow-500',
  },
  error: {
    bg: 'bg-red-50 border-red-200',
    text: 'text-red-800',
    icon: 'text-red-500',
  },
};

const icons = {
  info: 'M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z',
  success: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z',
  warning: 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z',
  error: 'M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z',
};

export function Alert({ type, title, message, onClose, className = '' }: AlertProps) {
  const styles = typeStyles[type];

  return (
    <div className={`border rounded-lg p-4 ${styles.bg} ${className}`} role="alert">
      <div className="flex items-start gap-3">
        <svg
          className={`w-5 h-5 flex-shrink-0 ${styles.icon}`}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={icons[type]} />
        </svg>
        <div className="flex-1">
          {title && <h4 className={`font-medium ${styles.text}`}>{title}</h4>}
          <p className={`text-sm ${styles.text} ${title ? 'mt-1' : ''}`}>{message}</p>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className={`${styles.text} hover:opacity-70`}
            aria-label="Cerrar alerta"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        )}
      </div>
    </div>
  );
}

/**
 * Button Component (Componente Botón)
 *
 * Reusable button with multiple variants and states.
 * Botón reutilizable con múltiples variantes y estados.
 */
import React from 'react';
import { Spinner } from './Spinner';

interface ButtonProps {
  /** Button style variant / Variante de estilo */
  variant?: 'primary' | 'secondary' | 'danger';
  /** Size of the button / Tamaño del botón */
  size?: 'sm' | 'md' | 'lg';
  /** Disabled state / Estado deshabilitado */
  disabled?: boolean;
  /** Loading state / Estado de carga */
  loading?: boolean;
  /** Click handler / Manejador de click */
  onClick?: () => void;
  /** Button type / Tipo de botón */
  type?: 'button' | 'submit' | 'reset';
  /** Additional CSS classes / Clases CSS adicionales */
  className?: string;
  /** Button content / Contenido del botón */
  children: React.ReactNode;
}

const variantStyles = {
  primary: 'bg-primary hover:bg-indigo-700 text-white focus:ring-primary',
  secondary: 'bg-gray-200 hover:bg-gray-300 text-gray-800 focus:ring-gray-400',
  danger: 'bg-red-600 hover:bg-red-700 text-white focus:ring-red-500',
};

const sizeStyles = {
  sm: 'px-3 py-1.5 text-sm',
  md: 'px-4 py-2 text-base',
  lg: 'px-6 py-3 text-lg',
};

export function Button({
  variant = 'primary',
  size = 'md',
  disabled = false,
  loading = false,
  onClick,
  type = 'button',
  className = '',
  children,
}: ButtonProps) {
  const isDisabled = disabled || loading;

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={isDisabled}
      className={`
        inline-flex items-center justify-center gap-2
        font-medium rounded-lg
        transition-colors duration-200
        focus:outline-none focus:ring-2 focus:ring-offset-2
        disabled:opacity-50 disabled:cursor-not-allowed
        ${variantStyles[variant]}
        ${sizeStyles[size]}
        ${className}
      `.trim()}
    >
      {loading && <Spinner size="sm" />}
      {children}
    </button>
  );
}

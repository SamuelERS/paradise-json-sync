/**
 * Container Component (Componente Contenedor)
 *
 * Centered container with max-width for content.
 * Contenedor centrado con ancho máximo para contenido.
 */
import React from 'react';

interface ContainerProps {
  /** Container size / Tamaño del contenedor */
  size?: 'sm' | 'md' | 'lg' | 'xl';
  /** Additional CSS classes / Clases CSS adicionales */
  className?: string;
  /** Container content / Contenido del contenedor */
  children: React.ReactNode;
}

const sizeStyles = {
  sm: 'max-w-2xl',
  md: 'max-w-3xl',
  lg: 'max-w-5xl',
  xl: 'max-w-7xl',
};

export function Container({ size = 'lg', className = '', children }: ContainerProps) {
  return (
    <div className={`${sizeStyles[size]} mx-auto px-4 sm:px-6 lg:px-8 ${className}`}>
      {children}
    </div>
  );
}

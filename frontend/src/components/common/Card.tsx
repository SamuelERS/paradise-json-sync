/**
 * Card Component (Componente Tarjeta)
 *
 * Container with shadow and rounded corners.
 * Contenedor con sombra y esquinas redondeadas.
 */
import React from 'react';

interface CardProps {
  /** Card title / Título de la tarjeta */
  title?: string;
  /** Additional CSS classes / Clases CSS adicionales */
  className?: string;
  /** Card content / Contenido de la tarjeta */
  children: React.ReactNode;
}

export function Card({ title, className = '', children }: CardProps) {
  return (
    <div className={`bg-white rounded-xl shadow-md overflow-hidden ${className}`}>
      {title && (
        <div className="px-6 py-4 border-b border-gray-100">
          <h3 className="text-lg font-semibold text-gray-800">{title}</h3>
        </div>
      )}
      <div className="p-6">{children}</div>
    </div>
  );
}

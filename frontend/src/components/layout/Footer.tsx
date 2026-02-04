/**
 * Footer Component (Componente Pie de Página)
 *
 * Page footer with copyright and links.
 * Pie de página con copyright y enlaces.
 */
import React from 'react';

export function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-gray-50 border-t border-gray-200">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-sm text-gray-500">
            {currentYear} Paradise JSON Sync. All rights reserved.
          </p>
          <div className="flex items-center gap-6">
            <a
              href="#help"
              className="text-sm text-gray-500 hover:text-primary transition-colors"
            >
              Ayuda
            </a>
            <a
              href="#docs"
              className="text-sm text-gray-500 hover:text-primary transition-colors"
            >
              Documentación
            </a>
            <span className="text-sm text-gray-400">v0.1.0</span>
          </div>
        </div>
      </div>
    </footer>
  );
}

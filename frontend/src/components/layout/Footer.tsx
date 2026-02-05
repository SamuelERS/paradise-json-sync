/**
 * Footer Component (Componente Pie de Página)
 *
 * Paradise-SystemLabs distinctive footer with signature message.
 * Pie de página distintivo de Paradise-SystemLabs con mensaje característico.
 */

export function Footer() {
  return (
    <footer className="bg-gray-900 border-t border-gray-700">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
        <div className="flex items-center justify-between text-sm">
          {/* Izquierda - Logo/Nombre */}
          <span className="text-gray-200 font-medium">
            Paradise-SystemLabs
          </span>

          {/* Centro - Distintivo */}
          <span className="text-gray-200 font-medium">
            #JesucristoEsDios <span className="text-red-500" aria-hidden="true">♥️</span>
          </span>

          {/* Derecha - Versión */}
          <span className="text-gray-400">
            Version: v0.1.0
          </span>
        </div>
      </div>
    </footer>
  );
}

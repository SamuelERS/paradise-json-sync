/**
 * Header Component (Componente Encabezado)
 *
 * Fixed header with logo and navigation.
 * Encabezado fijo con logo y navegación.
 */

interface HeaderProps {
  /** Application title / Título de la aplicación */
  title?: string;
}

export function Header({ title = 'Paradise JSON Sync' }: HeaderProps) {
  return (
    <header className="fixed top-0 left-0 right-0 bg-gray-900 z-50">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
              <svg
                className="w-5 h-5 text-white"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                aria-label="Paradise JSON Sync Logo"
                role="img"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4"
                />
              </svg>
            </div>
            <h1 className="text-xl font-bold text-white">{title}</h1>
          </div>
          <nav className="flex items-center gap-4">
            <span className="text-sm text-gray-300">v0.1.0</span>
          </nav>
        </div>
      </div>
      {/* Línea de acento con gradiente */}
      <div className="h-0.5 bg-gradient-to-r from-primary via-purple-500 to-secondary" />
    </header>
  );
}

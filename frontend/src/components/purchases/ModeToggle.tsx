/**
 * ModeToggle Component / Componente Toggle de Modo
 *
 * Toggle tabs to switch between Ventas (sales) and Compras (purchases) mode.
 */

interface ModeToggleProps {
  activeMode: 'ventas' | 'compras';
  onModeChange: (mode: 'ventas' | 'compras') => void;
}

export function ModeToggle({ activeMode, onModeChange }: ModeToggleProps) {
  return (
    <div className="flex gap-2 bg-gray-100 p-1 rounded-lg w-fit mx-auto mb-6">
      <button
        type="button"
        onClick={() => onModeChange('ventas')}
        className={`
          px-5 py-2.5 rounded-md text-sm font-medium transition-colors duration-200
          ${activeMode === 'ventas'
            ? 'bg-blue-600 text-white shadow-sm'
            : 'bg-transparent text-gray-600 hover:text-gray-800 hover:bg-gray-200'
          }
        `.trim()}
      >
        Facturas Emitidas
      </button>
      <button
        type="button"
        onClick={() => onModeChange('compras')}
        className={`
          px-5 py-2.5 rounded-md text-sm font-medium transition-colors duration-200
          ${activeMode === 'compras'
            ? 'bg-green-700 text-white shadow-sm'
            : 'bg-transparent text-gray-600 hover:text-gray-800 hover:bg-gray-200'
          }
        `.trim()}
      >
        Facturas Recibidas
      </button>
    </div>
  );
}

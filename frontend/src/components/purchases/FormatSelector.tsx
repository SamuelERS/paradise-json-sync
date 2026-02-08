/**
 * FormatSelector Component / Componente Selector de Formato
 *
 * Selector for output format (xlsx, csv, pdf, json).
 */

interface FormatSelectorProps {
  value: string;
  onChange: (format: string) => void;
}

const FORMATS = [
  { id: 'xlsx', label: 'Excel', icon: 'M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z' },
  { id: 'csv', label: 'CSV', icon: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z' },
  { id: 'pdf', label: 'PDF', icon: 'M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z' },
  { id: 'json', label: 'JSON', icon: 'M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4' },
];

export function FormatSelector({ value, onChange }: FormatSelectorProps) {
  return (
    <div>
      <h4 className="text-sm font-medium text-gray-700 mb-3">Formato de salida</h4>
      <div className="flex flex-wrap gap-3">
        {FORMATS.map((format) => (
          <button
            key={format.id}
            type="button"
            onClick={() => onChange(format.id)}
            className={`
              flex items-center gap-2 px-4 py-2.5 rounded-lg border-2 text-sm font-medium
              transition-colors duration-200
              ${value === format.id
                ? 'border-green-700 bg-green-50 text-green-700'
                : 'border-gray-200 bg-white text-gray-600 hover:border-gray-300'
              }
            `.trim()}
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={format.icon} />
            </svg>
            {format.label}
          </button>
        ))}
      </div>
    </div>
  );
}

/**
 * ColumnConfigurator Component / Componente Configurador de Columnas
 *
 * Configures which columns to include in the purchase export,
 * with predefined profiles and per-category checkboxes.
 */
import type { ColumnDef } from '../../types';

interface ColumnConfiguratorProps {
  columns: ColumnDef[];
  selectedColumns: string[];
  onColumnsChange: (columns: string[]) => void;
}

/** All 32 columns grouped by category */
export const PURCHASE_COLUMNS: ColumnDef[] = [
  // Identificación (7)
  { id: 'control_number', label: 'Número de Control', category: 'Identificación' },
  { id: 'document_number', label: 'Número de Documento', category: 'Identificación' },
  { id: 'document_type', label: 'Tipo de Documento', category: 'Identificación' },
  { id: 'issue_date', label: 'Fecha de Emisión', category: 'Identificación' },
  { id: 'emission_time', label: 'Hora de Emisión', category: 'Identificación' },
  { id: 'currency', label: 'Moneda', category: 'Identificación' },
  { id: 'dte_version', label: 'Versión DTE', category: 'Identificación' },
  // Proveedor (8)
  { id: 'supplier_name', label: 'Nombre del Proveedor', category: 'Proveedor' },
  { id: 'supplier_commercial', label: 'Nombre Comercial', category: 'Proveedor' },
  { id: 'supplier_nit', label: 'NIT Proveedor', category: 'Proveedor' },
  { id: 'supplier_nrc', label: 'NRC Proveedor', category: 'Proveedor' },
  { id: 'supplier_activity', label: 'Actividad Económica', category: 'Proveedor' },
  { id: 'supplier_address', label: 'Dirección Proveedor', category: 'Proveedor' },
  { id: 'supplier_phone', label: 'Teléfono Proveedor', category: 'Proveedor' },
  { id: 'supplier_email', label: 'Correo Proveedor', category: 'Proveedor' },
  // Receptor (3)
  { id: 'receiver_name', label: 'Nombre Receptor', category: 'Receptor' },
  { id: 'receiver_nit', label: 'NIT Receptor', category: 'Receptor' },
  { id: 'receiver_nrc', label: 'NRC Receptor', category: 'Receptor' },
  // Montos (9)
  { id: 'total_taxable', label: 'Total Gravado', category: 'Montos' },
  { id: 'total_exempt', label: 'Total Exento', category: 'Montos' },
  { id: 'total_non_subject', label: 'Total No Sujeto', category: 'Montos' },
  { id: 'total_discount', label: 'Total Descuento', category: 'Montos' },
  { id: 'subtotal', label: 'Subtotal', category: 'Montos' },
  { id: 'tax', label: 'IVA', category: 'Montos' },
  { id: 'iva_retained', label: 'IVA Retenido', category: 'Montos' },
  { id: 'total', label: 'Total', category: 'Montos' },
  { id: 'total_in_words', label: 'Total en Letras', category: 'Montos' },
  // Pago y Metadatos (5)
  { id: 'payment_condition', label: 'Condición de Pago', category: 'Pago y Metadatos' },
  { id: 'tax_seal', label: 'Sello Fiscal', category: 'Pago y Metadatos' },
  { id: 'source_file', label: 'Archivo Fuente', category: 'Pago y Metadatos' },
  { id: 'detected_format', label: 'Formato Detectado', category: 'Pago y Metadatos' },
  { id: 'detection_confidence', label: 'Confianza Detección', category: 'Pago y Metadatos' },
];

/** Predefined profiles */
export const PROFILE_BASICO: string[] = [
  'control_number', 'document_type', 'issue_date', 'supplier_name',
  'supplier_nit', 'subtotal', 'tax', 'total', 'payment_condition', 'source_file',
];

export const PROFILE_COMPLETO: string[] = PURCHASE_COLUMNS.map((c) => c.id);

export const PROFILE_CONTADOR: string[] = [
  'control_number', 'document_type', 'issue_date', 'emission_time',
  'supplier_name', 'supplier_nit', 'supplier_nrc', 'receiver_nit',
  'total_taxable', 'total_exempt', 'total_non_subject', 'total_discount',
  'subtotal', 'tax', 'total',
];

type ProfileName = 'basico' | 'completo' | 'contador' | 'personalizar';

function getActiveProfile(selectedColumns: string[]): ProfileName {
  const sorted = [...selectedColumns].sort();
  const basicSorted = [...PROFILE_BASICO].sort();
  const completeSorted = [...PROFILE_COMPLETO].sort();
  const contadorSorted = [...PROFILE_CONTADOR].sort();

  if (sorted.length === basicSorted.length && sorted.every((v, i) => v === basicSorted[i])) return 'basico';
  if (sorted.length === completeSorted.length && sorted.every((v, i) => v === completeSorted[i])) return 'completo';
  if (sorted.length === contadorSorted.length && sorted.every((v, i) => v === contadorSorted[i])) return 'contador';
  return 'personalizar';
}

/** Group columns by category */
function groupByCategory(columns: ColumnDef[]): Map<string, ColumnDef[]> {
  const groups = new Map<string, ColumnDef[]>();
  for (const col of columns) {
    const existing = groups.get(col.category) || [];
    existing.push(col);
    groups.set(col.category, existing);
  }
  return groups;
}

export function ColumnConfigurator({
  columns,
  selectedColumns,
  onColumnsChange,
}: ColumnConfiguratorProps) {
  const activeProfile = getActiveProfile(selectedColumns);
  const categories = groupByCategory(columns);

  const handleProfileChange = (profile: ProfileName) => {
    switch (profile) {
      case 'basico':
        onColumnsChange([...PROFILE_BASICO]);
        break;
      case 'completo':
        onColumnsChange([...PROFILE_COMPLETO]);
        break;
      case 'contador':
        onColumnsChange([...PROFILE_CONTADOR]);
        break;
      case 'personalizar':
        // Keep current selection
        break;
    }
  };

  const handleToggleColumn = (columnId: string) => {
    if (selectedColumns.includes(columnId)) {
      onColumnsChange(selectedColumns.filter((c) => c !== columnId));
    } else {
      onColumnsChange([...selectedColumns, columnId]);
    }
  };

  const handleSelectAll = () => {
    onColumnsChange(columns.map((c) => c.id));
  };

  const handleDeselectAll = () => {
    onColumnsChange([]);
  };

  const profiles: Array<{ id: ProfileName; label: string }> = [
    { id: 'basico', label: 'Básico' },
    { id: 'completo', label: 'Completo' },
    { id: 'contador', label: 'Contador' },
    { id: 'personalizar', label: 'Personalizar' },
  ];

  return (
    <div>
      <h4 className="text-sm font-medium text-gray-700 mb-3">Perfil de columnas</h4>

      {/* Profile buttons */}
      <div className="flex flex-wrap gap-2 mb-4">
        {profiles.map((profile) => (
          <button
            key={profile.id}
            type="button"
            onClick={() => handleProfileChange(profile.id)}
            className={`
              px-3 py-1.5 rounded-md text-sm font-medium transition-colors duration-200
              ${activeProfile === profile.id
                ? 'bg-green-700 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }
            `.trim()}
          >
            {profile.label}
          </button>
        ))}
      </div>

      {/* Select all / Deselect all */}
      <div className="flex gap-3 mb-4">
        <button
          type="button"
          onClick={handleSelectAll}
          className="text-xs text-green-700 hover:text-green-800 font-medium"
        >
          Seleccionar Todo
        </button>
        <button
          type="button"
          onClick={handleDeselectAll}
          className="text-xs text-gray-500 hover:text-gray-700 font-medium"
        >
          Deseleccionar Todo
        </button>
      </div>

      {/* Columns by category */}
      <div className="space-y-4">
        {Array.from(categories.entries()).map(([category, cols]) => (
          <div key={category}>
            <h5 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
              {category}
            </h5>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-1">
              {cols.map((col) => (
                <label
                  key={col.id}
                  className="flex items-center gap-2 py-1 px-2 rounded hover:bg-gray-50 cursor-pointer text-sm"
                >
                  <input
                    type="checkbox"
                    checked={selectedColumns.includes(col.id)}
                    onChange={() => handleToggleColumn(col.id)}
                    className="rounded border-gray-300 text-green-700 focus:ring-green-600"
                  />
                  <span className="text-gray-700">{col.label}</span>
                </label>
              ))}
            </div>
          </div>
        ))}
      </div>

      <p className="text-xs text-gray-400 mt-3">
        {selectedColumns.length} de {columns.length} columnas seleccionadas
      </p>
    </div>
  );
}

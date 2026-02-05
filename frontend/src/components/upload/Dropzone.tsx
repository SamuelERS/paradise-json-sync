/**
 * Dropzone Component (Componente Zona de Arrastre)
 * Drag and drop area for file uploads. / Área de arrastrar y soltar para carga de archivos.
 */
import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { MAX_FILES } from '../../config/constants';

interface DropzoneProps {
  /** Callback when files are selected / Callback cuando se seleccionan archivos */
  onFilesSelected: (_files: File[]) => void;
  /** Accepted file types / Tipos de archivo aceptados */
  acceptedTypes?: string[];
  /** Maximum number of files / Número máximo de archivos */
  maxFiles?: number;
  /** Disabled state / Estado deshabilitado */
  disabled?: boolean;
}

const ICON_PATH = 'M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12';

export function Dropzone({
  onFilesSelected, acceptedTypes = ['.json', '.pdf'], maxFiles = MAX_FILES, disabled = false,
}: DropzoneProps) {
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback((acceptedFiles: File[], rejectedFiles: unknown[]) => {
    setError(null);
    if (rejectedFiles.length > 0) {
      setError(`Algunos archivos no son válidos. Solo se aceptan archivos ${acceptedTypes.join(', ')}.`);
      return;
    }
    if (acceptedFiles.length > maxFiles) {
      setError(`Máximo ${maxFiles} archivos permitidos.`);
      return;
    }
    onFilesSelected(acceptedFiles);
  }, [onFilesSelected, maxFiles, acceptedTypes]);

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept: { 'application/json': ['.json'], 'application/pdf': ['.pdf'] },
    maxFiles,
    disabled,
  });

  const getBorderColor = () => {
    if (disabled) return 'border-gray-200 bg-gray-50';
    if (isDragReject) return 'border-red-400 bg-red-50';
    if (isDragActive) return 'border-primary bg-indigo-50';
    return 'border-gray-300 hover:border-primary';
  };

  return (
    <div className="w-full">
      <div {...getRootProps()} className={`group relative border-2 border-dashed rounded-xl p-8 transition-all duration-300 cursor-pointer hover:shadow-lg hover:shadow-primary/10 ${getBorderColor()} ${disabled ? 'cursor-not-allowed' : ''}`}>
        <input {...getInputProps()} />
        <div className="flex flex-col items-center gap-4 text-center">
          <div className={`w-16 h-16 rounded-full flex items-center justify-center transition-transform duration-300 group-hover:scale-110 ${isDragActive ? 'bg-primary' : 'bg-primary/10'}`}>
            <svg className={`w-8 h-8 ${isDragActive ? 'text-white' : 'text-primary'}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-label="Icono de carga de archivos" role="img">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={ICON_PATH} />
            </svg>
          </div>
          <div>
            <p className="text-lg font-medium text-gray-700">{isDragActive ? 'Suelta los archivos aquí' : 'Arrastra archivos aquí'}</p>
            <p className="text-sm text-gray-500 mt-1">o <span className="text-primary font-medium">haz clic para seleccionar</span></p>
          </div>
          <div className="flex items-center gap-4 text-xs text-gray-400">
            <span className="flex items-center gap-1"><span className="w-2 h-2 bg-green-400 rounded-full" />JSON</span>
            <span className="flex items-center gap-1"><span className="w-2 h-2 bg-red-400 rounded-full" />PDF</span>
            <span>Max: {maxFiles} archivos</span>
          </div>
        </div>
      </div>
      {error && <p className="mt-2 text-sm text-red-600">{error}</p>}
    </div>
  );
}

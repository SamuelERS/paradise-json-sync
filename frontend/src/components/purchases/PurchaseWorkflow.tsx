/**
 * PurchaseWorkflow Component / Componente Flujo de Compras
 *
 * Orchestrates the 4-step purchase processing workflow:
 * upload → configure → processing → done.
 */
import { useState, useCallback } from 'react';
import { Card, Button, Alert } from '../common';
import { ProgressBar } from '../common/ProgressBar';
import { PurchaseUpload } from './PurchaseUpload';
import { ColumnConfigurator, PURCHASE_COLUMNS, PROFILE_COMPLETO } from './ColumnConfigurator';
import { FormatSelector } from './FormatSelector';
import { usePurchaseWorkflow } from '../../hooks/usePurchaseWorkflow';
import type { PurchaseProcessOptions } from '../../types';

export function PurchaseWorkflow() {
  const {
    step,
    uploadData,
    status,
    isProcessing,
    processingProgress,
    error,
    setUploadData,
    startProcessing,
    downloadResult,
    reset,
    clearError,
  } = usePurchaseWorkflow();

  const [selectedColumns, setSelectedColumns] = useState<string[]>([...PROFILE_COMPLETO]);
  const [outputFormat, setOutputFormat] = useState('xlsx');
  const [includeSummary, setIncludeSummary] = useState(true);
  const [includeItemsSheet, setIncludeItemsSheet] = useState(false);

  const getColumnProfile = useCallback((): string => {
    const basicSorted = ['control_number', 'document_type', 'issue_date', 'supplier_name',
      'supplier_nit', 'subtotal', 'tax', 'total', 'payment_condition', 'source_file'].sort();
    const completeSorted = [...PROFILE_COMPLETO].sort();
    const contadorSorted = ['control_number', 'document_type', 'issue_date', 'emission_time',
      'supplier_name', 'supplier_nit', 'supplier_nrc', 'receiver_nit',
      'total_taxable', 'total_exempt', 'total_non_subject', 'total_discount',
      'subtotal', 'tax', 'total'].sort();

    const sorted = [...selectedColumns].sort();
    if (sorted.length === basicSorted.length && sorted.every((v, i) => v === basicSorted[i])) return 'basico';
    if (sorted.length === completeSorted.length && sorted.every((v, i) => v === completeSorted[i])) return 'completo';
    if (sorted.length === contadorSorted.length && sorted.every((v, i) => v === contadorSorted[i])) return 'contador';
    return 'custom';
  }, [selectedColumns]);

  const handleProcess = useCallback(async () => {
    if (!uploadData) return;

    const options: PurchaseProcessOptions = {
      upload_id: uploadData.upload_id,
      output_format: outputFormat,
      column_profile: getColumnProfile(),
      custom_columns: getColumnProfile() === 'custom' ? selectedColumns : undefined,
      options: {
        include_summary: includeSummary,
        include_items_sheet: includeItemsSheet,
      },
    };

    await startProcessing(options);
  }, [uploadData, outputFormat, selectedColumns, includeSummary, includeItemsSheet, startProcessing, getColumnProfile]);

  const stepLabel = status?.current_step || 'Procesando...';

  return (
    <div className="space-y-6">
      {error && (
        <Alert
          type="error"
          title="Error"
          message={error}
          onClose={clearError}
        />
      )}

      {/* Step: Upload */}
      {step === 'upload' && (
        <Card title="Cargar Facturas de Compra">
          <PurchaseUpload onUploaded={setUploadData} />
        </Card>
      )}

      {/* Step: Configure */}
      {step === 'configure' && (
        <Card title="Configuración de Exportación">
          <div className="space-y-6">
            {uploadData && (
              <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                <p className="text-sm text-green-700">
                  {uploadData.file_count} archivo{uploadData.file_count !== 1 ? 's' : ''} cargado{uploadData.file_count !== 1 ? 's' : ''}
                  {uploadData.json_count > 0 && ` (${uploadData.json_count} JSON`}
                  {uploadData.pdf_count > 0 && `${uploadData.json_count > 0 ? ', ' : ' ('}${uploadData.pdf_count} PDF`}
                  {(uploadData.json_count > 0 || uploadData.pdf_count > 0) && ')'}
                </p>
              </div>
            )}

            <ColumnConfigurator
              columns={PURCHASE_COLUMNS}
              selectedColumns={selectedColumns}
              onColumnsChange={setSelectedColumns}
            />

            <FormatSelector
              value={outputFormat}
              onChange={setOutputFormat}
            />

            {/* Additional options */}
            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-3">Opciones adicionales</h4>
              <div className="space-y-2">
                <label className="flex items-center gap-2 text-sm cursor-pointer">
                  <input
                    type="checkbox"
                    checked={includeSummary}
                    onChange={(e) => setIncludeSummary(e.target.checked)}
                    className="rounded border-gray-300 text-green-700 focus:ring-green-600"
                  />
                  <span className="text-gray-700">Incluir hoja resumen</span>
                </label>
                <label className="flex items-center gap-2 text-sm cursor-pointer">
                  <input
                    type="checkbox"
                    checked={includeItemsSheet}
                    onChange={(e) => setIncludeItemsSheet(e.target.checked)}
                    className="rounded border-gray-300 text-green-700 focus:ring-green-600"
                  />
                  <span className="text-gray-700">Incluir detalle de items</span>
                </label>
              </div>
            </div>

            <div className="flex justify-center pt-4">
              <Button
                variant="primary"
                size="lg"
                onClick={handleProcess}
                disabled={selectedColumns.length === 0}
                className="bg-green-700 hover:bg-green-800 focus:ring-green-600"
              >
                Procesar Facturas
              </Button>
            </div>
          </div>
        </Card>
      )}

      {/* Step: Processing */}
      {step === 'processing' && (
        <Card title="Procesando Facturas">
          <div className="text-center space-y-4 py-6">
            <ProgressBar
              progress={processingProgress}
              status="loading"
              showPercentage
            />
            <p className="text-sm text-gray-600">{stepLabel}</p>
            {isProcessing && (
              <p className="text-xs text-gray-400">
                Por favor espere mientras se procesan las facturas...
              </p>
            )}
          </div>
        </Card>
      )}

      {/* Step: Done */}
      {step === 'done' && (
        <Card title="Procesamiento Completado">
          <div className="space-y-4">
            {status?.result && (
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <p className="text-green-700 font-medium">
                  {status.result.invoice_count} factura{status.result.invoice_count !== 1 ? 's' : ''} procesada{status.result.invoice_count !== 1 ? 's' : ''}
                </p>
                {status.result.error_count > 0 && (
                  <p className="text-amber-600 text-sm mt-1">
                    {status.result.error_count} error{status.result.error_count !== 1 ? 'es' : ''}
                  </p>
                )}
              </div>
            )}

            {status?.result?.errors && status.result.errors.length > 0 && (
              <div className="space-y-2">
                <h4 className="text-sm font-medium text-red-700">Errores encontrados:</h4>
                {status.result.errors.map((err, i) => (
                  <div key={`${err.file}-${i}`} className="bg-red-50 border border-red-200 rounded-lg p-3">
                    <p className="text-sm font-medium text-red-800">{err.file}</p>
                    <p className="text-sm text-red-600 mt-1">{err.reason}</p>
                  </div>
                ))}
              </div>
            )}

            <div className="flex flex-wrap gap-3 justify-center pt-4">
              <Button
                variant="primary"
                size="lg"
                onClick={downloadResult}
                className="bg-green-700 hover:bg-green-800 focus:ring-green-600"
              >
                Descargar Resultado
              </Button>
              <Button
                variant="secondary"
                size="lg"
                onClick={reset}
              >
                Procesar más archivos
              </Button>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
}

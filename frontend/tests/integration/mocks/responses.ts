/**
 * Mock Response Data / Datos de Respuesta Mock
 *
 * Factory functions for generating mock API responses.
 * Funciones de fábrica para generar respuestas mock de API.
 */

/**
 * Generate unique ID for testing
 * Generar ID único para testing
 */
const generateId = (): string => {
  return `${Date.now()}-${Math.random().toString(36).substring(7)}`;
};

/**
 * Upload Response / Respuesta de Carga
 */
export interface UploadResponse {
  file_id: string;
  filename: string;
  size: number;
  type: string;
  status: 'uploaded';
  created_at: string;
}

export const mockUploadResponse = (filename: string, size = 1024): UploadResponse => ({
  file_id: generateId(),
  filename,
  size,
  type: filename.endsWith('.pdf') ? 'application/pdf' : 'application/json',
  status: 'uploaded',
  created_at: new Date().toISOString(),
});

/**
 * Process Response / Respuesta de Procesamiento
 */
export interface ProcessResponse {
  job_id: string;
  status: 'processing' | 'queued';
  file_ids: string[];
  created_at: string;
}

export const mockProcessResponse = (fileIds: string[]): ProcessResponse => ({
  job_id: generateId(),
  status: 'processing',
  file_ids: fileIds,
  created_at: new Date().toISOString(),
});

/**
 * Status Response / Respuesta de Estado
 */
export interface StatusResponse {
  job_id: string;
  status: 'queued' | 'processing' | 'completed' | 'failed';
  progress: number;
  message?: string;
  error?: string;
  files_processed?: number;
  files_total?: number;
  created_at: string;
  updated_at: string;
}

export const mockStatusResponse = (
  jobId: string,
  progress: number,
  status: StatusResponse['status'] = 'processing'
): StatusResponse => ({
  job_id: jobId,
  status,
  progress,
  message: progress < 100 ? 'Processing files...' : 'Processing complete',
  files_processed: Math.floor(progress / 100 * 2),
  files_total: 2,
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
});

export const mockStatusCompletedResponse = (jobId: string): StatusResponse => ({
  job_id: jobId,
  status: 'completed',
  progress: 100,
  message: 'Processing complete. Ready for download.',
  files_processed: 2,
  files_total: 2,
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
});

export const mockStatusFailedResponse = (jobId: string, error: string): StatusResponse => ({
  job_id: jobId,
  status: 'failed',
  progress: 0,
  error,
  files_processed: 0,
  files_total: 2,
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
});

/**
 * Error Response / Respuesta de Error
 */
export interface ErrorResponse {
  error: string;
  code: string;
  detail?: string;
  timestamp: string;
}

export const mockErrorResponse = (
  message: string,
  code: string,
  detail?: string
): ErrorResponse => ({
  error: message,
  code,
  detail,
  timestamp: new Date().toISOString(),
});

/**
 * Sample Invoice Data / Datos de Factura de Ejemplo
 */
export const sampleInvoice = {
  factura: {
    numero: 'FAC-2024-001234',
    fecha: '2024-01-15',
    fechaVencimiento: '2024-02-15',
    tipoComprobante: 'factura',
    moneda: 'USD',
  },
  emisor: {
    razonSocial: 'Test Company S.A.',
    ruc: '20123456789',
    direccion: 'Test Address 123',
    telefono: '+51 1 234 5678',
    email: 'test@company.com',
  },
  receptor: {
    razonSocial: 'Client Test S.R.L.',
    ruc: '20987654321',
    direccion: 'Client Address 456',
    telefono: '+51 1 876 5432',
    email: 'client@test.com',
  },
  items: [
    {
      codigo: 'TEST-001',
      descripcion: 'Test Service',
      cantidad: 1,
      unidadMedida: 'unidad',
      precioUnitario: 100.0,
      subtotal: 100.0,
      descuento: 0,
      igv: 18.0,
      total: 118.0,
    },
  ],
  totales: {
    subtotal: 100.0,
    descuentoTotal: 0.0,
    baseImponible: 100.0,
    igv: 18.0,
    total: 118.0,
  },
  observaciones: 'Test invoice',
  metodoPago: 'transferencia_bancaria',
  cuentaBancaria: '123-456789-0-01',
};

/**
 * Sample Invoice 2 Data / Datos de Factura de Ejemplo 2
 */
export const sampleInvoice2 = {
  factura: {
    numero: 'FAC-2024-001235',
    fecha: '2024-01-20',
    fechaVencimiento: '2024-02-20',
    tipoComprobante: 'factura',
    moneda: 'PEN',
  },
  emisor: {
    razonSocial: 'Another Company E.I.R.L.',
    ruc: '20111222333',
    direccion: 'Another Address 789',
    telefono: '+51 54 123 456',
    email: 'another@company.com',
  },
  receptor: {
    razonSocial: 'Client Two SAC',
    ruc: '20444555666',
    direccion: 'Client Two Address 321',
    telefono: '+51 54 654 321',
    email: 'clienttwo@test.com',
  },
  items: [
    {
      codigo: 'PROD-100',
      descripcion: 'Product Test',
      cantidad: 5,
      unidadMedida: 'unidad',
      precioUnitario: 50.0,
      subtotal: 250.0,
      descuento: 25.0,
      igv: 40.5,
      total: 265.5,
    },
  ],
  totales: {
    subtotal: 250.0,
    descuentoTotal: 25.0,
    baseImponible: 225.0,
    igv: 40.5,
    total: 265.5,
  },
  observaciones: 'Second test invoice',
  metodoPago: 'efectivo',
  cuentaBancaria: null,
};

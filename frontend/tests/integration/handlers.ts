/**
 * MSW Request Handlers / Manejadores de Peticiones MSW
 *
 * Mock handlers for API endpoints.
 * Manejadores mock para endpoints de API.
 */

import { http, HttpResponse, delay } from 'msw';
import {
  mockUploadResponse,
  mockProcessResponse,
  mockStatusResponse,
  mockStatusCompletedResponse,
  mockErrorResponse,
} from './mocks/responses';

// API Base URL / URL Base de API
const API_BASE = '/api/v1';

/**
 * Default handlers for all API endpoints
 * Handlers por defecto para todos los endpoints de API
 */
export const handlers = [
  /**
   * POST /api/v1/upload - File upload handler
   * POST /api/v1/upload - Handler de carga de archivos
   */
  http.post(`${API_BASE}/upload`, async ({ request }) => {
    // Simulate network delay / Simular retraso de red
    await delay(100);

    const formData = await request.formData();
    const file = formData.get('file');

    if (!file || !(file instanceof File)) {
      return HttpResponse.json(
        mockErrorResponse('No file provided', 'MISSING_FILE'),
        { status: 400 }
      );
    }

    // Check file type / Verificar tipo de archivo
    const validTypes = ['application/json', 'application/pdf'];
    if (!validTypes.includes(file.type)) {
      return HttpResponse.json(
        mockErrorResponse('Invalid file type. Only JSON and PDF are accepted.', 'INVALID_FILE_TYPE'),
        { status: 400 }
      );
    }

    // Return successful upload response
    // Retornar respuesta de carga exitosa
    return HttpResponse.json(mockUploadResponse(file.name));
  }),

  /**
   * POST /api/v1/process - Start processing handler
   * POST /api/v1/process - Handler de inicio de procesamiento
   */
  http.post(`${API_BASE}/process`, async ({ request }) => {
    await delay(100);

    const body = await request.json() as { file_ids?: string[]; options?: Record<string, unknown> };
    const { file_ids, options } = body;

    if (!file_ids || file_ids.length === 0) {
      return HttpResponse.json(
        mockErrorResponse('No files specified for processing', 'NO_FILES'),
        { status: 400 }
      );
    }

    return HttpResponse.json(mockProcessResponse(file_ids));
  }),

  /**
   * GET /api/v1/status/:jobId - Status check handler
   * GET /api/v1/status/:jobId - Handler de verificación de estado
   */
  http.get(`${API_BASE}/status/:jobId`, async ({ params }) => {
    await delay(50);

    const { jobId } = params;

    if (!jobId || jobId === 'nonexistent') {
      return HttpResponse.json(
        mockErrorResponse('Job not found', 'JOB_NOT_FOUND'),
        { status: 404 }
      );
    }

    // For testing, return completed status
    // Para testing, retornar estado completado
    // In real tests, you can override this with useHandlers()
    // En tests reales, puedes sobreescribir esto con useHandlers()
    return HttpResponse.json(mockStatusCompletedResponse(jobId as string));
  }),

  /**
   * GET /api/v1/download/:jobId - Download handler
   * GET /api/v1/download/:jobId - Handler de descarga
   */
  http.get(`${API_BASE}/download/:jobId`, async ({ params, request }) => {
    await delay(100);

    const { jobId } = params;
    const url = new URL(request.url);
    const format = url.searchParams.get('format') || 'excel';

    if (!jobId || jobId === 'nonexistent') {
      return HttpResponse.json(
        mockErrorResponse('Job not found', 'JOB_NOT_FOUND'),
        { status: 404 }
      );
    }

    // Generate mock file content based on format
    // Generar contenido de archivo mock basado en formato
    let contentType: string;
    let filename: string;
    let content: Uint8Array;

    switch (format) {
      case 'excel':
        contentType = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';
        filename = 'consolidated_invoices.xlsx';
        // Mock Excel content (minimal valid XLSX header)
        // Contenido Excel mock (header XLSX mínimo válido)
        content = new Uint8Array([0x50, 0x4B, 0x03, 0x04, 0x14, 0x00]);
        break;

      case 'pdf':
        contentType = 'application/pdf';
        filename = 'consolidated_invoices.pdf';
        // Mock PDF content (minimal valid PDF header)
        // Contenido PDF mock (header PDF mínimo válido)
        content = new Uint8Array([0x25, 0x50, 0x44, 0x46, 0x2D, 0x31, 0x2E, 0x34]);
        break;

      case 'csv':
        contentType = 'text/csv';
        filename = 'consolidated_invoices.csv';
        // Mock CSV content
        // Contenido CSV mock
        content = new TextEncoder().encode('numero,fecha,total\nFAC-001,2024-01-15,118.00');
        break;

      default:
        return HttpResponse.json(
          mockErrorResponse('Invalid format', 'INVALID_FORMAT'),
          { status: 400 }
        );
    }

    return new HttpResponse(content, {
      status: 200,
      headers: {
        'Content-Type': contentType,
        'Content-Disposition': `attachment; filename="${filename}"`,
      },
    });
  }),

  /**
   * GET /health - Health check handler
   * GET /health - Handler de verificación de salud
   */
  http.get('/health', async () => {
    return HttpResponse.json({
      status: 'healthy',
      version: '0.1.0',
      timestamp: new Date().toISOString(),
    });
  }),
];

/**
 * Handler for simulating processing in progress
 * Handler para simular procesamiento en progreso
 *
 * Use with useHandlers() to override default completed status
 * Usar con useHandlers() para sobreescribir el estado completado por defecto
 */
export const processingInProgressHandler = (jobId: string, progress: number) =>
  http.get(`${API_BASE}/status/${jobId}`, async () => {
    return HttpResponse.json(mockStatusResponse(jobId, progress));
  });

/**
 * Handler for simulating processing errors
 * Handler para simular errores de procesamiento
 */
export const processingErrorHandler = (jobId: string, errorMessage: string) =>
  http.get(`${API_BASE}/status/${jobId}`, async () => {
    return HttpResponse.json({
      job_id: jobId,
      status: 'failed',
      progress: 0,
      error: errorMessage,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    });
  });

/**
 * Handler for simulating upload errors
 * Handler para simular errores de carga
 */
export const uploadErrorHandler = (errorMessage: string) =>
  http.post(`${API_BASE}/upload`, async () => {
    return HttpResponse.json(
      mockErrorResponse(errorMessage, 'UPLOAD_ERROR'),
      { status: 500 }
    );
  });

/**
 * Handler for simulating slow network
 * Handler para simular red lenta
 */
export const slowNetworkHandler = (endpoint: string, delayMs: number) =>
  http.all(endpoint, async ({ request }) => {
    await delay(delayMs);
    // Pass through to actual handler after delay
    // Pasar al handler real después del retraso
    return new HttpResponse(null, { status: 408 }); // Timeout
  });

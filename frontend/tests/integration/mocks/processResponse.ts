/**
 * Process Response Mocks / Mocks de Respuesta de Procesamiento
 *
 * Specific mock data for process-related tests.
 * Datos mock específicos para tests relacionados con procesamiento.
 */

export { mockProcessResponse, type ProcessResponse } from './responses';

/**
 * Predefined process responses for common scenarios
 * Respuestas de procesamiento predefinidas para escenarios comunes
 */

export const processStarted = {
  job_id: 'job-001',
  status: 'processing' as const,
  file_ids: ['file-001'],
  created_at: '2024-01-15T10:30:00Z',
};

export const processStartedMultiple = {
  job_id: 'job-002',
  status: 'processing' as const,
  file_ids: ['file-001', 'file-002', 'file-003'],
  created_at: '2024-01-15T10:31:00Z',
};

export const processQueued = {
  job_id: 'job-003',
  status: 'queued' as const,
  file_ids: ['file-004'],
  created_at: '2024-01-15T10:32:00Z',
};

/**
 * Process error scenarios
 * Escenarios de error de procesamiento
 */

export const processNoFilesError = {
  error: 'No files specified for processing.',
  code: 'NO_FILES',
  timestamp: '2024-01-15T10:33:00Z',
};

export const processInvalidFilesError = {
  error: 'One or more file IDs are invalid or expired.',
  code: 'INVALID_FILES',
  timestamp: '2024-01-15T10:34:00Z',
};

export const processServerError = {
  error: 'An unexpected error occurred while starting the process.',
  code: 'PROCESS_ERROR',
  timestamp: '2024-01-15T10:35:00Z',
};

/**
 * Process response with custom options
 * Respuesta de procesamiento con opciones personalizadas
 */
export const processWithOptions = {
  job_id: 'job-004',
  status: 'processing' as const,
  file_ids: ['file-005', 'file-006'],
  options: {
    output_format: 'detailed',
    include_summary: true,
    currency_conversion: false,
  },
  created_at: '2024-01-15T10:36:00Z',
};

/**
 * Helper to create a process response with specific file IDs
 * Helper para crear una respuesta de procesamiento con IDs de archivo específicos
 */
export const createProcessResponse = (
  fileIds: string[],
  status: 'processing' | 'queued' = 'processing'
): typeof processStarted => ({
  job_id: `job-${Date.now()}`,
  status,
  file_ids: fileIds,
  created_at: new Date().toISOString(),
});

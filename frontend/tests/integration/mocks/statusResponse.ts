/**
 * Status Response Mocks / Mocks de Respuesta de Estado
 *
 * Specific mock data for status-related tests.
 * Datos mock específicos para tests relacionados con estado.
 */

export {
  mockStatusResponse,
  mockStatusCompletedResponse,
  mockStatusFailedResponse,
  type StatusResponse,
} from './responses';

/**
 * Predefined status responses for common scenarios
 * Respuestas de estado predefinidas para escenarios comunes
 */

export const statusQueued = {
  job_id: 'job-001',
  status: 'queued' as const,
  progress: 0,
  message: 'Job is queued for processing.',
  files_processed: 0,
  files_total: 2,
  created_at: '2024-01-15T10:30:00Z',
  updated_at: '2024-01-15T10:30:00Z',
};

export const statusProcessing25 = {
  job_id: 'job-001',
  status: 'processing' as const,
  progress: 25,
  message: 'Processing file 1 of 2...',
  files_processed: 0,
  files_total: 2,
  created_at: '2024-01-15T10:30:00Z',
  updated_at: '2024-01-15T10:30:30Z',
};

export const statusProcessing50 = {
  job_id: 'job-001',
  status: 'processing' as const,
  progress: 50,
  message: 'Processing file 1 of 2...',
  files_processed: 1,
  files_total: 2,
  created_at: '2024-01-15T10:30:00Z',
  updated_at: '2024-01-15T10:31:00Z',
};

export const statusProcessing75 = {
  job_id: 'job-001',
  status: 'processing' as const,
  progress: 75,
  message: 'Processing file 2 of 2...',
  files_processed: 1,
  files_total: 2,
  created_at: '2024-01-15T10:30:00Z',
  updated_at: '2024-01-15T10:31:30Z',
};

export const statusCompleted = {
  job_id: 'job-001',
  status: 'completed' as const,
  progress: 100,
  message: 'Processing complete. Ready for download.',
  files_processed: 2,
  files_total: 2,
  created_at: '2024-01-15T10:30:00Z',
  updated_at: '2024-01-15T10:32:00Z',
};

export const statusFailed = {
  job_id: 'job-001',
  status: 'failed' as const,
  progress: 25,
  error: 'Failed to parse invoice file: Invalid JSON structure.',
  files_processed: 0,
  files_total: 2,
  created_at: '2024-01-15T10:30:00Z',
  updated_at: '2024-01-15T10:30:45Z',
};

/**
 * Generate a sequence of status responses for progress simulation
 * Generar una secuencia de respuestas de estado para simulación de progreso
 */
export const statusProgressSequence = [
  statusQueued,
  statusProcessing25,
  statusProcessing50,
  statusProcessing75,
  statusCompleted,
];

/**
 * Get status response for a specific progress percentage
 * Obtener respuesta de estado para un porcentaje de progreso específico
 */
export const getStatusForProgress = (
  jobId: string,
  progress: number
): typeof statusQueued => {
  let status: 'queued' | 'processing' | 'completed' = 'processing';
  let message = 'Processing...';

  if (progress === 0) {
    status = 'queued';
    message = 'Job is queued for processing.';
  } else if (progress === 100) {
    status = 'completed';
    message = 'Processing complete. Ready for download.';
  } else if (progress < 50) {
    message = 'Processing file 1 of 2...';
  } else {
    message = 'Processing file 2 of 2...';
  }

  return {
    job_id: jobId,
    status,
    progress,
    message,
    files_processed: progress >= 50 ? 1 : 0,
    files_total: 2,
    created_at: '2024-01-15T10:30:00Z',
    updated_at: new Date().toISOString(),
  };
};

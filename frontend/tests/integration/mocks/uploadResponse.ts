/**
 * Upload Response Mocks / Mocks de Respuesta de Carga
 *
 * Specific mock data for upload-related tests.
 * Datos mock específicos para tests relacionados con carga.
 */

export { mockUploadResponse, type UploadResponse } from './responses';

/**
 * Predefined upload responses for common scenarios
 * Respuestas de carga predefinidas para escenarios comunes
 */

export const uploadedJsonFile = {
  file_id: 'json-file-001',
  filename: 'invoice.json',
  size: 2048,
  type: 'application/json',
  status: 'uploaded' as const,
  created_at: '2024-01-15T10:30:00Z',
};

export const uploadedPdfFile = {
  file_id: 'pdf-file-001',
  filename: 'invoice.pdf',
  size: 51200,
  type: 'application/pdf',
  status: 'uploaded' as const,
  created_at: '2024-01-15T10:31:00Z',
};

export const uploadedMultipleFiles = [
  {
    file_id: 'json-file-001',
    filename: 'invoice1.json',
    size: 2048,
    type: 'application/json',
    status: 'uploaded' as const,
    created_at: '2024-01-15T10:30:00Z',
  },
  {
    file_id: 'json-file-002',
    filename: 'invoice2.json',
    size: 2560,
    type: 'application/json',
    status: 'uploaded' as const,
    created_at: '2024-01-15T10:30:01Z',
  },
];

/**
 * Upload error scenarios
 * Escenarios de error de carga
 */

export const uploadInvalidTypeError = {
  error: 'Invalid file type. Only JSON and PDF are accepted.',
  code: 'INVALID_FILE_TYPE',
  timestamp: '2024-01-15T10:32:00Z',
};

export const uploadFileTooLargeError = {
  error: 'File size exceeds maximum limit of 10MB.',
  code: 'FILE_TOO_LARGE',
  timestamp: '2024-01-15T10:33:00Z',
};

export const uploadServerError = {
  error: 'An unexpected error occurred during file upload.',
  code: 'UPLOAD_ERROR',
  timestamp: '2024-01-15T10:34:00Z',
};

/**
 * Upload Service Tests / Tests del Servicio de Carga
 *
 * EN: Unit tests for the upload service.
 * ES: Tests unitarios para el servicio de carga.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import {
  validateFilesForUpload,
  getAcceptedTypes,
  createUploadFormData,
} from '../../src/services/uploadService';
import { ACCEPTED_FILE_TYPES, MAX_FILE_SIZE } from '../../src/config/constants';

// EN: Helper to create mock files with controlled size
// ES: Helper para crear archivos mock con tamaño controlado
function createMockFile(
  name: string,
  size: number = 1024,
  type: string = 'application/json'
): File {
  const blob = new Blob(['test content'], { type });
  const file = new File([blob], name, { type });
  // EN: Override size property for testing
  // ES: Sobrescribir propiedad size para testing
  Object.defineProperty(file, 'size', { value: size, writable: false });
  return file;
}

describe('Upload Service / Servicio de Carga', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('validateFilesForUpload / validarArchivosParaCarga', () => {
    it('should accept valid JSON files / debe aceptar archivos JSON válidos', () => {
      const files = [createMockFile('test.json')];
      const result = validateFilesForUpload(files);

      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });

    it('should accept valid PDF files / debe aceptar archivos PDF válidos', () => {
      const files = [createMockFile('test.pdf', 1024, 'application/pdf')];
      const result = validateFilesForUpload(files);

      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });

    it('should reject invalid file types / debe rechazar tipos de archivo inválidos', () => {
      const files = [createMockFile('test.txt', 1024, 'text/plain')];
      const result = validateFilesForUpload(files);

      expect(result.isValid).toBe(false);
      expect(result.errors.length).toBeGreaterThan(0);
    });

    it('should reject files that are too large / debe rechazar archivos muy grandes', () => {
      // EN: Create file larger than MAX_FILE_SIZE (50MB)
      // ES: Crear archivo más grande que MAX_FILE_SIZE (50MB)
      const largeFile = createMockFile('large.json', MAX_FILE_SIZE + 1);
      const result = validateFilesForUpload([largeFile]);

      expect(result.isValid).toBe(false);
      expect(result.errors.some((e) => e.includes('grande'))).toBe(true);
    });

    it('should validate multiple files / debe validar múltiples archivos', () => {
      const files = [
        createMockFile('valid.json'),
        createMockFile('invalid.txt', 1024, 'text/plain'),
      ];
      const result = validateFilesForUpload(files);

      expect(result.isValid).toBe(false);
      expect(result.errors.length).toBeGreaterThan(0);
    });

    it('should accept mix of JSON and PDF / debe aceptar mezcla de JSON y PDF', () => {
      const files = [
        createMockFile('data.json'),
        createMockFile('report.pdf', 1024, 'application/pdf'),
      ];
      const result = validateFilesForUpload(files);

      expect(result.isValid).toBe(true);
    });
  });

  describe('getAcceptedTypes / obtenerTiposAceptados', () => {
    it('should return accepted file types / debe retornar tipos de archivo aceptados', () => {
      const types = getAcceptedTypes();

      expect(types).toEqual(ACCEPTED_FILE_TYPES);
      expect(types).toContain('.json');
      expect(types).toContain('.pdf');
    });

    it('should return readonly array / debe retornar array de solo lectura', () => {
      const types = getAcceptedTypes();

      expect(Array.isArray(types)).toBe(true);
      expect(types.length).toBe(2);
    });
  });

  describe('createUploadFormData / crearFormDataDeCarga', () => {
    it('should create FormData with files / debe crear FormData con archivos', () => {
      const files = [
        createMockFile('test1.json'),
        createMockFile('test2.json'),
      ];
      const formData = createUploadFormData(files);

      expect(formData).toBeInstanceOf(FormData);
      expect(formData.getAll('files')).toHaveLength(2);
    });

    it('should handle empty file array / debe manejar array de archivos vacío', () => {
      const formData = createUploadFormData([]);

      expect(formData).toBeInstanceOf(FormData);
      expect(formData.getAll('files')).toHaveLength(0);
    });

    it('should append files with correct key / debe agregar archivos con clave correcta', () => {
      const files = [createMockFile('test.json')];
      const formData = createUploadFormData(files);

      const formFiles = formData.getAll('files');
      expect(formFiles).toHaveLength(1);
      expect((formFiles[0] as File).name).toBe('test.json');
    });
  });
});

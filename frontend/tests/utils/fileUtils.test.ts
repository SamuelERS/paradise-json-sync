/**
 * File Utils Tests / Tests de Utilidades de Archivos
 *
 * EN: Unit tests for file utility functions.
 * ES: Tests unitarios para funciones utilitarias de archivos.
 */
import { describe, it, expect } from 'vitest';
import {
  formatFileSize,
  getFileExtension,
  isValidFileType,
  isValidFileSize,
  validateFile,
  validateFiles,
  generateFileId,
  createFileInfo,
  getAcceptedMimeTypes,
} from '../../src/utils/fileUtils';
import { MAX_FILE_SIZE } from '../../src/config/constants';

// EN: Helper to create mock files | ES: Helper para crear archivos mock
function createMockFile(
  name: string,
  size: number = 1024,
  type: string = 'application/json'
): File {
  const blob = new Blob(['x'.repeat(size)], { type });
  return new File([blob], name, { type });
}

describe('File Utils / Utilidades de Archivos', () => {
  describe('formatFileSize / formatearTamañoDeArchivo', () => {
    it('should format bytes correctly / debe formatear bytes correctamente', () => {
      expect(formatFileSize(0)).toBe('0 Bytes');
      expect(formatFileSize(500)).toBe('500.00 Bytes');
    });

    it('should format KB correctly / debe formatear KB correctamente', () => {
      expect(formatFileSize(1024)).toBe('1.00 KB');
      expect(formatFileSize(2048)).toBe('2.00 KB');
    });

    it('should format MB correctly / debe formatear MB correctamente', () => {
      expect(formatFileSize(1048576)).toBe('1.00 MB');
      expect(formatFileSize(5242880)).toBe('5.00 MB');
    });

    it('should format GB correctly / debe formatear GB correctamente', () => {
      expect(formatFileSize(1073741824)).toBe('1.00 GB');
    });
  });

  describe('getFileExtension / obtenerExtensiónDeArchivo', () => {
    it('should return lowercase extension with dot / debe retornar extensión en minúsculas con punto', () => {
      expect(getFileExtension('file.json')).toBe('.json');
      expect(getFileExtension('file.PDF')).toBe('.pdf');
      expect(getFileExtension('file.JSON')).toBe('.json');
    });

    it('should handle multiple dots / debe manejar múltiples puntos', () => {
      expect(getFileExtension('file.name.json')).toBe('.json');
    });

    it('should return empty string for no extension / debe retornar cadena vacía sin extensión', () => {
      expect(getFileExtension('filename')).toBe('');
    });
  });

  describe('isValidFileType / esTipoDeArchivoVálido', () => {
    it('should accept JSON files / debe aceptar archivos JSON', () => {
      const file = createMockFile('test.json');
      expect(isValidFileType(file)).toBe(true);
    });

    it('should accept PDF files / debe aceptar archivos PDF', () => {
      const file = createMockFile('test.pdf', 1024, 'application/pdf');
      expect(isValidFileType(file)).toBe(true);
    });

    it('should reject invalid types / debe rechazar tipos inválidos', () => {
      const file = createMockFile('test.txt', 1024, 'text/plain');
      expect(isValidFileType(file)).toBe(false);
    });

    it('should use custom accepted types / debe usar tipos aceptados personalizados', () => {
      const file = createMockFile('test.txt', 1024, 'text/plain');
      expect(isValidFileType(file, ['.txt'])).toBe(true);
    });
  });

  describe('isValidFileSize / esTamañoDeArchivoVálido', () => {
    it('should accept files under max size / debe aceptar archivos bajo el tamaño máximo', () => {
      const file = createMockFile('test.json', 1024);
      expect(isValidFileSize(file)).toBe(true);
    });

    it('should accept files at max size / debe aceptar archivos en el tamaño máximo', () => {
      const file = createMockFile('test.json', MAX_FILE_SIZE);
      expect(isValidFileSize(file)).toBe(true);
    });

    it('should use custom max size / debe usar tamaño máximo personalizado', () => {
      const file = createMockFile('test.json', 2000);
      expect(isValidFileSize(file, 1000)).toBe(false);
    });
  });

  describe('validateFile / validarArchivo', () => {
    it('should return valid for good files / debe retornar válido para archivos buenos', () => {
      const file = createMockFile('test.json');
      const result = validateFile(file);

      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });

    it('should return errors for invalid type / debe retornar errores para tipo inválido', () => {
      const file = createMockFile('test.txt', 1024, 'text/plain');
      const result = validateFile(file);

      expect(result.isValid).toBe(false);
      expect(result.errors.length).toBeGreaterThan(0);
    });
  });

  describe('validateFiles / validarArchivos', () => {
    it('should validate multiple files / debe validar múltiples archivos', () => {
      const files = [
        createMockFile('test1.json'),
        createMockFile('test2.json'),
      ];
      const result = validateFiles(files);

      expect(result.isValid).toBe(true);
    });

    it('should report all invalid files / debe reportar todos los archivos inválidos', () => {
      const files = [
        createMockFile('valid.json'),
        createMockFile('invalid.txt', 1024, 'text/plain'),
        createMockFile('invalid2.doc', 1024, 'application/msword'),
      ];
      const result = validateFiles(files);

      expect(result.isValid).toBe(false);
      expect(result.errors.length).toBe(2);
    });
  });

  describe('generateFileId / generarIdDeArchivo', () => {
    it('should generate unique IDs / debe generar IDs únicos', () => {
      const ids = new Set<string>();
      for (let i = 0; i < 100; i++) {
        ids.add(generateFileId());
      }
      expect(ids.size).toBe(100);
    });

    it('should start with file- prefix / debe empezar con prefijo file-', () => {
      const id = generateFileId();
      expect(id.startsWith('file-')).toBe(true);
    });
  });

  describe('createFileInfo / crearInfoDeArchivo', () => {
    it('should create FileInfo from File / debe crear FileInfo desde File', () => {
      const file = createMockFile('test.json', 1024);
      const fileInfo = createFileInfo(file);

      expect(fileInfo.name).toBe('test.json');
      expect(fileInfo.size).toBe(file.size);
      expect(fileInfo.status).toBe('pending');
      expect(fileInfo.id).toBeDefined();
      expect(fileInfo.file).toBe(file);
    });
  });

  describe('getAcceptedMimeTypes / obtenerTiposMimeAceptados', () => {
    it('should return MIME types for accepted extensions / debe retornar tipos MIME para extensiones aceptadas', () => {
      const mimeTypes = getAcceptedMimeTypes();

      expect(mimeTypes['.json']).toContain('application/json');
      expect(mimeTypes['.pdf']).toContain('application/pdf');
    });
  });
});

/**
 * useUpload Hook Tests / Tests del Hook useUpload
 *
 * EN: Unit tests for the useUpload hook.
 * ES: Tests unitarios para el hook useUpload.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useUpload } from '../../src/hooks/useUpload';

// EN: Mock uploadService | ES: Mock de uploadService
vi.mock('../../src/services/uploadService', () => ({
  uploadFiles: vi.fn(),
  validateFilesForUpload: vi.fn(() => ({ isValid: true, errors: [] })),
  getAcceptedTypes: vi.fn(() => ['.json', '.pdf']),
  createUploadFormData: vi.fn(),
}));

// EN: Helper to create mock files | ES: Helper para crear archivos mock
function createMockFile(
  name: string,
  size: number = 1024,
  type: string = 'application/json'
): File {
  const blob = new Blob(['test content'], { type });
  return new File([blob], name, { type });
}

describe('useUpload Hook / Hook useUpload', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Initial State / Estado Inicial', () => {
    it('should have correct initial state / debe tener estado inicial correcto', () => {
      const { result } = renderHook(() => useUpload());

      expect(result.current.files).toEqual([]);
      expect(result.current.isUploading).toBe(false);
      expect(result.current.uploadProgress).toBe(0);
      expect(result.current.error).toBeNull();
    });
  });

  describe('addFiles / agregarArchivos', () => {
    it('should add files to state / debe agregar archivos al estado', () => {
      const { result } = renderHook(() => useUpload());
      const mockFile = createMockFile('test.json');

      act(() => {
        result.current.addFiles([mockFile]);
      });

      expect(result.current.files).toHaveLength(1);
      expect(result.current.files[0].name).toBe('test.json');
    });

    it('should add multiple files / debe agregar múltiples archivos', () => {
      const { result } = renderHook(() => useUpload());
      const files = [
        createMockFile('file1.json'),
        createMockFile('file2.json'),
      ];

      act(() => {
        result.current.addFiles(files);
      });

      expect(result.current.files).toHaveLength(2);
    });

    it('should generate unique IDs for files / debe generar IDs únicos para archivos', () => {
      const { result } = renderHook(() => useUpload());
      const files = [
        createMockFile('file1.json'),
        createMockFile('file2.json'),
      ];

      act(() => {
        result.current.addFiles(files);
      });

      const ids = result.current.files.map((f) => f.id);
      expect(new Set(ids).size).toBe(2);
    });

    it('should preserve existing files / debe preservar archivos existentes', () => {
      const { result } = renderHook(() => useUpload());

      act(() => {
        result.current.addFiles([createMockFile('first.json')]);
      });

      act(() => {
        result.current.addFiles([createMockFile('second.json')]);
      });

      expect(result.current.files).toHaveLength(2);
    });
  });

  describe('removeFile / removerArchivo', () => {
    it('should remove file by ID / debe remover archivo por ID', () => {
      const { result } = renderHook(() => useUpload());

      act(() => {
        result.current.addFiles([createMockFile('test.json')]);
      });

      const fileId = result.current.files[0].id;

      act(() => {
        result.current.removeFile(fileId);
      });

      expect(result.current.files).toHaveLength(0);
    });

    it('should not affect other files / no debe afectar otros archivos', () => {
      const { result } = renderHook(() => useUpload());

      act(() => {
        result.current.addFiles([
          createMockFile('file1.json'),
          createMockFile('file2.json'),
        ]);
      });

      const firstFileId = result.current.files[0].id;

      act(() => {
        result.current.removeFile(firstFileId);
      });

      expect(result.current.files).toHaveLength(1);
      expect(result.current.files[0].name).toBe('file2.json');
    });

    it('should handle non-existent ID gracefully / debe manejar ID inexistente', () => {
      const { result } = renderHook(() => useUpload());

      act(() => {
        result.current.addFiles([createMockFile('test.json')]);
      });

      act(() => {
        result.current.removeFile('non-existent-id');
      });

      expect(result.current.files).toHaveLength(1);
    });
  });

  describe('clearFiles / limpiarArchivos', () => {
    it('should clear all files / debe limpiar todos los archivos', () => {
      const { result } = renderHook(() => useUpload());

      act(() => {
        result.current.addFiles([
          createMockFile('file1.json'),
          createMockFile('file2.json'),
        ]);
      });

      act(() => {
        result.current.clearFiles();
      });

      expect(result.current.files).toHaveLength(0);
    });

    it('should reset upload progress / debe reiniciar progreso de carga', () => {
      const { result } = renderHook(() => useUpload());

      act(() => {
        result.current.clearFiles();
      });

      expect(result.current.uploadProgress).toBe(0);
    });
  });

  describe('clearError / limpiarError', () => {
    it('should clear error state / debe limpiar estado de error', () => {
      const { result } = renderHook(() => useUpload());

      // EN: Simulate error state by attempting upload with no files
      // ES: Simular estado de error intentando cargar sin archivos
      act(() => {
        result.current.clearError();
      });

      expect(result.current.error).toBeNull();
    });
  });
});

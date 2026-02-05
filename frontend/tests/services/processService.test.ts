/**
 * Process Service Tests / Tests del Servicio de Proceso
 *
 * EN: Unit tests for the process service.
 * ES: Tests unitarios para el servicio de proceso.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import {
  getDefaultOptions,
  validateProcessOptions,
  mergeProcessOptions,
  ProcessOptions,
} from '../../src/services/processService';

describe('Process Service / Servicio de Proceso', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('getDefaultOptions / obtenerOpcionesPorDefecto', () => {
    it('should return default options / debe retornar opciones por defecto', () => {
      const options = getDefaultOptions();

      expect(options).toBeDefined();
      expect(options.generateExcel).toBe(true);
      expect(options.generatePdf).toBe(false);
      expect(options.sortBy).toBe('date');
    });

    it('should return new object each time / debe retornar nuevo objeto cada vez', () => {
      const options1 = getDefaultOptions();
      const options2 = getDefaultOptions();

      expect(options1).not.toBe(options2);
      expect(options1).toEqual(options2);
    });
  });

  describe('validateProcessOptions / validarOpcionesDeProceso', () => {
    it('should validate correct options / debe validar opciones correctas', () => {
      const options: ProcessOptions = {
        generateExcel: true,
        generatePdf: false,
        sortBy: 'date',
      };

      expect(validateProcessOptions(options)).toBe(true);
    });

    it('should validate all sortBy options / debe validar todas las opciones de sortBy', () => {
      const sortOptions: ProcessOptions['sortBy'][] = [
        'date',
        'amount',
        'provider',
        'none',
      ];

      sortOptions.forEach((sortBy) => {
        const options: ProcessOptions = {
          generateExcel: true,
          generatePdf: false,
          sortBy,
        };
        expect(validateProcessOptions(options)).toBe(true);
      });
    });

    it('should reject when no output format selected / debe rechazar cuando no hay formato de salida', () => {
      const options: ProcessOptions = {
        generateExcel: false,
        generatePdf: false,
        sortBy: 'date',
      };

      expect(validateProcessOptions(options)).toBe(false);
    });

    it('should accept when both formats selected / debe aceptar cuando ambos formatos están seleccionados', () => {
      const options: ProcessOptions = {
        generateExcel: true,
        generatePdf: true,
        sortBy: 'date',
      };

      expect(validateProcessOptions(options)).toBe(true);
    });

    it('should reject invalid sortBy value / debe rechazar valor inválido de sortBy', () => {
      const options = {
        generateExcel: true,
        generatePdf: false,
        sortBy: 'invalid' as ProcessOptions['sortBy'],
      };

      expect(validateProcessOptions(options)).toBe(false);
    });
  });

  describe('mergeProcessOptions / combinarOpcionesDeProceso', () => {
    it('should merge partial options with defaults / debe combinar opciones parciales con defectos', () => {
      const partial = { generatePdf: true };
      const merged = mergeProcessOptions(partial);

      expect(merged.generateExcel).toBe(true); // default
      expect(merged.generatePdf).toBe(true); // overridden
      expect(merged.sortBy).toBe('date'); // default
    });

    it('should handle empty partial / debe manejar parcial vacío', () => {
      const merged = mergeProcessOptions({});

      expect(merged).toEqual(getDefaultOptions());
    });

    it('should override all options when provided / debe sobrescribir todas las opciones cuando se proveen', () => {
      const partial: ProcessOptions = {
        generateExcel: false,
        generatePdf: true,
        sortBy: 'amount',
      };
      const merged = mergeProcessOptions(partial);

      expect(merged).toEqual(partial);
    });

    it('should not mutate original defaults / no debe mutar los valores por defecto originales', () => {
      const defaults = getDefaultOptions();
      mergeProcessOptions({ generatePdf: true });
      const newDefaults = getDefaultOptions();

      expect(defaults).toEqual(newDefaults);
    });
  });
});

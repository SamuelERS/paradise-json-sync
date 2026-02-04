/**
 * Formatters Tests / Tests de Formateadores
 *
 * EN: Unit tests for formatter utility functions.
 * ES: Tests unitarios para funciones utilitarias de formateo.
 */
import { describe, it, expect } from 'vitest';
import {
  formatDate,
  formatDateTime,
  formatCurrency,
  formatPercentage,
  formatNumber,
  formatDuration,
  truncateText,
} from '../../src/utils/formatters';

describe('Formatters / Formateadores', () => {
  describe('formatDate / formatearFecha', () => {
    it('should format Date object / debe formatear objeto Date', () => {
      const date = new Date('2025-02-04T10:30:00Z');
      const formatted = formatDate(date);

      expect(formatted).toContain('2025');
      expect(formatted).toContain('4');
    });

    it('should format ISO string / debe formatear cadena ISO', () => {
      const formatted = formatDate('2025-02-04T10:30:00Z');

      expect(formatted).toContain('2025');
    });

    it('should return invalid date message for bad input / debe retornar mensaje de fecha inválida', () => {
      const formatted = formatDate('invalid-date');

      expect(formatted).toBe('Fecha inválida');
    });

    it('should use custom options / debe usar opciones personalizadas', () => {
      const date = new Date('2025-02-04');
      const formatted = formatDate(date, { year: 'numeric' });

      expect(formatted).toBe('2025');
    });
  });

  describe('formatDateTime / formatearFechaHora', () => {
    it('should include time in output / debe incluir hora en la salida', () => {
      const date = new Date('2025-02-04T10:30:00');
      const formatted = formatDateTime(date);

      expect(formatted).toContain('2025');
    });
  });

  describe('formatCurrency / formatearMoneda', () => {
    it('should format as MXN by default / debe formatear como MXN por defecto', () => {
      const formatted = formatCurrency(1234.56);

      expect(formatted).toContain('1');
      expect(formatted).toContain('234');
    });

    it('should format with custom currency / debe formatear con moneda personalizada', () => {
      const formatted = formatCurrency(1234.56, 'USD', 'en-US');

      expect(formatted).toContain('$');
      expect(formatted).toContain('1,234.56');
    });

    it('should handle zero / debe manejar cero', () => {
      const formatted = formatCurrency(0);

      expect(formatted).toContain('0');
    });

    it('should handle negative numbers / debe manejar números negativos', () => {
      const formatted = formatCurrency(-1234.56, 'USD', 'en-US');

      expect(formatted).toContain('-');
    });
  });

  describe('formatPercentage / formatearPorcentaje', () => {
    it('should format decimal as percentage / debe formatear decimal como porcentaje', () => {
      expect(formatPercentage(0.75)).toBe('75%');
      expect(formatPercentage(0.5)).toBe('50%');
      expect(formatPercentage(1)).toBe('100%');
    });

    it('should handle decimals / debe manejar decimales', () => {
      expect(formatPercentage(0.756, 1)).toBe('75.6%');
      expect(formatPercentage(0.7567, 2)).toBe('75.67%');
    });

    it('should handle non-decimal input / debe manejar entrada no decimal', () => {
      expect(formatPercentage(75, 0, false)).toBe('75%');
    });
  });

  describe('formatNumber / formatearNúmero', () => {
    it('should format with thousands separator / debe formatear con separador de miles', () => {
      const formatted = formatNumber(1234567.89, 2, 'en-US');

      expect(formatted).toContain('1,234,567');
    });

    it('should handle decimals / debe manejar decimales', () => {
      expect(formatNumber(123.456, 0, 'en-US')).toBe('123');
      expect(formatNumber(123.456, 2, 'en-US')).toBe('123.46');
    });
  });

  describe('formatDuration / formatearDuración', () => {
    it('should format milliseconds / debe formatear milisegundos', () => {
      expect(formatDuration(500)).toBe('500 ms');
    });

    it('should format seconds / debe formatear segundos', () => {
      expect(formatDuration(5000)).toBe('5 segundos');
      expect(formatDuration(1000)).toBe('1 segundo');
    });

    it('should format minutes and seconds / debe formatear minutos y segundos', () => {
      expect(formatDuration(125000)).toContain('minuto');
      expect(formatDuration(125000)).toContain('segundo');
    });

    it('should format hours / debe formatear horas', () => {
      expect(formatDuration(3700000)).toContain('hora');
    });
  });

  describe('truncateText / truncarTexto', () => {
    it('should truncate long text / debe truncar texto largo', () => {
      expect(truncateText('Hello World', 5)).toBe('Hello...');
    });

    it('should not truncate short text / no debe truncar texto corto', () => {
      expect(truncateText('Hello', 10)).toBe('Hello');
    });

    it('should handle exact length / debe manejar longitud exacta', () => {
      expect(truncateText('Hello', 5)).toBe('Hello');
    });

    it('should handle empty string / debe manejar cadena vacía', () => {
      expect(truncateText('', 5)).toBe('');
    });
  });
});

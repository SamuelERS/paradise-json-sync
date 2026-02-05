/**
 * Formatters / Formateadores
 *
 * EN: Utility functions for formatting dates, numbers, and other data types.
 * ES: Funciones utilitarias para formatear fechas, números y otros tipos de datos.
 */

/**
 * Format Date / Formatear Fecha
 *
 * EN: Formats a date to a localized string representation.
 * ES: Formatea una fecha a una representación de cadena localizada.
 *
 * @param date - Date object or ISO string / Objeto Date o cadena ISO
 * @param options - Intl.DateTimeFormat options / Opciones de Intl.DateTimeFormat
 * @returns Formatted date string / Cadena de fecha formateada
 *
 * @example
 * formatDate(new Date()) // "4 feb 2025"
 * formatDate("2025-02-04T10:30:00Z") // "4 feb 2025"
 */
export function formatDate(
  date: Date | string,
  options: Intl.DateTimeFormatOptions = {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  }
): string {
  const dateObj = typeof date === 'string' ? new Date(date) : date;

  if (isNaN(dateObj.getTime())) {
    return 'Fecha inválida';
  }

  return dateObj.toLocaleDateString('es-ES', options);
}

/**
 * Format Date Time / Formatear Fecha y Hora
 *
 * EN: Formats a date with time to a localized string.
 * ES: Formatea una fecha con hora a una cadena localizada.
 *
 * @param date - Date object or ISO string / Objeto Date o cadena ISO
 * @returns Formatted datetime string / Cadena de fecha y hora formateada
 *
 * @example
 * formatDateTime(new Date()) // "4 feb 2025, 10:30"
 */
export function formatDateTime(date: Date | string): string {
  return formatDate(date, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

/**
 * Format Currency / Formatear Moneda
 *
 * EN: Formats a number as currency (defaults to MXN).
 * ES: Formatea un número como moneda (por defecto MXN).
 *
 * @param amount - Amount to format / Cantidad a formatear
 * @param currency - Currency code / Código de moneda
 * @param locale - Locale for formatting / Localización para formateo
 * @returns Formatted currency string / Cadena de moneda formateada
 *
 * @example
 * formatCurrency(1234.56) // "$1,234.56"
 * formatCurrency(1234.56, 'USD') // "US$1,234.56"
 */
export function formatCurrency(
  amount: number,
  currency: string = 'MXN',
  locale: string = 'es-MX'
): string {
  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(amount);
}

/**
 * Format Percentage / Formatear Porcentaje
 *
 * EN: Formats a decimal value as a percentage.
 * ES: Formatea un valor decimal como porcentaje.
 *
 * @param value - Decimal value (0-1 or 0-100) / Valor decimal (0-1 o 0-100)
 * @param decimals - Number of decimal places / Número de decimales
 * @param isDecimal - If true, value is 0-1; if false, value is 0-100
 * @returns Formatted percentage string / Cadena de porcentaje formateada
 *
 * @example
 * formatPercentage(0.75) // "75%"
 * formatPercentage(75, 0, false) // "75%"
 * formatPercentage(0.756, 1) // "75.6%"
 */
export function formatPercentage(
  value: number,
  decimals: number = 0,
  isDecimal: boolean = true
): string {
  const percentage = isDecimal ? value * 100 : value;
  return `${percentage.toFixed(decimals)}%`;
}

/**
 * Format Number / Formatear Número
 *
 * EN: Formats a number with thousands separators.
 * ES: Formatea un número con separadores de miles.
 *
 * @param value - Number to format / Número a formatear
 * @param decimals - Number of decimal places / Número de decimales
 * @param locale - Locale for formatting / Localización para formateo
 * @returns Formatted number string / Cadena de número formateada
 *
 * @example
 * formatNumber(1234567.89) // "1,234,567.89"
 */
export function formatNumber(
  value: number,
  decimals: number = 2,
  locale: string = 'es-MX'
): string {
  return new Intl.NumberFormat(locale, {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value);
}

/**
 * Format Duration / Formatear Duración
 *
 * EN: Formats a duration in milliseconds to human-readable format.
 * ES: Formatea una duración en milisegundos a formato legible.
 *
 * @param ms - Duration in milliseconds / Duración en milisegundos
 * @returns Formatted duration string / Cadena de duración formateada
 *
 * @example
 * formatDuration(5000) // "5 segundos"
 * formatDuration(125000) // "2 minutos, 5 segundos"
 */
export function formatDuration(ms: number): string {
  if (ms < 1000) {
    return `${ms} ms`;
  }

  const seconds = Math.floor(ms / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);

  if (hours > 0) {
    const remainingMinutes = minutes % 60;
    return `${hours} hora${hours > 1 ? 's' : ''}, ${remainingMinutes} minuto${remainingMinutes !== 1 ? 's' : ''}`;
  }

  if (minutes > 0) {
    const remainingSeconds = seconds % 60;
    return `${minutes} minuto${minutes > 1 ? 's' : ''}, ${remainingSeconds} segundo${remainingSeconds !== 1 ? 's' : ''}`;
  }

  return `${seconds} segundo${seconds !== 1 ? 's' : ''}`;
}

/**
 * Truncate Text / Truncar Texto
 *
 * EN: Truncates text to a maximum length with ellipsis.
 * ES: Trunca texto a una longitud máxima con puntos suspensivos.
 *
 * @param text - Text to truncate / Texto a truncar
 * @param maxLength - Maximum length / Longitud máxima
 * @returns Truncated text / Texto truncado
 *
 * @example
 * truncateText("Hello World", 5) // "Hello..."
 */
export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) {
    return text;
  }
  return `${text.slice(0, maxLength)}...`;
}

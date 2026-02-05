/**
 * Config Module Exports / Exportaciones del Módulo de Configuración
 *
 * EN: Re-exports all configuration constants and types.
 * ES: Re-exporta todas las constantes y tipos de configuración.
 */
export {
  API_BASE_URL,
  API_TIMEOUT,
  ACCEPTED_FILE_TYPES,
  MAX_FILE_SIZE,
  MAX_FILES,
  POLLING_INTERVAL,
  API_ENDPOINTS,
  APP_STATUS,
  PROCESS_STATUS,
} from './constants';

export type { AppStatusType, ProcessStatusType } from './constants';

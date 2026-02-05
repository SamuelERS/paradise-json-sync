/**
 * API Client / Cliente de API
 *
 * EN: Base Axios instance configured for API communication.
 *     Includes interceptors for error handling and request configuration.
 * ES: Instancia base de Axios configurada para comunicación con la API.
 *     Incluye interceptores para manejo de errores y configuración de peticiones.
 */
import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios';
import { API_BASE_URL, API_TIMEOUT } from '../config/constants';
import { handleApiError, ApiErrorResponse } from '../utils/errorHandler';

/**
 * Create API Instance / Crear Instancia de API
 *
 * EN: Creates and configures the Axios instance with base settings.
 * ES: Crea y configura la instancia de Axios con configuraciones base.
 */
const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

/**
 * Request Interceptor / Interceptor de Petición
 *
 * EN: Adds common headers and configuration to all requests.
 * ES: Agrega headers comunes y configuración a todas las peticiones.
 */
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // EN: Add timestamp to prevent caching issues
    // ES: Agregar timestamp para prevenir problemas de caché
    if (config.params) {
      config.params._t = Date.now();
    }
    return config;
  },
  (error: AxiosError) => {
    return Promise.reject(error);
  }
);

/**
 * Response Interceptor / Interceptor de Respuesta
 *
 * EN: Handles successful responses and transforms errors.
 * ES: Maneja respuestas exitosas y transforma errores.
 */
api.interceptors.response.use(
  (response) => {
    // EN: Return full response (services access response.data)
    // ES: Retornar respuesta completa (servicios acceden a response.data)
    return response;
  },
  (error: AxiosError<ApiErrorResponse>) => {
    // EN: Transform error using centralized handler
    // ES: Transformar error usando manejador centralizado
    try {
      handleApiError(error);
    } catch (appError) {
      return Promise.reject(appError);
    }
    return Promise.reject(error);
  }
);

/**
 * API Instance Export / Exportación de Instancia de API
 *
 * EN: Export the configured Axios instance for use in services.
 * ES: Exportar la instancia de Axios configurada para uso en servicios.
 */
export default api;

/**
 * Create Form Data API / Crear API para FormData
 *
 * EN: Creates an Axios instance configured for multipart/form-data uploads.
 * ES: Crea una instancia de Axios configurada para cargas multipart/form-data.
 */
export const formDataApi: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT * 6, // EN: Extended timeout for large uploads (3 min) / ES: Timeout extendido para cargas grandes (3 min)
  headers: {
    'Accept': 'application/json',
  },
});

// EN: Apply same interceptors to formDataApi
// ES: Aplicar mismos interceptores a formDataApi
formDataApi.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    return config;
  },
  (error: AxiosError) => {
    return Promise.reject(error);
  }
);

formDataApi.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ApiErrorResponse>) => {
    try {
      handleApiError(error);
    } catch (appError) {
      return Promise.reject(appError);
    }
    return Promise.reject(error);
  }
);

/**
 * Get API Base URL / Obtener URL Base de API
 *
 * EN: Returns the configured API base URL.
 * ES: Retorna la URL base de API configurada.
 */
export function getApiBaseUrl(): string {
  return API_BASE_URL;
}

/**
 * Get API Timeout / Obtener Timeout de API
 *
 * EN: Returns the configured API timeout.
 * ES: Retorna el timeout de API configurado.
 */
export function getApiTimeout(): number {
  return API_TIMEOUT;
}

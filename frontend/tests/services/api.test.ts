/**
 * API Service Tests / Tests del Servicio API
 *
 * EN: Unit tests for the base API client configuration.
 * ES: Tests unitarios para la configuración del cliente API base.
 */
import { describe, it, expect } from 'vitest';
import api, { formDataApi, getApiBaseUrl, getApiTimeout } from '../../src/services/api';
import { API_BASE_URL, API_TIMEOUT } from '../../src/config/constants';

describe('API Client / Cliente API', () => {
  describe('Configuration / Configuración', () => {
    it('should have correct baseURL configured / debe tener baseURL correctamente configurada', () => {
      expect(getApiBaseUrl()).toBe(API_BASE_URL);
    });

    it('should have correct timeout configured / debe tener timeout correctamente configurado', () => {
      expect(getApiTimeout()).toBe(API_TIMEOUT);
    });

    it('should export api instance / debe exportar instancia api', () => {
      expect(api).toBeDefined();
    });

    it('should export formDataApi instance / debe exportar instancia formDataApi', () => {
      expect(formDataApi).toBeDefined();
    });

    it('should have api.defaults.baseURL configured / debe tener api.defaults.baseURL configurada', () => {
      expect(api.defaults.baseURL).toBe(API_BASE_URL);
    });

    it('should have api.defaults.timeout configured / debe tener api.defaults.timeout configurado', () => {
      expect(api.defaults.timeout).toBe(API_TIMEOUT);
    });

    it('should have correct Content-Type header / debe tener header Content-Type correcto', () => {
      expect(api.defaults.headers['Content-Type']).toBe('application/json');
    });

    it('should have request interceptors / debe tener interceptores de petición', () => {
      expect(api.interceptors.request).toBeDefined();
    });

    it('should have response interceptors / debe tener interceptores de respuesta', () => {
      expect(api.interceptors.response).toBeDefined();
    });
  });

  describe('formDataApi Configuration / Configuración de formDataApi', () => {
    it('should have double timeout for uploads / debe tener doble timeout para cargas', () => {
      expect(formDataApi.defaults.timeout).toBe(API_TIMEOUT * 2);
    });

    it('should have same baseURL as api / debe tener misma baseURL que api', () => {
      expect(formDataApi.defaults.baseURL).toBe(API_BASE_URL);
    });
  });
});

describe('API Constants / Constantes de API', () => {
  it('should have API_BASE_URL defined / debe tener API_BASE_URL definida', () => {
    expect(API_BASE_URL).toBeDefined();
    expect(typeof API_BASE_URL).toBe('string');
  });

  it('should have API_TIMEOUT as 30000ms / debe tener API_TIMEOUT como 30000ms', () => {
    expect(API_TIMEOUT).toBe(30000);
  });

  it('should have localhost as default baseURL / debe tener localhost como baseURL por defecto', () => {
    expect(API_BASE_URL).toContain('localhost');
  });
});

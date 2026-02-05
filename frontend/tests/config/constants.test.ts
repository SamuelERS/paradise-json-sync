/**
 * Constants Tests (Tests de Constantes)
 *
 * Tests for application configuration constants.
 * Tests para constantes de configuración de la aplicación.
 */
import { describe, it, expect } from 'vitest';
import {
  API_BASE_URL,
  API_TIMEOUT,
  ACCEPTED_FILE_TYPES,
  MAX_FILE_SIZE,
  MAX_FILES,
  POLLING_INTERVAL,
  API_ENDPOINTS,
  APP_STATUS,
  PROCESS_STATUS,
} from '../../src/config/constants';

describe('API Configuration', () => {
  describe('API_BASE_URL', () => {
    it('is a string', () => {
      expect(typeof API_BASE_URL).toBe('string');
    });
  });

  describe('API_TIMEOUT', () => {
    it('is 30 seconds', () => {
      expect(API_TIMEOUT).toBe(30000);
    });

    it('is a number', () => {
      expect(typeof API_TIMEOUT).toBe('number');
    });

    it('is positive', () => {
      expect(API_TIMEOUT).toBeGreaterThan(0);
    });
  });
});

describe('File Configuration', () => {
  describe('ACCEPTED_FILE_TYPES', () => {
    it('includes .json', () => {
      expect(ACCEPTED_FILE_TYPES).toContain('.json');
    });

    it('includes .pdf', () => {
      expect(ACCEPTED_FILE_TYPES).toContain('.pdf');
    });

    it('has exactly 2 types', () => {
      expect(ACCEPTED_FILE_TYPES.length).toBe(2);
    });

    it('is readonly array', () => {
      expect(Array.isArray(ACCEPTED_FILE_TYPES)).toBe(true);
    });
  });

  describe('MAX_FILE_SIZE', () => {
    it('is 10MB in bytes', () => {
      expect(MAX_FILE_SIZE).toBe(10 * 1024 * 1024);
    });

    it('equals 10485760 bytes', () => {
      expect(MAX_FILE_SIZE).toBe(10485760);
    });

    it('is a number', () => {
      expect(typeof MAX_FILE_SIZE).toBe('number');
    });
  });

  describe('MAX_FILES', () => {
    it('allows 500 files', () => {
      expect(MAX_FILES).toBe(500);
    });

    it('is a number', () => {
      expect(typeof MAX_FILES).toBe('number');
    });

    it('is positive', () => {
      expect(MAX_FILES).toBeGreaterThan(0);
    });
  });
});

describe('Polling Configuration', () => {
  describe('POLLING_INTERVAL', () => {
    it('is 2 seconds', () => {
      expect(POLLING_INTERVAL).toBe(2000);
    });

    it('is a number', () => {
      expect(typeof POLLING_INTERVAL).toBe('number');
    });
  });
});

describe('API_ENDPOINTS', () => {
  it('has UPLOAD endpoint', () => {
    expect(API_ENDPOINTS.UPLOAD).toBe('/api/upload');
  });

  it('has PROCESS endpoint', () => {
    expect(API_ENDPOINTS.PROCESS).toBe('/api/process');
  });

  it('has STATUS endpoint', () => {
    expect(API_ENDPOINTS.STATUS).toBe('/api/status');
  });

  it('has DOWNLOAD_EXCEL endpoint', () => {
    expect(API_ENDPOINTS.DOWNLOAD_EXCEL).toBe('/api/download/excel');
  });

  it('has DOWNLOAD_PDF endpoint', () => {
    expect(API_ENDPOINTS.DOWNLOAD_PDF).toBe('/api/download/pdf');
  });

  it('has DOWNLOAD_JSON endpoint', () => {
    expect(API_ENDPOINTS.DOWNLOAD_JSON).toBe('/api/download/json');
  });

  it('all endpoints start with /api/', () => {
    Object.values(API_ENDPOINTS).forEach((endpoint) => {
      expect(endpoint.startsWith('/api/')).toBe(true);
    });
  });

  it('has exactly 6 endpoints', () => {
    expect(Object.keys(API_ENDPOINTS).length).toBe(6);
  });
});

describe('APP_STATUS', () => {
  it('has IDLE status', () => {
    expect(APP_STATUS.IDLE).toBe('idle');
  });

  it('has UPLOADING status', () => {
    expect(APP_STATUS.UPLOADING).toBe('uploading');
  });

  it('has PROCESSING status', () => {
    expect(APP_STATUS.PROCESSING).toBe('processing');
  });

  it('has COMPLETED status', () => {
    expect(APP_STATUS.COMPLETED).toBe('completed');
  });

  it('has ERROR status', () => {
    expect(APP_STATUS.ERROR).toBe('error');
  });

  it('has exactly 5 statuses', () => {
    expect(Object.keys(APP_STATUS).length).toBe(5);
  });

  it('all values are lowercase strings', () => {
    Object.values(APP_STATUS).forEach((status) => {
      expect(status).toBe(status.toLowerCase());
      expect(typeof status).toBe('string');
    });
  });
});

describe('PROCESS_STATUS', () => {
  it('has PENDING status', () => {
    expect(PROCESS_STATUS.PENDING).toBe('pending');
  });

  it('has VALIDATING status', () => {
    expect(PROCESS_STATUS.VALIDATING).toBe('validating');
  });

  it('has EXTRACTING status', () => {
    expect(PROCESS_STATUS.EXTRACTING).toBe('extracting');
  });

  it('has CONSOLIDATING status', () => {
    expect(PROCESS_STATUS.CONSOLIDATING).toBe('consolidating');
  });

  it('has GENERATING status', () => {
    expect(PROCESS_STATUS.GENERATING).toBe('generating');
  });

  it('has COMPLETED status', () => {
    expect(PROCESS_STATUS.COMPLETED).toBe('completed');
  });

  it('has FAILED status', () => {
    expect(PROCESS_STATUS.FAILED).toBe('failed');
  });

  it('has exactly 7 statuses', () => {
    expect(Object.keys(PROCESS_STATUS).length).toBe(7);
  });

  it('all values are lowercase strings', () => {
    Object.values(PROCESS_STATUS).forEach((status) => {
      expect(status).toBe(status.toLowerCase());
      expect(typeof status).toBe('string');
    });
  });
});

describe('Constants Consistency', () => {
  it('APP_STATUS and PROCESS_STATUS have compatible COMPLETED values', () => {
    expect(APP_STATUS.COMPLETED).toBe('completed');
    expect(PROCESS_STATUS.COMPLETED).toBe('completed');
  });

  it('download endpoints exist for expected formats', () => {
    expect(API_ENDPOINTS.DOWNLOAD_EXCEL).toBeDefined();
    expect(API_ENDPOINTS.DOWNLOAD_PDF).toBeDefined();
    expect(API_ENDPOINTS.DOWNLOAD_JSON).toBeDefined();
  });
});

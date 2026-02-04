# Test Data / Datos de Prueba

This directory contains sample files for E2E testing.
Este directorio contiene archivos de ejemplo para tests E2E.

## Files / Archivos

### sample-invoice.json
A complete valid invoice with:
- Two line items (consulting service and software license)
- All required fields populated
- Currency: USD

Una factura válida completa con:
- Dos items (servicio de consultoría y licencia de software)
- Todos los campos requeridos completos
- Moneda: USD

### sample-invoice-2.json
A second valid invoice with:
- Four line items (office supplies)
- Different company data
- Currency: PEN

Una segunda factura válida con:
- Cuatro items (útiles de oficina)
- Datos de empresa diferentes
- Moneda: PEN

### invalid-invoice.json
An invalid JSON file for testing error handling:
- Missing required invoice structure
- Used to test validation errors

Un archivo JSON inválido para probar manejo de errores:
- Falta la estructura de factura requerida
- Usado para probar errores de validación

### sample.pdf
A simple one-page PDF invoice.
To generate this file, run: `node generate-pdf.js`

Un PDF de factura simple de una página.
Para generar este archivo, ejecutar: `node generate-pdf.js`

## Usage in Tests / Uso en Tests

```typescript
import { getTestDataPath } from '../utils/helpers';

// Get path to test file
const invoicePath = getTestDataPath('sample-invoice.json');

// Use in upload test
await uploadPage.uploadFile(invoicePath);
```

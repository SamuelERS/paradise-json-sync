# 08 - Estrategia de Testing (Testing Strategy)
# Testing Strategy (Estrategia de Testing - Cómo probamos que todo funciona)

---

## Observaciones Obligatorias (Mandatory Notes)

```
COBERTURA MÍNIMA OBLIGATORIA: 70%
COBERTURA IDEAL: 85%
COBERTURA LÓGICA CRÍTICA: 80%
CI/CD: Tests DEBEN pasar antes de merge
HERRAMIENTAS: pytest (Backend), Jest (Frontend)
```

---

## Por Que Testeamos (Why We Test)

**Explicación simple:**
Testear es como revisar tu mochila antes de un viaje:
- ¿Traje el pasaporte? ✓
- ¿Traje el cargador? ✓
- ¿Traje dinero? ✓

Si no revisas, puedes llegar al aeropuerto sin pasaporte.

En código:
- ¿La función suma bien? ✓
- ¿Maneja errores? ✓
- ¿No rompe otras cosas? ✓

Si no testeas, el código puede fallar en producción.

---

## Piramide de Testing (Testing Pyramid)

```
                    ┌─────┐
                    │ E2E │  ◄── Pocos, lentos, costosos
                    └─────┘
                   ┌───────┐
                   │ Integ │  ◄── Algunos, moderados
                   └───────┘
                 ┌───────────┐
                 │  Unit     │  ◄── Muchos, rápidos, baratos
                 └───────────┘

REGLA: Más tests unitarios, menos E2E
       70% Unit | 20% Integration | 10% E2E
```

---

## Tipos de Tests (Types of Tests)

### 1. Unit Tests (Pruebas Unitarias - Probar piezas individuales)

**¿Qué es?**
Probar una función o clase de forma aislada.
Como probar que un foco enciende antes de instalarlo.

**Ejemplo Backend (Python):**
```python
# tests/unit/test_json_processor.py

import pytest
from src.core.json_processor import JSONProcessor

class TestJSONProcessor:
    """
    Test JSON Processor (Pruebas del Procesador JSON)
    Verifica que el procesador lea y extraiga datos correctamente.
    """

    def test_process_valid_json(self, sample_json_data):
        """
        Test Process Valid JSON (Probar JSON Válido)
        Dado un JSON válido, debe extraer los campos correctamente.
        """
        # Arrange (Preparar)
        processor = JSONProcessor()
        json_content = sample_json_data

        # Act (Actuar)
        result = processor.process(json_content)

        # Assert (Verificar)
        assert result is not None
        assert result.document_number == "CFJ001"
        assert result.total == 100.00

    def test_process_invalid_json_raises_error(self):
        """
        Test Invalid JSON (Probar JSON Inválido)
        Dado un JSON mal formado, debe lanzar error específico.
        """
        processor = JSONProcessor()
        invalid_json = "{ esto no es json válido }"

        with pytest.raises(ValueError) as exc_info:
            processor.process(invalid_json)

        assert "JSON inválido" in str(exc_info.value)

    def test_process_missing_required_field(self):
        """
        Test Missing Field (Probar Campo Faltante)
        Si falta un campo requerido, debe indicar cuál falta.
        """
        processor = JSONProcessor()
        incomplete_json = {"fecha": "2025-01-01"}  # Falta document_number

        with pytest.raises(ValueError) as exc_info:
            processor.process(incomplete_json)

        assert "document_number" in str(exc_info.value)
```

**Ejemplo Frontend (JavaScript/Jest):**
```javascript
// tests/components/Button.test.jsx

import { render, screen, fireEvent } from '@testing-library/react';
import Button from '../../src/components/common/Button';

describe('Button Component', () => {
  /**
   * Test Button Renders (Probar que el Botón Renderiza)
   */
  test('renders with correct text', () => {
    render(<Button>Click me</Button>);

    expect(screen.getByText('Click me')).toBeInTheDocument();
  });

  /**
   * Test Click Handler (Probar Manejador de Click)
   */
  test('calls onClick when clicked', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click</Button>);

    fireEvent.click(screen.getByText('Click'));

    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  /**
   * Test Disabled State (Probar Estado Deshabilitado)
   */
  test('does not call onClick when disabled', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick} disabled>Click</Button>);

    fireEvent.click(screen.getByText('Click'));

    expect(handleClick).not.toHaveBeenCalled();
  });
});
```

**Cobertura requerida:** 70% mínimo

---

### 2. Integration Tests (Pruebas de Integración - Probar piezas juntas)

**¿Qué es?**
Probar que varias partes funcionan bien juntas.
Como probar que el foco funciona CON el interruptor.

**Ejemplo Backend (Python):**
```python
# tests/integration/test_api_endpoints.py

import pytest
from fastapi.testclient import TestClient
from src.main import app

class TestUploadEndpoint:
    """
    Test Upload Endpoint (Pruebas del Endpoint de Carga)
    Verifica el flujo completo de subir archivos.
    """

    @pytest.fixture
    def client(self):
        """Cliente de prueba para hacer requests"""
        return TestClient(app)

    def test_upload_single_json_file(self, client, sample_json_file):
        """
        Test Upload JSON (Probar Carga de JSON)
        Subir un archivo JSON debe retornar job_id.
        """
        # Arrange
        files = {"files": ("test.json", sample_json_file, "application/json")}

        # Act
        response = client.post("/api/v1/upload", files=files)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "job_id" in data
        assert data["files_received"] == 1

    def test_upload_rejects_invalid_extension(self, client):
        """
        Test Reject Invalid File (Probar Rechazo de Archivo Inválido)
        Subir archivo .exe debe ser rechazado.
        """
        files = {"files": ("virus.exe", b"malware", "application/octet-stream")}

        response = client.post("/api/v1/upload", files=files)

        assert response.status_code == 400
        assert "invalid_file_type" in response.json()["error"]


class TestFullProcessFlow:
    """
    Test Full Process Flow (Prueba de Flujo Completo)
    Verifica todo el camino: upload → process → download.
    """

    def test_complete_workflow(self, client, sample_files):
        """
        Test Complete Workflow (Probar Flujo Completo)
        Desde subir hasta descargar debe funcionar.
        """
        # 1. Upload
        upload_response = client.post("/api/v1/upload", files=sample_files)
        assert upload_response.status_code == 200
        job_id = upload_response.json()["job_id"]

        # 2. Process
        process_response = client.post(
            "/api/v1/process",
            json={"job_id": job_id, "options": {"generate_excel": True}}
        )
        assert process_response.status_code == 200

        # 3. Wait for completion (poll status)
        # En test real, usar mock o reducir timeout

        # 4. Download
        download_response = client.get(f"/api/v1/download/{job_id}?type=excel")
        assert download_response.status_code == 200
        assert "spreadsheet" in download_response.headers["content-type"]
```

**Cobertura requerida:** 60% mínimo

---

### 3. E2E Tests (Pruebas de Extremo a Extremo - Probar como usuario)

**¿Qué es?**
Probar la aplicación como lo haría un usuario real.
Como probar toda la instalación eléctrica de la casa.

**Ejemplo con Playwright:**
```javascript
// tests/e2e/upload-flow.spec.js

import { test, expect } from '@playwright/test';

test.describe('Upload Flow', () => {
  /**
   * Test User Can Upload Files (Usuario Puede Subir Archivos)
   */
  test('user can upload JSON files and see them listed', async ({ page }) => {
    // 1. Ir a la página principal
    await page.goto('/');

    // 2. Subir un archivo
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles('tests/fixtures/sample-invoice.json');

    // 3. Verificar que aparece en la lista
    await expect(page.locator('.file-list')).toContainText('sample-invoice.json');
  });

  /**
   * Test Complete Process (Proceso Completo)
   */
  test('user can process files and download results', async ({ page }) => {
    await page.goto('/');

    // Subir archivos
    await page.locator('input[type="file"]').setInputFiles([
      'tests/fixtures/invoice1.json',
      'tests/fixtures/invoice2.json'
    ]);

    // Click en procesar
    await page.click('button:has-text("Procesar")');

    // Esperar progreso
    await expect(page.locator('.progress-bar')).toBeVisible();

    // Esperar completado
    await expect(page.locator('.status')).toContainText('Completado', {
      timeout: 30000
    });

    // Click en descargar
    const [download] = await Promise.all([
      page.waitForEvent('download'),
      page.click('button:has-text("Descargar Excel")')
    ]);

    // Verificar que se descargó
    expect(download.suggestedFilename()).toContain('.xlsx');
  });
});
```

**Cobertura requerida:** Flujos críticos cubiertos

---

## Metricas de Cobertura (Coverage Metrics)

### Objetivos por Módulo

| Módulo | Cobertura Mínima | Cobertura Ideal |
|--------|-----------------|-----------------|
| `core/json_processor.py` | 80% | 95% |
| `core/pdf_processor.py` | 80% | 90% |
| `core/excel_exporter.py` | 80% | 90% |
| `api/endpoints/*.py` | 70% | 85% |
| `models/*.py` | 80% | 95% |
| `utils/*.py` | 60% | 75% |
| Frontend Components | 70% | 85% |
| Frontend Hooks | 70% | 85% |

### Cómo Medir Cobertura

**Backend (pytest-cov):**
```bash
# Correr tests con cobertura
pytest --cov=src --cov-report=html --cov-report=term

# Ver reporte en terminal
Name                          Stmts   Miss  Cover
-------------------------------------------------
src/core/json_processor.py       50      5    90%
src/core/pdf_processor.py        40      8    80%
src/api/endpoints/upload.py      30      6    80%
-------------------------------------------------
TOTAL                           300     45    85%
```

**Frontend (Jest):**
```bash
# Correr tests con cobertura
npm test -- --coverage

# Resultado
-----------------------|---------|----------|---------|---------|
File                   | % Stmts | % Branch | % Funcs | % Lines |
-----------------------|---------|----------|---------|---------|
All files              |   85.5  |    78.2  |    90.1 |   85.5  |
 components/Button.jsx |   100   |    100   |    100  |   100   |
 hooks/useUpload.js    |    80   |     75   |     85  |    80   |
-----------------------|---------|----------|---------|---------|
```

---

## Fixtures y Datos de Prueba (Test Fixtures)

### Backend Fixtures

```python
# tests/conftest.py

import pytest
import json
from pathlib import Path

@pytest.fixture
def sample_json_data():
    """
    Sample JSON Data (Datos JSON de Ejemplo)
    Retorna un diccionario con datos de factura válidos.
    """
    return {
        "document_number": "CFJ001",
        "issue_date": "2025-01-15",
        "client_name": "Juan Pérez",
        "client_id": "12345678-9",
        "items": [
            {
                "quantity": 2,
                "description": "Producto A",
                "unit_price": 50.00,
                "total": 100.00
            }
        ],
        "subtotal": 100.00,
        "tax": 13.00,
        "total": 113.00
    }

@pytest.fixture
def sample_json_file(sample_json_data, tmp_path):
    """
    Sample JSON File (Archivo JSON de Ejemplo)
    Crea un archivo temporal con datos de prueba.
    """
    file_path = tmp_path / "test_invoice.json"
    file_path.write_text(json.dumps(sample_json_data))
    return file_path

@pytest.fixture
def sample_pdf_file(tmp_path):
    """
    Sample PDF File (Archivo PDF de Ejemplo)
    Crea un PDF simple para pruebas.
    """
    import fitz
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((100, 100), "Test Invoice")
    file_path = tmp_path / "test.pdf"
    doc.save(str(file_path))
    doc.close()
    return file_path
```

### Frontend Fixtures

```javascript
// tests/fixtures/mockData.js

export const mockInvoice = {
  documentNumber: 'CFJ001',
  issueDate: '2025-01-15',
  clientName: 'Juan Pérez',
  total: 113.00
};

export const mockUploadResponse = {
  success: true,
  jobId: 'test-job-123',
  filesReceived: 2,
  message: 'Archivos recibidos'
};

export const mockStatusResponse = {
  jobId: 'test-job-123',
  status: 'processing',
  progress: 45,
  currentStep: 'Procesando archivos'
};
```

---

## Comandos de Testing (Testing Commands)

### Backend

```bash
# Correr todos los tests
pytest

# Correr con verbose
pytest -v

# Correr solo unit tests
pytest tests/unit/

# Correr solo integration tests
pytest tests/integration/

# Correr un archivo específico
pytest tests/unit/test_json_processor.py

# Correr un test específico
pytest tests/unit/test_json_processor.py::test_process_valid_json

# Con cobertura
pytest --cov=src --cov-report=html

# Fallar si cobertura < 70%
pytest --cov=src --cov-fail-under=70
```

### Frontend

```bash
# Correr todos los tests
npm test

# Modo watch (re-corre al cambiar código)
npm test -- --watch

# Con cobertura
npm test -- --coverage

# Correr archivo específico
npm test -- Button.test.jsx

# E2E con Playwright
npm run test:e2e
```

---

## Checklist de Testing (Testing Checklist)

### Antes de hacer PR

- [ ] Todos los tests pasan localmente
- [ ] Cobertura >= 70%
- [ ] No hay tests comentados o skipped sin justificación
- [ ] Tests nuevos para código nuevo
- [ ] Tests de edge cases (casos límite)
- [ ] Tests de errores esperados

### Para código crítico

- [ ] Cobertura >= 80%
- [ ] Tests de concurrencia si aplica
- [ ] Tests de rendimiento si aplica
- [ ] Tests de seguridad si maneja input de usuario

---

## Proximo Documento (Next Document)

Continúa con: `09_CI_CD_Pipeline.md` para ver la automatización.

---

**Versión:** 1.0
**Líneas:** ~420
**Cumple reglas:** Sí

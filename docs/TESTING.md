# Testing Guide / Guía de Testing

This document describes the testing infrastructure for Paradise JSON Sync.
Este documento describe la infraestructura de testing para Paradise JSON Sync.

## Table of Contents / Tabla de Contenidos

1. [Overview / Resumen](#overview)
2. [Quick Start / Inicio Rápido](#quick-start)
3. [E2E Tests with Playwright / Tests E2E con Playwright](#e2e-tests)
4. [Backend Integration Tests / Tests de Integración Backend](#backend-integration)
5. [Frontend Integration Tests / Tests de Integración Frontend](#frontend-integration)
6. [Running Tests / Ejecutar Tests](#running-tests)
7. [Writing New Tests / Escribir Nuevos Tests](#writing-tests)

---

## Overview / Resumen {#overview}

The testing infrastructure consists of three main layers:
La infraestructura de testing consiste en tres capas principales:

| Layer / Capa | Tool / Herramienta | Purpose / Propósito |
|--------------|-------------------|---------------------|
| E2E | Playwright | Full user flows / Flujos completos de usuario |
| Backend Integration | pytest + FastAPI TestClient | API endpoint testing / Testing de endpoints de API |
| Frontend Integration | Vitest + MSW | Component testing with mocked APIs / Testing de componentes con APIs mock |

### Directory Structure / Estructura de Directorios

```
paradise-json-sync/
├── e2e/                              # E2E tests with Playwright
│   ├── playwright.config.ts          # Playwright configuration
│   ├── fixtures/                     # Test data and fixtures
│   │   ├── test-data/               # Sample files for testing
│   │   └── auth.fixture.ts          # Auth fixture (for future use)
│   ├── pages/                        # Page Object Models
│   │   ├── HomePage.ts
│   │   ├── UploadPage.ts
│   │   └── ResultsPage.ts
│   ├── tests/                        # Test specifications
│   │   ├── upload.spec.ts
│   │   ├── process.spec.ts
│   │   ├── download.spec.ts
│   │   └── full-flow.spec.ts
│   └── utils/                        # Test utilities
│       └── helpers.ts
│
├── backend/
│   └── tests/
│       └── integration/              # Backend integration tests
│           ├── conftest.py           # pytest fixtures
│           ├── test_full_flow.py
│           └── test_error_handling.py
│
└── frontend/
    └── tests/
        ├── setup.ts                  # Vitest setup
        └── integration/              # Frontend integration tests
            ├── setup.ts              # MSW server setup
            ├── handlers.ts           # MSW request handlers
            ├── mocks/                # Mock data
            └── flows/                # Integration flow tests
```

---

## Quick Start / Inicio Rápido {#quick-start}

### Install Dependencies / Instalar Dependencias

```bash
# Install all dependencies / Instalar todas las dependencias
npm run install:all

# Or install individually / O instalar individualmente
npm run install:frontend
npm run install:backend
npm run install:e2e
```

### Run All Tests / Ejecutar Todos los Tests

```bash
# Run all tests (unit + integration + e2e)
npm run test:all

# Or run specific test suites
npm run test:unit           # Unit tests only
npm run test:integration    # Integration tests only
npm run test:e2e           # E2E tests only
```

---

## E2E Tests with Playwright / Tests E2E con Playwright {#e2e-tests}

### Configuration / Configuración

The Playwright configuration is in `e2e/playwright.config.ts`:
La configuración de Playwright está en `e2e/playwright.config.ts`:

- **Base URL**: `http://localhost:5173` (or from `BASE_URL` env var)
- **Browsers**: Chromium, Firefox, Mobile Chrome
- **Timeout**: 30 seconds
- **Retries**: 2 on CI, 0 locally
- **Screenshots**: On failure only
- **Video**: On first retry

### Running E2E Tests / Ejecutar Tests E2E

```bash
# Run all E2E tests
npm run test:e2e

# Run with browser visible
npm run test:e2e:headed

# Run in debug mode
npm run test:e2e:debug

# Run with UI mode
npm run test:e2e:ui

# Show test report
npm run test:e2e:report
```

### Page Object Models

We use Page Object Models (POM) to encapsulate page interactions:
Usamos Page Object Models (POM) para encapsular interacciones con páginas:

- **HomePage**: Main page navigation and state
- **UploadPage**: File upload interactions
- **ResultsPage**: Processing results and downloads

Example usage / Ejemplo de uso:

```typescript
import { HomePage, UploadPage, ResultsPage } from '../pages';

test('complete flow', async ({ page }) => {
  const homePage = new HomePage(page);
  const uploadPage = new UploadPage(page);
  const resultsPage = new ResultsPage(page);

  await homePage.goto();
  await uploadPage.uploadFile('fixtures/test-data/sample-invoice.json');
  await uploadPage.clickProcess();
  await resultsPage.waitForCompletion();
  await resultsPage.downloadExcel();
});
```

### Test Data / Datos de Prueba

Test files are located in `e2e/fixtures/test-data/`:
Los archivos de prueba están en `e2e/fixtures/test-data/`:

- `sample-invoice.json`: Valid invoice (USD)
- `sample-invoice-2.json`: Valid invoice (PEN)
- `invalid-invoice.json`: Invalid JSON for error testing
- `sample.pdf`: Simple PDF for testing

---

## Backend Integration Tests / Tests de Integración Backend {#backend-integration}

### Configuration / Configuración

Backend tests use pytest with FastAPI's TestClient:
Los tests del backend usan pytest con TestClient de FastAPI:

Configuration is in `backend/pyproject.toml`:
La configuración está en `backend/pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
markers = [
    "integration: marks tests as integration tests",
    "slow: marks tests as slow",
]
```

### Running Backend Tests / Ejecutar Tests del Backend

```bash
cd backend

# Run all backend tests
pytest tests/ -v

# Run integration tests only
pytest tests/integration/ -v

# Run with coverage
pytest --cov=app --cov-report=html

# Run excluding slow tests
pytest -m "not slow"
```

### Fixtures / Fixtures

Available fixtures in `conftest.py`:
Fixtures disponibles en `conftest.py`:

- `test_client`: FastAPI TestClient
- `sample_json_file`: Sample invoice JSON file
- `sample_pdf_file`: Sample PDF file
- `invalid_json_file`: Invalid JSON for error testing
- `corrupted_file`: Corrupted file for error testing
- `temp_upload_dir`: Temporary upload directory (cleaned after each test)

Example / Ejemplo:

```python
def test_upload_flow(test_client, sample_json_file):
    with open(sample_json_file, 'rb') as f:
        response = test_client.post(
            "/api/v1/upload",
            files={"file": ("invoice.json", f, "application/json")}
        )
    assert response.status_code == 200
```

---

## Frontend Integration Tests / Tests de Integración Frontend {#frontend-integration}

### Configuration / Configuración

Frontend tests use Vitest with MSW (Mock Service Worker):
Los tests del frontend usan Vitest con MSW (Mock Service Worker):

Configuration is in `frontend/vitest.config.ts`:
La configuración está en `frontend/vitest.config.ts`:

### Running Frontend Tests / Ejecutar Tests del Frontend

```bash
cd frontend

# Run all tests
npm test

# Run in watch mode
npm run test:watch

# Run with coverage
npm run test:coverage

# Run with UI
npm run test:ui

# Run integration tests only
npm run test:integration
```

### MSW Setup / Configuración de MSW

MSW handlers are in `frontend/tests/integration/handlers.ts`:
Los handlers de MSW están en `frontend/tests/integration/handlers.ts`:

```typescript
import { server, useHandlers } from '../setup';
import { processingErrorHandler } from '../handlers';

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

test('handles error', async () => {
  // Override default handler for this test
  useHandlers(processingErrorHandler('job-001', 'Error message'));

  // ... test code
});
```

### Mock Data / Datos Mock

Mock response factories are in `frontend/tests/integration/mocks/`:
Las fábricas de respuestas mock están en `frontend/tests/integration/mocks/`:

- `responses.ts`: Generic response factories
- `uploadResponse.ts`: Upload-specific mocks
- `statusResponse.ts`: Status-specific mocks
- `processResponse.ts`: Process-specific mocks

---

## Running Tests / Ejecutar Tests {#running-tests}

### From Root Directory / Desde Directorio Raíz

```bash
# All tests
npm run test:all

# Unit tests only
npm run test:unit

# Integration tests only
npm run test:integration

# E2E tests only
npm run test:e2e
```

### Individual Commands / Comandos Individuales

```bash
# E2E
cd e2e && npx playwright test

# Backend
cd backend && pytest tests/ -v

# Frontend
cd frontend && npm test
```

### Coverage Reports / Reportes de Cobertura

```bash
# Frontend coverage
npm run test:coverage:frontend

# Backend coverage
npm run test:coverage:backend
```

---

## Writing New Tests / Escribir Nuevos Tests {#writing-tests}

### E2E Test Guidelines / Guías para Tests E2E

1. **Use Page Objects**: Always use POMs, don't hardcode selectors in tests
2. **Independent Tests**: Each test should be independent
3. **Explicit Waits**: Use Playwright's built-in waiting, avoid fixed delays
4. **Cleanup**: Clean up after tests
5. **Bilingual Comments**: Document in both English and Spanish

```typescript
test('descriptive test name / nombre descriptivo del test', async ({ page }) => {
  // Arrange / Preparar
  const homePage = new HomePage(page);

  // Act / Actuar
  await homePage.goto();

  // Assert / Verificar
  expect(await homePage.isDropzoneVisible()).toBe(true);
});
```

### Backend Test Guidelines / Guías para Tests Backend

1. **Use Fixtures**: Leverage pytest fixtures for setup
2. **Async Support**: Use `pytest-asyncio` for async tests
3. **Error Cases**: Always test error scenarios
4. **Isolation**: Each test should be isolated

```python
@pytest.mark.integration
def test_descriptive_name(test_client, sample_json_file):
    """
    Test description in English.
    Descripción del test en español.
    """
    # Arrange
    # ...

    # Act
    response = test_client.post("/api/v1/upload", ...)

    # Assert
    assert response.status_code == 200
```

### Frontend Test Guidelines / Guías para Tests Frontend

1. **Use MSW**: Mock API calls with MSW
2. **Testing Library**: Use `@testing-library/react`
3. **User Events**: Use `userEvent` for interactions
4. **Accessibility**: Test accessibility when possible

```typescript
test('component behavior', async () => {
  const user = userEvent.setup();
  render(<Component />);

  await user.click(screen.getByRole('button'));

  expect(screen.getByText('Expected text')).toBeInTheDocument();
});
```

---

## Troubleshooting / Solución de Problemas

### E2E Tests Fail / Tests E2E Fallan

1. Ensure frontend and backend are running
2. Check `BASE_URL` environment variable
3. Run `npx playwright install` if browsers are missing

### Backend Tests Fail / Tests Backend Fallan

1. Check Python version (>=3.10)
2. Install dev dependencies: `pip install -r requirements-dev.txt`
3. Check if FastAPI app is properly configured

### Frontend Tests Fail / Tests Frontend Fallan

1. Run `npm install` to update dependencies
2. Check if MSW handlers match current API
3. Ensure `jsdom` environment is configured

---

## CI/CD Integration / Integración CI/CD

For CI environments, set:
Para entornos de CI, configurar:

```bash
export CI=true
export BASE_URL=http://localhost:5173
```

This enables:
Esto habilita:

- 2 retries for E2E tests
- Single worker for parallelism
- GitHub reporter for E2E

---

*Last updated: 2025-02-04*
*Última actualización: 2025-02-04*

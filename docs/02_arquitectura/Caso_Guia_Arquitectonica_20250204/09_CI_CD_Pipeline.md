# 09 - CI/CD Pipeline (Pipeline de Integración y Despliegue Continuo)
# CI/CD Pipeline (Pipeline CI/CD - Automatización del trabajo)

---

## Observaciones Obligatorias (Mandatory Notes)

```
TESTS REQUERIDOS: Pipeline DEBE correr tests antes de deploy
COBERTURA: Build falla si cobertura < 70%
PLATAFORMA: GitHub Actions
AMBIENTES: Development → Staging → Production
```

---

## Que es CI/CD (What is CI/CD)

**Explicación simple:**

**CI (Continuous Integration - Integración Continua):**
Es como tener un inspector que revisa tu trabajo cada vez que lo entregas.
- Cada vez que subes código, el inspector lo revisa
- Si encuentra errores, te avisa antes de que llegue al producto final

**CD (Continuous Deployment - Despliegue Continuo):**
Es como tener un repartidor automático.
- Cuando el código pasa la inspección, se publica automáticamente
- No tienes que hacerlo manualmente

**Analogía completa:**
Imagina una fábrica de juguetes:
1. Un trabajador hace un juguete (tú escribes código)
2. Un inspector lo revisa (CI corre tests)
3. Si está bien, va a la caja de envíos (merge a main)
4. Un repartidor lo lleva a la tienda (CD lo publica)

---

## Flujo General (General Flow)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        FLUJO CI/CD COMPLETO                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   DESARROLLO                                                            │
│   ┌─────────────┐                                                       │
│   │ Desarrollador│                                                      │
│   │ hace cambios │                                                      │
│   └──────┬──────┘                                                       │
│          │                                                              │
│          │  git push                                                    │
│          ▼                                                              │
│   ┌─────────────┐                                                       │
│   │   GitHub    │                                                       │
│   │   (PR)      │                                                       │
│   └──────┬──────┘                                                       │
│          │                                                              │
│   CI ════╪════════════════════════════════════════════════════════      │
│          ▼                                                              │
│   ┌─────────────────────────────────────────────────────────────┐       │
│   │                    GITHUB ACTIONS                            │       │
│   │  ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐      │       │
│   │  │  Lint   │ → │  Test   │ → │  Build  │ → │ Security│      │       │
│   │  │         │   │         │   │         │   │  Scan   │      │       │
│   │  └────┬────┘   └────┬────┘   └────┬────┘   └────┬────┘      │       │
│   │       │             │             │             │           │       │
│   │       ▼             ▼             ▼             ▼           │       │
│   │     ✓/✗           ✓/✗           ✓/✗           ✓/✗          │       │
│   │       └─────────────┴─────────────┴─────────────┘           │       │
│   │                          │                                   │       │
│   │                    TODO PASÓ?                                │       │
│   └──────────────────────────┬──────────────────────────────────┘       │
│                              │                                          │
│          ┌───────────────────┴───────────────────┐                      │
│          │                                       │                      │
│          ▼                                       ▼                      │
│   ┌─────────────┐                         ┌─────────────┐               │
│   │    ✓ SÍ     │                         │    ✗ NO     │               │
│   │   Merge OK  │                         │ Merge Block │               │
│   └──────┬──────┘                         └─────────────┘               │
│          │                                                              │
│   CD ════╪════════════════════════════════════════════════════════      │
│          ▼                                                              │
│   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐                  │
│   │   Deploy    │ → │   Deploy    │ → │   Deploy    │                  │
│   │  Staging    │   │ Producción  │   │   (Manual)  │                  │
│   └─────────────┘   └─────────────┘   └─────────────┘                  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Configuracion de GitHub Actions (GitHub Actions Configuration)

### Archivo Principal

```yaml
# .github/workflows/ci.yml
# CI Pipeline (Pipeline de Integración Continua)
# Se ejecuta en cada push y PR

name: CI Pipeline

# TRIGGERS (Disparadores - Cuándo se ejecuta)
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

# JOBS (Trabajos - Qué se hace)
jobs:

  # ============================================
  # JOB 1: LINT (Verificar estilo de código)
  # ============================================
  lint:
    name: Lint Code
    runs-on: ubuntu-latest

    steps:
      # Obtener el código
      - name: Checkout Code
        uses: actions/checkout@v4

      # Backend Lint
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install Backend Dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install ruff

      - name: Run Ruff (Python Linter)
        run: |
          cd backend
          ruff check .

      # Frontend Lint
      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: '18'

      - name: Install Frontend Dependencies
        run: |
          cd frontend
          npm ci

      - name: Run ESLint
        run: |
          cd frontend
          npm run lint

  # ============================================
  # JOB 2: TEST (Correr pruebas)
  # ============================================
  test:
    name: Run Tests
    runs-on: ubuntu-latest
    needs: lint  # Espera que lint pase

    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      # Backend Tests
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install Backend Dependencies
        run: |
          cd backend
          pip install -r requirements.txt

      - name: Run Backend Tests
        run: |
          cd backend
          pytest --cov=src --cov-report=xml --cov-fail-under=70

      # Frontend Tests
      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: '18'

      - name: Install Frontend Dependencies
        run: |
          cd frontend
          npm ci

      - name: Run Frontend Tests
        run: |
          cd frontend
          npm test -- --coverage --watchAll=false

      # Upload coverage report
      - name: Upload Coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./backend/coverage.xml,./frontend/coverage/lcov.info

  # ============================================
  # JOB 3: BUILD (Construir aplicación)
  # ============================================
  build:
    name: Build Application
    runs-on: ubuntu-latest
    needs: test  # Espera que test pase

    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      # Build Backend
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Verify Backend Build
        run: |
          cd backend
          pip install -r requirements.txt
          python -c "from src.main import app; print('Backend OK')"

      # Build Frontend
      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: '18'

      - name: Build Frontend
        run: |
          cd frontend
          npm ci
          npm run build

      # Guardar artifacts
      - name: Upload Frontend Build
        uses: actions/upload-artifact@v4
        with:
          name: frontend-build
          path: frontend/dist

  # ============================================
  # JOB 4: SECURITY (Escaneo de seguridad)
  # ============================================
  security:
    name: Security Scan
    runs-on: ubuntu-latest
    needs: lint

    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      # Python security
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Run Safety (Python Vulnerabilities)
        run: |
          pip install safety
          cd backend
          safety check -r requirements.txt

      # Node security
      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: '18'

      - name: Run npm audit
        run: |
          cd frontend
          npm audit --audit-level=high
```

---

### Workflow de Deploy

```yaml
# .github/workflows/deploy.yml
# CD Pipeline (Pipeline de Despliegue Continuo)
# Se ejecuta cuando hay merge a main

name: Deploy Pipeline

on:
  push:
    branches: [main]

jobs:
  # ============================================
  # DEPLOY TO STAGING (Desplegar a Staging)
  # ============================================
  deploy-staging:
    name: Deploy to Staging
    runs-on: ubuntu-latest

    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      # Deploy Backend to Render
      - name: Deploy Backend to Render
        env:
          RENDER_API_KEY: ${{ secrets.RENDER_API_KEY }}
        run: |
          curl -X POST "https://api.render.com/v1/services/${{ secrets.RENDER_SERVICE_ID }}/deploys" \
            -H "Authorization: Bearer $RENDER_API_KEY"

      # Deploy Frontend to SiteGround
      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: '18'

      - name: Build Frontend
        run: |
          cd frontend
          npm ci
          npm run build

      - name: Deploy Frontend via FTP
        uses: SamKirkland/FTP-Deploy-Action@v4.3.4
        with:
          server: ${{ secrets.FTP_SERVER }}
          username: ${{ secrets.FTP_USERNAME }}
          password: ${{ secrets.FTP_PASSWORD }}
          local-dir: ./frontend/dist/
          server-dir: /public_html/staging/

  # ============================================
  # DEPLOY TO PRODUCTION (Desplegar a Producción)
  # ============================================
  deploy-production:
    name: Deploy to Production
    runs-on: ubuntu-latest
    needs: deploy-staging
    environment: production  # Requiere aprobación manual

    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Deploy to Production
        run: |
          echo "Deploying to production..."
          # Comandos de deploy a producción
```

---

## Ambientes (Environments)

### Development (Desarrollo)

```
URL: http://localhost:5173 (Frontend)
     http://localhost:8000 (Backend)

PROPÓSITO: Desarrollo local
DEPLOY: Manual por desarrollador
```

### Staging (Pre-producción)

```
URL: https://staging.paradise-json-sync.com
     https://api-staging.paradise-json-sync.com

PROPÓSITO: Probar antes de producción
DEPLOY: Automático en merge a main
```

### Production (Producción)

```
URL: https://paradise-json-sync.com
     https://api.paradise-json-sync.com

PROPÓSITO: Usuarios reales
DEPLOY: Manual con aprobación
```

---

## Variables de Entorno y Secrets (Environment Variables)

### Secrets en GitHub

| Secret | Descripción | Usado en |
|--------|-------------|----------|
| `RENDER_API_KEY` | API key de Render | Deploy backend |
| `RENDER_SERVICE_ID` | ID del servicio en Render | Deploy backend |
| `FTP_SERVER` | Servidor FTP SiteGround | Deploy frontend |
| `FTP_USERNAME` | Usuario FTP | Deploy frontend |
| `FTP_PASSWORD` | Password FTP | Deploy frontend |
| `CODECOV_TOKEN` | Token para reportes | Coverage |

### Cómo Agregar Secrets

1. Ir a GitHub → Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Agregar nombre y valor
4. Guardar

---

## Checklist de CI/CD (CI/CD Checklist)

### Para que el Pipeline Pase

- [ ] Código sin errores de lint (Ruff + ESLint)
- [ ] Todos los tests pasan
- [ ] Cobertura >= 70%
- [ ] Build exitoso
- [ ] Sin vulnerabilidades críticas en dependencias

### Antes de Merge a Main

- [ ] PR aprobado por al menos 1 reviewer
- [ ] CI pipeline verde (todos los checks pasan)
- [ ] Branch actualizado con main
- [ ] Conflictos resueltos

---

## Troubleshooting (Resolución de Problemas)

### Pipeline Falla en Lint

```
ERROR: Ruff found issues

SOLUCIÓN:
1. Correr `ruff check . --fix` localmente
2. Revisar errores restantes manualmente
3. Commit los cambios
```

### Pipeline Falla en Tests

```
ERROR: Tests failing

SOLUCIÓN:
1. Correr `pytest -v` localmente
2. Ver qué test falla
3. Arreglar el código o el test
4. Verificar que pase localmente antes de push
```

### Pipeline Falla en Coverage

```
ERROR: Coverage below 70%

SOLUCIÓN:
1. Ver reporte de coverage (`pytest --cov=src --cov-report=html`)
2. Identificar código sin tests
3. Agregar tests para el código nuevo
4. Repetir hasta alcanzar 70%
```

---

## Proximo Documento (Next Document)

Continúa con: `10_Guia_de_Despliegue.md` para ver cómo publicar manualmente.

---

**Versión:** 1.0
**Líneas:** ~380
**Cumple reglas:** Sí

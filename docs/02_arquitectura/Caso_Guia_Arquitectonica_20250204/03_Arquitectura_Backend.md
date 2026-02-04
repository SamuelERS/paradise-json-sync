# 03 - Arquitectura Backend (Backend Architecture)
# Backend Architecture (Arquitectura Backend - El cerebro del sistema)

---

## Observaciones Obligatorias (Mandatory Notes)

```
TESTS REQUERIDOS: Sí - Cada módulo debe tener tests unitarios
COBERTURA MÍNIMA: 70% general, 80% para lógica crítica
CI/CD: Compatible - Tests corren en pipeline antes de merge
STACK: Python 3.11+ / FastAPI / Pandas / openpyxl / PyMuPDF
```

---

## Que es el Backend (What is the Backend)

**Explicación simple:**
El backend es como la cocina de un restaurante:
- No lo ves desde afuera
- Pero ahí es donde se prepara todo
- Recibe pedidos y devuelve platos listos

En nuestro caso:
- Recibe archivos JSON y PDF
- Los procesa
- Devuelve Excel y PDF unificado

---

## Estructura de Carpetas (Folder Structure)

```
backend/
├── 📄 main.py                    # Entry Point (Punto de Entrada - Donde inicia todo)
├── 📄 requirements.txt           # Dependencies (Dependencias - Lista de librerías)
├── 📄 .env.example               # Environment Template (Plantilla de Variables)
│
├── 📂 src/                       # Source Code (Código Fuente - El corazón)
│   │
│   ├── 📂 api/                   # API Layer (Capa de API - Los meseros)
│   │   ├── 📄 __init__.py
│   │   ├── 📄 routes.py          # Routes (Rutas - Los caminos disponibles)
│   │   └── 📂 endpoints/         # Endpoints (Puntos finales - Cada servicio)
│   │       ├── 📄 __init__.py
│   │       ├── 📄 upload.py      # Upload Endpoint (Subir archivos)
│   │       ├── 📄 process.py     # Process Endpoint (Procesar datos)
│   │       └── 📄 download.py    # Download Endpoint (Descargar resultados)
│   │
│   ├── 📂 core/                  # Core Logic (Lógica Central - Los cocineros)
│   │   ├── 📄 __init__.py
│   │   ├── 📄 json_processor.py  # JSON Processor (Procesador de JSON)
│   │   ├── 📄 pdf_processor.py   # PDF Processor (Procesador de PDF)
│   │   ├── 📄 excel_exporter.py  # Excel Exporter (Exportador de Excel)
│   │   └── 📄 data_validator.py  # Data Validator (Validador de Datos)
│   │
│   ├── 📂 models/                # Data Models (Modelos de Datos - Las formas)
│   │   ├── 📄 __init__.py
│   │   ├── 📄 invoice.py         # Invoice Model (Modelo de Factura)
│   │   ├── 📄 request.py         # Request Models (Modelos de Petición)
│   │   └── 📄 response.py        # Response Models (Modelos de Respuesta)
│   │
│   ├── 📂 config/                # Configuration (Configuración - Los ajustes)
│   │   ├── 📄 __init__.py
│   │   └── 📄 settings.py        # Settings (Ajustes de la aplicación)
│   │
│   └── 📂 utils/                 # Utilities (Utilidades - Herramientas extras)
│       ├── 📄 __init__.py
│       ├── 📄 file_handler.py    # File Handler (Manejador de Archivos)
│       └── 📄 logger.py          # Logger (Registrador de eventos)
│
└── 📂 tests/                     # Tests (Pruebas - El control de calidad)
    ├── 📄 __init__.py
    ├── 📄 conftest.py            # Test Config (Configuración de tests)
    ├── 📂 unit/                  # Unit Tests (Pruebas Unitarias)
    │   ├── 📄 test_json_processor.py
    │   ├── 📄 test_pdf_processor.py
    │   └── 📄 test_excel_exporter.py
    └── 📂 integration/           # Integration Tests (Pruebas de Integración)
        └── 📄 test_api_endpoints.py
```

---

## Descripcion de Modulos (Module Description)

### 1. API Layer (Capa de API - Los meseros)

**Responsabilidad:** Recibir pedidos y devolver respuestas.

**Archivos principales:**

#### `routes.py` (Rutas - El menú de opciones)
```python
# routes.py - Define qué caminos existen
from fastapi import APIRouter
from src.api.endpoints import upload, process, download

router = APIRouter()

# Agregar todas las rutas
router.include_router(upload.router, prefix="/upload", tags=["Upload"])
router.include_router(process.router, prefix="/process", tags=["Process"])
router.include_router(download.router, prefix="/download", tags=["Download"])
```

**Tests requeridos:**
- [ ] Test: Router incluye todas las rutas
- [ ] Test: Prefijos son correctos
- [ ] Test: Tags están asignados

---

### 2. Core Layer (Capa Central - Los cocineros)

**Responsabilidad:** Hacer el trabajo real de procesamiento.

#### `json_processor.py` (Procesador de JSON)

**¿Qué hace?** Lee archivos JSON y extrae información de facturas.

```python
# Ejemplo simplificado
class JSONProcessor:
    """
    JSON Processor (Procesador de JSON)
    Lee archivos JSON de facturas y extrae los datos importantes.

    Piensa en esto como: Un lector que abre cartas y anota
    la información importante en una lista.
    """

    def process_file(self, file_path: str) -> dict:
        """
        Process File (Procesar Archivo)
        Lee un archivo JSON y devuelve sus datos.

        Args:
            file_path: Ruta al archivo (como la dirección de una casa)

        Returns:
            dict: Los datos extraídos (como una ficha con la información)
        """
        # Lógica de procesamiento
        pass

    def process_batch(self, file_paths: list[str]) -> list[dict]:
        """
        Process Batch (Procesar Lote)
        Lee muchos archivos de una vez.

        Args:
            file_paths: Lista de rutas (muchas direcciones)

        Returns:
            list: Lista de datos extraídos
        """
        pass
```

**Tests requeridos:**
- [ ] Test: `process_file` lee JSON válido
- [ ] Test: `process_file` maneja JSON inválido
- [ ] Test: `process_batch` procesa múltiples archivos
- [ ] Test: Campos faltantes generan warning, no error

---

#### `pdf_processor.py` (Procesador de PDF)

**¿Qué hace?** Une múltiples PDFs en uno solo.

```python
class PDFProcessor:
    """
    PDF Processor (Procesador de PDF)
    Une varios archivos PDF en un solo documento.

    Piensa en esto como: Un encuadernador que toma muchas
    hojas sueltas y las une en un libro.
    """

    def merge_pdfs(self, pdf_paths: list[str], output_path: str) -> str:
        """
        Merge PDFs (Unir PDFs)
        Toma varios PDFs y los une en orden.

        Args:
            pdf_paths: Lista de archivos PDF a unir
            output_path: Dónde guardar el resultado

        Returns:
            str: Ruta del PDF unificado
        """
        pass
```

**Tests requeridos:**
- [ ] Test: Une 2 PDFs correctamente
- [ ] Test: Une 10+ PDFs sin error
- [ ] Test: Mantiene orden especificado
- [ ] Test: PDF corrupto no rompe todo el proceso

---

#### `excel_exporter.py` (Exportador de Excel)

**¿Qué hace?** Toma datos y genera un archivo Excel.

```python
class ExcelExporter:
    """
    Excel Exporter (Exportador de Excel)
    Convierte datos en una tabla de Excel bonita y ordenada.

    Piensa en esto como: Un secretario que toma notas
    desordenadas y las pasa en limpio a una planilla.
    """

    def export_to_excel(self, data: list[dict], output_path: str) -> str:
        """
        Export to Excel (Exportar a Excel)
        Crea un archivo Excel con los datos.

        Args:
            data: Lista de facturas (la información)
            output_path: Dónde guardar el archivo

        Returns:
            str: Ruta del archivo creado
        """
        pass
```

**Tests requeridos:**
- [ ] Test: Genera archivo Excel válido
- [ ] Test: Columnas tienen headers correctos
- [ ] Test: Datos aparecen en orden
- [ ] Test: Formato de fechas es correcto
- [ ] Test: Números tienen formato de moneda

---

### 3. Models Layer (Capa de Modelos - Las formas)

**Responsabilidad:** Definir cómo se ven los datos.

#### `invoice.py` (Modelo de Factura)

```python
from pydantic import BaseModel
from datetime import date
from decimal import Decimal

class Invoice(BaseModel):
    """
    Invoice Model (Modelo de Factura)
    Define qué información tiene una factura.

    Piensa en esto como: El formato de una ficha.
    Todas las fichas deben tener los mismos campos.
    """

    # Document Number (Número de Documento - El ID único de la factura)
    document_number: str

    # Issue Date (Fecha de Emisión - Cuándo se hizo)
    issue_date: date

    # Client Name (Nombre del Cliente - A quién se le vendió)
    client_name: str

    # Client ID (ID del Cliente - DUI, NIT, etc.)
    client_id: str

    # Items (Productos - Qué se vendió)
    items: list[dict]

    # Subtotal (Subtotal - Suma antes de impuestos)
    subtotal: Decimal

    # Tax (Impuesto - IVA u otros)
    tax: Decimal

    # Total (Total - Lo que se debe pagar)
    total: Decimal
```

**Tests requeridos:**
- [ ] Test: Crear Invoice con datos válidos
- [ ] Test: Rechazar Invoice sin campos requeridos
- [ ] Test: Validar formato de fecha
- [ ] Test: Validar que total = subtotal + tax

---

## Flujo de Datos (Data Flow)

```
┌─────────────────────────────────────────────────────────────────┐
│                    FLUJO DEL BACKEND                            │
│               (Cómo viajan los datos)                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. RECIBIR                                                     │
│     ┌─────────┐                                                 │
│     │ Usuario │ ─── sube archivos ───►  /api/upload             │
│     └─────────┘                              │                  │
│                                              ▼                  │
│  2. VALIDAR                          ┌─────────────┐            │
│                                      │ Validador   │            │
│                                      │ de Archivos │            │
│                                      └─────────────┘            │
│                                              │                  │
│                           ┌──────────────────┴────────────┐     │
│                           ▼                               ▼     │
│  3. PROCESAR      ┌─────────────┐                ┌───────────┐  │
│                   │ JSON        │                │ PDF       │  │
│                   │ Processor   │                │ Processor │  │
│                   └─────────────┘                └───────────┘  │
│                           │                               │     │
│                           ▼                               ▼     │
│  4. TRANSFORMAR   ┌─────────────┐                ┌───────────┐  │
│                   │ Datos       │                │ PDF       │  │
│                   │ Extraídos   │                │ Unificado │  │
│                   └─────────────┘                └───────────┘  │
│                           │                               │     │
│                           ▼                               │     │
│  5. EXPORTAR      ┌─────────────┐                         │     │
│                   │ Excel       │                         │     │
│                   │ Exporter    │                         │     │
│                   └─────────────┘                         │     │
│                           │                               │     │
│                           └───────────────┬───────────────┘     │
│                                           ▼                     │
│  6. RESPONDER                     ┌─────────────┐               │
│                                   │ /api/       │               │
│                                   │ download    │               │
│                                   └─────────────┘               │
│                                           │                     │
│                                           ▼                     │
│                                   ┌─────────────┐               │
│                                   │ Usuario     │               │
│                                   │ descarga    │               │
│                                   └─────────────┘               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Reglas de Codigo (Code Rules)

### 1. Una Funcion, Una Tarea (One Function, One Task)

```python
# ❌ MAL - Función que hace muchas cosas
def process_everything(files):
    # Lee archivos
    # Valida datos
    # Procesa JSONs
    # Une PDFs
    # Exporta Excel
    # 200 líneas de código mezclado
    pass

# ✅ BIEN - Funciones pequeñas y específicas
def read_files(file_paths: list[str]) -> list[bytes]:
    """Lee los archivos del disco"""
    pass

def validate_json(data: dict) -> bool:
    """Valida que el JSON tenga campos requeridos"""
    pass

def extract_invoice_data(json_data: dict) -> Invoice:
    """Extrae datos de factura del JSON"""
    pass
```

### 2. Maximo 50 Lineas por Funcion (Max 50 Lines per Function)

Si una función tiene más de 50 líneas, divídela.

### 3. Documentacion en Español e Ingles (Documentation in Both Languages)

```python
def calculate_total(subtotal: Decimal, tax_rate: Decimal) -> Decimal:
    """
    Calculate Total (Calcular Total)
    Suma el subtotal más el impuesto.

    Args:
        subtotal: Monto antes de impuestos (la cantidad base)
        tax_rate: Porcentaje de impuesto (ej: 0.13 para 13%)

    Returns:
        Decimal: El total a pagar

    Example:
        >>> calculate_total(100, 0.13)
        Decimal('113.00')
    """
    return subtotal + (subtotal * tax_rate)
```

---

## Configuracion de Tests (Test Configuration)

### Archivo `conftest.py`

```python
# tests/conftest.py
import pytest

@pytest.fixture
def sample_json_data():
    """
    Sample JSON Data (Datos JSON de Ejemplo)
    Devuelve un JSON de factura para usar en tests.
    """
    return {
        "document_number": "CFCJ2000000001",
        "issue_date": "2025-01-15",
        "client_name": "Juan Pérez",
        "total": 100.00
    }

@pytest.fixture
def sample_pdf_path(tmp_path):
    """
    Sample PDF Path (Ruta de PDF de Ejemplo)
    Crea un PDF temporal para tests.
    """
    # Crear PDF de prueba
    pass
```

### Ejecutar Tests

```bash
# Correr todos los tests
pytest

# Correr con cobertura
pytest --cov=src --cov-report=html

# Correr tests específicos
pytest tests/unit/test_json_processor.py
```

---

## Proximo Documento (Next Document)

Continúa con: `04_Arquitectura_Frontend.md` para ver la estructura del frontend.

---

**Versión:** 1.0
**Líneas:** ~380
**Cumple reglas:** Sí

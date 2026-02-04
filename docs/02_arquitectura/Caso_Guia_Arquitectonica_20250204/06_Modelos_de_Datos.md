# 06 - Modelos de Datos (Data Models)
# Data Models (Modelos de Datos - Las cajas donde guardamos información)

---

## Observaciones Obligatorias (Mandatory Notes)

```
TESTS REQUERIDOS: Sí - Validación de modelos debe tener tests
COBERTURA MÍNIMA: 80% para modelos (son críticos)
CI/CD: Compatible - Validación de schemas en pipeline
LIBRERÍA: Pydantic para validación en Python
```

---

## Que es un Modelo de Datos (What is a Data Model)

**Explicación simple:**
Un modelo de datos es como un formulario con casillas definidas:
- Cada casilla tiene un nombre
- Cada casilla espera un tipo de dato
- Si pones algo mal, te avisa

**Ejemplo del mundo real:**
Un formulario de inscripción tiene:
- Nombre (texto)
- Edad (número)
- Email (texto con formato especial)

Si pones "abc" en edad, el formulario te dice "esto no es un número".

---

## Modelos del Backend (Backend Models)

### 1. Invoice Model (Modelo de Factura)

**Propósito:** Representa una factura con todos sus datos.

```python
from pydantic import BaseModel, Field
from datetime import date
from decimal import Decimal
from typing import Optional
from enum import Enum

class InvoiceType(str, Enum):
    """
    Invoice Type (Tipo de Factura)
    Los tipos de documento fiscal permitidos.

    - FACTURA: Factura de consumidor final
    - CCF: Comprobante de crédito fiscal
    - NOTA_CREDITO: Nota de crédito
    """
    FACTURA = "factura"
    CCF = "ccf"
    NOTA_CREDITO = "nota_credito"


class InvoiceItem(BaseModel):
    """
    Invoice Item (Artículo de Factura)
    Un producto o servicio dentro de la factura.

    Piensa en esto como: Una línea en el ticket de compra.
    """

    # Quantity (Cantidad - Cuántos se vendieron)
    quantity: int = Field(
        ...,
        gt=0,
        description="Cantidad de productos vendidos"
    )

    # Description (Descripción - Qué es el producto)
    description: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Nombre o descripción del producto"
    )

    # Unit Price (Precio Unitario - Cuánto cuesta cada uno)
    unit_price: Decimal = Field(
        ...,
        ge=0,
        description="Precio por unidad"
    )

    # Total (Total de la línea = cantidad × precio)
    total: Decimal = Field(
        ...,
        ge=0,
        description="Total de esta línea"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "quantity": 2,
                "description": "Alimento para peces tropicales 100g",
                "unit_price": 5.00,
                "total": 10.00
            }
        }


class Invoice(BaseModel):
    """
    Invoice Model (Modelo de Factura)
    Representa una factura completa con todos sus datos.

    Piensa en esto como: El ticket completo de una compra,
    con toda la información del cliente, los productos y los totales.
    """

    # === IDENTIFICACIÓN ===

    # Document Number (Número de Documento - El código único de la factura)
    document_number: str = Field(
        ...,
        pattern=r"^[A-Z0-9-]+$",
        description="Número único de la factura (ej: CFCJ2000000149)"
    )

    # Document Type (Tipo de Documento - Factura, CCF, etc.)
    document_type: InvoiceType = Field(
        default=InvoiceType.FACTURA,
        description="Tipo de documento fiscal"
    )

    # === FECHAS ===

    # Issue Date (Fecha de Emisión - Cuándo se hizo la factura)
    issue_date: date = Field(
        ...,
        description="Fecha en que se emitió la factura"
    )

    # === CLIENTE ===

    # Client Name (Nombre del Cliente - A quién se le vendió)
    client_name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Nombre completo del cliente"
    )

    # Client ID (ID del Cliente - DUI, NIT, Pasaporte)
    client_id: Optional[str] = Field(
        None,
        description="Documento de identidad del cliente"
    )

    # Client Address (Dirección del Cliente)
    client_address: Optional[str] = Field(
        None,
        max_length=300,
        description="Dirección del cliente"
    )

    # === PRODUCTOS ===

    # Items (Productos - Lista de lo que se vendió)
    items: list[InvoiceItem] = Field(
        ...,
        min_length=1,
        description="Lista de productos vendidos"
    )

    # === TOTALES ===

    # Subtotal (Subtotal - Suma antes de impuestos)
    subtotal: Decimal = Field(
        ...,
        ge=0,
        description="Total antes de impuestos"
    )

    # Tax (Impuesto - IVA, generalmente 13%)
    tax: Decimal = Field(
        ...,
        ge=0,
        description="Monto del impuesto (IVA)"
    )

    # Total (Total - Lo que se debe pagar)
    total: Decimal = Field(
        ...,
        ge=0,
        description="Total a pagar (subtotal + tax)"
    )

    # === METADATOS ===

    # Source File (Archivo Fuente - De dónde vino)
    source_file: Optional[str] = Field(
        None,
        description="Nombre del archivo JSON original"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "document_number": "CFCJ2000000149",
                "document_type": "factura",
                "issue_date": "2025-01-15",
                "client_name": "Juan Pérez",
                "client_id": "12345678-9",
                "items": [
                    {
                        "quantity": 2,
                        "description": "Alimento para peces",
                        "unit_price": 5.00,
                        "total": 10.00
                    }
                ],
                "subtotal": 10.00,
                "tax": 1.30,
                "total": 11.30
            }
        }
```

**Tests requeridos:**
- [ ] Test: Crear Invoice con datos válidos
- [ ] Test: Rechazar sin document_number
- [ ] Test: Rechazar sin items
- [ ] Test: Validar que total = subtotal + tax
- [ ] Test: Validar formato de document_number

---

### 2. Upload Models (Modelos de Carga)

```python
class UploadRequest(BaseModel):
    """
    Upload Request (Petición de Carga)
    No tiene body específico, usa multipart/form-data.
    Este modelo es solo para documentación.
    """
    pass


class FileInfo(BaseModel):
    """
    File Info (Información de Archivo)
    Datos de un archivo subido.

    Piensa en esto como: La etiqueta en una caja
    que dice qué hay dentro.
    """

    # Name (Nombre - Cómo se llama el archivo)
    name: str = Field(..., description="Nombre del archivo")

    # Size (Tamaño - En bytes)
    size: int = Field(..., ge=0, description="Tamaño en bytes")

    # Type (Tipo - MIME type del archivo)
    type: str = Field(..., description="Tipo MIME del archivo")

    # Status (Estado - received, error, etc.)
    status: str = Field(..., description="Estado del archivo")


class UploadResponse(BaseModel):
    """
    Upload Response (Respuesta de Carga)
    Lo que devuelve el servidor al subir archivos.
    """

    # Success (Éxito - ¿Funcionó?)
    success: bool = Field(..., description="Si la operación fue exitosa")

    # Job ID (ID del Trabajo - Para seguimiento)
    job_id: str = Field(..., description="Identificador único del trabajo")

    # Files Received (Archivos Recibidos - Cuántos llegaron)
    files_received: int = Field(..., description="Cantidad de archivos recibidos")

    # Files Detail (Detalle de Archivos - Info de cada uno)
    files_detail: list[FileInfo] = Field(..., description="Detalle de cada archivo")

    # Message (Mensaje - Texto informativo)
    message: str = Field(..., description="Mensaje descriptivo")
```

**Tests requeridos:**
- [ ] Test: UploadResponse con datos válidos
- [ ] Test: FileInfo calcula tamaño correctamente
- [ ] Test: job_id no está vacío

---

### 3. Process Models (Modelos de Procesamiento)

```python
class ProcessOptions(BaseModel):
    """
    Process Options (Opciones de Procesamiento)
    Configuración de cómo procesar los archivos.

    Piensa en esto como: Las instrucciones que le das
    al cocinero de cómo quieres tu comida.
    """

    # Generate Excel (Generar Excel - ¿Crear archivo Excel?)
    generate_excel: bool = Field(
        default=True,
        description="Si debe generar archivo Excel"
    )

    # Generate PDF (Generar PDF - ¿Unir los PDFs?)
    generate_pdf: bool = Field(
        default=True,
        description="Si debe unir los PDFs"
    )

    # Sort By (Ordenar Por - Cómo ordenar los datos)
    sort_by: str = Field(
        default="date",
        pattern="^(date|document_number|client|total)$",
        description="Campo por el cual ordenar"
    )

    # Include Summary (Incluir Resumen - ¿Agregar hoja de totales?)
    include_summary: bool = Field(
        default=True,
        description="Si debe incluir hoja de resumen"
    )


class ProcessRequest(BaseModel):
    """
    Process Request (Petición de Procesamiento)
    Lo que envía el frontend para iniciar el proceso.
    """

    # Job ID (ID del Trabajo - Cuál trabajo procesar)
    job_id: str = Field(..., description="ID del trabajo a procesar")

    # Options (Opciones - Cómo procesar)
    options: ProcessOptions = Field(
        default_factory=ProcessOptions,
        description="Opciones de procesamiento"
    )


class ProcessResponse(BaseModel):
    """
    Process Response (Respuesta de Procesamiento)
    Lo que devuelve el servidor al iniciar proceso.
    """

    success: bool
    job_id: str
    status: str
    message: str
    estimated_time_seconds: Optional[int] = None
```

**Tests requeridos:**
- [ ] Test: ProcessOptions con valores por defecto
- [ ] Test: sort_by rechaza valores inválidos
- [ ] Test: ProcessRequest requiere job_id

---

### 4. Status Models (Modelos de Estado)

```python
class JobStatus(str, Enum):
    """
    Job Status (Estado del Trabajo)
    Los posibles estados de un trabajo.
    """
    PENDING = "pending"           # En cola, esperando
    PROCESSING = "processing"     # Trabajando
    COMPLETED = "completed"       # Terminado con éxito
    COMPLETED_WITH_ERRORS = "completed_with_errors"  # Terminado pero con errores
    FAILED = "failed"             # Falló


class FileError(BaseModel):
    """
    File Error (Error de Archivo)
    Información sobre un archivo que falló.
    """
    file: str = Field(..., description="Nombre del archivo")
    error: str = Field(..., description="Descripción del error")


class ProcessResults(BaseModel):
    """
    Process Results (Resultados del Proceso)
    Resumen de lo que se procesó.
    """
    files_processed: int = Field(..., description="Total de archivos procesados")
    files_success: int = Field(..., description="Archivos procesados con éxito")
    files_error: int = Field(..., description="Archivos con error")
    excel_ready: bool = Field(..., description="Si el Excel está listo")
    pdf_ready: bool = Field(..., description="Si el PDF está listo")


class StatusResponse(BaseModel):
    """
    Status Response (Respuesta de Estado)
    Información completa del estado de un trabajo.
    """

    # Job ID (ID del Trabajo)
    job_id: str

    # Status (Estado actual)
    status: JobStatus

    # Progress (Progreso de 0 a 100)
    progress: int = Field(..., ge=0, le=100)

    # Current Step (Paso actual - Qué está haciendo ahora)
    current_step: str

    # Steps Completed (Pasos completados)
    steps_completed: list[str] = []

    # Steps Pending (Pasos pendientes)
    steps_pending: list[str] = []

    # Results (Resultados - Solo si completó)
    results: Optional[ProcessResults] = None

    # Errors (Errores - Lista de archivos que fallaron)
    errors: list[FileError] = []

    # Download URL (URL de descarga - Solo si completó)
    download_url: Optional[str] = None
```

**Tests requeridos:**
- [ ] Test: StatusResponse con estado pending
- [ ] Test: StatusResponse con estado completed
- [ ] Test: Progress siempre entre 0 y 100
- [ ] Test: download_url presente solo si completed

---

## Modelos del Frontend (Frontend Models)

### TypeScript Interfaces

```typescript
/**
 * Invoice Interface (Interfaz de Factura)
 * Versión TypeScript del modelo de factura.
 */
interface Invoice {
  documentNumber: string;      // Número de documento
  documentType: 'factura' | 'ccf' | 'nota_credito';
  issueDate: string;           // Fecha en formato ISO
  clientName: string;
  clientId?: string;
  items: InvoiceItem[];
  subtotal: number;
  tax: number;
  total: number;
  sourceFile?: string;
}

interface InvoiceItem {
  quantity: number;
  description: string;
  unitPrice: number;
  total: number;
}

/**
 * Upload Response Interface
 */
interface UploadResponse {
  success: boolean;
  jobId: string;              // Nota: camelCase en frontend
  filesReceived: number;
  filesDetail: FileInfo[];
  message: string;
}

interface FileInfo {
  name: string;
  size: number;
  type: string;
  status: 'received' | 'error' | 'processing';
}

/**
 * Status Response Interface
 */
interface StatusResponse {
  jobId: string;
  status: 'pending' | 'processing' | 'completed' | 'completed_with_errors' | 'failed';
  progress: number;
  currentStep: string;
  stepsCompleted: string[];
  stepsPending: string[];
  results?: ProcessResults;
  errors: FileError[];
  downloadUrl?: string;
}
```

---

## Validaciones Importantes (Important Validations)

### Lista de Validaciones por Modelo

| Modelo | Campo | Validación | Error si falla |
|--------|-------|------------|----------------|
| Invoice | document_number | Regex `^[A-Z0-9-]+$` | "Formato de documento inválido" |
| Invoice | items | min_length=1 | "Factura debe tener al menos un producto" |
| Invoice | total | ge=0 | "Total no puede ser negativo" |
| InvoiceItem | quantity | gt=0 | "Cantidad debe ser mayor a 0" |
| ProcessOptions | sort_by | Enum válido | "Opción de ordenamiento inválida" |
| StatusResponse | progress | 0-100 | "Progreso fuera de rango" |

---

## Conversiones (Conversions)

### Python snake_case → JavaScript camelCase

```python
# Configuración en Pydantic para conversión automática
class BaseModel(BaseModel):
    class Config:
        # Permite usar alias en camelCase
        populate_by_name = True

        # Función para convertir automáticamente
        alias_generator = to_camel

def to_camel(string: str) -> str:
    """Convierte snake_case a camelCase"""
    components = string.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])
```

---

## Proximo Documento (Next Document)

Continúa con: `07_Flujo_de_Procesamiento.md` para ver cómo fluyen los datos.

---

**Versión:** 1.0
**Líneas:** ~400
**Cumple reglas:** Sí

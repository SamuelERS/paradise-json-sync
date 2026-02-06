# 🌐 API y Servicios — Rutas del Backend para Compras

> **⚠️ ANTES DE EMPEZAR:** Lee [EL_PUNTO_DE_PARTIDA](../../EL_PUNTO_DE_PARTIDA_by_SamuelERS.md) para identificar tu rol y qué documentos te corresponden leer según tu misión.

> **¿Qué es esto?** Este documento define los endpoints HTTP, servicios y flujo de datos del backend para el procesamiento de facturas de compra.

### Roles Requeridos para este Documento

| Rol | Misión aquí |
|-----|-------------|
| 👨‍💻 **Desarrollador de Elite (Backend)** | Implementar endpoints, schemas y servicio orquestador |
| ✅ **Inspector de Elite** | Verificar seguridad de endpoints, validación de inputs |
| ⚙️ **Ingeniero Operaciones** | Configurar rate limiting, monitoreo y logging |

### Tareas de Implementación (FASE 5)

| Tarea | Agente | Archivo Destino |
|-------|--------|-----------------|
| Crear router de compras | 👨‍💻 Desarrollador Backend | `backend/src/api/routes/purchases.py` |
| Crear schemas Pydantic | 👨‍💻 Desarrollador Backend | `backend/src/api/schemas/purchases.py` |
| Crear `PurchaseService` | 👨‍💻 Desarrollador Backend | `backend/src/services/purchase_service.py` |
| Integrar con `main.py` | 👨‍💻 Desarrollador Backend | `backend/src/main.py` |
| Tests de integración API (>=70%) | 👨‍💻 Desarrollador Backend | `backend/tests/api/test_purchases_api.py` |
| Revisión de seguridad | ✅ Inspector de Elite | Validar inputs, rate limits, error handling |

---

## 1. Diseño de Endpoints

Todos los endpoints de compras viven bajo el prefijo `/api/purchases/` para separación clara del módulo de ventas existente (`/api/`).

### Tabla de Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| `POST` | `/api/purchases/upload` | Subir archivos JSON/PDF de compras |
| `POST` | `/api/purchases/process` | Iniciar procesamiento del lote |
| `GET` | `/api/purchases/status/{job_id}` | Consultar estado del job |
| `GET` | `/api/purchases/download/{job_id}` | Descargar resultado |
| `GET` | `/api/purchases/formats` | Listar formatos soportados |
| `GET` | `/api/purchases/columns` | Listar columnas disponibles y perfiles |

---

## 2. Detalle de Endpoints

### 2.1 POST `/api/purchases/upload`

Sube archivos de facturas de compra. Mismo patrón que `/api/upload` existente.

**Request:**
```
Content-Type: multipart/form-data
Rate Limit: 10/minuto por IP

files: [archivo1.json, archivo2.json, factura.pdf, ...]
```

**Response (201):**
```json
{
  "success": true,
  "message": "50 archivos subidos correctamente",
  "data": {
    "upload_id": "uuid-del-upload",
    "files": [
      { "name": "factura_abc.json", "size": 2048, "type": "application/json" },
      { "name": "factura_xyz.pdf", "size": 50000, "type": "application/pdf" }
    ],
    "total_files": 50,
    "json_count": 48,
    "pdf_count": 2,
    "expires_at": "2026-02-06T15:30:00Z"
  }
}
```

**Validaciones:**
- Máximo 10,000 archivos (misma config que ventas)
- Máximo 10MB por archivo
- Solo acepta `.json` y `.pdf`
- Rate limit: 10 requests/minuto

**Reutiliza:** `FileService` existente para almacenamiento temporal.

---

### 2.2 POST `/api/purchases/process`

Inicia el procesamiento asíncrono del lote subido.

**Campos del request:**

| Campo | Tipo | Default | Descripción |
|-------|------|---------|-------------|
| `upload_id` | string | requerido | ID del upload previo |
| `output_format` | enum | `"xlsx"` | `xlsx`, `csv`, `pdf`, `json` |
| `column_profile` | enum | `"completo"` | `basico`, `completo`, `contador`, `custom` |
| `custom_columns` | list[str] | null | Lista de columnas si profile es `custom` |
| `options.include_summary` | bool | true | Incluir hoja de resumen |
| `options.include_items_sheet` | bool | true | Incluir hoja de items detallados |
| `options.group_by` | enum | `"none"` | `none`, `supplier`, `date`, `type` |
| `options.include_raw_data` | bool | false | Incluir JSON original en exportación |

**Response (202):**
```json
{
  "success": true,
  "message": "Procesamiento iniciado",
  "data": {
    "job_id": "uuid-del-job",
    "status": "processing",
    "estimated_time": 15,
    "created_at": "2026-02-06T14:30:00Z"
  }
}
```

**Reutiliza:** `JobService` existente para gestión de jobs asíncronos.

---

### 2.3 GET `/api/purchases/status/{job_id}`

Consulta el progreso del procesamiento.

**Response (200):**
```json
{
  "success": true,
  "data": {
    "job_id": "uuid-del-job",
    "status": "processing",
    "progress": 65,
    "step": "Validando facturas (33/50)",
    "stats": {
      "total_files": 50,
      "processed": 33,
      "valid": 30,
      "warnings": 2,
      "errors": 1,
      "formats_detected": {
        "DTE_STANDARD": 28,
        "DTE_VARIANT_A": 4,
        "UNKNOWN": 1
      }
    },
    "created_at": "2026-02-06T14:30:00Z",
    "updated_at": "2026-02-06T14:30:15Z"
  }
}
```

**Status posibles:** `processing`, `completed`, `failed`

**Cuando `status` = `completed`:**
```json
{
  "data": {
    "status": "completed",
    "progress": 100,
    "result": {
      "output_path": "/tmp/purchases/job-uuid/output.xlsx",
      "invoice_count": 47,
      "total_amount": 15234.56,
      "valid_count": 45,
      "warning_count": 2,
      "error_count": 3,
      "errors": [
        {
          "file": "factura_corrupta.json",
          "reason": "JSON inválido"
        }
      ],
      "formats_summary": {
        "DTE_STANDARD": 40,
        "DTE_VARIANT_A": 5,
        "GENERIC_FLAT": 2,
        "FAILED": 3
      }
    }
  }
}
```

---

### 2.4 GET `/api/purchases/download/{job_id}`

Descarga el archivo generado.

**Response (200):**
```
Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
Content-Disposition: attachment; filename="compras_2026-02-06.xlsx"

[binary file content]
```

**Reutiliza:** Mismo patrón de descarga que `/api/download/{job_id}`.

---

### 2.5 GET `/api/purchases/formats`

Retorna los formatos de factura soportados (informativo).

**Response (200):**
```json
{
  "formats": [
    {
      "id": "DTE_STANDARD",
      "name": "DTE Estándar (Hacienda)",
      "description": "Formato oficial del Ministerio de Hacienda"
    },
    {
      "id": "DTE_VARIANT_A",
      "name": "DTE Variante A",
      "description": "Items en 'detalle' en vez de 'cuerpoDocumento'"
    },
    {
      "id": "GENERIC_FLAT",
      "name": "JSON Plano Genérico",
      "description": "Formato plano sin estructura DTE"
    },
    {
      "id": "PDF_EXTRACTED",
      "name": "PDF (texto extraído)",
      "description": "Datos extraídos de factura en PDF"
    }
  ]
}
```

---

### 2.6 GET `/api/purchases/columns`

Retorna las columnas disponibles y los perfiles predeterminados.

**Response (200):**
```json
{
  "profiles": {
    "basico": {
      "name": "Básico",
      "description": "Solo campos esenciales",
      "columns": ["control_number", "document_type", "issue_date", "supplier_name", "total"]
    },
    "completo": {
      "name": "Completo",
      "description": "Todos los campos disponibles",
      "columns": ["...todos..."]
    },
    "contador": {
      "name": "Contador",
      "description": "Campos fiscales para contabilidad",
      "columns": ["control_number", "document_type", "issue_date", "supplier_name", "supplier_nit", "total_taxable", "total_exempt", "tax", "total"]
    }
  },
  "all_columns": [
    { "id": "control_number", "label": "N° Control", "category": "identificacion" },
    { "id": "document_type", "label": "Tipo Doc", "category": "identificacion" },
    { "id": "issue_date", "label": "Fecha", "category": "identificacion" },
    { "id": "supplier_name", "label": "Proveedor", "category": "proveedor" },
    { "id": "supplier_nit", "label": "NIT Proveedor", "category": "proveedor" },
    { "id": "total_taxable", "label": "Gravado", "category": "montos" },
    { "id": "total_exempt", "label": "Exento", "category": "montos" },
    { "id": "tax", "label": "IVA", "category": "montos" },
    { "id": "total", "label": "Total", "category": "montos" }
  ]
}
```

---

## 3. Schemas Pydantic

```python
# backend/src/api/schemas/purchases.py

class PurchaseProcessOptions(BaseModel):
    """Opciones de procesamiento de compras."""
    include_summary: bool = True
    include_items_sheet: bool = True
    group_by: Literal["none", "supplier", "date", "type"] = "none"
    include_raw_data: bool = False

class PurchaseProcessRequest(BaseModel):
    """Request para iniciar procesamiento de compras."""
    upload_id: str
    output_format: Literal["xlsx", "csv", "pdf", "json"] = "xlsx"
    column_profile: Literal["basico", "completo", "contador", "custom"] = "completo"
    custom_columns: Optional[list[str]] = None
    options: PurchaseProcessOptions = PurchaseProcessOptions()

class PurchaseFormatInfo(BaseModel):
    """Información de un formato soportado."""
    id: str
    name: str
    description: str

class PurchaseColumnInfo(BaseModel):
    """Información de una columna disponible."""
    id: str
    label: str
    category: str
```

---

## 4. Servicio: PurchaseProcessorService

```python
class PurchaseProcessorService:
    """
    Servicio que orquesta el procesamiento completo de facturas de compra.
    Conecta todos los componentes del pipeline.
    """

    def __init__(self):
        self.detector = FormatDetector()
        self.registry = create_default_registry()
        self.validator = PurchaseValidator()
        self.exporter = PurchaseExporter()
        self.pdf_extractor = PDFExtractor()  # FASE 7

    async def process(
        self,
        file_paths: list[str],
        config: PurchaseProcessRequest,
        progress_callback=None,
    ) -> ProcessingResult:
        """Pipeline completo: detect → map → validate → export"""

        invoices = []
        errors = []

        for i, path in enumerate(file_paths):
            try:
                # Reportar progreso
                if progress_callback:
                    progress_callback(i + 1, len(file_paths), f"Procesando {Path(path).name}")

                # 1. Clasificar archivo
                if path.endswith(".pdf"):
                    raw_data = self.pdf_extractor.extract(path)
                    detected = DetectionResult(format=DetectedFormat.PDF_EXTRACTED, confidence=0.8)
                else:
                    raw_data = self._load_json(path)
                    detected = self.detector.detect(raw_data)

                # 2. Mapear
                mapper = self.registry.get_mapper(detected.format)
                purchase = mapper.map(raw_data, source_file=path)
                purchase.detected_format = detected.format.value
                purchase.detection_confidence = detected.confidence

                # 3. Validar
                validation = self.validator.validate(purchase, existing=invoices)
                purchase.processing_warnings = [
                    str(issue) for issue in validation.issues
                ]

                if validation.is_valid:
                    invoices.append(purchase)
                else:
                    errors.append(ProcessingError(
                        file=path,
                        reason="; ".join(str(e) for e in validation.issues if e.level == "ERROR"),
                    ))

            except (MappingError, JSONDecodeError) as e:
                errors.append(ProcessingError(file=path, reason=str(e)))

        # 4. Exportar
        output_path = self.exporter.export(
            invoices=invoices,
            format=config.output_format,
            column_profile=config.column_profile,
            custom_columns=config.custom_columns,
            options=config.options,
        )

        return ProcessingResult(
            output_path=output_path,
            invoice_count=len(invoices),
            error_count=len(errors),
            errors=errors,
        )
```

---

## 5. Registro de Rutas en FastAPI

```python
# backend/src/api/routes/purchases.py

from fastapi import APIRouter, UploadFile, File, Depends, BackgroundTasks

router = APIRouter(prefix="/api/purchases", tags=["purchases"])

@router.post("/upload")
async def upload_purchase_files(files: list[UploadFile] = File(...)):
    """Sube archivos de facturas de compra."""
    ...

@router.post("/process", status_code=202)
async def process_purchases(
    request: PurchaseProcessRequest,
    background_tasks: BackgroundTasks,
):
    """Inicia procesamiento asíncrono de facturas de compra."""
    ...

@router.get("/status/{job_id}")
async def get_purchase_status(job_id: str):
    """Consulta estado del procesamiento."""
    ...

@router.get("/download/{job_id}")
async def download_purchase_result(job_id: str):
    """Descarga el archivo de resultado."""
    ...

@router.get("/formats")
async def list_formats():
    """Lista formatos de factura soportados."""
    ...

@router.get("/columns")
async def list_columns():
    """Lista columnas disponibles y perfiles."""
    ...
```

**Integración con `main.py`:**
```python
# backend/src/main.py (agregar)
from src.api.routes.purchases import router as purchases_router
app.include_router(purchases_router)
```

---

## 6. Testing de API

```
tests/api/test_purchases_api.py

├── test_upload_json_files             → Upload exitoso de JSONs
├── test_upload_pdf_files              → Upload exitoso de PDFs
├── test_upload_mixed_files            → Upload de JSONs + PDFs
├── test_upload_invalid_extension      → Archivo .txt → 400
├── test_upload_too_large              → Archivo >10MB → 413
├── test_upload_rate_limit             → Exceder rate limit → 429
├── test_process_basic                 → Procesamiento básico exitoso
├── test_process_with_column_profile   → Perfil de columnas
├── test_process_with_custom_columns   → Columnas personalizadas
├── test_process_invalid_upload_id     → Upload ID inexistente → 404
├── test_status_processing             → Status mientras procesa
├── test_status_completed              → Status cuando termina
├── test_download_result               → Descarga exitosa
├── test_list_formats                  → Lista formatos soportados
└── test_list_columns                  → Lista columnas disponibles
```

**Cobertura esperada:** >= 70%

---

## 7. Respuestas de Error

Estructura: `{ "success": false, "error": { "code": "...", "message": "...", "detail": "..." } }`

| HTTP | Código | Cuándo |
|------|--------|--------|
| 400 | `INVALID_REQUEST` | Request malformado, tipo de archivo no soportado, `custom_columns` vacío con profile `custom` |
| 404 | `NOT_FOUND` | `upload_id` o `job_id` no existe o ha expirado |
| 413 | `FILE_TOO_LARGE` | Archivo > 10MB |
| 429 | `RATE_LIMIT_EXCEEDED` | Más de 10 requests/minuto |

**Validación `custom_columns`:** Si `column_profile="custom"` pero `custom_columns` es `null`/vacío → 400. Si contiene IDs no reconocidos → 400 con lista de columnas inválidas.

---

> **Próximo documento:** [09_EXPORTADOR_COMPRAS](./09_EXPORTADOR_COMPRAS_(Reportes-Configurables-sin-Perder-Datos).md) — Reportes con columnas configurables.

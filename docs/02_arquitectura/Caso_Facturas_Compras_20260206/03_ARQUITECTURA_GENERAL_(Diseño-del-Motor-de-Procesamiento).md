# 🏗️ Arquitectura General — Motor de Procesamiento de Compras

> **¿Qué es esto?** Este documento describe CÓMO funciona el sistema por dentro: el pipeline completo desde que entra un archivo hasta que sale un reporte. Es el mapa técnico para el desarrollador.

---

## 1. Diagrama del Pipeline

```
  ┌─────────────────────────────────────────────────────────────┐
  │                      ENTRADA (Upload)                       │
  │              JSON (variantes DTE) + PDF                     │
  │           Hasta 10,000 archivos por lote                    │
  └──────────────────────┬──────────────────────────────────────┘
                         │
                         ▼
  ┌─────────────────────────────────────────────────────────────┐
  │              PASO 1: CLASIFICACIÓN DE ARCHIVO               │
  │                                                             │
  │  ¿Es JSON? → Paso 2A (Detector de Formato)                 │
  │  ¿Es PDF?  → Paso 2B (Extractor de PDF)                    │
  │  ¿Otro?    → Error: formato no soportado                   │
  └──────────────────────┬──────────────────────────────────────┘
                         │
            ┌────────────┴────────────┐
            ▼                         ▼
  ┌──────────────────┐     ┌───────────────────────┐
  │  PASO 2A:        │     │  PASO 2B:             │
  │  FormatDetector  │     │  PDFExtractor         │
  │                  │     │                       │
  │  Analiza JSON    │     │  Extrae texto del PDF │
  │  Identifica      │     │  Intenta parsear      │
  │  "fingerprint"   │     │  a estructura JSON    │
  │  del formato     │     │                       │
  └────────┬─────────┘     └───────────┬───────────┘
           │                           │
           └─────────┬─────────────────┘
                     ▼
  ┌─────────────────────────────────────────────────────────────┐
  │              PASO 3: MAPEO (Mapper Registry)                │
  │                                                             │
  │  FormatDetector dice: "Es formato DTE_STANDARD"             │
  │  MapperRegistry busca: DTEStandardMapper                    │
  │  Mapper convierte: JSON crudo → PurchaseInvoice canónico    │
  │                                                             │
  │  Si no hay mapper: GenericFallbackMapper (heurísticas)      │
  └──────────────────────┬──────────────────────────────────────┘
                         │
                         ▼
  ┌─────────────────────────────────────────────────────────────┐
  │              PASO 4: VALIDACIÓN                             │
  │                                                             │
  │  PurchaseValidator verifica:                                │
  │  ✓ Totales = Suma de items                                  │
  │  ✓ IVA calculado correctamente                              │
  │  ✓ Campos requeridos presentes                              │
  │  ✓ No hay duplicados en el lote                             │
  │  ✓ Fechas válidas y coherentes                              │
  │                                                             │
  │  Resultado: Lista de PurchaseInvoice validados              │
  │           + Lista de warnings                               │
  │           + Lista de errores (archivos rechazados)          │
  └──────────────────────┬──────────────────────────────────────┘
                         │
                         ▼
  ┌─────────────────────────────────────────────────────────────┐
  │              PASO 5: EXPORTACIÓN                            │
  │                                                             │
  │  PurchaseExporter genera reporte según configuración:       │
  │  - Formato: Excel / CSV / PDF / JSON                        │
  │  - Columnas: según perfil o selección manual                │
  │  - Resumen: por proveedor, fecha, tipo                      │
  │                                                             │
  │  JSON siempre exporta TODOS los campos (cero pérdida)       │
  └──────────────────────┬──────────────────────────────────────┘
                         │
                         ▼
  ┌─────────────────────────────────────────────────────────────┐
  │              SALIDA (Download)                              │
  │              Archivo listo para el contador                 │
  └─────────────────────────────────────────────────────────────┘
```

---

## 2. Estructura de Carpetas (Nuevo Código)

```
backend/src/
├── models/
│   ├── invoice.py                    ← EXISTENTE (no tocar)
│   └── purchase_invoice.py           ← NUEVO: Modelo canónico de compra
│
├── core/
│   ├── json_processor.py             ← EXISTENTE (no tocar)
│   ├── excel_exporter.py             ← EXISTENTE (no tocar)
│   │
│   └── purchases/                    ← NUEVO: Todo el módulo de compras
│       ├── __init__.py
│       ├── format_detector.py        ← Identifica formato del JSON
│       ├── mapper_registry.py        ← Registro central de mappers
│       ├── base_mapper.py            ← Clase abstracta para mappers
│       ├── mappers/                  ← Mappers específicos
│       │   ├── __init__.py
│       │   ├── dte_standard.py       ← Formato estándar Hacienda
│       │   ├── dte_variant_a.py      ← Variante A (ejemplo)
│       │   └── generic_fallback.py   ← Fallback heurístico
│       ├── validator.py              ← Validador de compras
│       ├── purchase_exporter.py      ← Exportador configurable
│       ├── pdf_extractor.py          ← Extractor de datos de PDF
│       └── processor.py              ← Orquestador del pipeline
│
├── api/
│   ├── routes/
│   │   ├── upload.py                 ← EXISTENTE (no tocar)
│   │   └── purchases.py             ← NUEVO: Endpoints de compras
│   └── schemas/
│       ├── upload.py                 ← EXISTENTE (no tocar)
│       └── purchases.py             ← NUEVO: Schemas de compras
│
└── services/
    ├── file_service.py               ← EXISTENTE (reutilizar)
    ├── job_service.py                ← EXISTENTE (reutilizar)
    └── purchase_service.py           ← NUEVO: Servicio de compras

backend/tests/
├── unit/
│   ├── test_purchase_invoice.py      ← Tests del modelo
│   ├── test_format_detector.py       ← Tests del detector
│   ├── test_mappers.py               ← Tests de mappers
│   ├── test_purchase_validator.py    ← Tests del validador
│   └── test_purchase_exporter.py     ← Tests del exportador
├── api/
│   └── test_purchases_api.py         ← Tests de endpoints
└── integration/
    └── test_purchase_pipeline.py     ← Tests del pipeline completo

frontend/src/
├── pages/
│   ├── Home.jsx                      ← EXISTENTE (agregar navegación)
│   └── Purchases.jsx                 ← NUEVO: Página de compras
├── components/
│   ├── DropzoneUpload.jsx            ← EXISTENTE (reutilizar)
│   ├── PurchaseUpload.jsx            ← NUEVO: Upload para compras
│   ├── ColumnConfigurator.jsx        ← NUEVO: Config de columnas
│   └── ModeToggle.jsx                ← NUEVO: Toggle Ventas/Compras
```

---

## 3. Componentes Principales

### 3.1 FormatDetector — El "Detective"

**Responsabilidad:** Recibe un JSON crudo y determina qué formato/variante es.

**Cómo funciona:**
1. Examina las claves del primer nivel del JSON
2. Busca "huellas digitales" (fingerprints): combinaciones de campos que identifican un formato
3. Asigna puntaje a cada formato candidato
4. Retorna el formato con mayor puntaje + nivel de confianza

**Ejemplo de fingerprints:**
```python
# Si tiene estas claves → es DTE Estándar
DTE_STANDARD = {"identificacion", "emisor", "receptor", "cuerpoDocumento", "resumen"}

# Si tiene estas variaciones → es Variante A
DTE_VARIANT_A = {"identificacion", "emisor", "receptor", "detalle", "totales"}
```

**Ver detalle completo:** [05_DETECTOR_FORMATO](./05_DETECTOR_FORMATO_(Sistema-Inteligente-de-Identificacion).md)

---

### 3.2 MapperRegistry + Mappers — Los "Traductores"

**Responsabilidad:** Convertir cada formato al modelo canónico `PurchaseInvoice`.

**Patrón usado:** Registry + Strategy

```python
# Registro: cada mapper se registra con su formato
registry.register(DetectedFormat.DTE_STANDARD, DTEStandardMapper())
registry.register(DetectedFormat.DTE_VARIANT_A, DTEVariantAMapper())
registry.register(DetectedFormat.UNKNOWN, GenericFallbackMapper())

# Uso: el registry devuelve el mapper correcto
mapper = registry.get_mapper(detected_format)
purchase_invoice = mapper.map(raw_json)
```

**Agregar soporte para un nuevo proveedor =** crear un mapper + registrarlo. Sin tocar nada más.

**Ver detalle completo:** [06_MAPPERS_Y_REGISTRO](./06_MAPPERS_Y_REGISTRO_(Convertidores-de-Formato-por-Proveedor).md)

---

### 3.3 PurchaseValidator — El "Inspector"

**Responsabilidad:** Verificar que los datos normalizados son correctos y completos.

**Validaciones:**
- Totales = suma de items (con tolerancia configurable)
- IVA = 13% de base gravable (con tolerancia)
- No hay duplicados (por número de control + NIT emisor)
- Campos requeridos presentes
- Fechas válidas y en rango razonable

**Ver detalle completo:** [07_VALIDADOR_COMPRAS](./07_VALIDADOR_COMPRAS_(Verificacion-y-Calidad-de-Datos).md)

---

### 3.4 PurchaseExporter — El "Reportero"

**Responsabilidad:** Generar reportes con columnas configurables.

**Diferencia con ExcelExporter actual:**
- El usuario elige qué columnas ver (checkboxes)
- Los datos completos siempre se mantienen internamente
- Perfiles predeterminados: "Básico", "Completo", "Contador"
- JSON siempre exporta todo (sin filtro de columnas)

**Ver detalle completo:** [09_EXPORTADOR_COMPRAS](./09_EXPORTADOR_COMPRAS_(Reportes-Configurables-sin-Perder-Datos).md)

---

### 3.5 PurchaseProcessor — El "Director de Orquesta"

**Responsabilidad:** Coordinar todo el pipeline en orden.

```python
class PurchaseProcessor:
    def process_batch(self, file_paths, export_config):
        results = []
        errors = []

        for path in file_paths:
            # Paso 1: Clasificar archivo
            file_type = classify_file(path)

            # Paso 2: Detectar formato (o extraer de PDF)
            if file_type == "json":
                raw_data = load_json(path)
                detected = self.detector.detect(raw_data)
            elif file_type == "pdf":
                raw_data = self.pdf_extractor.extract(path)
                detected = DetectedFormat.PDF_EXTRACTED

            # Paso 3: Mapear a modelo canónico
            mapper = self.registry.get_mapper(detected.format)
            purchase = mapper.map(raw_data, source_file=path)

            # Paso 4: Validar
            validation = self.validator.validate(purchase)
            if validation.has_errors:
                errors.append((path, validation.errors))
            else:
                results.append(purchase)

        # Paso 5: Exportar
        return self.exporter.export(results, export_config)
```

---

## 4. Comunicación entre Componentes

```
┌──────────┐     ┌──────────────┐     ┌──────────────┐
│ API      │────▶│ Purchase     │────▶│ Job          │
│ Routes   │     │ Service      │     │ Service      │
│ (HTTP)   │     │ (Orquesta)   │     │ (Async)      │
└──────────┘     └──────┬───────┘     └──────────────┘
                        │
                        ▼
                ┌──────────────┐
                │ Purchase     │
                │ Processor    │
                │ (Pipeline)   │
                └──────┬───────┘
                       │
          ┌────────────┼────────────────┐
          ▼            ▼                ▼
   ┌────────────┐ ┌──────────┐  ┌────────────┐
   │ Format     │ │ Mapper   │  │ Purchase   │
   │ Detector   │ │ Registry │  │ Validator  │
   └────────────┘ └──────────┘  └────────────┘
                       │
                       ▼
                ┌──────────────┐
                │ Purchase     │
                │ Exporter     │
                └──────────────┘
```

---

## 5. Reutilización del Sistema Existente

| Componente Existente | Cómo se Reutiliza |
|---------------------|-------------------|
| `FileService` | Misma gestión de archivos temporales y cleanup |
| `JobService` | Misma gestión de jobs asíncronos (procesamiento background) |
| `rate_limiter` | Mismo rate limiting para endpoints de compras |
| `multipart_config` | Misma configuración para 10,000 archivos |
| `ExcelExporter` (base) | Se extiende/compone para columnas configurables |
| `DropzoneUpload` (frontend) | Se reutiliza el componente de drag-and-drop |
| CI/CD pipeline | Se extiende con nuevos tests, no se reescribe |

---

## 6. Flujo de Datos Completo (Ejemplo)

```
1. Usuario sube 50 archivos JSON de 5 proveedores diferentes
   ↓
2. API recibe archivos → FileService los guarda en /tmp/{upload_id}/
   ↓
3. Usuario clickea "Procesar" → API crea Job asíncrono
   ↓
4. PurchaseProcessor itera por cada archivo:
   - archivo_1.json → FormatDetector: "DTE_STANDARD" (confianza: 95%)
                     → DTEStandardMapper: convierte a PurchaseInvoice
                     → PurchaseValidator: ✅ válido
   - archivo_2.json → FormatDetector: "DTE_VARIANT_A" (confianza: 87%)
                     → DTEVariantAMapper: convierte a PurchaseInvoice
                     → PurchaseValidator: ⚠️ warning (diferencia en totales)
   - archivo_3.json → FormatDetector: "UNKNOWN" (confianza: 40%)
                     → GenericFallbackMapper: intenta mapeo heurístico
                     → PurchaseValidator: ❌ error (campos requeridos faltantes)
   ↓
5. Resultado: 47 facturas válidas, 2 con warnings, 1 con error
   ↓
6. PurchaseExporter genera Excel con columnas seleccionadas por el usuario
   ↓
7. Usuario descarga el archivo
```

---

## 7. Principios de Diseño

### 7.1 Abierto para Extensión, Cerrado para Modificación
Agregar un nuevo formato = agregar un mapper y registrarlo. **Cero cambios** en el pipeline existente.

### 7.2 Separación de Responsabilidades
Cada componente hace UNA cosa. El detector no mapea. El mapper no valida. El validador no exporta.

### 7.3 Fail Gracefully
Un archivo con error no detiene el procesamiento del lote. Se registra el error y se continúa con el siguiente.

### 7.4 Cero Pérdida de Datos
El JSON original completo se puede almacenar en `raw_data` del modelo. El usuario decide qué ver, no qué guardar.

---

> **Próximo documento:** [04_MODELO_CANONICO](./04_MODELO_CANONICO_(Estructura-Universal-de-Factura-de-Compra).md) — La estructura de datos que lo une todo.

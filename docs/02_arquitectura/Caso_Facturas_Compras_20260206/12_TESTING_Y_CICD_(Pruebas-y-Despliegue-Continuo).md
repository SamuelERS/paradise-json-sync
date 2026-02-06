# 🧪 Testing y CI/CD — Pruebas y Despliegue Continuo

> **¿Qué es esto?** Este documento define la estrategia de testing para el módulo de compras y cómo se integra con el pipeline CI/CD existente. Cobertura mínima: 70%.

---

## 1. Estrategia de Testing (3 Capas)

Misma estrategia que el sistema actual, extendida para compras.

```
┌─────────────────────────────────────────────────────────┐
│  CAPA 3: E2E (Playwright)                                │
│  Flujo completo: Upload → Config → Process → Download    │
│  Cobertura: Flujos críticos del usuario                  │
├─────────────────────────────────────────────────────────┤
│  CAPA 2: Integración (pytest + Vitest)                   │
│  API endpoints + Componentes con mocks                   │
│  Cobertura: >= 70% de endpoints y componentes            │
├─────────────────────────────────────────────────────────┤
│  CAPA 1: Unitarias (pytest + Vitest)                     │
│  Modelos, detectores, mappers, validadores, exportador   │
│  Cobertura: >= 70% de lógica de negocio                  │
└─────────────────────────────────────────────────────────┘
```

---

## 2. Tests Unitarios Backend (pytest)

### 2.1 Modelo PurchaseInvoice

```
tests/unit/test_purchase_invoice.py

├── test_create_valid_invoice           → Instancia completa válida
├── test_create_minimal_invoice         → Solo campos requeridos
├── test_supplier_info_complete         → SupplierInfo con todos los campos
├── test_supplier_info_minimal          → SupplierInfo con solo nombre
├── test_document_types                 → Todos los PurchaseDocumentType
├── test_item_creation                  → PurchaseInvoiceItem válido
├── test_item_validation_total          → total ≈ quantity * unit_price
├── test_date_parsing_formats           → YYYY-MM-DD, DD/MM/YYYY, DD-MM-YYYY
├── test_total_validation               → total ≈ subtotal + tax
├── test_items_sum_validation           → subtotal ≈ suma items
├── test_raw_data_preserved             → raw_data guarda JSON original
├── test_decimal_encoding               → JSON encoding sin notación científica
└── test_invalid_required_fields        → Campos requeridos faltantes → error
```

### 2.2 FormatDetector

```
tests/unit/test_format_detector.py

├── test_detect_dte_standard            → Formato estándar → HIGH confidence
├── test_detect_dte_variant_a           → Items en "detalle" → MEDIUM+
├── test_detect_dte_variant_b           → Resumen aplanado → MEDIUM+
├── test_detect_generic_flat            → JSON plano → LOW-MEDIUM
├── test_detect_unknown                 → Sin campos reconocibles → NONE
├── test_confidence_high                → Score >= 0.90 → HIGH
├── test_confidence_medium              → 0.70 <= score < 0.90 → MEDIUM
├── test_confidence_low                 → 0.50 <= score < 0.70 → LOW
├── test_confidence_none                → Score < 0.50 → NONE/UNKNOWN
├── test_all_scores_returned            → Devuelve puntajes de todos los formatos
├── test_empty_json                     → JSON vacío → UNKNOWN
├── test_array_json                     → Lista en vez de dict → manejado
├── test_register_new_format            → Formato nuevo se detecta
└── test_items_key_detected             → Identifica clave de items
```

### 2.3 Mappers

```
tests/unit/test_mappers.py

├── DTEStandardMapper
│   ├── test_map_complete               → Todos los campos mapeados
│   ├── test_map_minimal                → Campos mínimos
│   ├── test_iva_included_in_prices     → IVA dentro de precios
│   ├── test_iva_separate               → IVA separado
│   ├── test_map_items_full             → Items con todos los campos DTE
│   ├── test_map_appendix               → Datos del apéndice
│   ├── test_raw_data_stored            → JSON original en raw_data
│   ├── test_supplier_mapping           → Emisor → SupplierInfo
│   ├── test_receiver_mapping           → Receptor → datos empresa
│   └── test_can_handle_true_false      → Reconoce/rechaza formatos
│
├── GenericFallbackMapper
│   ├── test_synonyms_search            → Busca por tabla de sinónimos
│   ├── test_nested_synonyms            → Sinónimos con notación punto
│   ├── test_partial_extraction         → Extrae lo que puede
│   ├── test_no_fields_error            → Nada extraíble → MappingError
│   └── test_always_can_handle          → can_handle siempre True
│
└── MapperRegistry
    ├── test_register_get               → Registrar y obtener
    ├── test_fallback_used              → UNKNOWN usa fallback
    ├── test_no_mapper_error            → Sin mapper → MapperNotFoundError
    └── test_list_formats               → Lista formatos registrados
```

### 2.4 PurchaseValidator

```
tests/unit/test_purchase_validator.py

├── test_valid_invoice                  → Sin errores ni warnings
├── test_missing_required_field         → ERROR: campo requerido
├── test_missing_recommended            → WARNING: campo recomendado
├── test_total_mismatch_within_tol      → Diferencia < 0.02 → OK
├── test_total_mismatch_over_tol        → Diferencia > 0.02 → WARNING
├── test_iva_13_percent_ok              → IVA correcto → OK
├── test_iva_wrong_percentage           → IVA incorrecto → WARNING
├── test_duplicate_control_number       → Mismo control+NIT → ERROR
├── test_duplicate_document_number      → Mismo doc number → WARNING
├── test_future_date                    → Fecha futura → WARNING
├── test_old_date                       → > 2 años → WARNING
├── test_batch_validation               → Lote mixto (válidas + inválidas)
├── test_custom_tolerance               → Tolerancia personalizada
└── test_validation_result_counts       → Conteo correcto por nivel
```

### 2.5 PurchaseExporter

```
tests/unit/test_purchase_exporter.py

├── test_excel_profile_basico           → 10 columnas en Excel
├── test_excel_profile_completo         → Todas las columnas
├── test_excel_profile_contador         → 15 columnas fiscales
├── test_excel_custom_columns           → Columnas personalizadas
├── test_excel_summary_sheet            → Hoja resumen por proveedor
├── test_excel_items_sheet              → Hoja de items detallados
├── test_csv_export                     → CSV con columnas configuradas
├── test_pdf_export                     → PDF genera correctamente
├── test_json_always_complete           → JSON tiene TODOS los campos
├── test_json_with_raw_data             → JSON incluye raw_data
├── test_empty_list_error               → Lista vacía → error
├── test_currency_format                → Formato $#,##0.00
└── test_group_by_supplier              → Agrupación por proveedor
```

### 2.6 PDFExtractor

```
tests/unit/test_pdf_extractor.py

├── test_extract_digital_pdf            → Extrae texto de PDF digital
├── test_extract_control_number         → Regex captura N° control
├── test_extract_nit                    → Regex captura NIT
├── test_extract_total                  → Regex captura total
├── test_extract_multiple_dates         → Diferentes formatos fecha
├── test_no_text_error                  → PDF sin texto → error
├── test_no_total_error                 → Sin total → error
├── test_partial_extraction             → Campos parciales → OK con warnings
├── test_normalize_output               → Datos normalizados correctamente
└── test_pdf_mapper_integration         → PDFExtractedMapper funciona
```

---

## 3. Tests de Integración API (pytest)

```
tests/api/test_purchases_api.py

├── test_upload_json_files              → 200: Upload exitoso
├── test_upload_pdf_files               → 200: PDF aceptado
├── test_upload_mixed                   → 200: JSON + PDF
├── test_upload_invalid_type            → 400: .txt rechazado
├── test_upload_too_large               → 413: >10MB
├── test_upload_rate_limit              → 429: Rate limit
├── test_process_basic_xlsx             → 202: Procesamiento XLSX
├── test_process_csv                    → 202: Procesamiento CSV
├── test_process_with_columns           → 202: Con perfil de columnas
├── test_process_invalid_upload         → 404: Upload ID inválido
├── test_status_processing              → 200: Status en progreso
├── test_status_completed               → 200: Status completado con stats
├── test_download_xlsx                  → 200: Descarga XLSX
├── test_download_csv                   → 200: Descarga CSV
├── test_list_formats                   → 200: Lista de formatos
└── test_list_columns                   → 200: Lista de columnas
```

---

## 4. Tests E2E (Playwright)

```
e2e/tests/
├── purchases-upload.spec.ts
│   ├── test: Subir archivos JSON de compra
│   ├── test: Subir archivos PDF de compra
│   ├── test: Subir mezcla JSON + PDF
│   └── test: Rechazar archivos no soportados
│
├── purchases-columns.spec.ts
│   ├── test: Seleccionar perfil Básico
│   ├── test: Seleccionar perfil Contador
│   ├── test: Seleccionar columnas personalizadas
│   └── test: Seleccionar/Deseleccionar todo
│
├── purchases-process.spec.ts
│   ├── test: Procesamiento exitoso muestra progreso
│   ├── test: Formatos detectados se muestran
│   └── test: Errores se reportan sin detener proceso
│
└── purchases-full-flow.spec.ts
    ├── test: Flujo completo con perfil Básico → Excel
    ├── test: Flujo completo con perfil Contador → CSV
    └── test: Flujo completo con PDF → JSON
```

---

## 5. Fixtures y Datos de Prueba

```
e2e/fixtures/test-data/purchases/
├── dte_standard_01.json          → DTE estándar completo
├── dte_standard_02.json          → DTE estándar minimal
├── dte_variant_a_01.json         → Items en "detalle"
├── dte_variant_b_01.json         → Resumen aplanado
├── generic_flat_01.json          → JSON plano
├── malformed_01.json             → JSON inválido (para test de errores)
├── duplicate_01.json             → Duplicado de dte_standard_01
└── sample_invoice.pdf            → PDF de factura digital

backend/tests/fixtures/purchases/
├── (mismos archivos que arriba)
└── expected_outputs/
    ├── basico_output.json        → Output esperado perfil básico
    └── completo_output.json      → Output esperado perfil completo
```

---

## 6. Cobertura y Umbrales

| Componente | Umbral Mínimo | Objetivo |
|------------|--------------|----------|
| `purchase_invoice.py` (modelo) | 70% | 85% |
| `format_detector.py` | 70% | 80% |
| `mappers/*.py` (todos) | 70% | 80% |
| `validator.py` | 70% | 85% |
| `purchase_exporter.py` | 70% | 75% |
| `pdf_extractor.py` | 70% | 75% |
| API routes `purchases.py` | 70% | 80% |
| Frontend componentes | 70% | 75% |
| **Total módulo compras** | **70%** | **80%** |

### Cómo verificar cobertura:

```bash
# Backend
cd backend && pytest tests/ --cov=src/core/purchases --cov=src/models/purchase_invoice --cov-report=term-missing

# Frontend
cd frontend && npm test -- --coverage

# E2E (no cuenta para cobertura de código, pero valida flujos)
npm run test:e2e
```

---

## 7. Integración con CI/CD Existente

### GitHub Actions (extender workflow existente)

```yaml
# .github/workflows/test.yml (agregar steps)

jobs:
  test-backend:
    steps:
      - name: Run backend tests (including purchases)
        run: |
          cd backend
          pytest tests/ --cov=src --cov-fail-under=70

  test-frontend:
    steps:
      - name: Run frontend tests (including purchase components)
        run: |
          cd frontend
          npm test -- --coverage --watchAll=false

  test-e2e:
    steps:
      - name: Run E2E tests (including purchase flows)
        run: |
          npm run test:e2e
```

### Pre-commit Hook

```bash
# Antes de cada commit, verificar que los tests pasan
cd backend && pytest tests/unit/ -x --tb=short
cd frontend && npm test -- --watchAll=false
```

---

## 8. Reglas de Testing

1. **Cada componente nuevo DEBE tener tests** antes de hacer merge
2. **Cobertura mínima 70%** — el CI falla si está por debajo
3. **Tests deben ser independientes** — no depender de orden de ejecución
4. **Fixtures compartidas** — datos de prueba en `fixtures/purchases/`
5. **Nombres descriptivos** — `test_detect_dte_standard_with_high_confidence`
6. **No mockear lo que se puede testear directo** — preferir tests de integración reales

---

> **Próximo documento:** [13_REGLAS_NO_NEGOCIABLES](./13_REGLAS_NO_NEGOCIABLES_(Normas-Obligatorias-para-Cada-Agente).md) — Las reglas que todo agente debe cumplir.

# ORDEN EJECUTIVA FASE 1 — Modelo de Datos PurchaseInvoice

```
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║                    ORDEN EJECUTIVA DE DESARROLLO                     ║
║                                                                      ║
║              FASE 1: Modelo de Datos (PurchaseInvoice)               ║
║              Emitida por: Director General de Implementacion         ║
║              Fecha: 2026-02-06                                       ║
║              Estado: ACTIVA                                          ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
```

---

## CONTEXTO DE LA MISION

Se esta construyendo un sistema de procesamiento inteligente de facturas de compra para Paradise JSON Sync. La guia arquitectonica completa (14 documentos, 73 tareas, 9 fases) esta en la rama `claude/invoice-processing-research-ULZwR` y **NO esta mergeada a main**.

Esta orden corresponde a la **FASE 1: Modelo de Datos**, la primera fase de implementacion despues de la documentacion.

---

## 1. LECTURA OBLIGATORIA ANTES DE ESCRIBIR CODIGO

El agente DEBE leer estos documentos **en este orden exacto** antes de tocar cualquier archivo:

| Orden | Documento | Ubicacion | Por que |
|-------|-----------|-----------|---------|
| 1 | EL_PUNTO_DE_PARTIDA | `docs/EL_PUNTO_DE_PARTIDA_by_SamuelERS.md` | Entender el sistema de roles |
| 2 | Reglas No Negociables | `docs/02_arquitectura/Caso_Facturas_Compras_20260206/13_REGLAS_NO_NEGOCIABLES_(Normas-Obligatorias-para-Cada-Agente).md` | Convenciones obligatorias |
| 3 | Modelo Canonico | `docs/02_arquitectura/Caso_Facturas_Compras_20260206/04_MODELO_CANONICO_(Estructura-Universal-de-Factura-de-Compra).md` | Especificacion completa del modelo a implementar |
| 4 | TODO List | `docs/02_arquitectura/Caso_Facturas_Compras_20260206/01_TODO_LIST_PRINCIPAL_(Lista-Maestra-de-Tareas).md` | Tareas 1.1 a 1.7 |
| 5 | Modelo Invoice existente | `backend/src/models/invoice.py` | Patron a seguir (Pydantic v2, validators, Decimal) |
| 6 | Tests existentes del modelo | `backend/tests/unit/test_models_invoice.py` | Patron de testing a replicar |
| 7 | Conftest existente | `backend/tests/conftest.py` | Fixtures a extender |

**IMPORTANTE:** Toda la documentacion arquitectonica esta en la rama `claude/invoice-processing-research-ULZwR`. El agente debe trabajar sobre **esa misma rama** o crear una rama hija desde ella.

---

## 2. DONDE ESTA EL PLAN ARQUITECTONICO

```
Repositorio: SamuelERS/paradise-json-sync
Rama del plan: claude/invoice-processing-research-ULZwR (NO esta en main)
Carpeta: docs/02_arquitectura/Caso_Facturas_Compras_20260206/
```

El agente debe hacer `git fetch origin claude/invoice-processing-research-ULZwR` si no tiene la rama localmente, y partir desde ahi.

---

## 3. ROL DEL AGENTE

| Aspecto | Valor |
|---------|-------|
| **Rol principal** | Desarrollador de Elite (Backend) |
| **Rol secundario** | Inspector de Elite (auto-revision) |
| **Responsabilidad** | Implementar el modelo PurchaseInvoice con tests >= 70% |

---

## 4. TAREAS A COMPLETAR (7 tareas)

Referencia: TODO List, tareas 1.1 a 1.7

### Tarea 1.1 — Crear modelo `PurchaseInvoice` en Pydantic v2

**Archivo destino:** `backend/src/models/purchase_invoice.py`

Modelo principal con estos grupos de campos:
- **Identificacion:** `document_number` (str, requerido), `control_number` (Optional[str]), `document_type` (PurchaseDocumentType), `issue_date` (date), `emission_time` (Optional[str]), `currency` (str, default "USD"), `dte_version` (Optional[int])
- **Proveedor:** `supplier` (SupplierInfo, requerido)
- **Receptor:** `receiver_name`, `receiver_nit`, `receiver_nrc`, `receiver_doc_type`, `receiver_address`, `receiver_phone`, `receiver_email` — todos Optional[str]
- **Items:** `items: list[PurchaseInvoiceItem] = []`
- **Resumen financiero:** `subtotal`, `total_taxable`, `total_exempt`, `total_non_subject`, `total_discount`, `tax`, `iva_retained`, `total` — todos Decimal (los que apliquen default=Decimal("0"))
- **Extras:** `total_in_words` (Optional[str]), `payment_condition` (Optional[int]), `appendix_data` (Optional[dict]), `tax_seal` (Optional[str])
- **Metadatos:** `source_file`, `detected_format` (Optional[str]), `detection_confidence` (Optional[float]), `processing_warnings` (list[str] = []), `raw_data` (Optional[dict] = None)

### Tarea 1.2 — Crear modelo `PurchaseInvoiceItem`

En el mismo archivo. Campos:
- `item_number` (Optional[int]), `product_code` (Optional[str])
- `description` (str, requerido)
- `unit_measure` (Optional[int])
- `quantity` (Decimal, requerido, gt=0)
- `unit_price` (Decimal, requerido)
- `original_price` (Optional[Decimal])
- `discount` (Decimal, default=0)
- `taxable_sale`, `exempt_sale`, `non_subject_sale`, `item_tax` (Decimal, default=0)
- `total` (Decimal, requerido)

### Tarea 1.3 — Crear enum `PurchaseDocumentType`

En el mismo archivo. 9 valores (ver doc 04, seccion 4):
`FACTURA`, `CCF`, `NOTA_CREDITO`, `NOTA_DEBITO`, `FACTURA_EXPORTACION`, `SUJETO_EXCLUIDO`, `COMPROBANTE_RETENCION`, `COMPROBANTE_DONACION`, `DESCONOCIDO`

### Tarea 1.4 — Crear modelo `SupplierInfo`

En el mismo archivo. Campos:
`name` (str, requerido), `commercial_name`, `nit`, `nrc`, `economic_activity`, `address`, `phone`, `email`, `establishment_code`, `establishment_type` — todos Optional[str]

### Tarea 1.5 — Campo `raw_data: Optional[dict] = None`

Ya incluido en tarea 1.1. Verificar que esta presente con el tipo correcto.

### Tarea 1.6 — Validadores del modelo

Implementar siguiendo el **mismo patron exacto** de `Invoice` en `backend/src/models/invoice.py`:

| Validador | Tipo | Comportamiento |
|-----------|------|---------------|
| `parse_date` | `@field_validator("issue_date", mode="before")` | Acepta str o date. Formatos: `%Y-%m-%d`, `%d/%m/%Y`, `%d-%m-%Y` |
| `validate_totals` | `@model_validator(mode="after")` | `total ≈ subtotal + tax` (tolerancia `Decimal("0.01")`). **WARNING, no error** si no coincide |
| `validate_items_subtotal` | `@model_validator(mode="after")` | `subtotal ≈ sum(items.total)` (tolerancia). **WARNING, no error** |
| `validate_item_total` | En `PurchaseInvoiceItem`, `@model_validator(mode="after")` | `total ≈ quantity * unit_price` (tolerancia). **WARNING, no error** |

**CRITICO:** Los validadores de totales emiten `logger.warning()`, **NO** lanzan `ValidationError`. Esto es identico al comportamiento del Invoice existente.

### Tarea 1.7 — Tests unitarios (>= 70% cobertura)

**Archivo destino:** `backend/tests/unit/test_purchase_invoice.py`

Seguir el **patron exacto** de `backend/tests/unit/test_models_invoice.py`:
- Clases de agrupacion: `TestPurchaseDocumentType`, `TestSupplierInfo`, `TestPurchaseInvoiceItem`, `TestPurchaseInvoice`
- Fixtures en `conftest.py`: `sample_supplier_info`, `sample_purchase_invoice_item`, `sample_purchase_invoice`
- Docstrings bilingues en las clases de test

**Tests minimos requeridos:**

```
test_purchase_invoice.py

├── TestPurchaseDocumentType
│   ├── test_all_document_types_exist        → 9 tipos
│   └── test_document_type_values            → Valores string correctos
│
├── TestSupplierInfo
│   ├── test_create_supplier_full            → Todos los campos
│   ├── test_create_supplier_minimal         → Solo name (requerido)
│   └── test_supplier_missing_name           → ValidationError
│
├── TestPurchaseInvoiceItem
│   ├── test_create_item_valid               → Item completo
│   ├── test_item_total_validation_warning   → total != qty*price → warning
│   ├── test_item_missing_description        → ValidationError
│   └── test_item_zero_quantity              → ValidationError (gt=0)
│
├── TestPurchaseInvoice
│   ├── test_create_invoice_full             → Factura completa
│   ├── test_create_invoice_minimal          → Campos minimos requeridos
│   ├── test_date_parsing_iso               → "2026-02-06"
│   ├── test_date_parsing_slash             → "06/02/2026"
│   ├── test_date_parsing_dash              → "06-02-2026"
│   ├── test_date_invalid                   → ValidationError
│   ├── test_total_validation_warning       → total != subtotal+tax → warning
│   ├── test_items_subtotal_warning         → subtotal != sum(items) → warning
│   ├── test_raw_data_stores_original       → raw_data preserva JSON
│   ├── test_all_document_types_accepted    → 9 tipos de documento
│   ├── test_missing_document_number        → ValidationError
│   └── test_supplier_required              → ValidationError sin supplier
```

**Cobertura minima: 70%.** Verificar con:
```bash
cd backend && python -m pytest tests/unit/test_purchase_invoice.py --cov=src/models/purchase_invoice --cov-report=term-missing --cov-fail-under=70
```

---

## 5. ARCHIVOS A CREAR/MODIFICAR

| Accion | Archivo | Descripcion |
|--------|---------|-------------|
| **CREAR** | `backend/src/models/purchase_invoice.py` | Modelo completo (< 500 lineas) |
| **MODIFICAR** | `backend/src/models/__init__.py` | Agregar exports: `PurchaseInvoice`, `PurchaseInvoiceItem`, `PurchaseDocumentType`, `SupplierInfo` |
| **CREAR** | `backend/tests/unit/test_purchase_invoice.py` | Tests unitarios (>= 70% cobertura) |
| **MODIFICAR** | `backend/tests/conftest.py` | Agregar fixtures: `sample_supplier_info`, `sample_purchase_invoice_item`, `sample_purchase_invoice` |

---

## 6. PATRONES TECNICOS OBLIGATORIOS

Estos patrones fueron extraidos del modelo `Invoice` existente y **deben replicarse exactamente**:

### Imports
```python
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
import logging

from pydantic import BaseModel, Field, field_validator, model_validator

logger = logging.getLogger(__name__)
```

### Model Config
```python
class Config:
    json_encoders = {
        Decimal: lambda v: float(v),
        date: lambda v: v.isoformat(),
    }
```

### Decimal Fields
```python
subtotal: Decimal = Field(default=Decimal("0"), ge=0)
total: Decimal = Field(..., ge=0)  # Requerido
```

### Type Annotations
- Usar `list[X]` (Python 3.10+ lowercase), NO `List[X]`
- Usar `Optional[X]` de typing
- Line length maximo: 100 caracteres (black + ruff)

### Docstrings
```python
"""
Purchase Invoice Model / Modelo de Factura de Compra
====================================================

Canonical data model for purchase invoices.
Modelo canonico para facturas de compra.
"""
```

---

## 7. REGLAS DE RETROCOMPATIBILIDAD

### NO TOCAR (bajo ninguna circunstancia)

| Archivo | Razon |
|---------|-------|
| `backend/src/models/invoice.py` | Sistema de ventas — funciona perfecto |
| `backend/src/core/json_processor.py` | Sistema de ventas |
| `backend/src/core/excel_exporter.py` | Sistema de ventas |
| `backend/src/api/routes/upload.py` | Endpoints de ventas |
| Cualquier archivo en `frontend/` | No aplica en FASE 1 |

### VERIFICAR DESPUES DE IMPLEMENTAR

```bash
# 1. Tests existentes DEBEN seguir pasando
cd backend && python -m pytest tests/ -v

# 2. Tests nuevos deben pasar con >= 70%
cd backend && python -m pytest tests/unit/test_purchase_invoice.py --cov=src/models/purchase_invoice --cov-report=term-missing --cov-fail-under=70

# 3. Cobertura global no debe bajar del 70%
cd backend && python -m pytest tests/ --cov=src --cov-fail-under=70
```

---

## 8. CONVENCION DE COMMITS

```
FASE-1 MODELO: descripcion clara en espanol de lo que se hizo
```

**Ejemplos validos:**
```
FASE-1 MODELO: Crear PurchaseInvoice, SupplierInfo y PurchaseDocumentType con validadores
FASE-1 MODELO: Tests unitarios del modelo PurchaseInvoice con 85% cobertura
```

---

## 9. ENTREGABLES ESPERADOS

Al finalizar, el agente debe entregar:

| Entregable | Requisito |
|------------|-----------|
| Modelo `PurchaseInvoice` funcional | Todos los campos del doc 04 |
| Modelo `PurchaseInvoiceItem` | Con validador de totales (warning) |
| Modelo `SupplierInfo` | Con campo `name` requerido |
| Enum `PurchaseDocumentType` | 9 valores |
| Validadores de fecha, totales, items | Patron identico a Invoice |
| Tests unitarios | >= 70% cobertura del archivo `purchase_invoice.py` |
| `__init__.py` actualizado | 4 nuevos exports |
| `conftest.py` actualizado | 3 nuevas fixtures |
| Tests existentes pasando | TODOS (cero regresiones) |
| TODO list actualizado | Tareas 1.1-1.7 marcadas 🟢 |

---

## 10. CERTIFICADO DE CALIDAD REQUERIDO

Al finalizar TODA la FASE 1, el agente DEBE:

1. **Ejecutar TODOS los tests** (existentes + nuevos) y confirmar que pasan
2. **Reportar cobertura exacta** del archivo `purchase_invoice.py`
3. **Confirmar cero regresiones** en tests existentes
4. **Revisar su propio codigo** buscando:
   - Deuda tecnica
   - Campos faltantes vs doc 04
   - Validadores faltantes
   - Tests faltantes
   - Lineas > 100 caracteres
   - Funciones > 50 lineas
   - Archivo > 500 lineas
5. **Emitir un certificado de garantia de calidad** con:
   - Resultado de tests (pasados/fallados)
   - Porcentaje de cobertura
   - Declaracion de retrocompatibilidad
   - Lista de archivos creados/modificados
   - Firma del agente

---

## 11. SETUP DEL ENTORNO

Antes de empezar, el agente debe asegurarse de que las dependencias estan instaladas:

```bash
cd /home/user/paradise-json-sync/backend
pip install -e ".[dev]"
```

Si hay problemas con el entorno, resolver ANTES de empezar a codificar.

---

```
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║  FIRMADO: Claude (Opus 4.6) — Director General de Implementacion    ║
║  FECHA: 2026-02-06                                                   ║
║  DESTINO: Desarrollador de Elite (Backend) — FASE 1                  ║
║  RAMA: claude/invoice-processing-research-ULZwR                      ║
║  PRIORIDAD: ALTA — Primera fase de implementacion                    ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
```

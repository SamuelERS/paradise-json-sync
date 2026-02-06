# 📊 Exportador de Compras — Reportes Configurables sin Perder Datos

> **⚠️ ANTES DE EMPEZAR:** Lee [EL_PUNTO_DE_PARTIDA](../../EL_PUNTO_DE_PARTIDA_by_SamuelERS.md) para identificar tu rol y qué documentos te corresponden leer según tu misión.

> **¿Qué es esto?** Este documento explica cómo el sistema genera reportes donde el usuario elige qué columnas ver, pero sin perder NINGÚN dato. La regla de oro: los datos siempre están completos, la vista es configurable.

### Roles Requeridos para este Documento

| Rol | Misión aquí |
|-----|-------------|
| 👨‍💻 **Desarrollador de Elite (Backend)** | Implementar `PurchaseExporter` con columnas dinámicas |
| 👨‍💻 **Desarrollador de Elite (Frontend)** | Implementar `ColumnConfigurator` en la UI |
| ✅ **Inspector de Elite** | Verificar que NINGÚN dato se pierde al filtrar columnas |

### Tareas de Implementación (FASE 6)

| Tarea | Agente | Archivo Destino |
|-------|--------|-----------------|
| Crear `PurchaseExporter` | 👨‍💻 Desarrollador Backend | `backend/src/core/purchases/purchase_exporter.py` |
| Definir columnas y perfiles | 👨‍💻 Desarrollador Backend | Mismo archivo |
| Exportación Excel dinámica | 👨‍💻 Desarrollador Backend | Mismo archivo |
| Exportación CSV dinámica | 👨‍💻 Desarrollador Backend | Mismo archivo |
| Exportación PDF dinámica | 👨‍💻 Desarrollador Backend | Mismo archivo |
| Exportación JSON completa | 👨‍💻 Desarrollador Backend | Mismo archivo |
| Tests unitarios (>=70%) | 👨‍💻 Desarrollador Backend | `backend/tests/unit/test_purchase_exporter.py` |
| Verificar cero pérdida datos | ✅ Inspector de Elite | Auditar JSON export vs input |

### Nota sobre Rendimiento

> Para lotes de más de 5,000 facturas, se recomienda exportar a CSV en lugar de Excel (menor uso de memoria).
> Excel soporta hasta 1,048,576 filas, pero archivos grandes (>10MB) pueden ser lentos de abrir.
> JSON siempre exporta todos los campos — sin límite de columnas configurables.

---

## 1. Principio Fundamental

```
┌─────────────────────────────────────────────────────────┐
│  DATOS COMPLETOS (siempre)                              │
│  ┌─────────────────────────────────────────────────┐    │
│  │  30+ campos por factura                          │    │
│  │  Todos almacenados en PurchaseInvoice            │    │
│  │  raw_data contiene JSON original                 │    │
│  └─────────────────────────────────────────────────┘    │
│                                                         │
│  VISTA CONFIGURABLE (el usuario decide)                 │
│  ┌─────────────────────────────────────────────────┐    │
│  │  Excel/CSV/PDF: solo columnas seleccionadas      │    │
│  │  JSON: SIEMPRE todos los campos                  │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

**Clave:** Si el usuario desactiva una columna en Excel, los datos NO se borran. Solo se ocultan en ese reporte. Si luego exporta a JSON o cambia el perfil, los datos están ahí.

---

## 2. Columnas Disponibles

### Categoría: Identificación del Documento

| ID | Label (Excel) | Descripción |
|----|---------------|-------------|
| `control_number` | N° Control | Número de control DTE |
| `document_number` | Código Gen. | UUID del documento |
| `document_type` | Tipo Doc | factura, ccf, nota_credito, etc. |
| `issue_date` | Fecha | Fecha de emisión |
| `emission_time` | Hora | Hora de emisión |
| `currency` | Moneda | USD por defecto |
| `dte_version` | Versión DTE | Versión del esquema |

### Categoría: Proveedor (Emisor)

| ID | Label (Excel) | Descripción |
|----|---------------|-------------|
| `supplier_name` | Proveedor | Nombre legal |
| `supplier_commercial` | Nombre Comercial | Nombre comercial |
| `supplier_nit` | NIT Proveedor | NIT del proveedor |
| `supplier_nrc` | NRC Proveedor | NRC del proveedor |
| `supplier_activity` | Actividad | Actividad económica |
| `supplier_address` | Dir. Proveedor | Dirección |
| `supplier_phone` | Tel. Proveedor | Teléfono |
| `supplier_email` | Email Proveedor | Correo electrónico |

### Categoría: Receptor (Nuestra Empresa)

| ID | Label (Excel) | Descripción |
|----|---------------|-------------|
| `receiver_name` | Receptor | Nombre de nuestra empresa |
| `receiver_nit` | NIT Receptor | Nuestro NIT |
| `receiver_nrc` | NRC Receptor | Nuestro NRC |

### Categoría: Montos

| ID | Label (Excel) | Descripción |
|----|---------------|-------------|
| `total_taxable` | Gravado | Total gravado |
| `total_exempt` | Exento | Total exento |
| `total_non_subject` | No Sujeto | Total no sujeto |
| `total_discount` | Descuento | Total descuentos |
| `subtotal` | Subtotal | Subtotal |
| `tax` | IVA | Impuesto al valor agregado |
| `iva_retained` | IVA Retenido | IVA retenido (si aplica) |
| `total` | Total | Total a pagar |
| `total_in_words` | Total Letras | Monto en palabras |

### Categoría: Pago y Adicional

| ID | Label (Excel) | Descripción |
|----|---------------|-------------|
| `payment_condition` | Condición | CONTADO / CRÉDITO |
| `tax_seal` | Sello Fiscal | Sello de Hacienda |
| `source_file` | Archivo | Nombre del archivo fuente |
| `detected_format` | Formato | Formato detectado |
| `detection_confidence` | Confianza | Nivel de confianza (0-1) |

---

## 3. Perfiles de Columnas

### Perfil "Básico" (10 columnas)

Para revisión rápida. Solo lo esencial.

```python
PROFILE_BASICO = [
    "control_number", "document_type", "issue_date",
    "supplier_name", "supplier_nit",
    "subtotal", "tax", "total",
    "payment_condition", "source_file",
]
```

### Perfil "Completo" (todas las columnas)

Todos los campos disponibles. Para auditoría total.

```python
PROFILE_COMPLETO = [col["id"] for col in ALL_COLUMNS]  # Todas
```

### Perfil "Contador" (15 columnas)

Los campos que el contador necesita para contabilidad fiscal.

```python
PROFILE_CONTADOR = [
    "control_number", "document_type", "issue_date", "emission_time",
    "supplier_name", "supplier_nit", "supplier_nrc",
    "receiver_nit",
    "total_taxable", "total_exempt", "total_non_subject",
    "total_discount", "subtotal", "tax", "total",
]
```

### Perfil "Custom" (selección manual)

El usuario elige exactamente qué columnas quiere.

---

## 4. Clase PurchaseExporter

```python
class PurchaseExporter:
    """
    Exportador de facturas de compra con columnas configurables.

    Reutiliza lógica de formateo del ExcelExporter existente
    pero con columnas dinámicas y perspectiva de compras.
    """

    def __init__(self, currency_symbol: str = "$", decimal_places: int = 2):
        self.currency_symbol = currency_symbol
        self.decimal_places = decimal_places

    def export(
        self,
        invoices: list[PurchaseInvoice],
        format: str,
        column_profile: str = "completo",
        custom_columns: list[str] = None,
        options: dict = None,
    ) -> str:
        """
        Exporta facturas al formato solicitado.

        Args:
            invoices: Lista de facturas de compra
            format: "xlsx", "csv", "pdf", "json"
            column_profile: "basico", "completo", "contador", "custom"
            custom_columns: Lista de IDs de columnas (si profile="custom")
            options: Opciones adicionales (summary, items, group_by)

        Returns:
            Ruta al archivo generado
        """
        # Resolver columnas
        columns = self._resolve_columns(column_profile, custom_columns)

        if format == "xlsx":
            return self._export_excel(invoices, columns, options)
        elif format == "csv":
            return self._export_csv(invoices, columns, options)
        elif format == "pdf":
            return self._export_pdf(invoices, columns, options)
        elif format == "json":
            return self._export_json(invoices, options)  # JSON siempre completo
```

---

## 5. Exportación Excel (Detalle)

```python
def _export_excel(self, invoices, columns, options):
    """
    Genera Excel con:
    - Hoja 1: Facturas (columnas configuradas)
    - Hoja 2: Resumen por proveedor (si include_summary=True)
    - Hoja 3: Items detallados (si include_items_sheet=True)
    """
    workbook = Workbook()

    # Hoja principal: solo columnas seleccionadas
    sheet = workbook.active
    sheet.title = "Compras - Facturas"

    # Headers dinámicos
    headers = [COLUMN_LABELS[col_id] for col_id in columns]
    for col, header in enumerate(headers, 1):
        cell = sheet.cell(row=1, column=col, value=header)
        self._style_header(cell)

    # Datos
    for row, invoice in enumerate(invoices, 2):
        for col, col_id in enumerate(columns, 1):
            value = self._get_column_value(invoice, col_id)
            cell = sheet.cell(row=row, column=col, value=value)
            if col_id in CURRENCY_COLUMNS:
                cell.number_format = "$#,##0.00"

    # Hoja resumen (agrupado por proveedor)
    if options.get("include_summary"):
        self._create_purchase_summary(workbook, invoices)

    # Hoja de items
    if options.get("include_items_sheet"):
        self._create_items_sheet(workbook, invoices)

    return workbook
```

### Resumen por Proveedor (Hoja 2)

```
┌────────────────────────────────────────────────────────────┐
│  RESUMEN POR PROVEEDOR                                     │
├──────────────────────┬──────────┬───────────┬──────────────┤
│  Proveedor           │ Facturas │ IVA       │ Total        │
├──────────────────────┼──────────┼───────────┼──────────────┤
│  DISTRIBUIDORA ABC   │ 12       │ $156.00   │ $1,356.00    │
│  SUMINISTROS XYZ     │ 8        │ $104.00   │ $904.00      │
│  SERVICIOS 123       │ 5        │ $65.00    │ $565.00      │
├──────────────────────┼──────────┼───────────┼──────────────┤
│  TOTAL               │ 25       │ $325.00   │ $2,825.00    │
└──────────────────────┴──────────┴───────────┴──────────────┘
```

---

## 6. Exportación JSON (Siempre Completa)

El JSON **nunca** filtra columnas. Siempre exporta todo. Esto garantiza cero pérdida de datos.

```python
def _export_json(self, invoices, options):
    """
    JSON siempre exporta TODOS los campos.
    Si include_raw_data=True, incluye el JSON original de cada factura.
    """
    data = {
        "metadata": {
            "exported_at": datetime.utcnow().isoformat(),
            "total_invoices": len(invoices),
            "total_amount": sum(float(inv.total) for inv in invoices),
            "format_version": "1.0",
            "type": "purchase_invoices",
        },
        "invoices": [
            self._invoice_to_full_dict(inv, include_raw=options.get("include_raw_data"))
            for inv in invoices
        ],
    }
    return data
```

---

## 7. Mapeo de Columna a Valor

```python
def _get_column_value(self, invoice: PurchaseInvoice, column_id: str):
    """
    Obtiene el valor de una columna para una factura.
    Mapea IDs de columna a atributos del modelo.
    """
    COLUMN_MAP = {
        "control_number": lambda inv: inv.control_number or "",
        "document_number": lambda inv: inv.document_number,
        "document_type": lambda inv: inv.document_type.value,
        "issue_date": lambda inv: inv.issue_date.isoformat(),
        "emission_time": lambda inv: inv.emission_time or "",
        "dte_version": lambda inv: inv.dte_version or "",
        "currency": lambda inv: inv.currency,
        "supplier_name": lambda inv: inv.supplier.name,
        "supplier_commercial": lambda inv: inv.supplier.commercial_name or "",
        "supplier_nit": lambda inv: inv.supplier.nit or "",
        "supplier_nrc": lambda inv: inv.supplier.nrc or "",
        "supplier_address": lambda inv: inv.supplier.address or "",
        "supplier_phone": lambda inv: inv.supplier.phone or "",
        "supplier_activity": lambda inv: inv.supplier.economic_activity or "",
        "supplier_email": lambda inv: inv.supplier.email or "",
        "receiver_name": lambda inv: inv.receiver_name or "",
        "receiver_nit": lambda inv: inv.receiver_nit or "",
        "receiver_nrc": lambda inv: inv.receiver_nrc or "",
        "total_taxable": lambda inv: float(inv.total_taxable),
        "total_exempt": lambda inv: float(inv.total_exempt),
        "total_non_subject": lambda inv: float(inv.total_non_subject),
        "total_discount": lambda inv: float(inv.total_discount),
        "subtotal": lambda inv: float(inv.subtotal),
        "tax": lambda inv: float(inv.tax),
        "iva_retained": lambda inv: float(inv.iva_retained),
        "total": lambda inv: float(inv.total),
        "total_in_words": lambda inv: inv.total_in_words or "",
        "payment_condition": lambda inv: self._payment_text(inv.payment_condition),
        "tax_seal": lambda inv: inv.tax_seal or "",
        "source_file": lambda inv: inv.source_file or "",
        "detected_format": lambda inv: inv.detected_format or "",
        "detection_confidence": lambda inv: f"{(inv.detection_confidence or 0)*100:.0f}%",
    }

    getter = COLUMN_MAP.get(column_id)
    return getter(invoice) if getter else ""
```

---

## 8. Testing del Exportador

```
tests/unit/test_purchase_exporter.py

├── test_export_excel_profile_basico      → 10 columnas
├── test_export_excel_profile_completo    → Todas las columnas
├── test_export_excel_profile_contador    → 15 columnas fiscales
├── test_export_excel_custom_columns      → Columnas personalizadas
├── test_export_excel_with_summary        → Hoja de resumen incluida
├── test_export_excel_with_items          → Hoja de items incluida
├── test_export_csv_basic                 → CSV con columnas básicas
├── test_export_pdf_basic                 → PDF con columnas básicas
├── test_export_json_always_complete      → JSON tiene TODOS los campos
├── test_export_json_with_raw_data        → JSON incluye raw_data original
├── test_column_value_mapping             → Cada columna devuelve valor correcto
├── test_currency_formatting              → Formato $#,##0.00
├── test_empty_invoices_list              → Lista vacía → error
└── test_group_by_supplier                → Resumen agrupado por proveedor
```

**Cobertura esperada:** >= 70%

---

> **Próximo documento:** [10_SOPORTE_PDF](./10_SOPORTE_PDF_(Extraccion-de-Datos-desde-PDF).md) — Cómo extraer datos desde PDF.

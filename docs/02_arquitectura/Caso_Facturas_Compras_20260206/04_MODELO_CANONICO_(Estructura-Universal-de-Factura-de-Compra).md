# 📐 Modelo Canónico — PurchaseInvoice

> **¿Qué es esto?** Este documento define la estructura de datos universal para las facturas de compra. Es el "idioma común" al que todos los formatos se traducen. Es el corazón del sistema.

---

## 1. ¿Qué es un Modelo Canónico?

Imagina que tienes 5 proveedores y cada uno habla un "idioma" diferente (formato JSON distinto). En lugar de enseñarle al sistema 5 idiomas, definimos un **idioma central** al que todos se traducen.

```
Proveedor A (formato A) ──┐
Proveedor B (formato B) ──┤
Proveedor C (formato C) ──┼──→ PurchaseInvoice (modelo canónico) ──→ Reporte
Proveedor D (formato D) ──┤
Proveedor E (formato E) ──┘
```

**Ventaja:** Agregar un nuevo proveedor = crear un traductor nuevo. El resto del sistema no cambia.

---

## 2. Relación con el Modelo Existente (Invoice)

| Aspecto | `Invoice` (Ventas) | `PurchaseInvoice` (Compras) |
|---------|--------------------|-----------------------------|
| **Archivo** | `models/invoice.py` | `models/purchase_invoice.py` |
| **Perspectiva** | La empresa es el EMISOR | La empresa es el RECEPTOR |
| **Campos emisor** | Son los datos de la empresa | Son los datos del PROVEEDOR |
| **Campos receptor** | Son los datos del CLIENTE | Son los datos de la EMPRESA |
| **Se toca** | NO — funciona perfecto | NUEVO — se crea desde cero |

**Decisión arquitectónica:** `PurchaseInvoice` es un modelo **independiente** de `Invoice`, no hereda de él. Razón: las perspectivas son opuestas y los campos adicionales son diferentes.

---

## 3. Estructura del Modelo PurchaseInvoice

### 3.1 Campos Principales (Core)

```python
class PurchaseInvoice(BaseModel):
    """Factura de compra normalizada — modelo canónico."""

    # === IDENTIFICACIÓN DEL DOCUMENTO ===
    document_number: str          # Código de generación (UUID del DTE)
    control_number: Optional[str] # Número de control (DTE-XX-XXXXXXXX-XXXXXXXXX)
    document_type: PurchaseDocumentType  # Tipo: factura, ccf, nota_credito, etc.
    issue_date: date              # Fecha de emisión
    emission_time: Optional[str]  # Hora de emisión (HH:MM:SS)
    currency: str = "USD"         # Moneda (ISO 4217)
    dte_version: Optional[int]    # Versión del esquema DTE (1, 2, 3)
```

### 3.2 Datos del Proveedor (Emisor en el DTE)

```python
    # === PROVEEDOR (quien emite la factura) ===
    supplier: SupplierInfo        # Objeto con todos los datos del proveedor

class SupplierInfo(BaseModel):
    """Información del proveedor que emite la factura."""
    name: str                         # Nombre legal (razón social)
    commercial_name: Optional[str]    # Nombre comercial
    nit: Optional[str]                # NIT del proveedor
    nrc: Optional[str]                # NRC del proveedor
    economic_activity: Optional[str]  # Actividad económica (código MH)
    address: Optional[str]            # Dirección completa
    phone: Optional[str]              # Teléfono
    email: Optional[str]              # Correo electrónico
    establishment_code: Optional[str] # Código de establecimiento (codEstableMH)
    establishment_type: Optional[str] # Tipo de establecimiento
```

### 3.3 Datos de la Empresa (Receptor en el DTE)

```python
    # === EMPRESA (quien recibe la factura = nosotros) ===
    receiver_name: Optional[str]      # Nombre de la empresa receptora
    receiver_nit: Optional[str]       # NIT de la empresa
    receiver_nrc: Optional[str]       # NRC de la empresa
    receiver_doc_type: Optional[str]  # Tipo de documento del receptor
    receiver_address: Optional[str]   # Dirección del receptor
    receiver_phone: Optional[str]     # Teléfono del receptor
    receiver_email: Optional[str]     # Correo del receptor
```

### 3.4 Items de Línea

```python
    # === ITEMS (productos/servicios comprados) ===
    items: list[PurchaseInvoiceItem] = []

class PurchaseInvoiceItem(BaseModel):
    """Ítem individual de la factura de compra."""
    item_number: Optional[int]        # Número de secuencia (numItem)
    product_code: Optional[str]       # Código del producto
    description: str                  # Descripción del producto/servicio
    unit_measure: Optional[int]       # Código de unidad de medida
    quantity: Decimal                  # Cantidad (>0)
    unit_price: Decimal               # Precio unitario
    original_price: Optional[Decimal] # Precio original antes de ajustes
    discount: Decimal = 0             # Monto de descuento
    taxable_sale: Decimal = 0         # Venta gravada
    exempt_sale: Decimal = 0          # Venta exenta
    non_subject_sale: Decimal = 0     # Venta no sujeta
    item_tax: Decimal = 0             # IVA del ítem
    total: Decimal                    # Total del ítem
```

### 3.5 Resumen Financiero

```python
    # === RESUMEN FINANCIERO ===
    subtotal: Decimal                 # Subtotal (suma de items)
    total_taxable: Decimal = 0        # Total gravado
    total_exempt: Decimal = 0         # Total exento
    total_non_subject: Decimal = 0    # Total no sujeto
    total_discount: Decimal = 0       # Total descuentos
    tax: Decimal = 0                  # IVA total
    iva_retained: Decimal = 0         # IVA retenido (si aplica)
    total: Decimal                    # Total a pagar
    total_in_words: Optional[str]     # Total en letras
    payment_condition: Optional[int]  # 1=Contado, 2=Crédito
```

### 3.6 Datos Adicionales y Metadatos

```python
    # === APÉNDICE / DATOS ADICIONALES ===
    appendix_data: Optional[dict]     # Datos del apéndice (variable por proveedor)

    # === SELLO FISCAL ===
    tax_seal: Optional[str]           # Sello recibido de Hacienda

    # === METADATOS DEL PROCESAMIENTO ===
    source_file: Optional[str]        # Archivo fuente original
    detected_format: Optional[str]    # Formato detectado por FormatDetector
    detection_confidence: Optional[float]  # Confianza de la detección (0-1)
    processing_warnings: list[str] = []    # Advertencias del procesamiento
    raw_data: Optional[dict] = None   # JSON original COMPLETO (cero pérdida)
```

---

## 4. Enum PurchaseDocumentType

```python
class PurchaseDocumentType(str, Enum):
    """Tipos de documento DTE que podemos recibir como compra."""

    FACTURA = "factura"                    # 01: Factura de Consumidor Final
    CCF = "ccf"                            # 03: Comprobante de Crédito Fiscal
    NOTA_CREDITO = "nota_credito"          # 05: Nota de Crédito
    NOTA_DEBITO = "nota_debito"            # 06: Nota de Débito
    FACTURA_EXPORTACION = "factura_exp"    # 11: Factura de Exportación
    SUJETO_EXCLUIDO = "sujeto_excluido"   # 14: Factura Sujeto Excluido
    COMPROBANTE_RETENCION = "retencion"    # 07: Comprobante de Retención
    COMPROBANTE_DONACION = "donacion"      # 15: Comprobante de Donación
    DESCONOCIDO = "desconocido"            # Tipo no reconocido
```

**Nota:** El modelo de ventas solo maneja `factura`, `ccf` y `nota_credito`. Las compras pueden incluir todos los tipos DTE porque recibimos documentos de todo tipo.

---

## 5. Validadores del Modelo

### 5.1 Validación de Fecha (igual que Invoice actual)

```python
@field_validator("issue_date", mode="before")
def parse_date(cls, value):
    """Acepta múltiples formatos: YYYY-MM-DD, DD/MM/YYYY, DD-MM-YYYY"""
```

### 5.2 Validación de Totales

```python
@model_validator(mode="after")
def validate_totals(self):
    """Verifica: total ≈ subtotal + tax (tolerancia: 0.01)"""

@model_validator(mode="after")
def validate_items_subtotal(self):
    """Verifica: subtotal ≈ suma de items.total (tolerancia: 0.01)"""
```

### 5.3 Validación de Item

```python
# En PurchaseInvoiceItem:
@model_validator(mode="after")
def validate_item_total(self):
    """
    Verifica: total ≈ quantity * unit_price (tolerancia: 0.01)
    WARNING (no error) si no coincide — algunos proveedores
    tienen descuentos embebidos en el precio.
    """
```

---

## 6. El Campo `raw_data` — Cero Pérdida de Datos

Este campo es **crítico**. Almacena el JSON original **completo** tal como llegó, sin modificar.

**¿Por qué?**
- Si un proveedor tiene campos personalizados que no mapeamos, no se pierden
- Permite auditoría: siempre se puede comparar el dato procesado con el original
- Si en el futuro agregamos un campo nuevo al modelo, podemos reprocesar sin re-subir
- La exportación JSON puede incluir `raw_data` para exportación completa

**Ejemplo:**
```python
purchase = PurchaseInvoice(
    document_number="ABC-123",
    # ... campos normalizados ...
    raw_data={
        "identificacion": { ... },     # JSON original completo
        "emisor": { ... },
        "receptor": { ... },
        "cuerpoDocumento": [ ... ],
        "resumen": { ... },
        "apendice": [ ... ],
        "campoPersonalizado": "valor"  # ← Esto NO se pierde
    }
)
```

---

## 7. Diferencias Clave vs Invoice Existente

| Aspecto | Invoice (Ventas) | PurchaseInvoice (Compras) |
|---------|-----------------|--------------------------|
| Tipos de documento | 3 (factura, ccf, nota_credito) | 9 (todos los DTE) |
| Datos del emisor | Fijos (nuestra empresa) | Variables (cada proveedor) |
| `SupplierInfo` | No existe | Objeto dedicado |
| `raw_data` | No existe | JSON original completo |
| `detected_format` | No existe | Resultado del FormatDetector |
| `detection_confidence` | No existe | Nivel de confianza (0-1) |
| `iva_retained` | No existe | IVA retenido en compras |
| `appendix_data` | Campos fijos (seller, doc) | Dict flexible |

---

## 8. Ejemplo de Instancia Completa

```python
purchase = PurchaseInvoice(
    # Identificación
    document_number="A1B2C3D4-E5F6-7890-ABCD-EF1234567890",
    control_number="DTE-03-00000001-000000000000001",
    document_type=PurchaseDocumentType.CCF,
    issue_date=date(2026, 2, 6),
    emission_time="14:30:00",
    currency="USD",

    # Proveedor
    supplier=SupplierInfo(
        name="DISTRIBUIDORA ABC S.A. DE C.V.",
        commercial_name="ABC Distribuciones",
        nit="0614-123456-789-0",
        nrc="12345-6",
        address="Blvd. Los Héroes, San Salvador",
        phone="2222-3333",
        email="ventas@abc.com.sv",
    ),

    # Items
    items=[
        PurchaseInvoiceItem(
            item_number=1,
            description="Papel Bond Carta Resma 500 hojas",
            quantity=Decimal("10"),
            unit_price=Decimal("3.50"),
            taxable_sale=Decimal("35.00"),
            item_tax=Decimal("4.55"),
            total=Decimal("35.00"),
        ),
    ],

    # Resumen
    subtotal=Decimal("35.00"),
    total_taxable=Decimal("35.00"),
    tax=Decimal("4.55"),
    total=Decimal("39.55"),
    total_in_words="TREINTA Y NUEVE 55/100 DÓLARES",
    payment_condition=1,  # Contado

    # Metadatos
    source_file="factura_abc_001.json",
    detected_format="DTE_STANDARD",
    detection_confidence=0.95,
    raw_data={"identificacion": {}, "emisor": {}, ...},
)
```

---

> **Próximo documento:** [05_DETECTOR_FORMATO](./05_DETECTOR_FORMATO_(Sistema-Inteligente-de-Identificacion).md) — Cómo identificamos cada formato automáticamente.

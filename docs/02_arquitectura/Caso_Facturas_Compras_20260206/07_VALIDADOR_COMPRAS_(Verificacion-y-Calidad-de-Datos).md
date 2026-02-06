# ✅ Validador de Compras — Verificación y Calidad de Datos

> **¿Qué es esto?** Este documento explica cómo el sistema verifica que los datos normalizados son correctos, completos y sin duplicados. Es el "inspector de calidad" del pipeline.

---

## 1. ¿Por Qué un Validador Separado?

El mapper convierte datos. El validador los **inspecciona**.

Analogía: el mapper es el traductor que traduce un documento. El validador es el revisor que verifica que la traducción tiene sentido — que los números cuadren, que no haya duplicados, que las fechas sean reales.

**No se valida en el mapper** porque:
- La validación es la misma para TODOS los formatos
- Un mapper con validación mezclada se vuelve difícil de mantener
- Separar responsabilidades = código más limpio (Principio SRP)

---

## 2. Tipos de Validación

### 2.1 Validación Estructural (¿Tiene lo que necesita?)

Verifica que los campos requeridos existan y tengan valores válidos.

```python
REQUIRED_FIELDS = {
    "document_number": "Número de documento",
    "issue_date": "Fecha de emisión",
    "total": "Total",
    "supplier.name": "Nombre del proveedor",
}

RECOMMENDED_FIELDS = {
    "control_number": "Número de control",
    "supplier.nit": "NIT del proveedor",
    "items": "Items de la factura (lista)",
    "subtotal": "Subtotal",
    "tax": "IVA",
}
```

**Resultado:**
- Campo requerido faltante → **ERROR** (la factura se rechaza)
- Campo recomendado faltante → **WARNING** (la factura se acepta con advertencia)

---

### 2.2 Validación Matemática (¿Los números cuadran?)

```python
def validate_totals(self, invoice: PurchaseInvoice) -> list[ValidationIssue]:
    """Verifica que los totales sean consistentes."""
    issues = []
    tolerance = Decimal("0.02")  # Tolerancia de 2 centavos

    # 1. Total ≈ Subtotal + IVA
    expected_total = invoice.subtotal + invoice.tax
    if abs(invoice.total - expected_total) > tolerance:
        issues.append(ValidationIssue(
            level="WARNING",
            field="total",
            message=f"Total ({invoice.total}) ≠ Subtotal ({invoice.subtotal}) + IVA ({invoice.tax})",
            expected=str(expected_total),
            actual=str(invoice.total),
        ))

    # 2. Subtotal ≈ Suma de items
    if invoice.items:
        items_sum = sum(item.total for item in invoice.items)
        if abs(invoice.subtotal - items_sum) > tolerance:
            issues.append(ValidationIssue(
                level="WARNING",
                field="subtotal",
                message=f"Subtotal ({invoice.subtotal}) ≠ Suma items ({items_sum})",
            ))

    # 3. IVA ≈ 13% de base gravable (El Salvador)
    if invoice.total_taxable > 0 and invoice.tax > 0:
        expected_iva = invoice.total_taxable * Decimal("0.13")
        if abs(invoice.tax - expected_iva) > Decimal("0.10"):
            issues.append(ValidationIssue(
                level="WARNING",
                field="tax",
                message=f"IVA ({invoice.tax}) ≠ 13% de gravado ({expected_iva})",
            ))

    # 4. Total Gravado + Exento + No Sujeto ≈ Subtotal
    category_sum = invoice.total_taxable + invoice.total_exempt + invoice.total_non_subject
    if category_sum > 0 and abs(invoice.subtotal - category_sum) > tolerance:
        issues.append(ValidationIssue(
            level="INFO",
            field="categories",
            message=f"Categorías ({category_sum}) ≠ Subtotal ({invoice.subtotal})",
        ))

    return issues
```

**Nota importante:** Las validaciones matemáticas son **warnings**, no errores. Razón: muchos proveedores tienen inconsistencias menores en sus facturas por redondeo. No debemos rechazar facturas por 1 centavo de diferencia.

---

### 2.3 Validación de Duplicados (¿Ya la procesamos?)

```python
def check_duplicates(
    self,
    invoice: PurchaseInvoice,
    existing: list[PurchaseInvoice],
) -> Optional[ValidationIssue]:
    """
    Detecta si la factura ya existe en el lote.
    Criterio: mismo control_number + mismo NIT emisor.
    """
    for existing_inv in existing:
        if (
            invoice.control_number
            and invoice.control_number == existing_inv.control_number
            and invoice.supplier.nit
            and invoice.supplier.nit == existing_inv.supplier.nit
        ):
            return ValidationIssue(
                level="ERROR",
                field="control_number",
                message=f"Factura duplicada: {invoice.control_number} "
                        f"del proveedor {invoice.supplier.name}",
                duplicate_of=existing_inv.source_file,
            )

    # Segundo criterio: mismo document_number
    for existing_inv in existing:
        if invoice.document_number == existing_inv.document_number:
            return ValidationIssue(
                level="WARNING",
                field="document_number",
                message=f"Posible duplicado por document_number: {invoice.document_number}",
                duplicate_of=existing_inv.source_file,
            )

    return None
```

---

### 2.4 Validación de Fechas (¿Tienen sentido?)

```python
def validate_dates(self, invoice: PurchaseInvoice) -> list[ValidationIssue]:
    """Verifica que las fechas sean coherentes."""
    issues = []
    today = date.today()

    # Fecha no puede ser futura
    if invoice.issue_date > today:
        issues.append(ValidationIssue(
            level="WARNING",
            field="issue_date",
            message=f"Fecha futura: {invoice.issue_date}",
        ))

    # Fecha no puede ser muy antigua (más de 2 años)
    cutoff = today.replace(year=today.year - 2)
    if invoice.issue_date < cutoff:
        issues.append(ValidationIssue(
            level="WARNING",
            field="issue_date",
            message=f"Fecha muy antigua: {invoice.issue_date} (más de 2 años)",
        ))

    return issues
```

---

## 3. Modelos de Validación

```python
class ValidationLevel(str, Enum):
    """Niveles de severidad de validación."""
    ERROR = "ERROR"       # Factura rechazada
    WARNING = "WARNING"   # Factura aceptada con advertencia
    INFO = "INFO"         # Informativo, no afecta aceptación


class ValidationIssue(BaseModel):
    """Un problema encontrado durante la validación."""
    level: ValidationLevel
    field: str                        # Campo con el problema
    message: str                      # Descripción del problema
    expected: Optional[str] = None    # Valor esperado
    actual: Optional[str] = None      # Valor encontrado
    duplicate_of: Optional[str] = None  # Archivo duplicado (si aplica)


class ValidationResult(BaseModel):
    """Resultado completo de validación de una factura."""
    is_valid: bool                    # True si no tiene ERRORES
    issues: list[ValidationIssue]     # Todos los problemas encontrados
    error_count: int                  # Cantidad de errores
    warning_count: int                # Cantidad de warnings
    info_count: int                   # Cantidad de infos

    @property
    def has_errors(self) -> bool:
        return self.error_count > 0

    @property
    def has_warnings(self) -> bool:
        return self.warning_count > 0
```

---

## 4. Clase PurchaseValidator

```python
class PurchaseValidator:
    """
    Validador de facturas de compra normalizadas.

    Ejecuta todas las validaciones y retorna un resultado completo.
    Las facturas con ERRORES se rechazan.
    Las facturas con WARNINGS se aceptan pero se reportan.
    """

    def __init__(self, tolerance: Decimal = Decimal("0.02")):
        self.tolerance = tolerance

    def validate(
        self,
        invoice: PurchaseInvoice,
        existing: list[PurchaseInvoice] = None,
    ) -> ValidationResult:
        """
        Ejecuta todas las validaciones sobre una factura.

        Args:
            invoice: Factura a validar
            existing: Lista de facturas ya procesadas (para duplicados)

        Returns:
            ValidationResult con todos los problemas encontrados
        """
        issues = []

        # 1. Validación estructural
        issues.extend(self.validate_required_fields(invoice))

        # 2. Validación matemática
        issues.extend(self.validate_totals(invoice))

        # 3. Validación de fechas
        issues.extend(self.validate_dates(invoice))

        # 4. Validación de duplicados
        if existing:
            dup = self.check_duplicates(invoice, existing)
            if dup:
                issues.append(dup)

        # Contar por nivel
        errors = [i for i in issues if i.level == ValidationLevel.ERROR]
        warnings = [i for i in issues if i.level == ValidationLevel.WARNING]
        infos = [i for i in issues if i.level == ValidationLevel.INFO]

        return ValidationResult(
            is_valid=len(errors) == 0,
            issues=issues,
            error_count=len(errors),
            warning_count=len(warnings),
            info_count=len(infos),
        )

    def validate_batch(
        self,
        invoices: list[PurchaseInvoice],
    ) -> dict:
        """
        Valida un lote completo de facturas.

        Returns:
            {
                "valid": [PurchaseInvoice, ...],
                "invalid": [(PurchaseInvoice, ValidationResult), ...],
                "total": int,
                "valid_count": int,
                "invalid_count": int,
                "warning_count": int,
            }
        """
        valid = []
        invalid = []
        warning_count = 0

        for invoice in invoices:
            result = self.validate(invoice, existing=valid)
            if result.is_valid:
                valid.append(invoice)
                if result.has_warnings:
                    warning_count += 1
            else:
                invalid.append((invoice, result))

        return {
            "valid": valid,
            "invalid": invalid,
            "total": len(invoices),
            "valid_count": len(valid),
            "invalid_count": len(invalid),
            "warning_count": warning_count,
        }
```

---

## 5. Tolerancia Configurable

La tolerancia es importante porque los sistemas de facturación de diferentes proveedores manejan el redondeo de forma distinta.

| Validación | Tolerancia Default | Configurable |
|------------|-------------------|--------------|
| Total vs Subtotal + IVA | $0.02 | Sí |
| Subtotal vs Suma Items | $0.02 | Sí |
| IVA vs 13% Gravado | $0.10 | Sí |
| Categorías vs Subtotal | $0.02 | Sí |

---

## 6. Testing del Validador

```
tests/unit/test_purchase_validator.py

├── test_valid_invoice                → Factura completamente válida
├── test_missing_required_field       → Falta campo requerido → ERROR
├── test_missing_recommended_field    → Falta campo recomendado → WARNING
├── test_total_mismatch_small         → Diferencia < tolerancia → OK
├── test_total_mismatch_large         → Diferencia > tolerancia → WARNING
├── test_iva_mismatch                 → IVA no es 13% → WARNING
├── test_duplicate_control_number     → Mismo control + NIT → ERROR
├── test_duplicate_document_number    → Mismo document_number → WARNING
├── test_future_date                  → Fecha futura → WARNING
├── test_old_date                     → Fecha >2 años → WARNING
├── test_batch_validation             → Lote con mezcla válidas/inválidas
├── test_batch_duplicate_detection    → Detecta duplicados en lote
└── test_custom_tolerance             → Tolerancia personalizada
```

**Cobertura esperada:** >= 70%

---

> **Próximo documento:** [08_API_Y_SERVICIOS](./08_API_Y_SERVICIOS_(Rutas-del-Backend-para-Compras).md) — Los endpoints del backend.

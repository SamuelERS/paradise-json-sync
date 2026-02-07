"""
Purchase Validator Tests / Pruebas del Validador de Compras
============================================================

Unit tests for PurchaseValidator, ValidationResult,
ValidationIssue, and ValidationLevel.
Pruebas unitarias para PurchaseValidator, ValidationResult,
ValidationIssue y ValidationLevel.

Coverage target / Objetivo de cobertura: >= 70%
"""

from datetime import date, timedelta
from decimal import Decimal

import pytest

from src.core.purchases.validator import (
    PurchaseValidator,
    ValidationIssue,
    ValidationLevel,
    ValidationResult,
    _get_field,
)
from src.models.purchase_invoice import (
    PurchaseDocumentType,
    PurchaseInvoice,
    PurchaseInvoiceItem,
    SupplierInfo,
)


# === Fixtures / Fixtures ===


@pytest.fixture
def validator() -> PurchaseValidator:
    """Default PurchaseValidator / Validador por defecto."""
    return PurchaseValidator()


@pytest.fixture
def valid_invoice() -> PurchaseInvoice:
    """
    A fully valid purchase invoice.
    Una factura de compra completamente valida.
    """
    return PurchaseInvoice(
        document_number="DOC-VALID-001",
        control_number="DTE-03-00000001-000000000000001",
        document_type=PurchaseDocumentType.CCF,
        issue_date=date.today() - timedelta(days=30),
        supplier=SupplierInfo(
            name="PROVEEDOR VALIDO S.A.",
            nit="0614-111111-111-1",
        ),
        items=[
            PurchaseInvoiceItem(
                description="Producto A",
                quantity=Decimal("10"),
                unit_price=Decimal("10.00"),
                total=Decimal("100.00"),
                taxable_sale=Decimal("100.00"),
            ),
        ],
        subtotal=Decimal("100.00"),
        total_taxable=Decimal("100.00"),
        tax=Decimal("13.00"),
        total=Decimal("113.00"),
        source_file="valida.json",
    )


@pytest.fixture
def invoice_missing_doc_number() -> PurchaseInvoice:
    """
    Invoice missing document_number (required field).
    Factura sin document_number (campo requerido).

    Note: PurchaseInvoice requires document_number, so we
    create a valid one then clear it via model_construct.
    """
    return PurchaseInvoice.model_construct(
        document_number=None,
        control_number="DTE-CTRL-001",
        issue_date=date.today(),
        supplier=SupplierInfo(name="TEST SUPPLIER"),
        items=[],
        subtotal=Decimal("0"),
        total_taxable=Decimal("0"),
        total_exempt=Decimal("0"),
        total_non_subject=Decimal("0"),
        total_discount=Decimal("0"),
        tax=Decimal("0"),
        iva_retained=Decimal("0"),
        total=Decimal("100.00"),
        processing_warnings=[],
    )


@pytest.fixture
def invoice_missing_control() -> PurchaseInvoice:
    """
    Invoice missing control_number (recommended field).
    Factura sin control_number (campo recomendado).
    """
    return PurchaseInvoice(
        document_number="DOC-NO-CTRL-001",
        control_number=None,
        issue_date=date.today() - timedelta(days=10),
        supplier=SupplierInfo(
            name="PROVEEDOR SIN CONTROL",
            nit="0614-222222-222-2",
        ),
        items=[
            PurchaseInvoiceItem(
                description="Servicio B",
                quantity=Decimal("1"),
                unit_price=Decimal("50.00"),
                total=Decimal("50.00"),
                taxable_sale=Decimal("50.00"),
            ),
        ],
        subtotal=Decimal("50.00"),
        total_taxable=Decimal("50.00"),
        tax=Decimal("6.50"),
        total=Decimal("56.50"),
    )


# === TestValidationModels ===


class TestValidationModels:
    """Tests for validation models / Pruebas de modelos de validacion."""

    def test_validation_level_values(self):
        """Test ValidationLevel enum has correct values.
        Verifica que ValidationLevel tiene los valores correctos."""
        assert ValidationLevel.ERROR == "ERROR"
        assert ValidationLevel.WARNING == "WARNING"
        assert ValidationLevel.INFO == "INFO"

    def test_validation_level_is_str_enum(self):
        """Test ValidationLevel inherits from str and Enum.
        Verifica herencia de str y Enum."""
        assert isinstance(ValidationLevel.ERROR, str)

    def test_validation_issue_creation(self):
        """Test creating ValidationIssue with all fields.
        Verifica creacion de ValidationIssue con todos los campos."""
        issue = ValidationIssue(
            level=ValidationLevel.ERROR,
            field="total",
            message="Mismatch",
            expected="100.00",
            actual="99.00",
            duplicate_of="other.json",
        )
        assert issue.level == ValidationLevel.ERROR
        assert issue.field == "total"
        assert issue.message == "Mismatch"
        assert issue.expected == "100.00"
        assert issue.actual == "99.00"
        assert issue.duplicate_of == "other.json"

    def test_validation_issue_minimal(self):
        """Test creating ValidationIssue with required fields only.
        Verifica creacion de ValidationIssue solo con campos requeridos."""
        issue = ValidationIssue(
            level=ValidationLevel.WARNING,
            field="tax",
            message="IVA mismatch",
        )
        assert issue.expected is None
        assert issue.actual is None
        assert issue.duplicate_of is None

    def test_validation_result_valid(self):
        """Test ValidationResult with zero errors => is_valid=True.
        Verifica ValidationResult con cero errores => is_valid=True."""
        result = ValidationResult(
            is_valid=True,
            issues=[],
            error_count=0,
            warning_count=0,
            info_count=0,
        )
        assert result.is_valid is True

    def test_validation_result_invalid(self):
        """Test ValidationResult with errors => is_valid=False.
        Verifica ValidationResult con errores => is_valid=False."""
        result = ValidationResult(
            is_valid=False,
            issues=[
                ValidationIssue(
                    level=ValidationLevel.ERROR,
                    field="document_number",
                    message="Missing",
                ),
            ],
            error_count=1,
            warning_count=0,
            info_count=0,
        )
        assert result.is_valid is False

    def test_has_errors_property(self):
        """Test has_errors property works correctly.
        Verifica que propiedad has_errors funciona correctamente."""
        result_with = ValidationResult(
            is_valid=False,
            issues=[],
            error_count=1,
            warning_count=0,
            info_count=0,
        )
        result_without = ValidationResult(
            is_valid=True,
            issues=[],
            error_count=0,
            warning_count=0,
            info_count=0,
        )
        assert result_with.has_errors is True
        assert result_without.has_errors is False

    def test_has_warnings_property(self):
        """Test has_warnings property works correctly.
        Verifica que propiedad has_warnings funciona correctamente."""
        result_with = ValidationResult(
            is_valid=True,
            issues=[],
            error_count=0,
            warning_count=2,
            info_count=0,
        )
        result_without = ValidationResult(
            is_valid=True,
            issues=[],
            error_count=0,
            warning_count=0,
            info_count=0,
        )
        assert result_with.has_warnings is True
        assert result_without.has_warnings is False


# === TestGetField ===


class TestGetField:
    """Tests for _get_field helper / Pruebas de helper _get_field."""

    def test_simple_field(self, valid_invoice):
        """Test access to a simple field.
        Verifica acceso a un campo simple."""
        assert _get_field(valid_invoice, "document_number") is not None

    def test_nested_field(self, valid_invoice):
        """Test access to a nested field via dot notation.
        Verifica acceso a un campo anidado con notacion de punto."""
        assert (
            _get_field(valid_invoice, "supplier.name")
            == "PROVEEDOR VALIDO S.A."
        )

    def test_missing_field(self, valid_invoice):
        """Test access to a nonexistent field returns None.
        Verifica que campo inexistente retorna None."""
        assert _get_field(valid_invoice, "nonexistent") is None

    def test_missing_nested(self, valid_invoice):
        """Test access to nonexistent nested field returns None.
        Verifica que campo anidado inexistente retorna None."""
        assert _get_field(valid_invoice, "supplier.foo") is None


# === TestPurchaseValidator ===


class TestPurchaseValidator:
    """Tests for PurchaseValidator / Pruebas de PurchaseValidator."""

    def test_valid_invoice(self, validator, valid_invoice):
        """Test a fully valid invoice returns is_valid=True.
        Verifica que factura valida retorna is_valid=True."""
        result = validator.validate(valid_invoice)
        assert result.is_valid is True
        assert result.error_count == 0

    def test_missing_required_field(
        self, validator, invoice_missing_doc_number,
    ):
        """Test missing document_number generates ERROR.
        Verifica que falta document_number genera ERROR."""
        result = validator.validate(invoice_missing_doc_number)
        assert result.is_valid is False
        assert result.error_count >= 1
        error_fields = [
            i.field for i in result.issues
            if i.level == ValidationLevel.ERROR
        ]
        assert "document_number" in error_fields

    def test_missing_recommended_field(
        self, validator, invoice_missing_control,
    ):
        """Test missing control_number generates WARNING.
        Verifica que falta control_number genera WARNING."""
        result = validator.validate(invoice_missing_control)
        warning_fields = [
            i.field for i in result.issues
            if i.level == ValidationLevel.WARNING
        ]
        assert "control_number" in warning_fields
        assert result.is_valid is True

    def test_total_mismatch_small(self, validator):
        """Test small total difference (within tolerance) => no issue.
        Verifica diferencia menor a tolerancia => sin problema."""
        invoice = PurchaseInvoice(
            document_number="DOC-SMALL-DIFF",
            issue_date=date.today() - timedelta(days=5),
            supplier=SupplierInfo(
                name="PROV", nit="0614-333333-333-3",
            ),
            items=[
                PurchaseInvoiceItem(
                    description="Item",
                    quantity=Decimal("1"),
                    unit_price=Decimal("100.00"),
                    total=Decimal("100.00"),
                    taxable_sale=Decimal("100.00"),
                ),
            ],
            subtotal=Decimal("100.00"),
            total_taxable=Decimal("100.00"),
            tax=Decimal("13.00"),
            total=Decimal("113.01"),  # 0.01 diff, within 0.02
        )
        result = validator.validate(invoice)
        total_issues = [
            i for i in result.issues if i.field == "total"
        ]
        assert len(total_issues) == 0

    def test_total_mismatch_large(self, validator):
        """Test large total difference => WARNING.
        Verifica diferencia grande en total => WARNING."""
        invoice = PurchaseInvoice(
            document_number="DOC-LARGE-DIFF",
            issue_date=date.today() - timedelta(days=5),
            supplier=SupplierInfo(
                name="PROV", nit="0614-444444-444-4",
            ),
            items=[
                PurchaseInvoiceItem(
                    description="Item",
                    quantity=Decimal("1"),
                    unit_price=Decimal("100.00"),
                    total=Decimal("100.00"),
                    taxable_sale=Decimal("100.00"),
                ),
            ],
            subtotal=Decimal("100.00"),
            total_taxable=Decimal("100.00"),
            tax=Decimal("13.00"),
            total=Decimal("115.00"),  # 2.00 diff, > 0.02
        )
        result = validator.validate(invoice)
        total_issues = [
            i for i in result.issues
            if i.field == "total"
            and i.level == ValidationLevel.WARNING
        ]
        assert len(total_issues) == 1
        assert result.is_valid is True  # WARNING, not ERROR

    def test_iva_mismatch(self, validator):
        """Test IVA not 13% of taxable => WARNING.
        Verifica IVA no es 13% de gravado => WARNING."""
        invoice = PurchaseInvoice(
            document_number="DOC-IVA-BAD",
            issue_date=date.today() - timedelta(days=5),
            supplier=SupplierInfo(
                name="PROV", nit="0614-555555-555-5",
            ),
            items=[
                PurchaseInvoiceItem(
                    description="Item",
                    quantity=Decimal("1"),
                    unit_price=Decimal("100.00"),
                    total=Decimal("100.00"),
                    taxable_sale=Decimal("100.00"),
                ),
            ],
            subtotal=Decimal("100.00"),
            total_taxable=Decimal("100.00"),
            tax=Decimal("15.00"),  # Should be ~13.00
            total=Decimal("115.00"),
        )
        result = validator.validate(invoice)
        tax_issues = [
            i for i in result.issues
            if i.field == "tax"
            and i.level == ValidationLevel.WARNING
        ]
        assert len(tax_issues) == 1

    def test_duplicate_control_number(self, validator, valid_invoice):
        """Test same control_number + NIT => ERROR duplicate.
        Verifica mismo control_number + NIT => ERROR duplicado."""
        duplicate = PurchaseInvoice(
            document_number="DOC-DUP-001",
            control_number=valid_invoice.control_number,
            issue_date=date.today() - timedelta(days=5),
            supplier=SupplierInfo(
                name="PROVEEDOR VALIDO S.A.",
                nit=valid_invoice.supplier.nit,
            ),
            subtotal=Decimal("50.00"),
            tax=Decimal("6.50"),
            total=Decimal("56.50"),
        )
        result = validator.validate(
            duplicate, existing=[valid_invoice],
        )
        assert result.is_valid is False
        dup_issues = [
            i for i in result.issues
            if i.field == "control_number"
            and i.level == ValidationLevel.ERROR
        ]
        assert len(dup_issues) == 1
        assert dup_issues[0].duplicate_of == "valida.json"

    def test_duplicate_document_number(self, validator, valid_invoice):
        """Test same document_number => WARNING duplicate.
        Verifica mismo document_number => WARNING duplicado."""
        dup = PurchaseInvoice(
            document_number=valid_invoice.document_number,
            control_number="DTE-03-DIFFERENT",
            issue_date=date.today() - timedelta(days=5),
            supplier=SupplierInfo(
                name="OTRO PROVEEDOR",
                nit="0614-999999-999-9",
            ),
            subtotal=Decimal("50.00"),
            tax=Decimal("6.50"),
            total=Decimal("56.50"),
        )
        result = validator.validate(dup, existing=[valid_invoice])
        dup_issues = [
            i for i in result.issues
            if i.field == "document_number"
            and i.level == ValidationLevel.WARNING
        ]
        assert len(dup_issues) == 1
        assert result.is_valid is True  # WARNING, not ERROR

    def test_future_date(self, validator):
        """Test future issue_date => WARNING.
        Verifica fecha futura => WARNING."""
        invoice = PurchaseInvoice(
            document_number="DOC-FUTURE",
            issue_date=date.today() + timedelta(days=30),
            supplier=SupplierInfo(
                name="PROV FUTURO", nit="0614-666666-666-6",
            ),
            subtotal=Decimal("100.00"),
            tax=Decimal("13.00"),
            total=Decimal("113.00"),
        )
        result = validator.validate(invoice)
        date_issues = [
            i for i in result.issues
            if i.field == "issue_date"
            and "futura" in i.message
        ]
        assert len(date_issues) == 1
        assert date_issues[0].level == ValidationLevel.WARNING

    def test_old_date(self, validator):
        """Test very old date (>2 years) => WARNING.
        Verifica fecha antigua (>2 anios) => WARNING."""
        invoice = PurchaseInvoice(
            document_number="DOC-OLD",
            issue_date=date(2020, 1, 1),
            supplier=SupplierInfo(
                name="PROV VIEJO", nit="0614-777777-777-7",
            ),
            subtotal=Decimal("100.00"),
            tax=Decimal("13.00"),
            total=Decimal("113.00"),
        )
        result = validator.validate(invoice)
        date_issues = [
            i for i in result.issues
            if i.field == "issue_date"
            and "antigua" in i.message
        ]
        assert len(date_issues) == 1
        assert date_issues[0].level == ValidationLevel.WARNING

    def test_batch_validation(self, validator, valid_invoice):
        """Test batch with mix of valid and invalid invoices.
        Verifica lote con mezcla de facturas validas e invalidas."""
        invalid = PurchaseInvoice.model_construct(
            document_number=None,
            issue_date=date.today(),
            supplier=SupplierInfo(name="BAD PROV"),
            items=[],
            subtotal=Decimal("0"),
            total_taxable=Decimal("0"),
            total_exempt=Decimal("0"),
            total_non_subject=Decimal("0"),
            total_discount=Decimal("0"),
            tax=Decimal("0"),
            iva_retained=Decimal("0"),
            total=Decimal("50.00"),
            processing_warnings=[],
        )
        batch = validator.validate_batch(
            [valid_invoice, invalid],
        )
        assert batch["total"] == 2
        assert batch["valid_count"] == 1
        assert batch["invalid_count"] == 1
        assert len(batch["valid"]) == 1
        assert len(batch["invalid"]) == 1

    def test_batch_duplicate_detection(self, validator):
        """Test batch detects duplicates within the batch.
        Verifica que lote detecta duplicados dentro del lote."""
        inv1 = PurchaseInvoice(
            document_number="DOC-BATCH-001",
            control_number="CTRL-BATCH-001",
            issue_date=date.today() - timedelta(days=5),
            supplier=SupplierInfo(
                name="PROV BATCH", nit="0614-888888-888-8",
            ),
            subtotal=Decimal("100.00"),
            total_taxable=Decimal("100.00"),
            tax=Decimal("13.00"),
            total=Decimal("113.00"),
            source_file="batch1.json",
        )
        inv2 = PurchaseInvoice(
            document_number="DOC-BATCH-002",
            control_number="CTRL-BATCH-001",
            issue_date=date.today() - timedelta(days=5),
            supplier=SupplierInfo(
                name="PROV BATCH", nit="0614-888888-888-8",
            ),
            subtotal=Decimal("100.00"),
            total_taxable=Decimal("100.00"),
            tax=Decimal("13.00"),
            total=Decimal("113.00"),
            source_file="batch2.json",
        )
        batch = validator.validate_batch([inv1, inv2])
        assert batch["valid_count"] == 1
        assert batch["invalid_count"] == 1
        # The second invoice should be invalid (duplicate)
        _, dup_result = batch["invalid"][0]
        dup_errors = [
            i for i in dup_result.issues
            if i.level == ValidationLevel.ERROR
            and "duplicada" in i.message.lower()
        ]
        assert len(dup_errors) == 1

    def test_custom_tolerance(self):
        """Test custom tolerance changes validation behavior.
        Verifica que tolerancia personalizada cambia la validacion."""
        # With large tolerance, small mismatches are ignored
        lenient = PurchaseValidator(tolerance=Decimal("5.00"))
        invoice = PurchaseInvoice(
            document_number="DOC-TOLERANT",
            issue_date=date.today() - timedelta(days=5),
            supplier=SupplierInfo(
                name="PROV TOL", nit="0614-999999-999-0",
            ),
            items=[
                PurchaseInvoiceItem(
                    description="Item",
                    quantity=Decimal("1"),
                    unit_price=Decimal("100.00"),
                    total=Decimal("100.00"),
                    taxable_sale=Decimal("100.00"),
                ),
            ],
            subtotal=Decimal("100.00"),
            total_taxable=Decimal("100.00"),
            tax=Decimal("13.00"),
            total=Decimal("117.00"),  # 4.00 off
        )
        result = lenient.validate(invoice)
        total_issues = [
            i for i in result.issues if i.field == "total"
        ]
        assert len(total_issues) == 0  # Within 5.00 tolerance

        # With tight tolerance, the same difference is flagged
        strict = PurchaseValidator(tolerance=Decimal("0.01"))
        result2 = strict.validate(invoice)
        total_issues2 = [
            i for i in result2.issues if i.field == "total"
        ]
        assert len(total_issues2) == 1

    def test_no_duplicates_without_existing(
        self, validator, valid_invoice,
    ):
        """Test validate with no existing list skips duplicate check.
        Verifica que sin lista existente se omite chequeo duplicados."""
        result = validator.validate(valid_invoice, existing=None)
        dup_issues = [
            i for i in result.issues
            if "duplicad" in i.message.lower()
        ]
        assert len(dup_issues) == 0

    def test_check_duplicates_returns_none(
        self, validator, valid_invoice,
    ):
        """Test check_duplicates returns None when no duplicate.
        Verifica que check_duplicates retorna None sin duplicado."""
        other = PurchaseInvoice(
            document_number="DOC-OTHER",
            control_number="CTRL-OTHER",
            issue_date=date.today(),
            supplier=SupplierInfo(
                name="PROV OTHER", nit="0614-000000-000-0",
            ),
            total=Decimal("50.00"),
        )
        result = validator.check_duplicates(
            valid_invoice, [other],
        )
        assert result is None

    def test_categories_mismatch_info(self, validator):
        """Test category sum != subtotal => INFO.
        Verifica categorias != subtotal => INFO."""
        invoice = PurchaseInvoice(
            document_number="DOC-CAT-MISMATCH",
            issue_date=date.today() - timedelta(days=5),
            supplier=SupplierInfo(
                name="PROV CAT", nit="0614-121212-121-2",
            ),
            subtotal=Decimal("100.00"),
            total_taxable=Decimal("80.00"),
            total_exempt=Decimal("10.00"),
            total_non_subject=Decimal("5.00"),
            tax=Decimal("13.00"),
            total=Decimal("113.00"),
        )
        result = validator.validate(invoice)
        cat_issues = [
            i for i in result.issues
            if i.field == "categories"
            and i.level == ValidationLevel.INFO
        ]
        assert len(cat_issues) == 1

    def test_batch_warning_count(self, validator):
        """Test batch counts invoices with warnings.
        Verifica que lote cuenta facturas con warnings."""
        inv_with_warn = PurchaseInvoice(
            document_number="DOC-WARN-BATCH",
            control_number=None,  # Missing recommended
            issue_date=date.today() - timedelta(days=5),
            supplier=SupplierInfo(
                name="PROV WARN", nit=None,
            ),
            subtotal=Decimal("100.00"),
            tax=Decimal("13.00"),
            total=Decimal("113.00"),
        )
        batch = validator.validate_batch([inv_with_warn])
        assert batch["valid_count"] == 1
        assert batch["warning_count"] == 1

    def test_validate_required_fields_direct(
        self, validator, valid_invoice,
    ):
        """Test validate_required_fields directly.
        Verifica validate_required_fields directamente."""
        issues = validator.validate_required_fields(valid_invoice)
        error_issues = [
            i for i in issues
            if i.level == ValidationLevel.ERROR
        ]
        assert len(error_issues) == 0

    def test_validate_totals_direct(
        self, validator, valid_invoice,
    ):
        """Test validate_totals directly.
        Verifica validate_totals directamente."""
        issues = validator.validate_totals(valid_invoice)
        # Valid invoice should have no total issues
        warning_issues = [
            i for i in issues
            if i.level == ValidationLevel.WARNING
        ]
        assert len(warning_issues) == 0

    def test_validate_dates_direct(
        self, validator, valid_invoice,
    ):
        """Test validate_dates directly.
        Verifica validate_dates directamente."""
        issues = validator.validate_dates(valid_invoice)
        assert len(issues) == 0

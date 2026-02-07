"""
Purchase Invoice Model Tests / Pruebas del Modelo de Factura de Compra
======================================================================

Unit tests for PurchaseInvoice, PurchaseInvoiceItem, SupplierInfo,
and PurchaseDocumentType models.
Pruebas unitarias para los modelos PurchaseInvoice,
PurchaseInvoiceItem, SupplierInfo y PurchaseDocumentType.
"""

from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from src.models.purchase_invoice import (
    PurchaseDocumentType,
    PurchaseInvoice,
    PurchaseInvoiceItem,
    SupplierInfo,
)


class TestPurchaseDocumentType:
    """Tests for PurchaseDocumentType enum / Pruebas para enum."""

    def test_all_document_types_exist(self):
        """Test that all 9 document types exist."""
        assert len(PurchaseDocumentType) == 9

    def test_document_type_values(self):
        """Test that all document types have correct string values."""
        assert PurchaseDocumentType.FACTURA.value == "factura"
        assert PurchaseDocumentType.CCF.value == "ccf"
        assert PurchaseDocumentType.NOTA_CREDITO.value == "nota_credito"
        assert PurchaseDocumentType.NOTA_DEBITO.value == "nota_debito"
        assert (
            PurchaseDocumentType.FACTURA_EXPORTACION.value
            == "factura_exp"
        )
        assert (
            PurchaseDocumentType.SUJETO_EXCLUIDO.value
            == "sujeto_excluido"
        )
        assert (
            PurchaseDocumentType.COMPROBANTE_RETENCION.value
            == "retencion"
        )
        assert (
            PurchaseDocumentType.COMPROBANTE_DONACION.value == "donacion"
        )
        assert PurchaseDocumentType.DESCONOCIDO.value == "desconocido"


class TestSupplierInfo:
    """Tests for SupplierInfo model / Pruebas para modelo SupplierInfo."""

    def test_create_supplier_full(self, sample_supplier_info):
        """Test creating a supplier with all fields."""
        assert sample_supplier_info.name == (
            "DISTRIBUIDORA ABC S.A. DE C.V."
        )
        assert sample_supplier_info.commercial_name == (
            "ABC Distribuciones"
        )
        assert sample_supplier_info.nit == "0614-123456-789-0"
        assert sample_supplier_info.nrc == "12345-6"
        assert sample_supplier_info.economic_activity == (
            "Venta al por mayor"
        )
        assert sample_supplier_info.address == (
            "Blvd. Los Heroes, San Salvador"
        )
        assert sample_supplier_info.phone == "2222-3333"
        assert sample_supplier_info.email == "ventas@abc.com.sv"
        assert sample_supplier_info.establishment_code == "S001"
        assert sample_supplier_info.establishment_type == "Sucursal"

    def test_create_supplier_minimal(self):
        """Test creating a supplier with only required field (name)."""
        supplier = SupplierInfo(name="Proveedor Minimo")
        assert supplier.name == "Proveedor Minimo"
        assert supplier.commercial_name is None
        assert supplier.nit is None
        assert supplier.nrc is None
        assert supplier.economic_activity is None
        assert supplier.address is None
        assert supplier.phone is None
        assert supplier.email is None
        assert supplier.establishment_code is None
        assert supplier.establishment_type is None

    def test_supplier_missing_name(self):
        """Test that missing name raises ValidationError."""
        with pytest.raises(ValidationError):
            SupplierInfo()


class TestPurchaseInvoiceItem:
    """Tests for PurchaseInvoiceItem / Pruebas para PurchaseInvoiceItem."""

    def test_create_item_valid(self, sample_purchase_invoice_item):
        """Test creating a valid purchase invoice item."""
        item = sample_purchase_invoice_item
        assert item.item_number == 1
        assert item.product_code == "PAP-001"
        assert item.description == "Papel Bond Carta Resma 500 hojas"
        assert item.unit_measure == 59
        assert item.quantity == Decimal("10")
        assert item.unit_price == Decimal("3.50")
        assert item.taxable_sale == Decimal("35.00")
        assert item.item_tax == Decimal("4.55")
        assert item.total == Decimal("35.00")

    def test_item_total_validation_warning(self, caplog):
        """Test total != qty*price emits warning but doesn't fail."""
        import logging

        with caplog.at_level(logging.WARNING):
            item = PurchaseInvoiceItem(
                description="Test item",
                quantity=Decimal("2"),
                unit_price=Decimal("10.00"),
                total=Decimal("25.00"),  # Wrong: should be 20.00
            )
        assert item.total == Decimal("25.00")
        assert "mismatch" in caplog.text.lower()

    def test_item_missing_description(self):
        """Test that missing description raises ValidationError."""
        with pytest.raises(ValidationError):
            PurchaseInvoiceItem(
                quantity=Decimal("1"),
                unit_price=Decimal("10.00"),
                total=Decimal("10.00"),
            )

    def test_item_zero_quantity(self):
        """Test that zero quantity raises ValidationError (gt=0)."""
        with pytest.raises(ValidationError):
            PurchaseInvoiceItem(
                description="Test",
                quantity=Decimal("0"),
                unit_price=Decimal("10.00"),
                total=Decimal("0"),
            )

    def test_item_defaults(self):
        """Test that default values are set correctly."""
        item = PurchaseInvoiceItem(
            description="Simple item",
            quantity=Decimal("1"),
            unit_price=Decimal("50.00"),
            total=Decimal("50.00"),
        )
        assert item.item_number is None
        assert item.product_code is None
        assert item.unit_measure is None
        assert item.original_price is None
        assert item.discount == Decimal("0")
        assert item.taxable_sale == Decimal("0")
        assert item.exempt_sale == Decimal("0")
        assert item.non_subject_sale == Decimal("0")
        assert item.item_tax == Decimal("0")


class TestPurchaseInvoice:
    """Tests for PurchaseInvoice / Pruebas para PurchaseInvoice."""

    def test_create_invoice_full(self, sample_purchase_invoice):
        """Test creating a complete purchase invoice."""
        inv = sample_purchase_invoice
        assert inv.document_number == (
            "A1B2C3D4-E5F6-7890-ABCD-EF1234567890"
        )
        assert inv.control_number == (
            "DTE-03-00000001-000000000000001"
        )
        assert inv.document_type == PurchaseDocumentType.CCF
        assert inv.issue_date == date(2026, 2, 6)
        assert inv.emission_time == "14:30:00"
        assert inv.currency == "USD"
        assert inv.dte_version == 3
        assert inv.supplier.name == "DISTRIBUIDORA ABC S.A. DE C.V."
        assert inv.receiver_name == "MI EMPRESA S.A. DE C.V."
        assert len(inv.items) == 1
        assert inv.subtotal == Decimal("35.00")
        assert inv.total_taxable == Decimal("35.00")
        assert inv.tax == Decimal("4.55")
        assert inv.total == Decimal("39.55")
        assert inv.total_in_words == (
            "TREINTA Y NUEVE 55/100 DOLARES"
        )
        assert inv.payment_condition == 1
        assert inv.source_file == "factura_abc_001.json"
        assert inv.detected_format == "DTE_STANDARD"
        assert inv.detection_confidence == 0.95
        assert inv.raw_data is not None

    def test_create_invoice_minimal(self):
        """Test creating invoice with only required fields."""
        inv = PurchaseInvoice(
            document_number="MIN-001",
            issue_date=date(2026, 2, 6),
            supplier=SupplierInfo(name="Proveedor Minimo"),
            total=Decimal("0"),
        )
        assert inv.document_number == "MIN-001"
        assert inv.document_type == PurchaseDocumentType.FACTURA
        assert inv.currency == "USD"
        assert inv.subtotal == Decimal("0")
        assert inv.tax == Decimal("0")
        assert inv.total == Decimal("0")
        assert inv.items == []
        assert inv.processing_warnings == []
        assert inv.raw_data is None

    def test_date_parsing_iso(self):
        """Test date parsing from ISO format (YYYY-MM-DD)."""
        inv = PurchaseInvoice(
            document_number="DATE-001",
            issue_date="2026-02-06",
            supplier=SupplierInfo(name="Test"),
            total=Decimal("0"),
        )
        assert inv.issue_date == date(2026, 2, 6)

    def test_date_parsing_slash(self):
        """Test date parsing from DD/MM/YYYY format."""
        inv = PurchaseInvoice(
            document_number="DATE-002",
            issue_date="06/02/2026",
            supplier=SupplierInfo(name="Test"),
            total=Decimal("0"),
        )
        assert inv.issue_date == date(2026, 2, 6)

    def test_date_parsing_dash(self):
        """Test date parsing from DD-MM-YYYY format."""
        inv = PurchaseInvoice(
            document_number="DATE-003",
            issue_date="06-02-2026",
            supplier=SupplierInfo(name="Test"),
            total=Decimal("0"),
        )
        assert inv.issue_date == date(2026, 2, 6)

    def test_date_invalid(self):
        """Test that invalid date format raises ValidationError."""
        with pytest.raises(ValidationError):
            PurchaseInvoice(
                document_number="DATE-BAD",
                issue_date="February 6, 2026",
                supplier=SupplierInfo(name="Test"),
                total=Decimal("0"),
            )

    def test_total_validation_warning(self, caplog):
        """Test total != subtotal+tax emits warning, not error."""
        import logging

        with caplog.at_level(logging.WARNING):
            inv = PurchaseInvoice(
                document_number="TOT-001",
                issue_date=date(2026, 2, 6),
                supplier=SupplierInfo(name="Test"),
                subtotal=Decimal("100.00"),
                tax=Decimal("13.00"),
                total=Decimal("150.00"),  # Wrong: should be 113.00
            )
        assert inv.total == Decimal("150.00")
        assert "mismatch" in caplog.text.lower()

    def test_items_subtotal_warning(self, caplog):
        """Test subtotal != sum(items) emits warning, not error."""
        import logging

        item = PurchaseInvoiceItem(
            description="Test",
            quantity=Decimal("1"),
            unit_price=Decimal("100.00"),
            total=Decimal("100.00"),
        )
        with caplog.at_level(logging.WARNING):
            inv = PurchaseInvoice(
                document_number="SUB-001",
                issue_date=date(2026, 2, 6),
                supplier=SupplierInfo(name="Test"),
                items=[item],
                subtotal=Decimal("200.00"),  # Wrong: should be 100
                total=Decimal("200.00"),
            )
        assert inv.subtotal == Decimal("200.00")
        assert "subtotal mismatch" in caplog.text.lower()

    def test_raw_data_stores_original(self):
        """Test raw_data preserves original JSON without loss."""
        original = {
            "identificacion": {"version": 3},
            "emisor": {"nombre": "Test"},
            "campoPersonalizado": "valor_custom",
        }
        inv = PurchaseInvoice(
            document_number="RAW-001",
            issue_date=date(2026, 2, 6),
            supplier=SupplierInfo(name="Test"),
            total=Decimal("0"),
            raw_data=original,
        )
        assert inv.raw_data == original
        assert inv.raw_data["campoPersonalizado"] == "valor_custom"

    def test_all_document_types_accepted(self):
        """Test that all 9 document types are accepted."""
        for doc_type in PurchaseDocumentType:
            inv = PurchaseInvoice(
                document_number=f"TYPE-{doc_type.name}",
                issue_date=date(2026, 2, 6),
                document_type=doc_type,
                supplier=SupplierInfo(name="Test"),
                total=Decimal("0"),
            )
            assert inv.document_type == doc_type

    def test_missing_document_number(self):
        """Test that missing document_number raises ValidationError."""
        with pytest.raises(ValidationError):
            PurchaseInvoice(
                issue_date=date(2026, 2, 6),
                supplier=SupplierInfo(name="Test"),
                total=Decimal("0"),
            )

    def test_supplier_required(self):
        """Test that supplier is required (ValidationError without)."""
        with pytest.raises(ValidationError):
            PurchaseInvoice(
                document_number="NO-SUP-001",
                issue_date=date(2026, 2, 6),
                total=Decimal("0"),
            )

    def test_processing_warnings_default_empty(self):
        """Test that processing_warnings defaults to empty list."""
        inv = PurchaseInvoice(
            document_number="WARN-001",
            issue_date=date(2026, 2, 6),
            supplier=SupplierInfo(name="Test"),
            total=Decimal("0"),
        )
        assert inv.processing_warnings == []

    def test_detection_confidence_range(self):
        """Test that detection_confidence is bounded 0-1."""
        inv = PurchaseInvoice(
            document_number="CONF-001",
            issue_date=date(2026, 2, 6),
            supplier=SupplierInfo(name="Test"),
            total=Decimal("0"),
            detection_confidence=0.85,
        )
        assert inv.detection_confidence == 0.85
        with pytest.raises(ValidationError):
            PurchaseInvoice(
                document_number="CONF-BAD",
                issue_date=date(2026, 2, 6),
                supplier=SupplierInfo(name="Test"),
                total=Decimal("0"),
                detection_confidence=1.5,
            )

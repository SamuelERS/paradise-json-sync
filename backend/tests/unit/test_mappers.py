"""
Mapper Tests / Pruebas de Mappers
==================================

Unit tests for BaseMapper, MapperRegistry, DTEStandardMapper,
and GenericFallbackMapper.
Pruebas unitarias para BaseMapper, MapperRegistry, DTEStandardMapper,
y GenericFallbackMapper.

Coverage target / Objetivo de cobertura: >= 70%
"""

from decimal import Decimal

import pytest

from src.core.purchases.base_mapper import BaseMapper, MappingError
from src.core.purchases.format_detector import DetectedFormat
from src.core.purchases.mapper_registry import (
    MapperNotFoundError,
    MapperRegistry,
    create_default_registry,
)
from src.core.purchases.mappers.dte_standard import DTEStandardMapper
from src.core.purchases.mappers.generic_fallback import (
    GenericFallbackMapper,
)
from src.models.purchase_invoice import (
    PurchaseDocumentType,
    PurchaseInvoice,
)


# === Fixtures / Fixtures ===


@pytest.fixture
def dte_mapper() -> DTEStandardMapper:
    """DTEStandardMapper instance / Instancia de DTEStandardMapper."""
    return DTEStandardMapper()


@pytest.fixture
def fallback_mapper() -> GenericFallbackMapper:
    """GenericFallbackMapper instance / Instancia de GenericFallbackMapper."""
    return GenericFallbackMapper()


@pytest.fixture
def complete_dte_json() -> dict:
    """
    Complete DTE standard JSON with all fields.
    JSON DTE estandar completo con todos los campos.
    """
    return {
        "identificacion": {
            "version": 3,
            "ambiente": "01",
            "tipoDte": "03",
            "numeroControl": "DTE-03-00000001-000000000000001",
            "codigoGeneracion": "A1B2C3D4-E5F6-7890-ABCD-EF1234567890",
            "tipoModelo": 1,
            "tipoOperacion": 1,
            "fecEmi": "2026-02-06",
            "horEmi": "14:30:00",
            "tipoMoneda": "USD",
        },
        "emisor": {
            "nit": "0614-123456-789-0",
            "nrc": "12345-6",
            "nombre": "DISTRIBUIDORA ABC S.A. DE C.V.",
            "nombreComercial": "ABC Distribuciones",
            "descActividad": "Venta al por mayor",
            "direccion": {
                "complemento": "Blvd. Los Heroes #123",
                "municipio": "San Salvador",
                "departamento": "San Salvador",
            },
            "telefono": "2222-3333",
            "correo": "ventas@abc.com.sv",
            "codEstableMH": "S001",
        },
        "receptor": {
            "nit": "0614-999999-999-9",
            "nombre": "MI EMPRESA S.A. DE C.V.",
            "nrc": "99999-9",
            "numDocumento": "0614-999999-999-9",
            "tipoDocumento": "36",
            "direccion": "Col. Escalon, San Salvador",
        },
        "cuerpoDocumento": [
            {
                "numItem": 1,
                "codigo": "PAP-001",
                "descripcion": "Papel Bond Carta Resma",
                "uniMedida": 59,
                "cantidad": 10,
                "precioUni": 3.50,
                "ventaGravada": 35.00,
                "ventaExenta": 0,
                "ventaNoSuj": 0,
                "montoDescu": 0,
                "ivaItem": 4.55,
            },
            {
                "numItem": 2,
                "codigo": "LAP-001",
                "descripcion": "Lapiceros azules caja",
                "uniMedida": 59,
                "cantidad": 5,
                "precioUni": 2.00,
                "ventaGravada": 10.00,
                "ventaExenta": 0,
                "ventaNoSuj": 0,
                "montoDescu": 0,
                "ivaItem": 1.30,
            },
        ],
        "resumen": {
            "totalGravada": 45.00,
            "totalExenta": 0,
            "totalNoSuj": 0,
            "totalDescu": 0,
            "subTotal": 45.00,
            "totalIva": 5.85,
            "totalPagar": 50.85,
            "totalLetras": "CINCUENTA 85/100 DOLARES",
            "condicionOperacion": 1,
        },
        "apendice": [
            {"campo": "observacion", "valor": "Entrega lunes"}
        ],
        "selloRecibido": "SELLO-ABC-12345",
    }


@pytest.fixture
def minimal_dte_json() -> dict:
    """
    Minimal valid DTE JSON (required fields only).
    JSON DTE minimo valido (solo campos requeridos).
    """
    return {
        "identificacion": {
            "codigoGeneracion": "MIN-UUID-001",
            "tipoDte": "01",
            "fecEmi": "2026-01-15",
        },
        "emisor": {
            "nombre": "PROVEEDOR MINIMO S.A.",
        },
        "receptor": {
            "nombre": "MI EMPRESA",
        },
        "cuerpoDocumento": [
            {
                "descripcion": "Servicio basico",
                "cantidad": 1,
                "precioUni": 100.00,
                "ventaGravada": 100.00,
            },
        ],
        "resumen": {
            "totalGravada": 100.00,
            "totalIva": 13.00,
            "totalPagar": 113.00,
        },
    }


@pytest.fixture
def generic_synonym_json() -> dict:
    """
    JSON with common field synonyms for fallback mapper.
    JSON con sinonimos de campos comunes para mapper de respaldo.
    """
    return {
        "numero_factura": "F-2026-001",
        "fecha": "2026-02-06",
        "proveedor": "FERRETERIA XYZ",
        "total": 250.00,
        "items": [
            {
                "descripcion": "Tornillos 1/4",
                "cantidad": 100,
                "precio": 1.50,
                "total": 150.00,
            },
            {
                "descripcion": "Clavos 2 pulgadas",
                "cantidad": 50,
                "precio": 2.00,
                "total": 100.00,
            },
        ],
    }


# === TestBaseMapper ===


class TestBaseMapper:
    """Tests for BaseMapper ABC / Pruebas para BaseMapper ABC."""

    def test_cannot_instantiate(self):
        """Test that BaseMapper cannot be instantiated directly.
        Verifica que BaseMapper no se puede instanciar directamente."""
        with pytest.raises(TypeError):
            BaseMapper()

    def test_parse_decimal_from_int(self, dte_mapper):
        """Test _parse_decimal with int input.
        Verifica _parse_decimal con entrada int."""
        assert dte_mapper._parse_decimal(42) == Decimal("42")

    def test_parse_decimal_from_float(self, dte_mapper):
        """Test _parse_decimal with float input.
        Verifica _parse_decimal con entrada float."""
        assert dte_mapper._parse_decimal(3.5) == Decimal("3.5")

    def test_parse_decimal_from_string(self, dte_mapper):
        """Test _parse_decimal with string input.
        Verifica _parse_decimal con entrada string."""
        assert dte_mapper._parse_decimal("45.00") == Decimal("45.00")

    def test_parse_decimal_from_string_comma(self, dte_mapper):
        """Test _parse_decimal with comma as decimal separator.
        Verifica _parse_decimal con coma como separador decimal."""
        result = dte_mapper._parse_decimal("45,50")
        assert result == Decimal("45.50")

    def test_parse_decimal_from_none(self, dte_mapper):
        """Test _parse_decimal with None returns zero.
        Verifica _parse_decimal con None retorna cero."""
        assert dte_mapper._parse_decimal(None) == Decimal("0")

    def test_parse_decimal_from_decimal(self, dte_mapper):
        """Test _parse_decimal with Decimal passthrough.
        Verifica _parse_decimal con Decimal pasa directamente."""
        val = Decimal("99.99")
        assert dte_mapper._parse_decimal(val) is val

    def test_parse_decimal_invalid(self, dte_mapper):
        """Test _parse_decimal with invalid input returns zero.
        Verifica _parse_decimal con entrada invalida retorna cero."""
        assert dte_mapper._parse_decimal("abc") == Decimal("0")

    def test_parse_date_string_iso(self, dte_mapper):
        """Test _parse_date with ISO format string.
        Verifica _parse_date con string formato ISO."""
        from datetime import date
        result = dte_mapper._parse_date("2026-02-06")
        assert result == date(2026, 2, 6)

    def test_parse_date_string_slash(self, dte_mapper):
        """Test _parse_date with DD/MM/YYYY format.
        Verifica _parse_date con formato DD/MM/YYYY."""
        from datetime import date
        result = dte_mapper._parse_date("06/02/2026")
        assert result == date(2026, 2, 6)

    def test_parse_date_string_dash(self, dte_mapper):
        """Test _parse_date with DD-MM-YYYY format.
        Verifica _parse_date con formato DD-MM-YYYY."""
        from datetime import date
        result = dte_mapper._parse_date("06-02-2026")
        assert result == date(2026, 2, 6)

    def test_parse_date_none(self, dte_mapper):
        """Test _parse_date with None returns None.
        Verifica _parse_date con None retorna None."""
        assert dte_mapper._parse_date(None) is None

    def test_parse_date_date_object(self, dte_mapper):
        """Test _parse_date with date object passthrough.
        Verifica _parse_date con objeto date pasa directamente."""
        from datetime import date
        d = date(2026, 1, 1)
        assert dte_mapper._parse_date(d) == d

    def test_parse_date_invalid(self, dte_mapper):
        """Test _parse_date with invalid format returns None.
        Verifica _parse_date con formato invalido retorna None."""
        assert dte_mapper._parse_date("not-a-date") is None

    def test_safe_get_existing_key(self, dte_mapper):
        """Test _safe_get with existing nested keys.
        Verifica _safe_get con claves anidadas existentes."""
        data = {"a": {"b": {"c": 42}}}
        assert dte_mapper._safe_get(data, "a", "b", "c") == 42

    def test_safe_get_missing_key(self, dte_mapper):
        """Test _safe_get with missing key returns default.
        Verifica _safe_get con clave faltante retorna default."""
        data = {"a": {"b": 1}}
        assert dte_mapper._safe_get(data, "a", "x", default="N/A") == "N/A"

    def test_safe_get_non_dict(self, dte_mapper):
        """Test _safe_get when intermediate value is not dict.
        Verifica _safe_get cuando valor intermedio no es dict."""
        data = {"a": "string_value"}
        assert dte_mapper._safe_get(data, "a", "b", default=None) is None

    def test_safe_get_default_none(self, dte_mapper):
        """Test _safe_get default is None when not specified.
        Verifica _safe_get default es None cuando no se especifica."""
        assert dte_mapper._safe_get({}, "x") is None


# === TestMappingError ===


class TestMappingError:
    """Tests for MappingError / Pruebas para MappingError."""

    def test_basic_error(self):
        """Test creating MappingError with message only.
        Verifica creacion de MappingError solo con mensaje."""
        err = MappingError("test error")
        assert str(err) == "test error"
        assert err.message == "test error"
        assert err.source_file == ""
        assert err.partial_data is None

    def test_error_with_all_fields(self):
        """Test MappingError with all fields.
        Verifica MappingError con todos los campos."""
        err = MappingError(
            message="mapping failed",
            source_file="test.json",
            partial_data={"key": "value"},
        )
        assert err.message == "mapping failed"
        assert err.source_file == "test.json"
        assert err.partial_data == {"key": "value"}

    def test_error_is_exception(self):
        """Test that MappingError is an Exception subclass.
        Verifica que MappingError es subclase de Exception."""
        assert issubclass(MappingError, Exception)


# === TestDTEStandardMapper ===


class TestDTEStandardMapper:
    """Tests for DTEStandardMapper / Pruebas para DTEStandardMapper."""

    def test_can_handle(self, dte_mapper, complete_dte_json):
        """Test can_handle recognizes DTE standard format.
        Verifica que can_handle reconoce formato DTE estandar."""
        assert dte_mapper.can_handle(complete_dte_json) is True

    def test_can_handle_rejects_wrong(self, dte_mapper):
        """Test can_handle rejects non-DTE format.
        Verifica que can_handle rechaza formato no-DTE."""
        wrong_data = {"foo": "bar", "baz": 123}
        assert dte_mapper.can_handle(wrong_data) is False

    def test_can_handle_rejects_partial(self, dte_mapper):
        """Test can_handle rejects partial DTE (missing keys).
        Verifica que can_handle rechaza DTE parcial."""
        partial = {
            "identificacion": {},
            "emisor": {},
            # missing receptor, cuerpoDocumento, resumen
        }
        assert dte_mapper.can_handle(partial) is False

    def test_map_complete_invoice(
        self, dte_mapper, complete_dte_json,
    ):
        """Test mapping a complete DTE invoice.
        Verifica mapeo de factura DTE completa."""
        result = dte_mapper.map(complete_dte_json, "test.json")

        assert isinstance(result, PurchaseInvoice)
        assert result.document_number == (
            "A1B2C3D4-E5F6-7890-ABCD-EF1234567890"
        )
        assert result.control_number == (
            "DTE-03-00000001-000000000000001"
        )
        assert result.document_type == PurchaseDocumentType.CCF
        assert result.currency == "USD"
        assert result.dte_version == 3
        assert result.emission_time == "14:30:00"

    def test_map_supplier_info(
        self, dte_mapper, complete_dte_json,
    ):
        """Test supplier mapping from emisor section.
        Verifica mapeo de proveedor desde seccion emisor."""
        result = dte_mapper.map(complete_dte_json)

        assert result.supplier.name == (
            "DISTRIBUIDORA ABC S.A. DE C.V."
        )
        assert result.supplier.commercial_name == (
            "ABC Distribuciones"
        )
        assert result.supplier.nit == "0614-123456-789-0"
        assert result.supplier.nrc == "12345-6"
        assert result.supplier.phone == "2222-3333"
        assert result.supplier.email == "ventas@abc.com.sv"

    def test_map_receiver_info(
        self, dte_mapper, complete_dte_json,
    ):
        """Test receiver mapping from receptor section.
        Verifica mapeo de receptor desde seccion receptor."""
        result = dte_mapper.map(complete_dte_json)

        assert result.receiver_name == "MI EMPRESA S.A. DE C.V."
        assert result.receiver_nit == "0614-999999-999-9"
        assert result.receiver_nrc == "99999-9"

    def test_map_items(self, dte_mapper, complete_dte_json):
        """Test mapping of cuerpoDocumento to items.
        Verifica mapeo de cuerpoDocumento a items."""
        result = dte_mapper.map(complete_dte_json)

        assert len(result.items) == 2
        assert result.items[0].description == "Papel Bond Carta Resma"
        assert result.items[0].quantity == Decimal("10")
        assert result.items[0].unit_price == Decimal("3.5")
        assert result.items[0].item_number == 1
        assert result.items[1].description == "Lapiceros azules caja"

    def test_map_financial_summary(
        self, dte_mapper, complete_dte_json,
    ):
        """Test mapping of resumen to financial fields.
        Verifica mapeo de resumen a campos financieros."""
        result = dte_mapper.map(complete_dte_json)

        assert result.total == Decimal("50.85")
        assert result.tax == Decimal("5.85")
        assert result.subtotal == Decimal("45.00")
        assert result.total_taxable == Decimal("45.00")
        assert result.total_in_words == "CINCUENTA 85/100 DOLARES"
        assert result.payment_condition == 1

    def test_map_minimal_invoice(
        self, dte_mapper, minimal_dte_json,
    ):
        """Test mapping a minimal DTE invoice.
        Verifica mapeo de factura DTE minima."""
        result = dte_mapper.map(minimal_dte_json, "minimal.json")

        assert isinstance(result, PurchaseInvoice)
        assert result.document_number == "MIN-UUID-001"
        assert result.document_type == PurchaseDocumentType.FACTURA
        assert result.total == Decimal("113.00")
        assert result.tax == Decimal("13.00")
        assert result.source_file == "minimal.json"

    def test_map_with_appendix(
        self, dte_mapper, complete_dte_json,
    ):
        """Test mapping preserves appendix data.
        Verifica que mapeo preserva datos de apendice."""
        result = dte_mapper.map(complete_dte_json)

        assert result.appendix_data is not None
        assert "entries" in result.appendix_data
        assert len(result.appendix_data["entries"]) == 1

    def test_map_without_appendix(
        self, dte_mapper, minimal_dte_json,
    ):
        """Test mapping without appendix.
        Verifica mapeo sin apendice."""
        result = dte_mapper.map(minimal_dte_json)
        assert result.appendix_data is None

    def test_preserves_raw_data(
        self, dte_mapper, complete_dte_json,
    ):
        """Test that raw_data contains the original JSON.
        Verifica que raw_data contiene el JSON original."""
        result = dte_mapper.map(complete_dte_json)

        assert result.raw_data is not None
        assert result.raw_data == complete_dte_json

    def test_document_type_mapping_ccf(self, dte_mapper):
        """Test tipoDte '03' maps to CCF.
        Verifica que tipoDte '03' mapea a CCF."""
        assert dte_mapper._map_document_type("03") == (
            PurchaseDocumentType.CCF
        )

    def test_document_type_mapping_factura(self, dte_mapper):
        """Test tipoDte '01' maps to FACTURA.
        Verifica que tipoDte '01' mapea a FACTURA."""
        assert dte_mapper._map_document_type("01") == (
            PurchaseDocumentType.FACTURA
        )

    def test_document_type_mapping_nota_credito(self, dte_mapper):
        """Test tipoDte '05' maps to NOTA_CREDITO.
        Verifica que tipoDte '05' mapea a NOTA_CREDITO."""
        assert dte_mapper._map_document_type("05") == (
            PurchaseDocumentType.NOTA_CREDITO
        )

    def test_document_type_mapping_nota_debito(self, dte_mapper):
        """Test tipoDte '06' maps to NOTA_DEBITO.
        Verifica que tipoDte '06' mapea a NOTA_DEBITO."""
        assert dte_mapper._map_document_type("06") == (
            PurchaseDocumentType.NOTA_DEBITO
        )

    def test_document_type_mapping_exportacion(self, dte_mapper):
        """Test tipoDte '11' maps to FACTURA_EXPORTACION.
        Verifica que tipoDte '11' mapea a FACTURA_EXPORTACION."""
        assert dte_mapper._map_document_type("11") == (
            PurchaseDocumentType.FACTURA_EXPORTACION
        )

    def test_document_type_mapping_sujeto_excluido(self, dte_mapper):
        """Test tipoDte '14' maps to SUJETO_EXCLUIDO.
        Verifica que tipoDte '14' mapea a SUJETO_EXCLUIDO."""
        assert dte_mapper._map_document_type("14") == (
            PurchaseDocumentType.SUJETO_EXCLUIDO
        )

    def test_document_type_mapping_retencion(self, dte_mapper):
        """Test tipoDte '07' maps to COMPROBANTE_RETENCION.
        Verifica que tipoDte '07' mapea a COMPROBANTE_RETENCION."""
        assert dte_mapper._map_document_type("07") == (
            PurchaseDocumentType.COMPROBANTE_RETENCION
        )

    def test_document_type_mapping_donacion(self, dte_mapper):
        """Test tipoDte '15' maps to COMPROBANTE_DONACION.
        Verifica que tipoDte '15' mapea a COMPROBANTE_DONACION."""
        assert dte_mapper._map_document_type("15") == (
            PurchaseDocumentType.COMPROBANTE_DONACION
        )

    def test_document_type_mapping_unknown(self, dte_mapper):
        """Test unknown tipoDte maps to DESCONOCIDO.
        Verifica que tipoDte desconocido mapea a DESCONOCIDO."""
        assert dte_mapper._map_document_type("99") == (
            PurchaseDocumentType.DESCONOCIDO
        )

    def test_tax_seal_sellorecibido(self, dte_mapper, complete_dte_json):
        """Test tax seal extraction from selloRecibido.
        Verifica extraccion de sello fiscal de selloRecibido."""
        result = dte_mapper.map(complete_dte_json)
        assert result.tax_seal == "SELLO-ABC-12345"

    def test_tax_seal_SelloRecibido(self, dte_mapper, minimal_dte_json):
        """Test tax seal extraction from SelloRecibido (uppercase S).
        Verifica extraccion de sello fiscal de SelloRecibido."""
        minimal_dte_json["SelloRecibido"] = "SELLO-UPPER-999"
        result = dte_mapper.map(minimal_dte_json)
        assert result.tax_seal == "SELLO-UPPER-999"

    def test_address_from_dict(self, dte_mapper, complete_dte_json):
        """Test address extraction from dict with parts.
        Verifica extraccion de direccion de dict con partes."""
        result = dte_mapper.map(complete_dte_json)
        assert result.supplier.address is not None
        assert "San Salvador" in result.supplier.address

    def test_address_from_string(self, dte_mapper, complete_dte_json):
        """Test address extraction from string.
        Verifica extraccion de direccion de string."""
        result = dte_mapper.map(complete_dte_json)
        assert result.receiver_address == (
            "Col. Escalon, San Salvador"
        )

    def test_map_with_conftest_fixture(
        self, dte_mapper, sample_dte_standard_json,
    ):
        """Test mapping with conftest sample DTE JSON fixture.
        Verifica mapeo con fixture sample_dte_standard_json de conftest."""
        result = dte_mapper.map(sample_dte_standard_json, "conftest.json")

        assert isinstance(result, PurchaseInvoice)
        assert result.document_number == (
            "A1B2C3D4-E5F6-7890-ABCD-EF1234567890"
        )
        assert result.document_type == PurchaseDocumentType.CCF
        assert result.supplier.name == (
            "DISTRIBUIDORA ABC S.A. DE C.V."
        )
        assert result.total == Decimal("39.55")
        assert result.raw_data == sample_dte_standard_json

    def test_map_empty_cuerpo(self, dte_mapper):
        """Test mapping with empty cuerpoDocumento.
        Verifica mapeo con cuerpoDocumento vacio."""
        data = {
            "identificacion": {
                "codigoGeneracion": "EMPTY-BODY",
                "tipoDte": "01",
                "fecEmi": "2026-01-01",
            },
            "emisor": {"nombre": "TEST"},
            "receptor": {"nombre": "ME"},
            "cuerpoDocumento": [],
            "resumen": {"totalPagar": 0, "totalIva": 0},
        }
        result = dte_mapper.map(data)
        assert result.items == []
        assert result.total == Decimal("0")


# === TestGenericFallbackMapper ===


class TestGenericFallbackMapper:
    """Tests for GenericFallbackMapper / Pruebas para GenericFallbackMapper."""

    def test_can_handle_always_true(self, fallback_mapper):
        """Test can_handle always returns True.
        Verifica que can_handle siempre retorna True."""
        assert fallback_mapper.can_handle({}) is True
        assert fallback_mapper.can_handle({"x": 1}) is True

    def test_map_with_synonyms(
        self, fallback_mapper, generic_synonym_json,
    ):
        """Test mapping using field synonyms.
        Verifica mapeo usando sinonimos de campos."""
        result = fallback_mapper.map(generic_synonym_json, "syn.json")

        assert isinstance(result, PurchaseInvoice)
        assert result.document_number == "F-2026-001"
        assert result.total == Decimal("250")
        assert result.source_file == "syn.json"

    def test_map_finds_supplier_name(
        self, fallback_mapper, generic_synonym_json,
    ):
        """Test that fallback finds supplier via synonym.
        Verifica que fallback encuentra proveedor via sinonimo."""
        result = fallback_mapper.map(generic_synonym_json)
        assert result.supplier.name == "FERRETERIA XYZ"

    def test_map_finds_items(
        self, fallback_mapper, generic_synonym_json,
    ):
        """Test that fallback maps items list.
        Verifica que fallback mapea lista de items."""
        result = fallback_mapper.map(generic_synonym_json)
        assert len(result.items) == 2
        assert result.items[0].description == "Tornillos 1/4"

    def test_map_minimal_fields(self, fallback_mapper):
        """Test mapping with minimum recognizable fields.
        Verifica mapeo con campos minimos reconocibles."""
        data = {
            "invoice_number": "INV-999",
            "total_amount": 500.00,
        }
        result = fallback_mapper.map(data)
        assert result.document_number == "INV-999"
        assert result.total == Decimal("500")

    def test_error_no_fields(self, fallback_mapper):
        """Test MappingError when no recognizable fields found.
        Verifica MappingError cuando no se encuentran campos."""
        with pytest.raises(MappingError) as exc_info:
            fallback_mapper.map({"foo": "bar"}, "bad.json")
        assert "campos minimos" in exc_info.value.message
        assert exc_info.value.source_file == "bad.json"

    def test_error_empty_dict(self, fallback_mapper):
        """Test MappingError with empty dictionary.
        Verifica MappingError con diccionario vacio."""
        with pytest.raises(MappingError):
            fallback_mapper.map({})

    def test_preserves_raw_data(
        self, fallback_mapper, generic_synonym_json,
    ):
        """Test that raw_data preserves original JSON.
        Verifica que raw_data preserva el JSON original."""
        result = fallback_mapper.map(generic_synonym_json)
        assert result.raw_data == generic_synonym_json

    def test_nested_synonym_dot_notation(self, fallback_mapper):
        """Test synonym with dot notation for nested keys.
        Verifica sinonimo con notacion punto para claves anidadas."""
        data = {
            "codigoGeneracion": "CODE-123",
            "total": 100.00,
            "emisor": {"nombre": "NESTED SUPPLIER"},
        }
        result = fallback_mapper.map(data)
        assert result.supplier.name == "NESTED SUPPLIER"

    def test_find_field_returns_none(self, fallback_mapper):
        """Test _find_field returns None for unknown canonical.
        Verifica que _find_field retorna None para canonico desconocido."""
        result = fallback_mapper._find_field(
            {"x": 1}, "nonexistent_field",
        )
        assert result is None

    def test_map_no_total_raises(self, fallback_mapper):
        """Test that missing total raises MappingError.
        Verifica que falta de total lanza MappingError."""
        data = {"numero_factura": "F-001"}
        with pytest.raises(MappingError):
            fallback_mapper.map(data)

    def test_map_no_doc_number_raises(self, fallback_mapper):
        """Test that missing doc number raises MappingError.
        Verifica que falta de numero lanza MappingError."""
        data = {"total": 100.00}
        with pytest.raises(MappingError):
            fallback_mapper.map(data)


# === TestMapperRegistry ===


class TestMapperRegistry:
    """Tests for MapperRegistry / Pruebas para MapperRegistry."""

    def test_register_and_get(self):
        """Test registering and retrieving a mapper.
        Verifica registro y obtencion de un mapper."""
        registry = MapperRegistry()
        mapper = DTEStandardMapper()
        registry.register(DetectedFormat.DTE_STANDARD, mapper)

        result = registry.get_mapper(DetectedFormat.DTE_STANDARD)
        assert result is mapper

    def test_fallback(self):
        """Test fallback is used for unregistered formats.
        Verifica que fallback se usa para formatos no registrados."""
        registry = MapperRegistry()
        fallback = GenericFallbackMapper()
        registry.set_fallback(fallback)

        result = registry.get_mapper(DetectedFormat.UNKNOWN)
        assert result is fallback

    def test_fallback_for_variant(self):
        """Test fallback is used for VARIANT_A (not registered).
        Verifica que fallback se usa para VARIANT_A (no registrado)."""
        registry = MapperRegistry()
        registry.register(
            DetectedFormat.DTE_STANDARD, DTEStandardMapper(),
        )
        fallback = GenericFallbackMapper()
        registry.set_fallback(fallback)

        result = registry.get_mapper(DetectedFormat.DTE_VARIANT_A)
        assert result is fallback

    def test_no_mapper_no_fallback(self):
        """Test MapperNotFoundError without mapper or fallback.
        Verifica MapperNotFoundError sin mapper ni fallback."""
        registry = MapperRegistry()

        with pytest.raises(MapperNotFoundError) as exc_info:
            registry.get_mapper(DetectedFormat.UNKNOWN)
        assert "UNKNOWN" in str(exc_info.value)

    def test_list_formats(self):
        """Test listing all registered formats.
        Verifica listado de todos los formatos registrados."""
        registry = MapperRegistry()
        registry.register(
            DetectedFormat.DTE_STANDARD, DTEStandardMapper(),
        )
        registry.register(
            DetectedFormat.DTE_VARIANT_A, GenericFallbackMapper(),
        )

        formats = registry.list_formats()
        assert DetectedFormat.DTE_STANDARD in formats
        assert DetectedFormat.DTE_VARIANT_A in formats
        assert len(formats) == 2

    def test_list_formats_empty(self):
        """Test list_formats with no registered mappers.
        Verifica list_formats sin mappers registrados."""
        registry = MapperRegistry()
        assert registry.list_formats() == []

    def test_create_default_registry(self):
        """Test the factory function creates correct registry.
        Verifica que la funcion fabrica crea registry correcto."""
        registry = create_default_registry()

        assert isinstance(registry, MapperRegistry)
        formats = registry.list_formats()
        assert DetectedFormat.DTE_STANDARD in formats
        assert len(formats) == 1

        # Should have fallback for UNKNOWN
        mapper = registry.get_mapper(DetectedFormat.UNKNOWN)
        assert isinstance(mapper, GenericFallbackMapper)

    def test_create_default_registry_dte_mapper(self):
        """Test default registry has DTEStandardMapper.
        Verifica que registry default tiene DTEStandardMapper."""
        registry = create_default_registry()
        mapper = registry.get_mapper(DetectedFormat.DTE_STANDARD)
        assert isinstance(mapper, DTEStandardMapper)

    def test_registered_mapper_overrides_fallback(self):
        """Test registered mapper takes precedence over fallback.
        Verifica que mapper registrado tiene precedencia sobre fallback."""
        registry = MapperRegistry()
        dte_mapper = DTEStandardMapper()
        fallback = GenericFallbackMapper()

        registry.register(DetectedFormat.DTE_STANDARD, dte_mapper)
        registry.set_fallback(fallback)

        result = registry.get_mapper(DetectedFormat.DTE_STANDARD)
        assert result is dte_mapper
        assert result is not fallback

    def test_mapper_not_found_error_is_exception(self):
        """Test MapperNotFoundError is an Exception subclass.
        Verifica que MapperNotFoundError es subclase de Exception."""
        assert issubclass(MapperNotFoundError, Exception)

# 🔄 Mappers y Registro — Convertidores de Formato por Proveedor

> **¿Qué es esto?** Este documento explica cómo se convierte cada formato de JSON al modelo canónico `PurchaseInvoice`. Cada formato tiene su propio "traductor" (mapper) y un registro central los coordina.

---

## 1. Concepto: Patrón Strategy + Registry

Imagina una oficina de traducciones:

- El **Registry** es la recepcionista. Le dices "necesito traducir del Formato A" y ella te asigna al traductor correcto.
- Cada **Mapper** es un traductor especializado. Sabe exactamente cómo convertir un formato específico al "idioma común" (PurchaseInvoice).
- El **Fallback** es el traductor genérico. Si nadie más puede, él lo intenta con heurísticas.

```
FormatDetector dice: "Es DTE_STANDARD"
        ↓
MapperRegistry busca: ¿Quién maneja DTE_STANDARD?
        ↓
DTEStandardMapper: "Yo lo traduzco"
        ↓
Resultado: PurchaseInvoice normalizado
```

---

## 2. Clase Abstracta: BaseMapper

Todos los mappers heredan de esta clase. Define el contrato que CADA mapper debe cumplir.

```python
from abc import ABC, abstractmethod

class BaseMapper(ABC):
    """
    Clase base para todos los mappers de formato.
    Cada mapper convierte un formato específico al modelo PurchaseInvoice.
    """

    @abstractmethod
    def map(self, data: dict, source_file: str = "") -> PurchaseInvoice:
        """
        Convierte datos JSON crudos a PurchaseInvoice.

        Args:
            data: Diccionario con los datos JSON crudos
            source_file: Ruta del archivo fuente

        Returns:
            PurchaseInvoice normalizado

        Raises:
            MappingError: Si la conversión falla
        """
        pass

    @abstractmethod
    def can_handle(self, data: dict) -> bool:
        """
        Verifica si este mapper puede manejar los datos dados.
        Usado como validación secundaria después del FormatDetector.
        """
        pass

    def _parse_decimal(self, value) -> Decimal:
        """Utilidad compartida: convierte valor a Decimal."""
        # Misma lógica que JSONProcessor._parse_decimal actual
        ...

    def _parse_date(self, value) -> date:
        """Utilidad compartida: parsea fecha de múltiples formatos."""
        # Misma lógica que Invoice.parse_date actual
        ...

    def _safe_get(self, data: dict, *keys, default=None):
        """
        Acceso seguro a claves anidadas.
        Ejemplo: _safe_get(data, "resumen", "totalPagar", default=0)
        """
        current = data
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        return current
```

---

## 3. MapperRegistry — El Registro Central

```python
class MapperRegistry:
    """
    Registro central de mappers.
    Asocia cada DetectedFormat con su mapper correspondiente.
    """

    def __init__(self):
        self._mappers: dict[DetectedFormat, BaseMapper] = {}
        self._fallback: Optional[BaseMapper] = None

    def register(self, format: DetectedFormat, mapper: BaseMapper) -> None:
        """Registra un mapper para un formato específico."""
        self._mappers[format] = mapper

    def set_fallback(self, mapper: BaseMapper) -> None:
        """Define el mapper de fallback para formatos desconocidos."""
        self._fallback = mapper

    def get_mapper(self, format: DetectedFormat) -> BaseMapper:
        """
        Obtiene el mapper para un formato.
        Si no existe, retorna el fallback.
        Si no hay fallback, lanza error.
        """
        if format in self._mappers:
            return self._mappers[format]
        if self._fallback:
            return self._fallback
        raise MapperNotFoundError(f"No mapper registered for {format}")

    def list_formats(self) -> list[DetectedFormat]:
        """Lista todos los formatos soportados."""
        return list(self._mappers.keys())
```

### Inicialización del Registry

```python
def create_default_registry() -> MapperRegistry:
    """Crea el registry con todos los mappers predeterminados."""
    registry = MapperRegistry()

    # Registrar mappers
    registry.register(DetectedFormat.DTE_STANDARD, DTEStandardMapper())
    registry.register(DetectedFormat.DTE_VARIANT_A, DTEVariantAMapper())
    registry.register(DetectedFormat.DTE_VARIANT_B, DTEVariantBMapper())
    registry.register(DetectedFormat.GENERIC_FLAT, GenericFlatMapper())
    registry.register(DetectedFormat.PDF_EXTRACTED, PDFExtractedMapper())

    # Fallback para formatos desconocidos
    registry.set_fallback(GenericFallbackMapper())

    return registry
```

---

## 4. DTEStandardMapper — El Mapper Principal

Este es el mapper más importante. Convierte el formato estándar de Hacienda.

```python
class DTEStandardMapper(BaseMapper):
    """
    Mapper para formato DTE estándar de Hacienda de El Salvador.

    Estructura esperada:
    {
        "identificacion": { "codigoGeneracion", "tipoDte", "fecEmi", ... },
        "emisor": { "nit", "nombre", "nrc", ... },
        "receptor": { "nombre", "numDocumento", ... },
        "cuerpoDocumento": [ { "numItem", "descripcion", ... } ],
        "resumen": { "totalPagar", "totalIva", "subTotal", ... },
        "apendice": [ ... ]  (opcional)
    }

    NOTA: Este mapper es SIMILAR a _normalize_dte_format en json_processor.py
    pero adaptado para la perspectiva de COMPRAS (emisor = proveedor).
    """

    def can_handle(self, data: dict) -> bool:
        required = {"identificacion", "emisor", "receptor", "cuerpoDocumento", "resumen"}
        return required.issubset(data.keys())

    def map(self, data: dict, source_file: str = "") -> PurchaseInvoice:
        identificacion = data.get("identificacion", {})
        emisor = data.get("emisor", {})
        receptor = data.get("receptor", {})
        resumen = data.get("resumen", {})
        cuerpo = data.get("cuerpoDocumento", [])
        apendice = data.get("apendice", [])

        # Mapear proveedor (en compras, el EMISOR es nuestro proveedor)
        supplier = SupplierInfo(
            name=emisor.get("nombre", ""),
            commercial_name=emisor.get("nombreComercial"),
            nit=emisor.get("nit"),
            nrc=emisor.get("nrc"),
            economic_activity=emisor.get("descActividad"),
            address=self._extract_address(emisor.get("direccion", {})),
            phone=emisor.get("telefono"),
            email=emisor.get("correo"),
            establishment_code=emisor.get("codEstableMH"),
        )

        # Mapear items
        items = self._map_items(cuerpo)

        # Calcular totales (misma lógica de IVA que json_processor)
        subtotal, tax, total = self._calculate_totals(resumen, items)

        # Procesar apéndice
        appendix = self._map_appendix(apendice)

        return PurchaseInvoice(
            # Identificación
            document_number=identificacion.get("codigoGeneracion", ""),
            control_number=identificacion.get("numeroControl"),
            document_type=self._map_document_type(identificacion.get("tipoDte", "01")),
            issue_date=identificacion.get("fecEmi", ""),
            emission_time=identificacion.get("horEmi"),
            currency=identificacion.get("tipoMoneda", "USD"),
            dte_version=identificacion.get("version"),

            # Proveedor
            supplier=supplier,

            # Receptor (nosotros)
            receiver_name=receptor.get("nombre"),
            receiver_nit=receptor.get("numDocumento"),
            receiver_nrc=receptor.get("nrc"),
            receiver_doc_type=receptor.get("tipoDocumento"),
            receiver_address=self._extract_address(receptor.get("direccion", {})),

            # Items y totales
            items=items,
            subtotal=subtotal,
            total_taxable=self._parse_decimal(resumen.get("totalGravada", 0)),
            total_exempt=self._parse_decimal(resumen.get("totalExenta", 0)),
            total_non_subject=self._parse_decimal(resumen.get("totalNoSuj", 0)),
            total_discount=self._parse_decimal(resumen.get("totalDescu", 0)),
            tax=tax,
            total=total,
            total_in_words=resumen.get("totalLetras"),
            payment_condition=resumen.get("condicionOperacion"),

            # Adicionales
            appendix_data=appendix,
            tax_seal=data.get("SelloRecibido") or data.get("selloRecibido"),
            source_file=source_file,
            raw_data=data,  # JSON original completo
        )
```

---

## 5. GenericFallbackMapper — El Último Recurso

Cuando ningún mapper reconoce el formato, este intenta extraer datos por heurísticas.

```python
class GenericFallbackMapper(BaseMapper):
    """
    Mapper de último recurso. Busca campos por nombres comunes.
    Usa una tabla de sinónimos para encontrar datos.
    """

    # Tabla de sinónimos: campo canónico → posibles nombres en el JSON
    FIELD_SYNONYMS = {
        "document_number": [
            "codigoGeneracion", "codigo_generacion", "numero_factura",
            "invoice_number", "no_factura", "numero", "doc_number",
        ],
        "date": [
            "fecEmi", "fecha", "fecha_emision", "date", "issue_date",
            "fecha_factura", "invoice_date",
        ],
        "supplier_name": [
            "nombre_emisor", "emisor.nombre", "proveedor", "vendor",
            "supplier", "razon_social_emisor",
        ],
        "total": [
            "totalPagar", "total", "monto_total", "total_amount",
            "montoTotalOperacion", "totalAPagar", "grand_total",
        ],
        "items": [
            "cuerpoDocumento", "detalle", "items", "lineas",
            "productos", "lines", "line_items",
        ],
    }

    def can_handle(self, data: dict) -> bool:
        """Siempre puede intentar — es el fallback."""
        return True

    def map(self, data: dict, source_file: str = "") -> PurchaseInvoice:
        """
        Intenta mapear buscando campos por sinónimos.
        Si no encuentra campos mínimos, lanza MappingError.
        """
        # Buscar cada campo por sus sinónimos
        doc_number = self._find_field(data, "document_number")
        date_value = self._find_field(data, "date")
        total_value = self._find_field(data, "total")

        # Campos mínimos requeridos
        if not doc_number or not total_value:
            raise MappingError(
                "No se pudieron extraer campos mínimos (número, total)"
            )

        # Construir PurchaseInvoice con lo que se encuentre
        ...

    def _find_field(self, data: dict, canonical_name: str):
        """
        Busca un campo en el JSON usando la tabla de sinónimos.
        Soporta claves anidadas con notación punto: "emisor.nombre"
        """
        for synonym in self.FIELD_SYNONYMS.get(canonical_name, []):
            if "." in synonym:
                # Clave anidada
                parts = synonym.split(".")
                value = self._safe_get(data, *parts)
            else:
                value = data.get(synonym)

            if value is not None:
                return value
        return None
```

---

## 6. Agregar un Nuevo Mapper (Guía)

Cuando llegan datos de un nuevo proveedor con formato diferente:

### Paso 1: Identificar el formato
Examinar el JSON manualmente y documentar su estructura.

### Paso 2: Crear el mapper
```python
# backend/src/core/purchases/mappers/dte_nuevo_proveedor.py

class DTENuevoProveedorMapper(BaseMapper):
    """Mapper para el formato específico del proveedor X."""

    def can_handle(self, data: dict) -> bool:
        # Verificar claves únicas de este formato
        return "detalle" in data and "montos" in data

    def map(self, data: dict, source_file: str = "") -> PurchaseInvoice:
        # Lógica de conversión específica
        ...
```

### Paso 3: Agregar fingerprint al detector
```python
FINGERPRINT_NUEVO = {
    "required_keys": {"identificacion", "emisor", "detalle", "montos"},
    ...
}
detector.register_format(DetectedFormat.DTE_NUEVO, FINGERPRINT_NUEVO)
```

### Paso 4: Registrar en el registry
```python
registry.register(DetectedFormat.DTE_NUEVO, DTENuevoProveedorMapper())
```

### Paso 5: Agregar tests
```python
# tests/unit/test_mappers.py
def test_nuevo_proveedor_mapper():
    mapper = DTENuevoProveedorMapper()
    result = mapper.map(SAMPLE_JSON_NUEVO)
    assert result.total == Decimal("113.00")
    assert result.supplier.name == "PROVEEDOR X"
```

**Archivos tocados:** 3 (nuevo mapper, detector, registry). Nada más cambia.

---

## 7. Manejo de Errores

```python
class MappingError(Exception):
    """Error durante el mapeo de un formato al modelo canónico."""

    def __init__(self, message: str, source_file: str = "", partial_data: dict = None):
        self.message = message
        self.source_file = source_file
        self.partial_data = partial_data  # Datos parciales extraídos antes del error
        super().__init__(message)
```

**Política de errores:**
- Un mapper que falla **no detiene** el procesamiento del lote
- El error se registra con el archivo fuente y datos parciales
- El pipeline continúa con el siguiente archivo
- Al final, el reporte incluye la lista de archivos con error

---

## 8. Testing

```
tests/unit/test_mappers.py

Casos de prueba por mapper:
├── DTEStandardMapper
│   ├── test_map_complete_invoice      → JSON con todos los campos
│   ├── test_map_minimal_invoice       → JSON con solo campos requeridos
│   ├── test_map_iva_included          → IVA incluido en precios
│   ├── test_map_iva_separate          → IVA separado
│   ├── test_map_with_appendix         → Con apéndice
│   ├── test_map_without_appendix      → Sin apéndice
│   ├── test_preserves_raw_data        → raw_data contiene JSON original
│   └── test_can_handle                → Reconoce formato correcto
│
├── GenericFallbackMapper
│   ├── test_map_with_synonyms         → Encuentra campos por sinónimos
│   ├── test_map_nested_synonyms       → Sinónimos con notación punto
│   ├── test_map_minimal_fields        → Campos mínimos encontrados
│   ├── test_error_no_fields           → No encuentra nada → MappingError
│   └── test_can_handle_always_true    → Siempre retorna True
│
└── MapperRegistry
    ├── test_register_and_get          → Registrar y obtener mapper
    ├── test_fallback                  → Usa fallback para UNKNOWN
    ├── test_no_mapper_no_fallback     → Error sin mapper ni fallback
    └── test_list_formats              → Lista todos los formatos registrados
```

**Cobertura esperada:** >= 70% por mapper

---

> **Próximo documento:** [07_VALIDADOR_COMPRAS](./07_VALIDADOR_COMPRAS_(Verificacion-y-Calidad-de-Datos).md) — Cómo verificamos que los datos están correctos.

# 📄 Soporte PDF — Extracción de Datos desde PDF

> **⚠️ ANTES DE EMPEZAR:** Lee [EL_PUNTO_DE_PARTIDA](../../EL_PUNTO_DE_PARTIDA_by_SamuelERS.md) para identificar tu rol y qué documentos te corresponden leer según tu misión.

> **¿Qué es esto?** Este documento explica cómo el sistema extrae datos de facturas que llegan en formato PDF en lugar de JSON. Cubre la estrategia por fases y las herramientas a usar.

### Roles Requeridos para este Documento

| Rol | Misión aquí |
|-----|-------------|
| 👨‍💻 **Desarrollador de Elite (Backend)** | Implementar `PDFExtractor` y `PDFExtractedMapper` |
| 🕵️ **Investigador de Elite** | Analizar PDFs reales de proveedores para calibrar regex |

### Tareas de Implementación (FASE 7)

| Tarea | Agente | Archivo Destino |
|-------|--------|-----------------|
| Crear `PDFExtractor` | 👨‍💻 Desarrollador Backend | `backend/src/core/purchases/pdf_extractor.py` |
| Definir patrones regex | 🕵️ Investigador + 👨‍💻 Dev | Mismo archivo |
| Crear `PDFExtractedMapper` | 👨‍💻 Desarrollador Backend | `backend/src/core/purchases/mappers/pdf_extracted.py` |
| Tests unitarios (>=70%) | 👨‍💻 Desarrollador Backend | `backend/tests/unit/test_pdf_extractor.py` |
| Calibrar con PDFs reales | 🕵️ Investigador | Cuando haya muestras disponibles |

### Nota sobre raw_data en PDFs

> Para facturas extraídas de PDF, el campo `raw_data` del modelo `PurchaseInvoice` será `None` (no se almacena el binario del PDF). En su lugar, `source_file` apunta al PDF original y `processing_warnings` incluye la advertencia: "Datos extraídos de PDF — verificar manualmente".

---

## 1. Contexto: ¿Por Qué PDF?

Algunos proveedores envían facturas como PDF en lugar de JSON. Hay dos tipos:

| Tipo de PDF | Descripción | Dificultad |
|-------------|-------------|------------|
| **PDF Digital** | Generado por software, texto seleccionable | Baja — se extrae texto directamente |
| **PDF Escaneado** | Foto/escaneo de documento físico | Alta — requiere OCR |

**Esta fase cubre solo PDFs digitales.** Los escaneados son un proyecto futuro.

---

## 2. Estrategia por Fases

### Fase 1 (Esta Implementación): PDF Digital

- Extraer texto del PDF usando PyMuPDF (ya es dependencia del proyecto)
- Parsear el texto con patrones regex para encontrar campos clave
- Convertir datos extraídos a `PurchaseInvoice`
- Si la extracción falla, reportar error gracefully

### Fase 2 (Futuro): PDF Escaneado + OCR

- Usar Tesseract.js o servicio cloud para OCR
- Pipeline: PDF → Imagen → OCR → Texto → Parseo
- Mayor complejidad, menor confianza
- **No implementar ahora**

### Fase 3 (Futuro): Extracción Inteligente con LLM

- Usar modelos de lenguaje para interpretar facturas
- Pipeline: PDF → Texto/Imagen → LLM → Datos estructurados
- Mayor precisión, costo por API call
- **No implementar ahora**

---

## 3. Arquitectura del Extractor de PDF

```
┌──────────────────────────────────────────────────────┐
│  PDFExtractor                                         │
│                                                       │
│  Paso 1: Abrir PDF con PyMuPDF                        │
│  Paso 2: Extraer texto de cada página                 │
│  Paso 3: Buscar campos por patrones regex             │
│  Paso 4: Construir diccionario de datos               │
│  Paso 5: Retornar datos para que el mapper convierta  │
└──────────────────────────────────────────────────────┘
```

---

## 4. Clase PDFExtractor

```python
class PDFExtractor:
    """
    Extrae datos estructurados de facturas PDF.
    Fase 1: Solo PDFs digitales (texto seleccionable).
    """

    # Patrones regex para campos comunes en facturas DTE PDF
    PATTERNS = {
        "control_number": [
            r"DTE-\d{2}-[A-Z0-9]+-[A-Z0-9]+",
            r"N[°ú]mero de Control[:\s]+([^\n]+)",
            r"No\.\s*Control[:\s]+([^\n]+)",
        ],
        "document_number": [
            r"C[óo]digo de Generaci[óo]n[:\s]+([A-F0-9-]+)",
            r"UUID[:\s]+([A-F0-9-]+)",
        ],
        "date": [
            r"Fecha de Emisi[óo]n[:\s]+(\d{2}/\d{2}/\d{4})",
            r"Fecha[:\s]+(\d{4}-\d{2}-\d{2})",
            r"Fecha[:\s]+(\d{2}-\d{2}-\d{4})",
        ],
        "supplier_name": [
            r"Emisor[:\s]+([^\n]+)",
            r"Raz[óo]n Social[:\s]+([^\n]+)",
            r"Nombre del Emisor[:\s]+([^\n]+)",
        ],
        "supplier_nit": [
            r"NIT[:\s]+(\d{4}-\d{6}-\d{3}-\d)",
            r"NIT del Emisor[:\s]+([^\n]+)",
        ],
        "total": [
            r"Total a Pagar[:\s]+\$?([\d,]+\.\d{2})",
            r"TOTAL[:\s]+\$?([\d,]+\.\d{2})",
            r"Total Pagar[:\s]+\$?([\d,]+\.\d{2})",
        ],
        "iva": [
            r"IVA[:\s]+\$?([\d,]+\.\d{2})",
            r"Total IVA[:\s]+\$?([\d,]+\.\d{2})",
            r"Impuesto[:\s]+\$?([\d,]+\.\d{2})",
        ],
        "subtotal": [
            r"Sub\s?Total[:\s]+\$?([\d,]+\.\d{2})",
            r"SubTotal Ventas[:\s]+\$?([\d,]+\.\d{2})",
        ],
    }

    def extract(self, pdf_path: str) -> dict:
        """
        Extrae datos de un PDF de factura.

        Args:
            pdf_path: Ruta al archivo PDF

        Returns:
            Diccionario con datos extraídos (formato similar a JSON normalizado)

        Raises:
            PDFExtractionError: Si no se puede extraer texto
        """
        text = self._extract_text(pdf_path)

        if not text or len(text.strip()) < 50:
            raise PDFExtractionError(
                "PDF sin texto extraíble (posiblemente escaneado)",
                file_path=pdf_path,
            )

        data = {}
        for field, patterns in self.PATTERNS.items():
            value = self._find_pattern(text, patterns)
            if value:
                data[field] = value

        # Verificar campos mínimos
        if not data.get("total"):
            raise PDFExtractionError(
                "No se pudo extraer el total del PDF",
                file_path=pdf_path,
                partial_data=data,
            )

        return self._normalize_extracted(data, pdf_path)

    def _extract_text(self, pdf_path: str) -> str:
        """Extrae todo el texto del PDF usando PyMuPDF."""
        import fitz  # PyMuPDF — ya es dependencia del proyecto

        text_parts = []
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text_parts.append(page.get_text())

        return "\n".join(text_parts)

    def _find_pattern(self, text: str, patterns: list[str]) -> Optional[str]:
        """
        Busca el primer patrón regex que coincida en el texto.
        Retorna el grupo capturado o el match completo.
        """
        import re
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # Si tiene grupo capturado, usarlo. Si no, el match completo.
                return match.group(1) if match.groups() else match.group(0)
        return None

    def _normalize_extracted(self, data: dict, source: str) -> dict:
        """
        Convierte datos extraídos a formato normalizado
        compatible con los mappers.
        """
        return {
            "document_number": data.get("document_number", f"PDF-{Path(source).stem}"),
            "control_number": data.get("control_number"),
            "issue_date": data.get("date", date.today().isoformat()),
            "supplier_name": data.get("supplier_name", "Proveedor (PDF)"),
            "supplier_nit": data.get("supplier_nit"),
            "subtotal": self._parse_amount(data.get("subtotal", "0")),
            "tax": self._parse_amount(data.get("iva", "0")),
            "total": self._parse_amount(data.get("total", "0")),
            "source_file": source,
            "_extracted_from_pdf": True,
            "_extraction_fields_found": list(data.keys()),
        }
```

---

## 5. PDFExtractedMapper

Mapper específico para datos extraídos de PDF.

```python
class PDFExtractedMapper(BaseMapper):
    """
    Mapper para datos extraídos de PDF.
    Los datos llegan con menos campos que un JSON normal.
    """

    def can_handle(self, data: dict) -> bool:
        return data.get("_extracted_from_pdf", False)

    def map(self, data: dict, source_file: str = "") -> PurchaseInvoice:
        """
        Crea PurchaseInvoice con datos parciales de PDF.
        Campos no encontrados quedan como None.
        """
        supplier = SupplierInfo(
            name=data.get("supplier_name", "Proveedor Desconocido"),
            nit=data.get("supplier_nit"),
        )

        return PurchaseInvoice(
            document_number=data.get("document_number", ""),
            control_number=data.get("control_number"),
            document_type=PurchaseDocumentType.DESCONOCIDO,
            issue_date=data.get("issue_date"),
            supplier=supplier,
            subtotal=self._parse_decimal(data.get("subtotal", 0)),
            tax=self._parse_decimal(data.get("tax", 0)),
            total=self._parse_decimal(data.get("total", 0)),
            items=[],  # PDFs raramente tienen items parseables
            source_file=source_file,
            detected_format="PDF_EXTRACTED",
            processing_warnings=[
                "Datos extraídos de PDF — verificar manualmente",
                f"Campos encontrados: {data.get('_extraction_fields_found', [])}",
            ],
        )
```

---

## 6. Limitaciones Conocidas (Fase 1)

| Limitación | Detalle |
|------------|---------|
| Solo PDFs digitales | No funciona con escaneos o fotos |
| Sin items detallados | Difícil extraer tabla de items de texto plano |
| Confianza menor | Los datos de PDF son menos confiables que JSON |
| Formatos de PDF variados | Cada proveedor genera PDFs con layouts diferentes |
| Caracteres especiales | Algunos PDFs tienen problemas con acentos/ñ |
| PDFs multi-página | Se concatena texto de todas las páginas; no se maneja factura por página |
| PDFs protegidos | No se soportan PDFs con contraseña; se reporta error claro |
| raw_data | Para PDFs, `raw_data=None`; el archivo original se referencia en `source_file` |

**Mitigación:** Toda factura extraída de PDF lleva un warning obligatorio: "Datos extraídos de PDF — verificar manualmente".

---

## 7. Testing

```
tests/unit/test_pdf_extractor.py

├── test_extract_digital_pdf           → PDF con texto seleccionable
├── test_extract_all_fields            → Encuentra todos los campos
├── test_extract_partial_fields        → Encuentra algunos campos
├── test_extract_no_text               → PDF sin texto → error
├── test_extract_no_total              → No encuentra total → error
├── test_pattern_control_number        → Regex encuentra N° control
├── test_pattern_nit                   → Regex encuentra NIT
├── test_pattern_total                 → Regex encuentra total
├── test_pattern_date_formats          → Múltiples formatos de fecha
├── test_normalize_extracted_data      → Normalización de datos extraídos
└── test_pdf_mapper_integration        → PDFExtractedMapper funciona
```

**Cobertura esperada:** >= 70%

---

## 8. Dependencias

| Herramienta | Paquete | Estado |
|-------------|---------|--------|
| PyMuPDF | `PyMuPDF>=1.23` | Ya instalado (se usa en pdf_processor.py) |
| Regex | `re` (stdlib) | Incluido en Python |

**No se requieren nuevas dependencias** para la Fase 1 de PDF.

---

> **Próximo documento:** [11_FRONTEND_UI](./11_FRONTEND_UI_(Interfaz-de-Usuario-para-Compras).md) — La interfaz de usuario.

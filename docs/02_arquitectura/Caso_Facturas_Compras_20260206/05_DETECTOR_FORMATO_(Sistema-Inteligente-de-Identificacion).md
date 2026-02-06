# 🔍 Detector de Formato — Sistema Inteligente de Identificación

> **¿Qué es esto?** Este documento explica cómo el sistema identifica automáticamente el formato de cada JSON de factura de compra, sin configuración manual por proveedor.

---

## 1. El Problema (En Palabras Simples)

Llegan 50 facturas JSON de 5 proveedores diferentes. Cada uno usa un sistema diferente. El sistema debe "mirar" cada JSON y decir: "Este es formato A, este es formato B, este no lo conozco pero voy a intentar".

Es como un detective que mira las huellas digitales para identificar a quién pertenecen.

---

## 2. Concepto: Fingerprinting

Un **fingerprint** es una combinación de características que identifica un formato:
- ¿Qué claves tiene en el primer nivel?
- ¿Hay secciones como `identificacion`, `emisor`, `receptor`?
- ¿Los items están en `cuerpoDocumento` o en `detalle` o en `lineas`?
- ¿El resumen se llama `resumen` o `totales` o `montos`?

Cada combinación única = un formato diferente.

---

## 3. Formatos Conocidos (Iniciales)

### 3.1 DTE_STANDARD — Formato Hacienda Estándar

El formato "oficial" que Hacienda de El Salvador define. La mayoría de sistemas lo siguen.

```json
{
  "identificacion": {
    "version": 3,
    "ambiente": "01",
    "tipoDte": "03",
    "numeroControl": "DTE-03-...",
    "codigoGeneracion": "UUID...",
    "tipoModelo": 1,
    "tipoOperacion": 1,
    "fecEmi": "2026-02-06",
    "horEmi": "14:30:00",
    "tipoMoneda": "USD"
  },
  "emisor": { "nit": "...", "nrc": "...", "nombre": "..." },
  "receptor": { "nit": "...", "nombre": "..." },
  "cuerpoDocumento": [ { "numItem": 1, ... } ],
  "resumen": { "totalPagar": 100.00, ... },
  "apendice": [ ... ]
}
```

**Fingerprint:**
```python
FINGERPRINT_DTE_STANDARD = {
    "required_keys": {"identificacion", "emisor", "receptor", "cuerpoDocumento", "resumen"},
    "optional_keys": {"apendice", "extension", "otrosDocumentos"},
    "nested_checks": {
        "identificacion": {"codigoGeneracion", "tipoDte", "fecEmi"},
        "resumen": {"totalPagar"},
    },
    "items_key": "cuerpoDocumento",
}
```

---

### 3.2 DTE_VARIANT_A — Items en "detalle"

Algunos sistemas renombran `cuerpoDocumento` a `detalle` o usan variaciones.

```json
{
  "identificacion": { "codigoGeneracion": "...", "tipoDte": "01", ... },
  "emisor": { ... },
  "receptor": { ... },
  "detalle": [ { "numItem": 1, ... } ],
  "totales": { "totalAPagar": 100.00, ... }
}
```

**Fingerprint:**
```python
FINGERPRINT_DTE_VARIANT_A = {
    "required_keys": {"identificacion", "emisor", "receptor", "detalle"},
    "nested_checks": {
        "identificacion": {"codigoGeneracion"},
    },
    "items_key": "detalle",
    "total_key_alternatives": ["totalAPagar", "montoTotalOperacion"],
}
```

---

### 3.3 DTE_VARIANT_B — Resumen aplanado

Algunos sistemas "aplanan" el resumen directamente en la raíz.

```json
{
  "identificacion": { ... },
  "emisor": { ... },
  "receptor": { ... },
  "cuerpoDocumento": [ ... ],
  "totalGravada": 100.00,
  "totalIva": 13.00,
  "totalPagar": 113.00
}
```

**Fingerprint:**
```python
FINGERPRINT_DTE_VARIANT_B = {
    "required_keys": {"identificacion", "emisor", "cuerpoDocumento"},
    "root_total_keys": {"totalPagar", "totalGravada", "totalIva"},
    "items_key": "cuerpoDocumento",
}
```

---

### 3.4 GENERIC_FLAT — Formato plano genérico

JSONs sin la estructura DTE típica, pero con campos reconocibles.

```json
{
  "numero_factura": "F-001",
  "fecha": "2026-02-06",
  "proveedor": "ABC S.A.",
  "nit_proveedor": "0614-...",
  "items": [ { "descripcion": "...", "total": 10.00 } ],
  "total": 113.00
}
```

**Fingerprint:**
```python
FINGERPRINT_GENERIC_FLAT = {
    "heuristic_keys": {
        "invoice_number": ["numero_factura", "numero", "factura_no", "invoice_number", "no_factura"],
        "date": ["fecha", "fecha_emision", "date", "fecEmi"],
        "supplier": ["proveedor", "emisor", "vendor", "supplier"],
        "total": ["total", "totalPagar", "monto_total", "total_amount"],
    },
}
```

---

## 4. Algoritmo de Detección

```python
class FormatDetector:
    """Identifica el formato de un JSON de factura."""

    def detect(self, data: dict) -> DetectionResult:
        """
        Analiza un JSON y determina su formato.

        Returns:
            DetectionResult con formato, confianza y detalles.
        """
        scores = {}

        # Paso 1: Comparar contra fingerprints conocidos
        for format_name, fingerprint in self.fingerprints.items():
            score = self._calculate_score(data, fingerprint)
            scores[format_name] = score

        # Paso 2: Elegir el formato con mayor puntaje
        best_format = max(scores, key=scores.get)
        best_score = scores[best_format]

        # Paso 3: Determinar confianza
        if best_score >= 0.90:
            confidence = "HIGH"
        elif best_score >= 0.70:
            confidence = "MEDIUM"
        elif best_score >= 0.50:
            confidence = "LOW"
        else:
            best_format = DetectedFormat.UNKNOWN
            confidence = "NONE"

        return DetectionResult(
            format=best_format,
            confidence=best_score,
            confidence_level=confidence,
            scores=scores,  # Todos los puntajes para debug
        )
```

### 4.1 Cálculo de Puntaje

```python
def _calculate_score(self, data: dict, fingerprint: dict) -> float:
    """
    Calcula qué tan bien un JSON coincide con un fingerprint.

    Puntaje de 0.0 a 1.0:
    - Claves requeridas presentes: +0.4 (proporcional)
    - Claves anidadas presentes: +0.3 (proporcional)
    - Claves opcionales presentes: +0.1 (bonus)
    - Formato de valores esperado: +0.2 (tipos correctos)
    """
    score = 0.0
    max_score = 1.0

    # Verificar claves requeridas (peso: 40%)
    required = fingerprint.get("required_keys", set())
    if required:
        present = required.intersection(data.keys())
        score += 0.4 * (len(present) / len(required))

    # Verificar estructura anidada (peso: 30%)
    nested = fingerprint.get("nested_checks", {})
    if nested:
        nested_score = 0
        for parent_key, child_keys in nested.items():
            if parent_key in data and isinstance(data[parent_key], dict):
                present_children = child_keys.intersection(data[parent_key].keys())
                nested_score += len(present_children) / len(child_keys)
        score += 0.3 * (nested_score / len(nested))
    else:
        score += 0.3  # Sin checks anidados = puntaje completo

    # Verificar claves opcionales (bonus: 10%)
    optional = fingerprint.get("optional_keys", set())
    if optional:
        present = optional.intersection(data.keys())
        score += 0.1 * (len(present) / len(optional))

    # Verificar tipos de datos (peso: 20%)
    score += self._check_value_types(data, fingerprint) * 0.2

    return min(score, max_score)
```

---

## 5. Resultado de la Detección

```python
class DetectionResult(BaseModel):
    """Resultado del análisis de formato."""

    format: DetectedFormat           # Formato identificado
    confidence: float                # Puntaje (0.0 - 1.0)
    confidence_level: str            # "HIGH", "MEDIUM", "LOW", "NONE"
    scores: dict[str, float]         # Puntajes de todos los formatos (para debug)
    items_key: Optional[str]         # Clave donde están los items
    total_key: Optional[str]         # Clave donde está el total
    metadata: dict = {}              # Info adicional del análisis


class DetectedFormat(str, Enum):
    """Formatos reconocidos por el detector."""

    DTE_STANDARD = "DTE_STANDARD"       # Formato oficial Hacienda
    DTE_VARIANT_A = "DTE_VARIANT_A"     # Variante con 'detalle'
    DTE_VARIANT_B = "DTE_VARIANT_B"     # Variante con resumen aplanado
    GENERIC_FLAT = "GENERIC_FLAT"       # JSON plano genérico
    PDF_EXTRACTED = "PDF_EXTRACTED"     # Datos extraídos de PDF
    UNKNOWN = "UNKNOWN"                 # No reconocido
```

---

## 6. Extensibilidad

### Agregar un nuevo formato detectado:

1. Definir el fingerprint del formato
2. Agregarlo al enum `DetectedFormat`
3. Registrarlo en el `FormatDetector`

```python
# Paso 1: Definir fingerprint
FINGERPRINT_NUEVO = {
    "required_keys": {"factura", "proveedor", "lineas"},
    "nested_checks": { "factura": {"numero", "fecha"} },
    "items_key": "lineas",
}

# Paso 2: Agregar al enum
class DetectedFormat(str, Enum):
    # ... formatos existentes ...
    DTE_VARIANT_C = "DTE_VARIANT_C"  # Nuevo formato

# Paso 3: Registrar
detector.register_format(DetectedFormat.DTE_VARIANT_C, FINGERPRINT_NUEVO)
```

**Sin tocar** el código del detector, los mappers existentes, ni el pipeline.

---

## 7. Manejo de Formatos Desconocidos

Cuando ningún fingerprint tiene puntaje >= 0.50:

1. El formato se marca como `UNKNOWN`
2. Se usa el `GenericFallbackMapper` (ver documento 06)
3. El mapper intenta buscar campos por nombres comunes (heurísticas)
4. Si puede extraer datos mínimos (número, fecha, total), lo procesa con warning
5. Si no puede extraer nada, registra un error pero no detiene el lote

---

## 8. Testing del Detector

```
tests/unit/test_format_detector.py

Casos de prueba:
├── test_detect_dte_standard          → JSON estándar Hacienda
├── test_detect_dte_variant_a         → JSON con "detalle" en vez de "cuerpoDocumento"
├── test_detect_dte_variant_b         → JSON con resumen aplanado
├── test_detect_generic_flat          → JSON plano sin estructura DTE
├── test_detect_unknown               → JSON sin campos reconocibles
├── test_confidence_levels            → Verificar HIGH/MEDIUM/LOW/NONE
├── test_scores_all_formats           → Verificar que devuelve puntajes de todos
├── test_empty_json                   → JSON vacío → UNKNOWN
├── test_array_instead_of_object      → Lista en vez de dict → error graceful
└── test_register_new_format          → Agregar formato nuevo dinámicamente
```

**Cobertura esperada:** >= 70%

---

> **Próximo documento:** [06_MAPPERS_Y_REGISTRO](./06_MAPPERS_Y_REGISTRO_(Convertidores-de-Formato-por-Proveedor).md) — Cómo se convierte cada formato al modelo canónico.

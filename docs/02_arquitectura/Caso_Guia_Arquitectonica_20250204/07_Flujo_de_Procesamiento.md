# 07 - Flujo de Procesamiento (Processing Flow)
# Processing Flow (Flujo de Procesamiento - El camino de los datos)

---

## Observaciones Obligatorias (Mandatory Notes)

```
TESTS REQUERIDOS: Sí - Cada paso del flujo debe tener tests
COBERTURA MÍNIMA: 70%
CI/CD: Compatible - Flujo completo debe probarse en pipeline
MONITOREO: Logs en cada paso para debugging
```

---

## Que es el Flujo de Procesamiento (What is the Processing Flow)

**Explicación simple:**
El flujo de procesamiento es como una cadena de montaje en una fábrica:
1. Entra materia prima (archivos)
2. Pasa por varias estaciones de trabajo (pasos)
3. Sale el producto terminado (Excel y PDF)

Cada estación hace una tarea específica y pasa el trabajo a la siguiente.

---

## Vista General del Flujo (Flow Overview)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    FLUJO COMPLETO DE PARADISE JSON SYNC                 │
│                                                                         │
│   USUARIO          FRONTEND           BACKEND              RESULTADO    │
│      │                 │                  │                    │        │
│      │  Selecciona     │                  │                    │        │
│      │  archivos       │                  │                    │        │
│      ├────────────────►│                  │                    │        │
│      │                 │                  │                    │        │
│      │                 │  POST /upload    │                    │        │
│      │                 ├─────────────────►│                    │        │
│      │                 │                  │ Guarda archivos    │        │
│      │                 │◄─────────────────┤ Retorna job_id     │        │
│      │                 │                  │                    │        │
│      │  Click          │                  │                    │        │
│      │  "Procesar"     │                  │                    │        │
│      ├────────────────►│                  │                    │        │
│      │                 │                  │                    │        │
│      │                 │  POST /process   │                    │        │
│      │                 ├─────────────────►│                    │        │
│      │                 │                  │ Inicia proceso     │        │
│      │                 │◄─────────────────┤                    │        │
│      │                 │                  │                    │        │
│      │                 │  GET /status     │                    │        │
│      │  Ve progreso    │◄────────────────►│ (cada 2 segundos)  │        │
│      │◄────────────────┤                  │                    │        │
│      │                 │                  │                    │        │
│      │                 │                  │  ┌──────────────┐  │        │
│      │                 │                  │  │ PROCESANDO   │  │        │
│      │                 │                  │  │ 1.Validar    │  │        │
│      │                 │                  │  │ 2.Extraer    │  │        │
│      │                 │                  │  │ 3.Transformar│  │        │
│      │                 │                  │  │ 4.Exportar   │  │        │
│      │                 │                  │  └──────────────┘  │        │
│      │                 │                  │                    │        │
│      │                 │  GET /download   │                    │        │
│      │  Descarga       │◄────────────────►│                    │        │
│      │  archivos       │                  │                    │        │
│      │◄────────────────┤                  │                    ├──────► │
│      │                 │                  │                    │ Excel  │
│      │                 │                  │                    │ PDF    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Pasos Detallados (Detailed Steps)

### Paso 1: Upload (Carga de Archivos)

**¿Qué pasa?**
El usuario selecciona archivos y el sistema los recibe.

```
ENTRADA:  Archivos .json y .pdf del usuario
SALIDA:   job_id único para seguimiento
TIEMPO:   Depende del tamaño (~1-5 segundos)
```

**Diagrama:**
```
┌──────────────────────────────────────────────────────┐
│                    PASO 1: UPLOAD                    │
├──────────────────────────────────────────────────────┤
│                                                      │
│   Usuario                                            │
│     │                                                │
│     │  archivos.json + archivos.pdf                  │
│     ▼                                                │
│   ┌─────────────┐                                    │
│   │  Dropzone   │ ◄── Zona de arrastre               │
│   └─────────────┘                                    │
│         │                                            │
│         │  FormData con archivos                     │
│         ▼                                            │
│   ┌─────────────┐                                    │
│   │   /upload   │ ◄── Endpoint del backend           │
│   └─────────────┘                                    │
│         │                                            │
│         ▼                                            │
│   ┌─────────────────────────────────────┐            │
│   │  1. Validar extensiones             │            │
│   │  2. Validar tamaños                 │            │
│   │  3. Crear job_id único              │            │
│   │  4. Guardar en /tmp/jobs/{job_id}/  │            │
│   │  5. Registrar metadata              │            │
│   └─────────────────────────────────────┘            │
│         │                                            │
│         │  job_id: "abc-123-def"                     │
│         ▼                                            │
│   Respuesta al frontend                              │
│                                                      │
└──────────────────────────────────────────────────────┘
```

**Validaciones en este paso:**
- [ ] Extensión debe ser `.json` o `.pdf`
- [ ] Tamaño máximo por archivo: 10 MB
- [ ] Cantidad máxima: 100 archivos

**Tests requeridos:**
- [ ] Test: Upload exitoso con archivos válidos
- [ ] Test: Rechazo de extensiones inválidas
- [ ] Test: Rechazo de archivos muy grandes
- [ ] Test: job_id es único

---

### Paso 2: Validation (Validación de Contenido)

**¿Qué pasa?**
El sistema verifica que los archivos tengan contenido válido.

```
ENTRADA:  Archivos en /tmp/jobs/{job_id}/
SALIDA:   Lista de archivos válidos y errores
TIEMPO:   ~100ms por archivo
```

**Diagrama:**
```
┌──────────────────────────────────────────────────────┐
│                 PASO 2: VALIDATION                   │
├──────────────────────────────────────────────────────┤
│                                                      │
│   Para cada archivo JSON:                            │
│   ┌─────────────────────────────────────────────┐    │
│   │  1. ¿Es JSON válido? (parseable)            │    │
│   │  2. ¿Tiene campo 'document_number'?         │    │
│   │  3. ¿Tiene campo 'issue_date'?              │    │
│   │  4. ¿Tiene campo 'total'?                   │    │
│   └─────────────────────────────────────────────┘    │
│                                                      │
│   Para cada archivo PDF:                             │
│   ┌─────────────────────────────────────────────┐    │
│   │  1. ¿Es PDF válido? (no corrupto)           │    │
│   │  2. ¿Se puede abrir?                        │    │
│   │  3. ¿Tiene al menos 1 página?               │    │
│   └─────────────────────────────────────────────┘    │
│                                                      │
│   RESULTADO:                                         │
│   ┌─────────────────────────────────────────────┐    │
│   │  valid_files: ["f1.json", "f2.json", ...]   │    │
│   │  invalid_files: [                           │    │
│   │    {"file": "f3.json", "error": "..."}      │    │
│   │  ]                                          │    │
│   └─────────────────────────────────────────────┘    │
│                                                      │
└──────────────────────────────────────────────────────┘
```

**Tests requeridos:**
- [ ] Test: JSON válido pasa validación
- [ ] Test: JSON con campos faltantes genera error específico
- [ ] Test: PDF corrupto genera error pero no detiene proceso
- [ ] Test: Cuenta correcta de válidos/inválidos

---

### Paso 3: Extraction (Extracción de Datos)

**¿Qué pasa?**
El sistema lee los archivos JSON y extrae la información importante.

```
ENTRADA:  Lista de archivos JSON válidos
SALIDA:   Lista de objetos Invoice
TIEMPO:   ~50ms por archivo
```

**Diagrama:**
```
┌──────────────────────────────────────────────────────┐
│                  PASO 3: EXTRACTION                  │
├──────────────────────────────────────────────────────┤
│                                                      │
│   Archivo JSON                     Objeto Invoice    │
│   ┌──────────────┐                 ┌──────────────┐  │
│   │{             │                 │Invoice(      │  │
│   │ "numero":    │  ──────────►    │ document_    │  │
│   │   "CFJ001",  │  extraer        │   number=    │  │
│   │ "fecha":     │  campos         │   "CFJ001",  │  │
│   │   "2025-01", │                 │ issue_date=  │  │
│   │ "cliente":   │                 │   date(...), │  │
│   │   "Juan",    │                 │ client_name= │  │
│   │ "items":[...│                 │   "Juan",    │  │
│   │ ],          │                 │ ...          │  │
│   │ "total":100  │                 │)             │  │
│   │}             │                 └──────────────┘  │
│   └──────────────┘                                   │
│                                                      │
│   MAPEO DE CAMPOS:                                   │
│   ┌─────────────────────────────────────────────┐    │
│   │  JSON Field    →    Invoice Field           │    │
│   │  ─────────────────────────────────────────  │    │
│   │  "numero"      →    document_number         │    │
│   │  "fecha"       →    issue_date              │    │
│   │  "cliente"     →    client_name             │    │
│   │  "nit"         →    client_id               │    │
│   │  "productos"   →    items                   │    │
│   │  "subtotal"    →    subtotal                │    │
│   │  "iva"         →    tax                     │    │
│   │  "total"       →    total                   │    │
│   └─────────────────────────────────────────────┘    │
│                                                      │
└──────────────────────────────────────────────────────┘
```

**Tests requeridos:**
- [ ] Test: Extrae todos los campos correctamente
- [ ] Test: Mapea nombres alternativos (numero → document_number)
- [ ] Test: Convierte fechas a formato estándar
- [ ] Test: Maneja campos opcionales faltantes

---

### Paso 4: Transform & Sort (Transformación y Ordenamiento)

**¿Qué pasa?**
Los datos se limpian, normalizan y ordenan según preferencias.

```
ENTRADA:  Lista de Invoice sin ordenar
SALIDA:   Lista de Invoice ordenada y limpia
TIEMPO:   ~10ms para 1000 registros
```

**Diagrama:**
```
┌──────────────────────────────────────────────────────┐
│                PASO 4: TRANSFORM & SORT              │
├──────────────────────────────────────────────────────┤
│                                                      │
│   TRANSFORMACIONES:                                  │
│   ┌─────────────────────────────────────────────┐    │
│   │  1. Normalizar nombres de cliente           │    │
│   │     "juan perez" → "Juan Pérez"             │    │
│   │                                             │    │
│   │  2. Formatear montos                        │    │
│   │     100 → Decimal("100.00")                 │    │
│   │                                             │    │
│   │  3. Unificar formato de fechas              │    │
│   │     "15/01/2025" → date(2025, 1, 15)        │    │
│   │                                             │    │
│   │  4. Eliminar duplicados                     │    │
│   │     (mismo document_number)                 │    │
│   └─────────────────────────────────────────────┘    │
│                                                      │
│   ORDENAMIENTO (según opción del usuario):           │
│   ┌─────────────────────────────────────────────┐    │
│   │  sort_by="date"                             │    │
│   │    → Ordenar por issue_date ascendente      │    │
│   │                                             │    │
│   │  sort_by="document_number"                  │    │
│   │    → Ordenar por número de documento        │    │
│   │                                             │    │
│   │  sort_by="client"                           │    │
│   │    → Ordenar por nombre de cliente          │    │
│   │                                             │    │
│   │  sort_by="total"                            │    │
│   │    → Ordenar por monto total                │    │
│   └─────────────────────────────────────────────┘    │
│                                                      │
└──────────────────────────────────────────────────────┘
```

**Tests requeridos:**
- [ ] Test: Normaliza nombres correctamente
- [ ] Test: Ordena por fecha ascendente
- [ ] Test: Detecta y elimina duplicados
- [ ] Test: Mantiene integridad de datos

---

### Paso 5: Excel Export (Exportación a Excel)

**¿Qué pasa?**
Los datos procesados se convierten en un archivo Excel.

```
ENTRADA:  Lista de Invoice ordenada
SALIDA:   Archivo .xlsx
TIEMPO:   ~500ms para 1000 registros
```

**Estructura del Excel:**
```
┌──────────────────────────────────────────────────────┐
│              ESTRUCTURA DEL EXCEL                    │
├──────────────────────────────────────────────────────┤
│                                                      │
│   HOJA 1: "Facturas" (Invoices)                      │
│   ┌────────────────────────────────────────────────┐ │
│   │ A          B         C          D       E      │ │
│   │ Documento  Fecha     Cliente    Items   Total  │ │
│   │ ─────────────────────────────────────────────  │ │
│   │ CFJ001     2025-01   Juan P.    3       $100   │ │
│   │ CFJ002     2025-01   María G.   5       $250   │ │
│   │ ...                                            │ │
│   └────────────────────────────────────────────────┘ │
│                                                      │
│   HOJA 2: "Resumen" (Summary) - Si include_summary   │
│   ┌────────────────────────────────────────────────┐ │
│   │ Métrica                    Valor               │ │
│   │ ─────────────────────────────────────────────  │ │
│   │ Total Facturas             100                 │ │
│   │ Suma Total                 $15,000.00          │ │
│   │ Promedio por Factura       $150.00             │ │
│   │ Fecha más antigua          2025-01-01          │ │
│   │ Fecha más reciente         2025-01-31          │ │
│   └────────────────────────────────────────────────┘ │
│                                                      │
└──────────────────────────────────────────────────────┘
```

**Tests requeridos:**
- [ ] Test: Genera Excel válido
- [ ] Test: Headers correctos en fila 1
- [ ] Test: Formato de moneda en columna Total
- [ ] Test: Hoja de resumen tiene cálculos correctos

---

### Paso 6: PDF Merge (Unificación de PDFs)

**¿Qué pasa?**
Todos los PDFs se unen en un solo documento.

```
ENTRADA:  Lista de archivos PDF
SALIDA:   Archivo PDF único
TIEMPO:   ~100ms por página
```

**Diagrama:**
```
┌──────────────────────────────────────────────────────┐
│                  PASO 6: PDF MERGE                   │
├──────────────────────────────────────────────────────┤
│                                                      │
│   ANTES:                           DESPUÉS:          │
│                                                      │
│   ┌────────┐                       ┌────────────┐    │
│   │PDF 1   │                       │            │    │
│   │ (5 pág)│                       │  PDF       │    │
│   └────────┘                       │  UNIFICADO │    │
│   ┌────────┐                       │            │    │
│   │PDF 2   │  ──────────────────►  │ Página 1   │    │
│   │ (3 pág)│       UNIR           │ Página 2   │    │
│   └────────┘                       │ ...        │    │
│   ┌────────┐                       │ Página 15  │    │
│   │PDF 3   │                       │            │    │
│   │ (7 pág)│                       │ Marcadores:│    │
│   └────────┘                       │ - PDF 1    │    │
│                                    │ - PDF 2    │    │
│                                    │ - PDF 3    │    │
│                                    └────────────┘    │
│                                                      │
│   ORDENAMIENTO (mismo que sort_by):                  │
│   Los PDFs se ordenan según el document_number       │
│   de la factura correspondiente.                     │
│                                                      │
└──────────────────────────────────────────────────────┘
```

**Tests requeridos:**
- [ ] Test: Une 2 PDFs correctamente
- [ ] Test: Mantiene orden especificado
- [ ] Test: Crea marcadores para navegación
- [ ] Test: PDF corrupto se salta sin detener proceso

---

## Manejo de Errores en el Flujo (Error Handling)

### Estrategia: Fail-Safe (A prueba de fallos)

```
PRINCIPIO: Un archivo malo NO debe detener todo el proceso.

Si un archivo falla:
1. Se registra el error
2. Se continúa con los demás
3. Al final, se reportan los errores

Resultado: "98 de 100 procesados correctamente, 2 con errores"
```

**Ejemplo de error parcial:**
```json
{
  "status": "completed_with_errors",
  "results": {
    "files_processed": 100,
    "files_success": 98,
    "files_error": 2
  },
  "errors": [
    {
      "file": "factura_corrupta.json",
      "error": "JSON inválido: Unexpected token at line 15"
    },
    {
      "file": "factura_sin_total.json",
      "error": "Campo requerido 'total' no encontrado"
    }
  ]
}
```

---

## Proximo Documento (Next Document)

Continúa con: `08_Estrategia_de_Testing.md` para ver cómo probamos todo.

---

**Versión:** 1.0
**Líneas:** ~350
**Cumple reglas:** Sí

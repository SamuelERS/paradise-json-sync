# 🚨 Reglas No Negociables — Normas Obligatorias para Cada Agente

> **⚠️ ANTES DE EMPEZAR:** Lee [EL_PUNTO_DE_PARTIDA](../../EL_PUNTO_DE_PARTIDA_by_SamuelERS.md) para identificar tu rol y qué documentos te corresponden leer según tu misión.

> **⚠️ LECTURA OBLIGATORIA ANTES DE ESCRIBIR UNA SOLA LÍNEA DE CÓDIGO.**
>
> Este documento aplica a TODO agente (IA o humano) que trabaje en el módulo de facturas de compra. Sin excepciones.

### Todos los Roles Deben Leer Este Documento

| Rol | Por qué debe leerlo |
|-----|---------------------|
| 🧑‍🍳 **Chef Arquitecto** | Para verificar que el diseño cumple las restricciones |
| 👨‍💻 **Desarrollador de Elite** | Para saber CÓMO escribir código, commits, y tests |
| ✍️ **Documentador de Elite** | Para saber CÓMO nombrar archivos y mantener documentación |
| 🕵️ **Investigador de Elite** | Para saber QUÉ buscar al analizar formatos y proveedores |
| ✅ **Inspector de Elite** | Para tener el checklist de revisión de código |
| ⚙️ **Ingeniero Operaciones** | Para saber las restricciones de CI/CD y despliegue |
| 📋 **Director de Proyecto** | Para verificar que las órdenes de trabajo cumplen las normas |

---

## 1. Convención de Commits

### Formato Obligatorio

```
FASE-X MODULO: Descripción clara en español de lo que se hizo
```

### Ejemplos Correctos

```
FASE-0 DOCUMENTACION: Guía arquitectónica completa del sistema de facturas de compra
FASE-1 MODELO: Crear PurchaseInvoice con validadores y tests
FASE-2 DETECTOR: Implementar FormatDetector con fingerprinting para DTE
FASE-3 MAPPERS: Agregar DTEStandardMapper y GenericFallbackMapper
FASE-4 VALIDADOR: Crear PurchaseValidator con detección de duplicados
FASE-5 API: Endpoints de upload, process, status y download para compras
FASE-6 EXPORTADOR: PurchaseExporter con columnas configurables y perfiles
FASE-7 PDF: Extractor de texto PDF con patrones regex
FASE-8 FRONTEND: Toggle Ventas/Compras y configurador de columnas
FASE-9 INTEGRACION: Tests E2E del flujo completo y verificación de cobertura
```

### Ejemplos Incorrectos (NO hacer)

```
❌ fix: updated files
❌ WIP
❌ changes
❌ Phase 1 model (no está en español)
❌ Se hicieron varias cosas (no dice QUÉ)
❌ FASE-1: modelo (sin módulo, sin descripción clara)
```

---

## 2. Convención de Código

### 2.1 Archivos

| Regla | Límite |
|-------|--------|
| Máximo líneas por archivo | 500 |
| Máximo líneas por función | 50 |
| Una función = una responsabilidad | Obligatorio |
| Nombres de archivo | snake_case (Python), PascalCase (React components) |

### 2.2 Tipos

| Regla | Obligatorio |
|-------|------------|
| Zero `any` en TypeScript | Sí |
| Type annotations en Python | Sí (mypy strict) |
| Pydantic models para datos | Sí |
| Enums para valores fijos | Sí |

### 2.3 Documentación en Código

Cada archivo nuevo DEBE tener:

```python
"""
Nombre del Módulo / Module Name
================================

Descripción breve en español.
Brief description in English.

This module provides / Este módulo provee:
- Función A: descripción
- Función B: descripción
"""
```

Cada función pública DEBE tener:

```python
def mi_funcion(param: str) -> bool:
    """
    Descripción corta de qué hace.
    Short description of what it does.

    Args / Argumentos:
        param: Descripción del parámetro

    Returns / Retorna:
        Descripción del retorno

    Raises / Lanza:
        ErrorType: Cuándo se lanza
    """
```

---

## 3. Convención de Documentación

### Nombres de Archivos Técnicos

Todos los archivos de documentación deben tener:

```
[NN]_NOMBRE_DESCRIPTIVO_(Nombre-en-Español-de-lo-que-es).md
```

**Ejemplo:**
```
05_DETECTOR_FORMATO_(Sistema-Inteligente-de-Identificacion).md
```

El nombre entre paréntesis en español permite que cualquier persona no programadora entienda de qué trata el documento sin abrirlo.

### Máximo 500 Líneas

Si un documento supera 500 líneas, se divide en partes. No hay excepciones.

### Emojis Oficiales

Solo los emojis definidos en `REGLAS_DOCUMENTACION.md`:

| Emoji | Uso |
|-------|-----|
| ⚠️ | Advertencia / Riesgo |
| 🚧 | En construcción |
| 🔍 | En investigación |
| ✅ | Completado |
| ❌ | Error / Rechazado |
| 🏁 | Caso finalizado |
| 🔴 | Pendiente |
| 🟡 | En progreso |
| 🟢 | Completado y verificado |

---

## 4. Convención de Testing

| Regla | Valor |
|-------|-------|
| Cobertura mínima | 70% |
| Tests antes de merge | Obligatorio |
| Nombres descriptivos | `test_detect_dte_standard_with_high_confidence` |
| Fixtures compartidas | En `fixtures/purchases/` |
| Tests independientes | No depender de orden |
| Tests de regresión | Si se arregla un bug, agregar test |

### Comando de Verificación

```bash
# Backend: debe pasar con >= 70%
cd backend && pytest tests/ --cov=src --cov-fail-under=70

# Frontend: debe pasar
cd frontend && npm test -- --watchAll=false

# E2E: debe pasar
npm run test:e2e
```

---

## 5. Convención de Arquitectura

### Lo que NO se toca

| Archivo/Módulo | Razón |
|---------------|-------|
| `backend/src/models/invoice.py` | Sistema de ventas — funciona perfecto |
| `backend/src/core/json_processor.py` | Sistema de ventas — no modificar |
| `backend/src/core/excel_exporter.py` | Se puede reutilizar pero NO modificar |
| `backend/src/api/routes/upload.py` | Endpoints de ventas — intactos |
| `frontend/src/components/DropzoneUpload.jsx` | Se reutiliza pero NO se modifica |

### Dónde va el código nuevo

| Tipo | Ubicación |
|------|-----------|
| Modelo de compras | `backend/src/models/purchase_invoice.py` |
| Lógica de compras | `backend/src/core/purchases/` |
| API de compras | `backend/src/api/routes/purchases.py` |
| Schemas de compras | `backend/src/api/schemas/purchases.py` |
| Servicio de compras | `backend/src/services/purchase_service.py` |
| Frontend compras | `frontend/src/components/Purchase*.jsx` |
| Tests backend | `backend/tests/unit/test_purchase_*.py` |
| Tests API | `backend/tests/api/test_purchases_api.py` |
| Tests E2E | `e2e/tests/purchases-*.spec.ts` |
| Fixtures | `e2e/fixtures/test-data/purchases/` |

---

## 6. Información No Negociable por Agente

Cada agente que trabaje en este proyecto DEBE conocer:

### Antes de Empezar

1. Leer `docs/REGLAS_DE_LA_CASA.md` (Constitución)
2. Leer `docs/REGLAS_DESARROLLO.md` (Estándares técnicos)
3. Leer este documento (`13_REGLAS_NO_NEGOCIABLES`)
4. Leer `01_TODO_LIST_PRINCIPAL` para saber el estado actual

### Al Trabajar

5. Actualizar `01_TODO_LIST_PRINCIPAL` al completar cada tarea
6. Commits en español con formato `FASE-X MODULO: descripción`
7. Tests antes de commit — mínimo 70% cobertura
8. No crear archivos sueltos en `docs/` (usar carpeta del caso)
9. Máximo 500 líneas por archivo, 50 por función
10. Documentación bilingüe en código (español/inglés)

### Al Finalizar

11. Verificar que todos los tests pasan
12. Actualizar TODO list con tareas completadas
13. Si se creó documentación nueva, actualizar `00_README.md`

---

## 7. Regla de Oro (Repetida por Importancia)

> **"No toleramos la pérdida de datos."**
>
> - El campo `raw_data` del modelo SIEMPRE almacena el JSON original
> - Las columnas configurables solo afectan la VISTA, no los DATOS
> - La exportación JSON SIEMPRE incluye todos los campos
> - Si un mapper no encuentra un campo, queda como `None`, nunca se inventa

---

## 8. Compatibilidad y Retrocompatibilidad

### Con el sistema existente de ventas

| Aspecto | Regla |
|---------|-------|
| Endpoints existentes | No se modifican |
| Modelos existentes | No se modifican |
| Frontend existente | Cambio mínimo: solo agregar toggle |
| Tests existentes | Deben seguir pasando |
| Dependencias | No agregar nuevas sin justificación |
| CI/CD | Extender, no reescribir |

### Con esta guía arquitectónica

| Aspecto | Regla |
|---------|-------|
| Nombres de clases | Deben coincidir con los definidos aquí |
| Estructura de carpetas | Debe seguir lo definido en doc 03 |
| Endpoints | Deben coincidir con lo definido en doc 08 |
| Perfiles de columnas | Deben coincidir con lo definido en doc 09 |

---

## 9. Checklist Pre-Commit

Antes de cada commit, verificar:

- [ ] ¿El commit sigue formato `FASE-X MODULO: descripción en español`?
- [ ] ¿Los tests pasan? (`pytest` + `npm test`)
- [ ] ¿La cobertura es >= 70%?
- [ ] ¿No se modificaron archivos del sistema de ventas?
- [ ] ¿Los archivos nuevos tienen < 500 líneas?
- [ ] ¿Las funciones nuevas tienen < 50 líneas?
- [ ] ¿El código tiene type annotations?
- [ ] ¿Las funciones tienen docstrings bilingües?
- [ ] ¿Se actualizó el TODO list?

---

## 10. Tabla de Referencia Rápida

| Qué necesito saber | Dónde lo encuentro |
|--------------------|--------------------|
| Estado actual del proyecto | `01_TODO_LIST_PRINCIPAL` |
| Qué vamos a construir | `02_VISION_Y_ALCANCE` |
| Cómo funciona el pipeline | `03_ARQUITECTURA_GENERAL` |
| Estructura del modelo | `04_MODELO_CANONICO` |
| Cómo detectar formatos | `05_DETECTOR_FORMATO` |
| Cómo crear un mapper | `06_MAPPERS_Y_REGISTRO` |
| Reglas de validación | `07_VALIDADOR_COMPRAS` |
| Endpoints de la API | `08_API_Y_SERVICIOS` |
| Columnas y exportación | `09_EXPORTADOR_COMPRAS` |
| Extracción de PDF | `10_SOPORTE_PDF` |
| Diseño de la UI | `11_FRONTEND_UI` |
| Estrategia de testing | `12_TESTING_Y_CICD` |
| Reglas obligatorias | `13_REGLAS_NO_NEGOCIABLES` (este documento) |

---

> **Fin de la guía arquitectónica.** Cualquier desarrollador o agente que siga estos documentos podrá implementar el sistema de facturas de compra de forma profesional, modular y con calidad verificable.

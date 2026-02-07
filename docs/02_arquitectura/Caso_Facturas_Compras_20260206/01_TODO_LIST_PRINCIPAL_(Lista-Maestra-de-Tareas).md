# 📋 TODO LIST PRINCIPAL — Facturas de Compra

> **⚠️ ANTES DE EMPEZAR:** Lee [EL_PUNTO_DE_PARTIDA](../../EL_PUNTO_DE_PARTIDA_by_SamuelERS.md) para identificar tu rol y qué documentos te corresponden leer según tu misión.

> **Este es el documento de control central del proyecto.**
> Aquí se rastrea el progreso de cada fase, módulo y tarea.
> Actualizar este archivo es **obligatorio** al completar cualquier tarea.

### Roles Requeridos para este Documento

| Rol | Misión aquí |
|-----|-------------|
| 📋 **Director de Proyecto** | Actualizar estados, coordinar fases, asignar tareas |
| ✍️ **Documentador de Elite** | Mantener formato y coherencia con otros documentos |
| 🧑‍🍳 **Todos los Agentes** | Consultar antes de empezar y actualizar al terminar cada tarea |

### Asignación de Agentes por Fase

| Fase | Agente(s) Requerido(s) | Justificación |
|------|------------------------|---------------|
| FASE 0 | ✍️ Documentador + 🕵️ Investigador | Documentación técnica + investigación de formatos |
| FASE 1 | 👨‍💻 Desarrollador de Elite (Backend) | Modelos Pydantic, validadores, tests unitarios |
| FASE 2 | 👨‍💻 Desarrollador de Elite (Backend) + 🕵️ Investigador | Análisis de formatos reales + implementación detector |
| FASE 3 | 👨‍💻 Desarrollador de Elite (Backend) | Mappers con patrón Strategy, tests por mapper |
| FASE 4 | 👨‍💻 Desarrollador de Elite (Backend) + ✅ Inspector | Validaciones matemáticas requieren revisión rigurosa |
| FASE 5 | 👨‍💻 Desarrollador de Elite (Backend) | Endpoints FastAPI, schemas, servicio orquestador |
| FASE 6 | 👨‍💻 Desarrollador de Elite (Backend) | Exportador con columnas dinámicas |
| FASE 7 | 👨‍💻 Desarrollador de Elite (Backend) + 🕵️ Investigador | Regex sobre PDFs requiere análisis de muestras reales |
| FASE 8 | 👨‍💻 Desarrollador de Elite (Frontend) | React, Tailwind, componentes, Vitest |
| FASE 9 | ✅ Inspector de Elite + ⚙️ Ingeniero Operaciones | Inspección final, CI/CD, E2E, cobertura |

---

## Convención de Estados

| Emoji | Estado | Significado |
|-------|--------|-------------|
| 🔴 | Pendiente | No iniciado |
| 🟡 | En Progreso | Trabajo activo |
| 🟢 | Completado | Terminado y verificado |
| ⏸️ | Pausado | Bloqueado o en espera |

---

## FASE 0: Documentación y Guía Arquitectónica

> **Objetivo:** Crear toda la documentación técnica antes de escribir código.

| # | Tarea | Estado | Responsable | Notas |
|---|-------|--------|-------------|-------|
| 0.1 | Investigación de formatos DTE y variaciones | 🟢 | Claude | Completado en sesión inicial |
| 0.2 | Investigación de herramientas (parsers, validadores) | 🟢 | Claude | AJV/Zod, pdf-parse, fast-xml-parser |
| 0.3 | Documento: Visión y Alcance | 🟢 | Claude | `02_VISION_Y_ALCANCE` |
| 0.4 | Documento: Arquitectura General | 🟢 | Claude | `03_ARQUITECTURA_GENERAL` |
| 0.5 | Documento: Modelo Canónico | 🟢 | Claude | `04_MODELO_CANONICO` |
| 0.6 | Documento: Detector de Formato | 🟢 | Claude | `05_DETECTOR_FORMATO` |
| 0.7 | Documento: Mappers y Registro | 🟢 | Claude | `06_MAPPERS_Y_REGISTRO` |
| 0.8 | Documento: Validador de Compras | 🟢 | Claude | `07_VALIDADOR_COMPRAS` |
| 0.9 | Documento: API y Servicios | 🟢 | Claude | `08_API_Y_SERVICIOS` |
| 0.10 | Documento: Exportador Configurable | 🟢 | Claude | `09_EXPORTADOR_COMPRAS` |
| 0.11 | Documento: Soporte PDF | 🟢 | Claude | `10_SOPORTE_PDF` |
| 0.12 | Documento: Frontend UI | 🟢 | Claude | `11_FRONTEND_UI` |
| 0.13 | Documento: Testing y CI/CD | 🟢 | Claude | `12_TESTING_Y_CICD` |
| 0.14 | Documento: Reglas No Negociables | 🟢 | Claude | `13_REGLAS_NO_NEGOCIABLES` |

---

## FASE 1: Modelo de Datos (PurchaseInvoice)

> **Objetivo:** Crear el modelo canónico que unifica todos los formatos.
> **Prerequisito:** FASE 0 completada.

| # | Tarea | Estado | Responsable | Notas |
|---|-------|--------|-------------|-------|
| 1.1 | Crear modelo `PurchaseInvoice` en Pydantic | 🟢 | Claude (Opus 4.6) | 497 líneas, 33 campos, Pydantic v2 |
| 1.2 | Crear modelo `PurchaseInvoiceItem` | 🟢 | Claude (Opus 4.6) | 13 campos con validador de totales |
| 1.3 | Crear enum `PurchaseDocumentType` | 🟢 | Claude (Opus 4.6) | 9 valores verificados por test |
| 1.4 | Crear modelo `SupplierInfo` | 🟢 | Claude (Opus 4.6) | name requerido + 9 opcionales |
| 1.5 | Agregar campo `raw_data: Optional[dict]` a PurchaseInvoice | 🟢 | Claude (Opus 4.6) | JSON original preservado sin pérdida |
| 1.6 | Validadores del modelo (totales, IVA, fechas) | 🟢 | Claude (Opus 4.6) | 4 validadores, WARNING no ERROR |
| 1.7 | Tests unitarios del modelo (>=70% cobertura) | 🟢 | Claude (Opus 4.6) | 24 tests, 98.47% cobertura |

---

## FASE 2: Detector de Formato (FormatDetector)

> **Objetivo:** Identificar automáticamente el formato/variante de cada JSON.
> **Prerequisito:** FASE 1 completada.

| # | Tarea | Estado | Responsable | Notas |
|---|-------|--------|-------------|-------|
| 2.1 | Crear clase `FormatDetector` | 🟢 | Claude (Opus 4.6) | 496 líneas, fingerprinting + scoring |
| 2.2 | Implementar fingerprinting por estructura JSON | 🟢 | Claude (Opus 4.6) | 4 fingerprints, pesos 40/30/10/20 |
| 2.3 | Implementar detección de versión DTE | 🟢 | Claude (Opus 4.6) | Via nested_checks en identificacion |
| 2.4 | Crear enum `DetectedFormat` con todos los formatos | 🟢 | Claude (Opus 4.6) | 6 valores incluyendo PDF_EXTRACTED |
| 2.5 | Implementar fallback para formatos desconocidos | 🟢 | Claude (Opus 4.6) | UNKNOWN cuando score < 0.50 |
| 2.6 | Tests unitarios (>=70% cobertura) | 🟢 | Claude (Opus 4.6) | 18 tests, 94.35% cobertura |
| 2.7 | Integrar con muestras reales cuando estén disponibles | ⏸️ | — | Depende de datos reales de proveedores |

---

## FASE 3: Mappers y Registro (MapperRegistry)

> **Objetivo:** Convertir cada formato detectado al modelo canónico.
> **Prerequisito:** FASE 1 + FASE 2 completadas.

| # | Tarea | Estado | Responsable | Notas |
|---|-------|--------|-------------|-------|
| 3.1 | Crear interfaz `BaseMapper` (clase abstracta) | 🔴 | — | Contrato para todos los mappers |
| 3.2 | Crear `MapperRegistry` (registro central) | 🔴 | — | Patrón Registry + Strategy |
| 3.3 | Implementar `DTEStandardMapper` | 🔴 | — | Formato estándar de Hacienda |
| 3.4 | Implementar `GenericFallbackMapper` | 🔴 | — | Heurísticas para formatos desconocidos |
| 3.5 | Tests unitarios por mapper (>=70%) | 🔴 | — | Un test file por mapper |
| 3.6 | Agregar mappers adicionales según datos reales | 🔴 | — | Se irán sumando mappers |

---

## FASE 4: Validador de Compras

> **Objetivo:** Verificar integridad de datos normalizados.
> **Prerequisito:** FASE 3 completada.

| # | Tarea | Estado | Responsable | Notas |
|---|-------|--------|-------------|-------|
| 4.1 | Crear `PurchaseValidator` | 🔴 | — | `backend/src/core/purchases/validator.py` |
| 4.2 | Validación de totales (items vs resumen) | 🔴 | — | Con tolerancia configurable |
| 4.3 | Detección de facturas duplicadas | 🔴 | — | Por número de control + emisor |
| 4.4 | Validación de cálculos IVA | 🔴 | — | 13% estándar El Salvador |
| 4.5 | Reporte de validación (warnings, errors) | 🔴 | — | Mismo patrón que JSONProcessor |
| 4.6 | Tests unitarios (>=70%) | 🔴 | — | Casos válidos e inválidos |

---

## FASE 5: API y Servicios Backend

> **Objetivo:** Crear endpoints para upload, procesamiento y descarga.
> **Prerequisito:** FASES 1-4 completadas.

| # | Tarea | Estado | Responsable | Notas |
|---|-------|--------|-------------|-------|
| 5.1 | Crear router `/api/purchases/upload` | 🔴 | — | Mismo patrón que `/api/upload` |
| 5.2 | Crear router `/api/purchases/process` | 🔴 | — | Con opciones de formato y columnas |
| 5.3 | Crear router `/api/purchases/status/{job_id}` | 🔴 | — | Reutilizar JobService |
| 5.4 | Crear router `/api/purchases/download/{job_id}` | 🔴 | — | Reutilizar descarga existente |
| 5.5 | Crear `PurchaseProcessorService` | 🔴 | — | Orquesta: detect → map → validate → export |
| 5.6 | Crear schemas Pydantic para request/response | 🔴 | — | `backend/src/api/schemas/purchases.py` |
| 5.7 | Tests de integración API (>=70%) | 🔴 | — | `backend/tests/api/test_purchases.py` |

---

## FASE 6: Exportador Configurable

> **Objetivo:** Generar reportes con columnas activables/desactivables.
> **Prerequisito:** FASE 5 completada.

| # | Tarea | Estado | Responsable | Notas |
|---|-------|--------|-------------|-------|
| 6.1 | Crear `PurchaseExporter` extendiendo ExcelExporter | 🔴 | — | Herencia o composición |
| 6.2 | Implementar sistema de columnas configurables | 🔴 | — | Activar/desactivar sin perder datos |
| 6.3 | Definir perfiles de columnas predeterminados | 🔴 | — | "Básico", "Completo", "Contador" |
| 6.4 | Exportación Excel con columnas dinámicas | 🔴 | — | Resumen + detalle por factura |
| 6.5 | Exportación CSV con columnas dinámicas | 🔴 | — | Mismo conjunto configurable |
| 6.6 | Exportación PDF con columnas dinámicas | 🔴 | — | Layout adaptativo |
| 6.7 | Exportación JSON completa (siempre todos los datos) | 🔴 | — | JSON nunca pierde columnas |
| 6.8 | Tests unitarios de exportación (>=70%) | 🔴 | — | Verificar cada formato |

---

## FASE 7: Soporte PDF

> **Objetivo:** Extraer datos de facturas que llegan como PDF.
> **Prerequisito:** FASE 1 completada (modelo canónico).

| # | Tarea | Estado | Responsable | Notas |
|---|-------|--------|-------------|-------|
| 7.1 | Investigar PDFs de muestra (estructura típica) | 🔴 | — | Depende de muestras reales |
| 7.2 | Implementar extractor texto de PDF (pdf-parse/PyMuPDF) | 🔴 | — | Para PDFs digitales |
| 7.3 | Implementar parser de texto a datos estructurados | 🔴 | — | Regex + heurísticas |
| 7.4 | Crear `PDFExtractedMapper` | 🔴 | — | Registrar en MapperRegistry |
| 7.5 | Tests unitarios (>=70%) | 🔴 | — | Con PDFs de prueba |

---

## FASE 8: Frontend — Modo Compras

> **Objetivo:** Interfaz de usuario para subir y procesar facturas de compra.
> **Prerequisito:** FASES 5-6 completadas.

| # | Tarea | Estado | Responsable | Notas |
|---|-------|--------|-------------|-------|
| 8.1 | Agregar toggle/tab Ventas ←→ Compras | 🔴 | — | En la navegación principal |
| 8.2 | Crear vista de upload para compras | 🔴 | — | Reutilizar DropzoneUpload |
| 8.3 | Crear panel de configuración de columnas | 🔴 | — | Checkboxes para activar/desactivar |
| 8.4 | Crear vista de progreso de procesamiento | 🔴 | — | Reutilizar job status polling |
| 8.5 | Crear vista de descarga de resultados | 🔴 | — | Con selector de formato |
| 8.6 | Tests de componentes (Vitest, >=70%) | 🔴 | — | `frontend/tests/` |
| 8.7 | Tests E2E del flujo completo (Playwright) | 🔴 | — | `e2e/tests/purchases.spec.ts` |

---

## FASE 9: Integración y Polish

> **Objetivo:** Pruebas end-to-end completas, documentación final.
> **Prerequisito:** TODAS las fases anteriores.

| # | Tarea | Estado | Responsable | Notas |
|---|-------|--------|-------------|-------|
| 9.1 | Test E2E flujo completo: upload → process → download | 🔴 | — | Con datos reales |
| 9.2 | Test de rendimiento con 10,000 facturas | 🔴 | — | Benchmark de tiempo |
| 9.3 | Verificar cobertura total >=70% | 🔴 | — | pytest --cov + vitest |
| 9.4 | Actualizar CI/CD pipeline para incluir compras | 🔴 | — | GitHub Actions |
| 9.5 | Documentación de usuario final | 🔴 | — | Cómo usar el modo Compras |
| 9.6 | Actualizar `00_README.md` del caso a 🟢 | 🔴 | — | Cuando todo esté verificado |

---

## Resumen de Progreso

| Fase | Descripción | Tareas | Completadas | Estado |
|------|-------------|--------|-------------|--------|
| 0 | Documentación Arquitectónica | 14 | 14 | 🟢 |
| 1 | Modelo de Datos | 7 | 7 | 🟢 |
| 2 | Detector de Formato | 7 | 6 | 🟢 |
| 3 | Mappers y Registro | 6 | 0 | 🔴 |
| 4 | Validador de Compras | 6 | 0 | 🔴 |
| 5 | API y Servicios | 7 | 0 | 🔴 |
| 6 | Exportador Configurable | 8 | 0 | 🔴 |
| 7 | Soporte PDF | 5 | 0 | 🔴 |
| 8 | Frontend UI | 7 | 0 | 🔴 |
| 9 | Integración y Polish | 6 | 0 | 🔴 |
| **TOTAL** | | **73** | **27** | **🟡** |

---

> **Nota:** Este TODO list se actualiza cada vez que se completa una tarea.
> Formato de commit para actualizaciones: `FASE-X MODULO: descripción clara de lo completado`

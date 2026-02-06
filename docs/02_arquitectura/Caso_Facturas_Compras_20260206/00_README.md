# Caso: Sistema de Procesamiento Inteligente de Facturas de Compra

> **⚠️ ANTES DE EMPEZAR:** Lee [EL_PUNTO_DE_PARTIDA](../../EL_PUNTO_DE_PARTIDA_by_SamuelERS.md) para identificar tu rol y qué documentos te corresponden leer según tu misión.

### Rol Requerido para este Documento

| Rol | Misión aquí |
|-----|-------------|
| 📋 **Director de Proyecto** | Mantener actualizado el estado del caso, coordinar fases |
| ✍️ **Documentador de Elite** | Verificar estructura, actualizar estados, prevenir duplicación |

---

| Campo | Valor |
|-------|-------|
| **Fecha inicio** | 2026-02-06 |
| **Fecha actualización** | 2026-02-06 |
| **Estado** | 🟡 En progreso |
| **Prioridad** | Alta |
| **Responsable** | Claude (Documentador Elite) + SamuelERS (Director) |

---

## Resumen

Sistema modular para procesar facturas de compra (gastos de la empresa) provenientes de múltiples proveedores. Cada proveedor emite facturas DTE de El Salvador en formato JSON, pero con variaciones en la estructura según su sistema ERP. El sistema debe detectar inteligentemente el formato, normalizar los datos a un modelo canónico unificado, y generar reportes consolidados — sin perder ni un solo dato.

---

## Problema que Resolvemos

El sistema actual procesa **facturas de venta** (las que la empresa emite a sus clientes). Funciona perfecto y **no se toca**.

Ahora necesitamos procesar **facturas de compra** (las que los proveedores le emiten a la empresa). El reto: cada proveedor usa un sistema diferente que genera JSONs con estructuras distintas, aunque todos siguen el estándar DTE de El Salvador.

---

## Documentos en este Caso

| # | Archivo | Descripción |
|---|---------|-------------|
| 01 | `01_TODO_LIST_PRINCIPAL_(Lista-Maestra-de-Tareas).md` | Lista maestra de todas las tareas del proyecto. Control central. |
| 02 | `02_VISION_Y_ALCANCE_(Que-Vamos-a-Construir-y-Por-Que).md` | Qué es el sistema, por qué lo necesitamos, qué resuelve. |
| 03 | `03_ARQUITECTURA_GENERAL_(Diseño-del-Motor-de-Procesamiento).md` | Diseño completo del pipeline: entrada, detección, mapeo, validación, salida. |
| 04 | `04_MODELO_CANONICO_(Estructura-Universal-de-Factura-de-Compra).md` | Definición del modelo `PurchaseInvoice` — el corazón de datos del sistema. |
| 05 | `05_DETECTOR_FORMATO_(Sistema-Inteligente-de-Identificacion).md` | Cómo el sistema identifica automáticamente el formato de cada JSON. |
| 06 | `06_MAPPERS_Y_REGISTRO_(Convertidores-de-Formato-por-Proveedor).md` | Convertidores que transforman cada formato al modelo canónico. |
| 07 | `07_VALIDADOR_COMPRAS_(Verificacion-y-Calidad-de-Datos).md` | Reglas de validación: totales, duplicados, campos requeridos. |
| 08 | `08_API_Y_SERVICIOS_(Rutas-del-Backend-para-Compras).md` | Endpoints, servicios y flujo de datos en el backend. |
| 09 | `09_EXPORTADOR_COMPRAS_(Reportes-Configurables-sin-Perder-Datos).md` | Exportación con columnas configurables. Cero pérdida de datos. |
| 10 | `10_SOPORTE_PDF_(Extraccion-de-Datos-desde-PDF).md` | Cómo extraer datos de facturas que llegan en formato PDF. |
| 11 | `11_FRONTEND_UI_(Interfaz-de-Usuario-para-Compras).md` | Diseño de la interfaz: modo Compras, configuración de columnas. |
| 12 | `12_TESTING_Y_CICD_(Pruebas-y-Despliegue-Continuo).md` | Estrategia de testing (>=70% cobertura) y pipeline CI/CD. |
| 13 | `13_REGLAS_NO_NEGOCIABLES_(Normas-Obligatorias-para-Cada-Agente).md` | Reglas que TODO agente debe cumplir: commits, código, documentación. |

---

## Compatibilidad con el Sistema Existente

- **Backend:** Extiende FastAPI existente — nuevos endpoints `/api/purchases/*`
- **Frontend:** Nuevo modo "Compras" en la UI existente — toggle Ventas/Compras
- **Modelos:** Nuevo `PurchaseInvoice` independiente del `Invoice` actual
- **Exportador:** Reutiliza `ExcelExporter` con columnas configurables
- **Tests:** Misma estructura pytest + Playwright, mismos umbrales de cobertura
- **CI/CD:** Se extiende el pipeline existente — no se reescribe

---

## Regla de Oro

> **"No toleramos la pérdida de datos."**
>
> Toda la información de cada factura se almacena. El usuario decide qué columnas ver u ocultar, pero los datos siempre están completos en el sistema.

---

## Resultado

🟡 En progreso — Guía arquitectónica completada. Pendiente implementación.

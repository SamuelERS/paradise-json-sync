# 🎯 Visión y Alcance — Sistema de Facturas de Compra

> **⚠️ ANTES DE EMPEZAR:** Lee [EL_PUNTO_DE_PARTIDA](../../EL_PUNTO_DE_PARTIDA_by_SamuelERS.md) para identificar tu rol y qué documentos te corresponden leer según tu misión.

> **¿Qué es esto?** Este documento explica QUÉ vamos a construir, POR QUÉ lo necesitamos, y QUÉ NO vamos a tocar. Es el punto de partida para cualquier persona que se sume al proyecto.

### Roles Requeridos para este Documento

| Rol | Misión aquí |
|-----|-------------|
| 🧑‍🍳 **Chef Arquitecto** | Validar que la visión es técnicamente viable y alineada |
| 📋 **Director de Proyecto** | Entender alcance antes de crear órdenes de trabajo |
| 🧑‍🍳 **Todos los Agentes** | Lectura obligatoria — entender QUÉ se construye antes de CÓMO |

---

## 1. El Problema (En Palabras Simples)

Imagina que eres dueño de una tienda. Cada día, tus proveedores te envían facturas: el que te vende pan, el de la leche, el del café. Cada uno usa un sistema diferente para generar su factura.

- El panadero usa un sistema que pone el total arriba
- El lechero usa otro que pone el total abajo
- El cafetero usa uno que anida todo dentro de subcategorías

**Todas son facturas válidas**, pero cada una está "empaquetada" de forma diferente. Si quieres hacer un reporte unificado para tu contador, necesitas un sistema que entienda **todas** estas variaciones y las unifique.

**Eso es exactamente lo que vamos a construir.**

---

## 2. ¿Qué Existe Hoy? (Y Qué NO Tocamos)

### Lo que ya funciona (NO SE MODIFICA):

```
┌──────────────────────────────────────────────────────┐
│  SISTEMA ACTUAL — Facturas de VENTA                   │
│                                                       │
│  Flujo: Correo → Descarga JSON → Upload → Proceso    │
│         → Reportes Excel/CSV/PDF/JSON para Contador   │
│                                                       │
│  Estado: ✅ PERFECTO — No se toca                     │
│                                                       │
│  Archivos clave:                                      │
│  - backend/src/models/invoice.py                      │
│  - backend/src/core/json_processor.py                 │
│  - backend/src/core/excel_exporter.py                 │
│  - backend/src/api/routes/ (todos los endpoints)      │
│  - frontend/src/ (toda la UI actual)                  │
└──────────────────────────────────────────────────────┘
```

### Lo que vamos a construir (NUEVO):

```
┌──────────────────────────────────────────────────────┐
│  SISTEMA NUEVO — Facturas de COMPRA                   │
│                                                       │
│  Flujo: Upload JSON/PDF de proveedores → Detección    │
│         automática de formato → Normalización          │
│         → Validación → Reportes Configurables          │
│                                                       │
│  Estado: 🔴 Por construir                             │
│                                                       │
│  Archivos nuevos (propuestos):                        │
│  - backend/src/models/purchase_invoice.py             │
│  - backend/src/core/purchases/                        │
│  - backend/src/api/routes/purchases.py                │
│  - frontend/src/pages/Purchases.jsx                   │
└──────────────────────────────────────────────────────┘
```

---

## 3. Contexto Técnico Clave

### ¿Por qué JSON y no XML?

**El Salvador es el único país de Latinoamérica que usa JSON** para su facturación electrónica (DTE — Documento Tributario Electrónico). Todos los demás países (México, Costa Rica, Panamá) usan XML.

Esto significa:
- Las facturas de compra son **DTE JSON de El Salvador** (formato de Hacienda/MH)
- El formato base es el mismo esquema DTE para todos
- **El reto real**: cada sistema ERP del proveedor serializa el DTE con sus propias variaciones

### Variaciones Reales que Enfrentamos

| Variación | Ejemplo Real |
|-----------|-------------|
| Nombres de campos diferentes | `totalPagar` vs `montoTotalOperacion` vs `totalAPagar` |
| Estructuras anidadas | Items en `cuerpoDocumento` vs `detalle` vs `lineas` |
| Campos presentes/ausentes | Algunos incluyen `apendice`, otros no |
| Formatos de fecha | `2026-02-06` vs `06/02/2026` vs `06-02-2026` |
| IVA incluido vs excluido | En precio unitario o calculado aparte |
| Versiones de esquema | v1, v2, v3 del DTE con campos diferentes |
| PDF con datos embebidos | Facturas como PDF (no JSON) |

---

## 4. Requisitos Funcionales

### 4.1 Detección Inteligente de Formato
- El sistema **identifica automáticamente** el formato de cada JSON
- Sin configuración manual por proveedor
- Si no reconoce el formato, intenta mapeo genérico por heurísticas

### 4.2 Normalización Universal
- Convierte CUALQUIER formato detectado a un modelo canónico unificado
- El modelo canónico tiene TODOS los campos posibles (superset)
- Campos no encontrados quedan como `null`, nunca se inventan datos

### 4.3 Cero Pérdida de Datos
- **TODA** la información del JSON original se almacena
- El usuario configura qué columnas VER en los reportes
- Activar/desactivar columnas, pero los datos siempre están completos
- Exportación JSON siempre incluye todos los campos

### 4.4 Reportes Consolidados
- Mismos formatos de salida: Excel, CSV, PDF, JSON
- Columnas configurables con perfiles predeterminados
- Resumen estadístico por proveedor, fecha, tipo

### 4.5 Soporte PDF
- Facturas que llegan como PDF (no JSON)
- Fase 1: PDFs digitales (texto seleccionable)
- Fase 2 (futuro): PDFs escaneados (OCR)

### 4.6 Rendimiento
- Capacidad para 10,000 facturas por procesamiento
- Procesamiento asíncrono (mismo patrón de jobs actual)

---

## 5. Requisitos No Funcionales

| Requisito | Estándar |
|-----------|----------|
| Cobertura de tests | >= 70% (mínimo) en todo componente nuevo |
| CI/CD | Compatible con GitHub Actions existente |
| Máximo líneas/función | 50 (según REGLAS_PROGRAMADOR) |
| Máximo líneas/archivo | 500 (según REGLAS_PROGRAMADOR) |
| Tipos | Zero `any` — todo tipado estricto |
| Documentación | Bilingüe (español/inglés en código) |
| Seguridad | Validación de inputs, sin inyección de datos |
| Retrocompatibilidad | No romper nada del sistema de ventas |

---

## 6. Lo Que NO Está en el Alcance

Para ser claros y evitar scope creep:

| Excluido | Razón |
|----------|-------|
| Modificar sistema de ventas | Funciona perfecto, no se toca |
| Base de datos persistente | El sistema es de procesamiento batch, no de almacenamiento |
| Integración con correo electrónico | Las facturas se descargan manualmente |
| OCR avanzado para PDFs escaneados | Fase 2 futura, no en esta iteración |
| Soporte multi-país (México, CR) | Solo El Salvador por ahora |
| Portal de proveedores | Los proveedores no interactúan con el sistema |
| Autenticación de usuarios | No aplica en el contexto actual |

---

## 7. Criterios de Éxito

El sistema se considera exitoso cuando:

1. Puede procesar JSONs DTE de al menos 3 proveedores diferentes sin configuración manual
2. El reporte consolidado tiene la misma calidad que los reportes de ventas actuales
3. El usuario puede activar/desactivar columnas sin perder datos
4. Procesa 10,000 facturas sin errores de rendimiento
5. Cobertura de tests >= 70% en todos los componentes nuevos
6. Pipeline CI/CD pasa sin errores
7. Un desarrollador nuevo puede entender el sistema leyendo esta documentación

---

## 8. Glosario

| Término | Significado |
|---------|-------------|
| **DTE** | Documento Tributario Electrónico — estándar de facturación de El Salvador |
| **Factura de Compra** | Factura que un proveedor emite a la empresa (gasto) |
| **Factura de Venta** | Factura que la empresa emite a sus clientes (ingreso) |
| **Modelo Canónico** | Estructura de datos unificada que sirve como "idioma común" |
| **Mapper** | Convertidor que transforma un formato específico al modelo canónico |
| **Fingerprint** | Huella digital de un formato — combinación de campos que lo identifica |
| **CCF** | Comprobante de Crédito Fiscal — tipo de factura para empresas |
| **NIT** | Número de Identificación Tributaria |
| **NRC** | Número de Registro de Contribuyente |
| **IVA** | Impuesto al Valor Agregado — 13% en El Salvador |

---

> **Próximo documento:** [03_ARQUITECTURA_GENERAL](./03_ARQUITECTURA_GENERAL_(Diseño-del-Motor-de-Procesamiento).md) — Cómo funciona el motor por dentro.

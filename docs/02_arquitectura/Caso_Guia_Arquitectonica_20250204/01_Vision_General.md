# 01 - Vision General (Visión General)
# General Vision (Visión General - Qué es este proyecto y para qué sirve)

---

## Observaciones Obligatorias (Mandatory Notes)

```
TESTS REQUERIDOS: Sí - Mínimo 70% coverage
CI/CD: Compatible - Este documento define requisitos que deben validarse en pipeline
STACK: Python 3.11+ / FastAPI / React + Vite / Pandas / openpyxl / PyMuPDF
```

---

## El Problema (The Problem - Lo que queremos resolver)

### Situacion Actual (Current Situation - Cómo están las cosas hoy)

Imagina que trabajas en una empresa que genera **500 facturas al mes**. Cada factura se guarda como:
- Un archivo `.json` (con los datos)
- Un archivo `.pdf` (con la imagen de la factura)

**El dolor de cabeza:**
1. Para ver todas las facturas, tienes que abrir 500 archivos uno por uno
2. Para buscar una factura específica, puedes tardar horas
3. Para hacer un reporte, tienes que copiar y pegar datos manualmente

**Esto es como:** Tener una biblioteca donde cada libro está en una caja cerrada. Para encontrar algo, tienes que abrir todas las cajas.

### Consecuencias (Consequences - Por qué esto es malo)

| Problema | Tiempo perdido | Riesgo |
|----------|---------------|--------|
| Buscar una factura | 15-30 minutos | Frustración |
| Hacer reporte mensual | 4-8 horas | Errores de copiado |
| Verificar totales | 2-4 horas | Números incorrectos |
| Auditoría | Días enteros | Multas |

---

## La Solucion (The Solution - Lo que hace Paradise JSON Sync)

### Que Hace (What It Does - En palabras simples)

Paradise JSON Sync es como un **asistente mágico** que:

1. **Abre todos los archivos** por ti (JSONs y PDFs)
2. **Extrae la información importante** (fecha, cliente, total)
3. **Lo organiza todo** en una tabla de Excel
4. **Une los PDFs** en un solo documento

**El resultado:** En vez de 500 archivos desordenados, tienes:
- 1 Excel con todo ordenado y filtrable
- 1 PDF con todas las facturas juntas

**Esto es como:** Un bibliotecario robot que abre todas las cajas, lee los libros, y te hace un índice ordenado.

### Beneficios (Benefits - Por qué esto es bueno)

| Antes | Después | Ahorro |
|-------|---------|--------|
| 8 horas de reporte | 5 minutos | 7h 55min |
| 500 archivos | 2 archivos | 498 menos |
| Errores de copiado | Sin errores | 100% precisión |
| Búsqueda manual | Ctrl+F en Excel | Instantáneo |

---

## Funcionalidades Principales (Main Features - Las capacidades del sistema)

### 1. JSON Processor (Procesador de JSON - Lee archivos de datos)

**¿Qué es un JSON?**
Es como una ficha de información estructurada. Imagina una ficha de biblioteca:
```
Título: Don Quijote
Autor: Cervantes
Año: 1605
```

En JSON se ve así:
```json
{
  "titulo": "Don Quijote",
  "autor": "Cervantes",
  "año": 1605
}
```

**¿Qué hace el procesador?**
- [ ] Lee cientos de archivos JSON
- [ ] Extrae campos específicos (fecha, cliente, monto)
- [ ] Valida que los datos estén completos
- [ ] Genera alertas si hay problemas

**Tests requeridos:**
- [ ] Test: Procesa JSON válido correctamente
- [ ] Test: Detecta JSON inválido
- [ ] Test: Maneja archivos vacíos
- [ ] Test: Procesa múltiples archivos

### 2. Excel Exporter (Exportador de Excel - Crea tablas ordenadas)

**¿Qué hace?**
Toma todos los datos extraídos y los pone en una tabla de Excel.

**Características:**
- [ ] Columnas ordenadas (Fecha, Cliente, Producto, Total)
- [ ] Formato automático (fechas como fechas, números como números)
- [ ] Filtros activados para buscar fácil
- [ ] Totales calculados automáticamente

**Tests requeridos:**
- [ ] Test: Genera archivo Excel válido
- [ ] Test: Columnas tienen formato correcto
- [ ] Test: Totales se calculan bien
- [ ] Test: Archivos grandes (1000+ filas)

### 3. PDF Merger (Unificador de PDF - Junta documentos)

**¿Qué hace?**
Toma muchos PDFs separados y los une en uno solo.

**Características:**
- [ ] Ordena por fecha o número de documento
- [ ] Mantiene la calidad original
- [ ] Agrega marcadores para navegar fácil
- [ ] Comprime si es necesario

**Tests requeridos:**
- [ ] Test: Une 2 PDFs correctamente
- [ ] Test: Maneja PDFs con imágenes
- [ ] Test: Archivos grandes (100+ páginas)
- [ ] Test: PDFs corruptos no rompen todo

### 4. Web Interface (Interfaz Web - La pantalla que ves)

**¿Qué hace?**
Es la "cara" del programa. Donde subes archivos y ves resultados.

**Características:**
- [ ] Arrastra y suelta archivos (drag & drop)
- [ ] Barra de progreso mientras procesa
- [ ] Descarga de resultados con un clic
- [ ] Mensajes de error claros

**Tests requeridos:**
- [ ] Test: Upload de archivos funciona
- [ ] Test: Progreso se muestra correctamente
- [ ] Test: Descarga genera archivo válido
- [ ] Test: Errores se muestran claramente

---

## Requisitos del Sistema (System Requirements - Lo que necesitas para usarlo)

### Para Usuarios (For Users - Quien usa la aplicación)

| Requisito | Mínimo | Recomendado |
|-----------|--------|-------------|
| Navegador | Chrome 90+ | Chrome 120+ |
| Internet | 1 Mbps | 10 Mbps |
| Conocimientos | Saber usar internet | Conocer Excel |

### Para Desarrolladores (For Developers - Quien programa)

| Requisito | Versión | ¿Para qué? |
|-----------|---------|-----------|
| Python | 3.11+ | El cerebro del backend |
| Node.js | 18+ | Para el frontend |
| Git | Cualquiera | Control de versiones |
| VS Code | Cualquiera | Editor recomendado |

---

## Alcance del Proyecto (Project Scope - Qué sí y qué no hace)

### Que SI Hace (What It DOES)

- [x] Procesa archivos JSON de facturas
- [x] Procesa archivos PDF de facturas
- [x] Exporta a Excel (.xlsx)
- [x] Exporta a CSV (texto separado por comas)
- [x] Une PDFs en uno solo
- [x] Funciona en navegador web
- [x] Muestra progreso de procesamiento

### Que NO Hace (What It DOESN'T Do)

- [ ] NO edita facturas (solo las lee)
- [ ] NO se conecta a sistemas de facturación externos
- [ ] NO guarda datos en la nube
- [ ] NO envía emails
- [ ] NO genera facturas nuevas

---

## Usuarios Objetivo (Target Users - Para quién es esto)

### Primario: Contador o Administrativo

**Perfil:**
- Maneja facturas diariamente
- Usa Excel para reportes
- No es programador

**Necesidad:**
- Ahorrar tiempo en reportes
- Evitar errores de copiado
- Tener todo organizado

### Secundario: Auditor

**Perfil:**
- Revisa documentación contable
- Necesita acceso rápido a facturas
- Busca discrepancias

**Necesidad:**
- Ver todas las facturas juntas
- Buscar por filtros (fecha, monto)
- Verificar totales

---

## Metricas de Exito (Success Metrics - Cómo sabemos que funciona)

| Métrica | Objetivo | Cómo medimos |
|---------|----------|--------------|
| Tiempo de procesamiento | < 1 seg por archivo | Logs del sistema |
| Errores de procesamiento | < 1% | Archivos fallidos / total |
| Precisión de datos | 100% | Comparación manual |
| Satisfacción de usuario | > 4/5 estrellas | Feedback directo |

---

## Diagrama Conceptual (Conceptual Diagram - El dibujo general)

```
┌─────────────────────────────────────────────────────────────────┐
│                     PARADISE JSON SYNC                          │
│           (El asistente que organiza facturas)                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ENTRADA                PROCESO                  SALIDA        │
│   (Input)               (Process)                (Output)       │
│                                                                 │
│  ┌─────────┐         ┌─────────────┐          ┌─────────────┐  │
│  │ Archivos│         │   BACKEND   │          │   Excel     │  │
│  │  .json  │ ──────► │  (Python)   │ ───────► │   (.xlsx)   │  │
│  │         │         │             │          │             │  │
│  └─────────┘         │  Lee datos  │          └─────────────┘  │
│                      │  Valida     │                            │
│  ┌─────────┐         │  Procesa    │          ┌─────────────┐  │
│  │ Archivos│ ──────► │  Genera     │ ───────► │   PDF       │  │
│  │  .pdf   │         │             │          │  (unificado)│  │
│  │         │         └─────────────┘          │             │  │
│  └─────────┘                │                 └─────────────┘  │
│                             │                                   │
│                      ┌──────┴──────┐                           │
│                      │  FRONTEND   │                           │
│                      │   (React)   │                           │
│                      │             │                           │
│                      │ Pantalla    │                           │
│                      │ del usuario │                           │
│                      └─────────────┘                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Proximo Documento (Next Document)

Continúa con: `02_Stack_Tecnologico.md` para conocer las herramientas que usamos.

---

**Versión:** 1.0
**Líneas:** ~250
**Cumple reglas:** Sí

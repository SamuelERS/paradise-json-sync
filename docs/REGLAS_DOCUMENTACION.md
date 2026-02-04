# 📋 REGLAS DE DOCUMENTACIÓN - PARADISE JSON SYNC

> **⚠️ ESTE ARCHIVO ES DE LECTURA OBLIGATORIA ANTES DE CREAR O MODIFICAR DOCUMENTACIÓN**
>
> Última actualización: 2025-02-04

---

## 🧠 Nuestra Filosofía: Anti-Bobos by SamuelERS

> **"Aquí somos bobos haciendo cosas geniales con tecnologías geniales como tú y nuestros agentes similares."**

Nuestro enfoque es simple: crear sistemas robustos y profesionales sin la complejidad innecesaria. La simplicidad y la comunicación directa son la base de la excelencia.

---

## 🌴 CONTEXTO DEL PROYECTO

**Paradise JSON Sync** es una herramienta para consolidar y procesar archivos `.json` y `.pdf` de facturación, generando reportes en Excel, CSV y PDF unificado.

### Stack Técnico
- **Backend:** Python 3.11+ / FastAPI
- **Frontend:** React + Vite (PWA)
- **Procesamiento:** Pandas, openpyxl, PyMuPDF

---

## 🚨 REGLAS FUNDAMENTALES

### 1. NO CREAR MONOLITOS
- **Máximo 500 líneas por documento**
- Si un documento crece más, dividirlo en módulos
- Cada documento debe tener UN propósito claro

### 2. NO CREAR DOCUMENTOS SUELTOS EN RAÍZ
- **PROHIBIDO** crear archivos `.md` directamente en `docs/`
- Todo documento nuevo va dentro de una carpeta `Caso_*`
- Excepciones: `README.md`, `REGLAS_DOCUMENTACION.md`

### 3. ESTRUCTURA MODULAR OBLIGATORIA
- Un problema = Una carpeta `Caso_*`
- Dentro de cada caso: documentos pequeños y específicos
- Usar prefijos numéricos: `01_`, `02_`, etc.

### 4. ROL DEL DOCUMENTADOR (IA O HUMANO)
- ✅ **Mantener orden:** Verificar estructura de carpetas y convenciones
- ✅ **Actualizar estados:** Mantener `00_README.md` de cada caso actualizado
- ✅ **Prevenir duplicación:** Auditar y consolidar información repetida
- ✅ **Eliminar irrelevancia:** Remover información obsoleta o innecesaria

---

## 📁 ESTRUCTURA DE CARPETAS

```
docs/
├── 📋 REGLAS_DOCUMENTACION.md    ← ESTE ARCHIVO (leer primero)
├── 📖 README.md                   ← Índice general
│
├── 01_guias/                      ← Guías de uso del sistema
│   └── Caso_[Nombre]_[YYYYMMDD]/
│
├── 02_arquitectura/               ← Documentación técnica
│   └── Caso_[Nombre]_[YYYYMMDD]/
│
├── 03_api/                        ← Documentación de API FastAPI
│   └── Caso_[Nombre]_[YYYYMMDD]/
│
├── 04_desarrollo/                 ← Para desarrolladores
│   └── Caso_[Nombre]_[YYYYMMDD]/
│
├── 05_operaciones/                ← Despliegue y mantenimiento
│   └── Caso_[Nombre]_[YYYYMMDD]/
│
├── _plantillas/                   ← Plantillas para nuevos documentos
│
└── _archivo/                      ← Casos antiguos archivados
    └── YYYY/
```

---

## 📝 CONVENCIÓN DE NOMBRES

### Carpetas de Caso
```
Caso_[NombreDescriptivo]_[YYYYMMDD]/
```

**Ejemplos para Paradise JSON Sync:**
- `Caso_Procesador_JSON_20250204/`
- `Caso_Exportador_Excel_20250204/`
- `Caso_Fusion_PDF_20250204/`
- `Caso_Dropzone_Upload_20250204/`

### Archivos dentro de Caso
```
[NN]_[NombreDescriptivo].md
```

**Ejemplos:**
- `00_README.md` ← Obligatorio
- `01_Diagnostico.md`
- `02_Solucion.md`
- `03_Verificacion.md`

---

## 🗣️ COMUNICACIÓN VISUAL: USO DE EMOJIS

| Emoji | Significado | Uso |
|---|---|---|
| ⚠️ | **Advertencia** | Riesgo o cambio importante |
| 🚧 | **En Construcción** | Trabajo pesado en progreso |
| 🔍 | **En Investigación** | Diagnóstico activo |
| ✅ | **Completado** | Tarea o módulo finalizado |
| ❌ | **Rechazado / Error** | Prueba fallida o prohibido |
| 🏁 | **Caso Finalizado** | Caso completado y verificado |
| 🔴 | **Pendiente** | No iniciado o bloqueado |
| 🟡 | **En Progreso** | Trabajo activo |
| 🟢 | **Completado** | Resuelto y verificado |

---

## 📊 ESTADO DE CASOS

Cada carpeta `Caso_*` DEBE tener `00_README.md`:

```markdown
# Caso: [Nombre del Problema]

| Campo | Valor |
|-------|-------|
| **Fecha inicio** | YYYY-MM-DD |
| **Fecha actualización** | YYYY-MM-DD |
| **Estado** | 🔴 Pendiente / 🟡 En progreso / 🟢 Completado |
| **Prioridad** | Alta / Media / Baja |
| **Responsable** | [Nombre o IA] |

## Resumen
[Descripción breve en 2-3 líneas]

## Documentos en este caso
- `01_*.md` - [Descripción]

## Resultado
[Solo si está completado]
```

---

## 🤖 INSTRUCCIONES PARA IAs

### Al INICIAR una sesión:
1. Leer `docs/REGLAS_DOCUMENTACION.md`
2. Verificar si existe un `Caso_*` relacionado
3. Si existe → Actualizar documentos existentes
4. Si no existe → Crear nuevo `Caso_*`

### Al CREAR documentación:
1. **NUNCA** crear archivos sueltos en `docs/`
2. Crear carpeta `Caso_[Nombre]_[YYYYMMDD]/`
3. Crear `00_README.md` con estado
4. Máximo 500 líneas por documento

### Al FINALIZAR:
1. Actualizar `00_README.md` del caso
2. Si completado → Cambiar estado a 🟢

---

## 📚 CATEGORÍAS PARA PARADISE JSON SYNC

| Carpeta | Qué va aquí |
|---------|-------------|
| `01_guias/` | Cómo usar la app, troubleshooting |
| `02_arquitectura/` | Diseño técnico, flujo de datos |
| `03_api/` | Endpoints FastAPI, schemas |
| `04_desarrollo/` | Testing, contribución, pendientes |
| `05_operaciones/` | Deploy en Render/SiteGround |

---

## ✅ CHECKLIST ANTES DE DOCUMENTAR

- [ ] ¿Leí `REGLAS_DOCUMENTACION.md`?
- [ ] ¿Busqué si existe un `Caso_*` relacionado?
- [ ] ¿El documento va en una carpeta `Caso_*`?
- [ ] ¿Tiene menos de 500 líneas?
- [ ] ¿Creé/actualicé el `00_README.md` del caso?

---

**Versión:** 1.0
**Proyecto:** Paradise JSON Sync
**Creado:** 2025-02-04
**Propósito:** Estandarizar documentación del proyecto

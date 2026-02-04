# 🌴 Paradise JSON Sync

> Herramienta interna para consolidar y procesar múltiples archivos `.json` y `.pdf` generados desde sistemas de facturación, facilitando procesos contables y documentales.

![Status](https://img.shields.io/badge/status-en%20desarrollo-yellow)
![Python](https://img.shields.io/badge/python-3.11+-blue)
![React](https://img.shields.io/badge/react-18+-blue)
![License](https://img.shields.io/badge/license-Privado-red)

---

## 🎯 Objetivo

Diseñar una solución capaz de procesar archivos `.json` y `.pdf` almacenados en carpetas, consolidando la información sin pérdida de datos y generando salidas organizadas en:

- **Excel (.xlsx)**
- **CSV (.csv)**
- **PDF unificado**

---

## 📂 Estructura del Proyecto

```
paradise-json-sync/
├── backend/          # API REST en FastAPI (Python)
├── frontend/         # PWA con React + Vite
├── .gitignore
└── README.md
```

---

## ✅ Funcionalidades Principales

### 1. Procesamiento de archivos `.json`
- Lectura masiva de archivos JSON (500+)
- Extracción de campos clave: fecha, documento, cliente, productos, totales
- Consolidación en Excel y CSV con trazabilidad por archivo origen

### 2. Procesamiento de archivos `.pdf`
- Unificación de múltiples PDFs en un documento consolidado
- Organización estructurada por fecha o número de documento

### 3. Validaciones
- Evitar pérdida de información
- Detección de archivos duplicados
- Generación de resumen post-procesamiento

---

## 🧠 Stack Técnico

### Backend
- **Python 3.11+** – Lenguaje base
- **FastAPI** – Framework API REST
- **Pandas** – Procesamiento de datos
- **openpyxl / xlsxwriter** – Generación Excel
- **PyMuPDF / PyPDF2** – Manipulación PDF

### Frontend
- **React.js + Vite** – Framework moderno
- **PWA** – Instalable, offline-ready
- **Tailwind CSS** – Diseño responsive
- **React Dropzone** – Carga de archivos

---

## 📊 Modelo de Datos (Excel Output)

| Campo           | Fuente JSON                        |
|-----------------|------------------------------------|
| Fecha Emisión   | `identificacion.fecEmi`            |
| Hora Emisión    | `identificacion.horEmi`            |
| Nº Documento    | `apendice["N° Documento"]`         |
| Nº Control      | `identificacion.numeroControl`     |
| Cliente         | `receptor.nombre`                  |
| Producto        | `cuerpoDocumento[].descripcion`    |
| Cantidad        | `cuerpoDocumento[].cantidad`       |
| Total a Pagar   | `resumen.totalPagar`               |
| Archivo Origen  | Nombre del archivo `.json`         |

---

## 🚀 Despliegue Previsto

- **Frontend:** SiteGround (estático)
- **Backend:** Render / Railway / Fly.io

---

## 🛠️ Estado Actual

- [x] Estructura base del proyecto
- [ ] Implementación backend (FastAPI endpoints)
- [ ] Implementación frontend (React UI)
- [ ] Integración completa
- [ ] Testing y validación
- [ ] Despliegue en producción

---

## 📌 Requisitos del Sistema

- **Python:** 3.11 o superior
- **Node.js:** 18 o superior
- **Compatible con:** Windows, macOS, Linux

---

## 📄 Licencia

Proyecto privado – Paradise System Labs © 2025

---

## 👥 Equipo

Desarrollado internamente para optimizar procesos contables y documentales.

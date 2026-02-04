# 🌴 Paradise JSON Sync

> **Si no puedes explicarlo de forma simple, es que no lo has entendido bien.**
> — Nuestra filosofía de desarrollo

![Status](https://img.shields.io/badge/status-en%20desarrollo-yellow)
![Python](https://img.shields.io/badge/python-3.11+-blue)
![React](https://img.shields.io/badge/react-18+-blue)
![License](https://img.shields.io/badge/license-Privado-red)

---

## 💡 Nuestra Filosofía: Simple para Todos

En Paradise System Labs creemos que:

> **"Si un niño de 12 años no puede entenderlo, entonces nosotros tampoco lo hemos entendido bien."**

Por eso toda nuestra documentación y código sigue estas reglas:
- Explicamos las cosas como si fuera para alguien que nunca las ha visto
- Usamos ejemplos del mundo real (cocina, cajones, construcción)
- Si algo suena complicado, lo simplificamos hasta que sea claro

---

## 🎯 ¿Qué es Paradise JSON Sync? (Explicación Simple)

**El problema:**
Imagina que tienes 500 facturas guardadas en tu computadora. Cada factura es un archivo separado. Si quisieras ver todas juntas, tendrías que abrir una por una. ¡Eso tomaría horas!

**La solución:**
Paradise JSON Sync es como un asistente que:
1. Abre todas las facturas por ti (archivos `.json`)
2. Las junta en una sola tabla de Excel
3. También puede unir todos los PDFs en un solo documento

**Resultado:**
En vez de 500 archivos, tienes 1 Excel ordenado y 1 PDF con todo junto.

---

## 📂 ¿Cómo está organizado? (Estructura)

Piensa en el proyecto como una casa con habitaciones:

```
paradise-json-sync/
├── backend/     → La cocina (donde se procesan los archivos)
├── frontend/    → La sala (lo que ves en pantalla)
├── docs/        → La biblioteca (instrucciones y reglas)
└── README.md    → El letrero de bienvenida (este archivo)
```

| Carpeta | ¿Qué es? | Ejemplo del mundo real |
|---------|----------|------------------------|
| `backend/` | El cerebro que procesa | Como un chef que cocina |
| `frontend/` | La pantalla con botones | Como el menú de un restaurante |
| `docs/` | Las instrucciones | Como un libro de recetas |

---

## ✅ ¿Qué puede hacer? (Funcionalidades)

### 1. Procesar archivos JSON
- **¿Qué hace?** Lee cientos de archivos de facturas
- **¿Cómo?** Extrae la información importante (fecha, cliente, total)
- **¿Resultado?** Una tabla de Excel con todo ordenado

### 2. Procesar archivos PDF
- **¿Qué hace?** Toma muchos PDFs separados
- **¿Cómo?** Los une en orden (por fecha o número)
- **¿Resultado?** Un solo PDF con todas las facturas

### 3. Validar que nada se pierda
- Cuenta cuántos archivos procesó
- Avisa si hay duplicados
- Muestra un resumen: "498 procesados, 2 con errores"

---

## 🧠 ¿Con qué está hecho? (Tecnología)

### El cerebro (Backend)
| Herramienta | ¿Para qué sirve? |
|-------------|------------------|
| Python | El idioma en que hablamos con la computadora |
| FastAPI | El mesero que recibe pedidos y entrega respuestas |
| Pandas | El organizador que ordena datos en tablas |
| openpyxl | El que escribe archivos Excel |
| PyMuPDF | El que une PDFs |

### La pantalla (Frontend)
| Herramienta | ¿Para qué sirve? |
|-------------|------------------|
| React | Construye la pantalla con botones |
| Vite | Hace que cargue rápido |
| Tailwind | Le da colores y estilo bonito |
| Dropzone | Permite arrastrar archivos con el mouse |

---

## 📊 ¿Qué información extrae? (Datos)

De cada factura JSON, sacamos:

| Dato | ¿Qué es? | Ejemplo |
|------|----------|---------|
| Fecha | Cuándo se hizo la factura | 2025-01-15 |
| Documento | Número de la factura | CFCJ2000000149 |
| Cliente | A quién se le vendió | Juan Pérez |
| Producto | Qué se vendió | Comida para peces |
| Total | Cuánto costó | $10.00 |

---

## 🚀 ¿Dónde vivirá? (Despliegue)

- **Frontend:** SiteGround (donde se ve la página)
- **Backend:** Render / Railway (donde trabaja el cerebro)

---

## 🛠️ ¿En qué vamos? (Estado Actual)

| Tarea | Estado |
|-------|--------|
| ✅ Estructura de carpetas | Listo |
| 🔴 Programar el backend | Pendiente |
| 🔴 Programar el frontend | Pendiente |
| 🔴 Conectar todo | Pendiente |
| 🔴 Probar que funcione | Pendiente |
| 🔴 Publicar en internet | Pendiente |

---

## 📌 ¿Qué necesitas para usarlo?

- **Python:** versión 3.11 o más nueva
- **Node.js:** versión 18 o más nueva
- **Sistema:** Windows, Mac o Linux

---

## 📄 Licencia

Proyecto privado – Paradise System Labs © 2025

---

## 👥 ¿Quién lo hace?

Desarrollado por Paradise System Labs para hacer más fácil el trabajo contable.

> *"Hacemos cosas geniales con tecnología genial, explicadas de forma simple."*

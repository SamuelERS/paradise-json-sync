# 🧠 Backend – Paradise JSON Sync

API REST desarrollada con **FastAPI** para procesar archivos `.json` y `.pdf`.

---

## 📂 Estructura

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # Punto de entrada FastAPI
│   ├── api/
│   │   └── routes.py        # Endpoints (upload, process, export)
│   ├── services/
│   │   ├── processor.py     # Consolidación de JSON y PDF
│   │   └── exporter.py      # Generación Excel, CSV, PDF
│   ├── utils/
│   │   └── file_utils.py    # Validaciones y utilidades
│   └── models/
│       └── schemas.py       # Modelos Pydantic
├── requirements.txt
└── README.md
```

---

## 🚀 Instalación

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## ▶️ Ejecución

```bash
uvicorn app.main:app --reload
```

La API estará disponible en: `http://localhost:8000`

Documentación interactiva: `http://localhost:8000/docs`

---

## 📌 Endpoints Previstos

| Método | Endpoint            | Descripción                          |
|--------|---------------------|--------------------------------------|
| POST   | `/upload`           | Subir archivos JSON y PDF            |
| POST   | `/process`          | Procesar archivos consolidados       |
| GET    | `/export/excel`     | Descargar reporte Excel              |
| GET    | `/export/csv`       | Descargar reporte CSV                |
| GET    | `/export/pdf`       | Descargar PDF unificado              |
| GET    | `/health`           | Estado del servidor                  |

---

## 🛠️ Tecnologías

- FastAPI
- Pandas
- openpyxl / xlsxwriter
- PyMuPDF / PyPDF2
- Pydantic

---

## 📄 Licencia

Proyecto privado – Paradise System Labs © 2025

# FastAPI Application Entry Point
# Paradise JSON Sync Backend

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Paradise JSON Sync",
    description="Consolidación de archivos JSON y PDF de facturación",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok", "service": "paradise-json-sync"}


# TODO: Implementar endpoints para:
# - POST /upload - Carga de archivos JSON y PDF
# - POST /process - Procesamiento de archivos
# - GET /export/excel - Exportar a Excel
# - GET /export/csv - Exportar a CSV
# - GET /export/pdf - Exportar PDF consolidado

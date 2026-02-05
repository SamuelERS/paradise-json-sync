"""
Paradise JSON Sync API
======================

FastAPI application for invoice consolidation.
Aplicación FastAPI para consolidación de facturas.

This API provides endpoints for:
Este API provee endpoints para:
- Uploading JSON/PDF files / Subir archivos JSON/PDF
- Processing and validating invoices / Procesar y validar facturas
- Exporting to Excel/CSV/PDF / Exportar a Excel/CSV/PDF
- Monitoring job status / Monitorear estado de trabajos
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.exceptions import setup_exception_handlers
from src.api.routes import download, health, process, status, upload

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Paradise JSON Sync API",
    description="API para consolidar facturas JSON/PDF en reportes Excel / API for consolidating JSON/PDF invoices into Excel reports",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Alternative dev server
        "https://paradise-json-sync.com",  # Production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(upload.router, prefix="/api", tags=["Upload"])
app.include_router(process.router, prefix="/api", tags=["Process"])
app.include_router(status.router, prefix="/api", tags=["Status"])
app.include_router(download.router, prefix="/api", tags=["Download"])

# Setup exception handlers
setup_exception_handlers(app)

logger.info("Paradise JSON Sync API started")


@app.get("/", include_in_schema=False)
async def root():
    """
    Root endpoint redirect to docs.
    Endpoint raíz redirige a docs.
    """
    return {
        "message": "Paradise JSON Sync API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health",
    }

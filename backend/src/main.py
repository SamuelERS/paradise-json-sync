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
import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from src.api.exceptions import setup_exception_handlers
from src.api.routes import download, health, process, status, upload

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

# Configure rate limiter
# Configurar limitador de tasa
limiter = Limiter(key_func=get_remote_address)

# Create FastAPI app
app = FastAPI(
    title="Paradise JSON Sync API",
    description="API para consolidar facturas JSON/PDF en reportes Excel / API for consolidating JSON/PDF invoices into Excel reports",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS from environment variable
# CORS configurado desde variable de entorno
CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173,http://localhost:3000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept"],
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

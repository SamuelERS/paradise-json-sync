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

# IMPORTANT: Import multipart config FIRST to apply the patch before FastAPI initialization
# IMPORTANTE: Importar multipart config PRIMERO para aplicar el parche antes de inicializar FastAPI
# This enables bulk uploads of up to 10000 files (default Starlette limit is 1000)
# Esto habilita uploads masivos de hasta 10000 archivos (límite predeterminado de Starlette es 1000)
import src.core.multipart_config  # noqa: F401 - Import for side effects

import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from src.api.exceptions import setup_exception_handlers
from src.api.routes import download, health, process, purchases, status, upload
from src.core.rate_limiter import TESTING, limiter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

if TESTING:
    logger.info("Running in TESTING mode - Rate limiting DISABLED")

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
CORS_ORIGINS = [
    origin.strip() for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://localhost:3000,https://paradise-json-sync.com"
    ).split(",")
]

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
app.include_router(purchases.router, prefix="/api/purchases", tags=["Purchases"])

# Setup exception handlers (includes MultiPartException and HTTPException handlers)
# Configurar manejadores de excepciones (incluye MultiPartException y HTTPException)
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

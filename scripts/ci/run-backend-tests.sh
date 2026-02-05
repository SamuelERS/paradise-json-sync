#!/bin/bash
# Script para ejecutar tests del backend
# OT-006: Pipeline CI/CD
set -e

COVERAGE_MINIMUM=${COVERAGE_MINIMUM:-70}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "=========================================="
echo "Running Backend Tests"
echo "Coverage minimum: ${COVERAGE_MINIMUM}%"
echo "=========================================="

cd "$PROJECT_ROOT/backend"

# Crear entorno virtual si no existe
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activar entorno virtual
source venv/bin/activate

# Instalar dependencias
echo "Installing dependencies..."
pip install -r requirements.txt
pip install pytest pytest-cov pytest-asyncio

# Ejecutar tests con cobertura
echo "Running tests with coverage..."
pytest tests/ \
    --cov=app \
    --cov-report=xml \
    --cov-report=html \
    --cov-report=term-missing \
    --cov-fail-under=${COVERAGE_MINIMUM} \
    -v

echo "=========================================="
echo "Backend tests completed successfully!"
echo "=========================================="

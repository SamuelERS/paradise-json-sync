#!/bin/bash
# Script para ejecutar tests del frontend
# OT-006: Pipeline CI/CD
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "=========================================="
echo "Running Frontend Tests"
echo "=========================================="

cd "$PROJECT_ROOT/frontend"

# Instalar dependencias si es necesario
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm ci
fi

# Ejecutar tests con cobertura
echo "Running tests with coverage..."
npm run test:coverage -- --reporter=verbose

echo "=========================================="
echo "Frontend tests completed successfully!"
echo "=========================================="

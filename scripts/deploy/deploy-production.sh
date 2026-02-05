#!/bin/bash
# Script para deploy a producción
# OT-006: Pipeline CI/CD
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "=========================================="
echo "Deploying to PRODUCTION"
echo "=========================================="

# Verificar parámetros
VERSION=${1:-}
if [ -z "$VERSION" ]; then
    echo "ERROR: Version parameter required"
    echo "Usage: $0 <version> [--confirm]"
    echo "Example: $0 v1.0.0 --confirm"
    exit 1
fi

CONFIRM=${2:-}
if [ "$CONFIRM" != "--confirm" ]; then
    echo "ERROR: Confirmation required"
    echo "Usage: $0 <version> --confirm"
    exit 1
fi

# Verificar variables de entorno requeridas
if [ -z "$RENDER_API_KEY" ]; then
    echo "ERROR: RENDER_API_KEY not set"
    exit 1
fi

if [ -z "$RENDER_PRODUCTION_SERVICE_ID" ]; then
    echo "ERROR: RENDER_PRODUCTION_SERVICE_ID not set"
    exit 1
fi

echo "Deploying version: $VERSION"
echo ""

# Crear tag de versión
echo "Creating version tag..."
cd "$PROJECT_ROOT"
git tag -a "$VERSION" -m "Version $VERSION" || echo "Tag already exists"
git push origin "$VERSION" || echo "Tag already pushed"

# Deploy Backend a Render
echo "Deploying backend to Render..."
DEPLOY_RESPONSE=$(curl -s -X POST \
    "https://api.render.com/v1/services/${RENDER_PRODUCTION_SERVICE_ID}/deploys" \
    -H "Authorization: Bearer ${RENDER_API_KEY}" \
    -H "Content-Type: application/json")

echo "Backend deploy triggered: $DEPLOY_RESPONSE"

# Build Frontend
echo "Building frontend..."
cd "$PROJECT_ROOT/frontend"
npm ci
npm run build

# Deploy Frontend (si está configurado FTP)
if [ -n "$FTP_SERVER" ] && [ -n "$FTP_PRODUCTION_USERNAME" ] && [ -n "$FTP_PRODUCTION_PASSWORD" ]; then
    echo "Deploying frontend via FTP..."
    if command -v lftp &> /dev/null; then
        lftp -u "$FTP_PRODUCTION_USERNAME,$FTP_PRODUCTION_PASSWORD" "$FTP_SERVER" << EOF
mirror -R dist/ /public_html/
bye
EOF
    else
        echo "WARNING: lftp not installed, skipping FTP deploy"
    fi
else
    echo "FTP credentials not configured, skipping frontend deploy"
fi

# Smoke tests (más tiempo para producción)
echo "Running smoke tests..."
sleep 60

if [ -n "$PRODUCTION_API_URL" ]; then
    echo "Testing API health..."
    curl -f "${PRODUCTION_API_URL}/health" || echo "WARNING: API health check failed"
fi

if [ -n "$PRODUCTION_URL" ]; then
    echo "Testing frontend..."
    curl -f "${PRODUCTION_URL}" || echo "WARNING: Frontend check failed"
fi

echo "=========================================="
echo "Production deployment completed!"
echo "Version: $VERSION"
echo "=========================================="

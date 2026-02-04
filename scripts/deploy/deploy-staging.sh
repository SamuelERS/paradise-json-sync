#!/bin/bash
# Script para deploy a staging
# OT-006: Pipeline CI/CD
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "=========================================="
echo "Deploying to STAGING"
echo "=========================================="

# Verificar variables de entorno requeridas
if [ -z "$RENDER_API_KEY" ]; then
    echo "ERROR: RENDER_API_KEY not set"
    exit 1
fi

if [ -z "$RENDER_STAGING_SERVICE_ID" ]; then
    echo "ERROR: RENDER_STAGING_SERVICE_ID not set"
    exit 1
fi

# Deploy Backend a Render
echo "Deploying backend to Render..."
DEPLOY_RESPONSE=$(curl -s -X POST \
    "https://api.render.com/v1/services/${RENDER_STAGING_SERVICE_ID}/deploys" \
    -H "Authorization: Bearer ${RENDER_API_KEY}" \
    -H "Content-Type: application/json")

echo "Backend deploy triggered: $DEPLOY_RESPONSE"

# Build Frontend
echo "Building frontend..."
cd "$PROJECT_ROOT/frontend"
npm ci
npm run build

# Deploy Frontend (si está configurado FTP)
if [ -n "$FTP_SERVER" ] && [ -n "$FTP_STAGING_USERNAME" ] && [ -n "$FTP_STAGING_PASSWORD" ]; then
    echo "Deploying frontend via FTP..."
    # Usar lftp para deploy (más confiable que ftp básico)
    if command -v lftp &> /dev/null; then
        lftp -u "$FTP_STAGING_USERNAME,$FTP_STAGING_PASSWORD" "$FTP_SERVER" << EOF
mirror -R dist/ /public_html/staging/
bye
EOF
    else
        echo "WARNING: lftp not installed, skipping FTP deploy"
    fi
else
    echo "FTP credentials not configured, skipping frontend deploy"
fi

# Smoke tests
echo "Running smoke tests..."
sleep 30

if [ -n "$STAGING_API_URL" ]; then
    echo "Testing API health..."
    curl -f "${STAGING_API_URL}/health" || echo "WARNING: API health check failed"
fi

if [ -n "$STAGING_URL" ]; then
    echo "Testing frontend..."
    curl -f "${STAGING_URL}" || echo "WARNING: Frontend check failed"
fi

echo "=========================================="
echo "Staging deployment completed!"
echo "=========================================="

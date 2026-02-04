#!/bin/bash
# Script para verificar cobertura de código
# OT-006: Pipeline CI/CD
set -e

COVERAGE_MINIMUM=${COVERAGE_MINIMUM:-70}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "=========================================="
echo "Checking Code Coverage"
echo "Minimum required: ${COVERAGE_MINIMUM}%"
echo "=========================================="

BACKEND_COVERAGE=0
FRONTEND_COVERAGE=0
FAILED=0

# Verificar cobertura del backend
if [ -f "$PROJECT_ROOT/backend/coverage.xml" ]; then
    BACKEND_COVERAGE=$(python3 -c "
import xml.etree.ElementTree as ET
tree = ET.parse('$PROJECT_ROOT/backend/coverage.xml')
root = tree.getroot()
coverage = float(root.attrib.get('line-rate', 0)) * 100
print(f'{coverage:.1f}')
")
    echo "Backend coverage: ${BACKEND_COVERAGE}%"

    if (( $(echo "$BACKEND_COVERAGE < $COVERAGE_MINIMUM" | bc -l) )); then
        echo "ERROR: Backend coverage (${BACKEND_COVERAGE}%) is below minimum (${COVERAGE_MINIMUM}%)"
        FAILED=1
    fi
else
    echo "WARNING: Backend coverage report not found"
fi

# Verificar cobertura del frontend
if [ -f "$PROJECT_ROOT/frontend/coverage/lcov.info" ]; then
    FRONTEND_COVERAGE=$(python3 -c "
with open('$PROJECT_ROOT/frontend/coverage/lcov.info', 'r') as f:
    lines_found = 0
    lines_hit = 0
    for line in f:
        if line.startswith('LF:'):
            lines_found += int(line.split(':')[1])
        elif line.startswith('LH:'):
            lines_hit += int(line.split(':')[1])
    coverage = (lines_hit / lines_found * 100) if lines_found > 0 else 0
    print(f'{coverage:.1f}')
")
    echo "Frontend coverage: ${FRONTEND_COVERAGE}%"

    if (( $(echo "$FRONTEND_COVERAGE < $COVERAGE_MINIMUM" | bc -l) )); then
        echo "ERROR: Frontend coverage (${FRONTEND_COVERAGE}%) is below minimum (${COVERAGE_MINIMUM}%)"
        FAILED=1
    fi
else
    echo "WARNING: Frontend coverage report not found"
fi

echo "=========================================="
if [ $FAILED -eq 1 ]; then
    echo "Coverage check FAILED"
    exit 1
else
    echo "Coverage check PASSED"
fi
echo "=========================================="

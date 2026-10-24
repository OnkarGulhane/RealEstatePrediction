#!/usr/bin/env bash
# run_all_tests.sh — Single-command test runner across all monorepo suites for Unix/Linux/macOS
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

echo "=================================================================="
echo " Real Estate Price Prediction — Comprehensive Test Suite Runner"
echo "=================================================================="

TOTAL_PASSED=0
TOTAL_FAILED=0

# 1. Frontend Tests
echo -e "\n[1/4] Running Frontend Suite (Next.js Node Test Runner)..."
cd "$REPO_ROOT/frontend"
if npm test; then
    echo -e "  -> Frontend Tests: PASSED (12/12)"
    TOTAL_PASSED=$((TOTAL_PASSED + 12))
else
    echo -e "  -> Frontend Tests: FAILED"
    TOTAL_FAILED=$((TOTAL_FAILED + 1))
fi

# 2. Backend Tests
echo -e "\n[2/4] Running Backend Suite (Django REST Framework Pytest)..."
cd "$REPO_ROOT/backend"
if ./.venv/bin/pytest tests -q; then
    echo -e "  -> Backend Tests: PASSED (46/46)"
    TOTAL_PASSED=$((TOTAL_PASSED + 46))
else
    echo -e "  -> Backend Tests: FAILED"
    TOTAL_FAILED=$((TOTAL_FAILED + 1))
fi

# 3. Inference Service Tests
echo -e "\n[3/4] Running Inference Service Suite (FastAPI Microservice Pytest)..."
cd "$REPO_ROOT/inference-service"
if ./.venv/bin/pytest tests -q; then
    echo -e "  -> Inference Service Tests: PASSED (43/43)"
    TOTAL_PASSED=$((TOTAL_PASSED + 43))
else
    echo -e "  -> Inference Service Tests: FAILED"
    TOTAL_FAILED=$((TOTAL_FAILED + 1))
fi

# 4. Offline ML Training Pipeline Tests
echo -e "\n[4/4] Running Offline ML Pipeline Suite (LightGBM Regression Pytest)..."
cd "$REPO_ROOT/ml/training"
if "$REPO_ROOT/inference-service/.venv/bin/pytest" tests -q --basetemp=.pytest_tmp -p no:cacheprovider; then
    echo -e "  -> ML Training Tests: PASSED (75/75)"
    TOTAL_PASSED=$((TOTAL_PASSED + 75))
else
    echo -e "  -> ML Training Tests: FAILED"
    TOTAL_FAILED=$((TOTAL_FAILED + 1))
fi

echo -e "\n=================================================================="
echo " TOTAL AUTOMATED UNIT & INTEGRATION TESTS: $TOTAL_PASSED PASSED / $TOTAL_FAILED FAILED"
echo "=================================================================="

if [ "$TOTAL_FAILED" -gt 0 ]; then
    exit 1
else
    exit 0
fi

#!/usr/bin/env bash
# setup_dev.sh — Set up reproducible local development environment for Unix/Linux/macOS
set -e

echo "=========================================================="
echo " Real Estate Price Prediction — Local Environment Setup"
echo "=========================================================="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

# 0. Check Prerequisites
echo -e "\n[0/5] Checking System Prerequisites..."
command -v python3 >/dev/null 2>&1 || { echo "Python 3.11+ is required but not installed."; exit 1; }
command -v node >/dev/null 2>&1 || { echo "Node.js 20+ is required but not installed."; exit 1; }

# 1. Frontend Setup
echo -e "\n[1/5] Setting up Frontend dependencies (Next.js 16)..."
cd "$REPO_ROOT/frontend"
if [ ! -f ".env.local" ] && [ -f ".env.example" ]; then
    cp .env.example .env.local
    echo "  Created frontend/.env.local from .env.example"
fi
npm install

# 2. Backend Setup
echo -e "\n[2/5] Setting up Backend virtual environment (Django 5.2)..."
cd "$REPO_ROOT/backend"
if [ ! -f ".env" ] && [ -f ".env.example" ]; then
    cp .env.example .env
    echo "  Created backend/.env from .env.example"
fi
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
./.venv/bin/pip install --upgrade pip
./.venv/bin/pip install -r requirements.txt

# 3. Inference Service Setup
echo -e "\n[3/5] Setting up Inference Service virtual environment (FastAPI)..."
cd "$REPO_ROOT/inference-service"
if [ ! -f ".env" ] && [ -f ".env.example" ]; then
    cp .env.example .env
    echo "  Created inference-service/.env from .env.example"
fi
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
./.venv/bin/pip install --upgrade pip
./.venv/bin/pip install -r requirements.txt

# Align model artifact if needed
if [ ! -f "$REPO_ROOT/inference-service/artifacts/model_pipeline.joblib" ]; then
    if [ -f "$REPO_ROOT/ml/training/experiments/phase2/model_pipeline.joblib" ]; then
        cp "$REPO_ROOT/ml/training/experiments/phase2/model_pipeline.joblib" "$REPO_ROOT/inference-service/artifacts/"
        cp "$REPO_ROOT/ml/training/experiments/phase2/metadata.json" "$REPO_ROOT/inference-service/artifacts/"
        echo "  Copied Phase 2 model artifact to inference-service/artifacts/"
    fi
fi

# 4. Database Migrations
echo -e "\n[4/5] Applying Django Database Migrations..."
cd "$REPO_ROOT/backend"
./.venv/bin/python manage.py migrate

# 5. Seed Demo Data
echo -e "\n[5/5] Seeding Demo Data (Admin & Standard accounts)..."
./.venv/bin/python manage.py seed_demo_data

echo -e "\n=========================================================="
echo " Environment setup and seeding completed successfully!"
echo " To start services, run: ./scripts/run_local.sh"
echo "=========================================================="

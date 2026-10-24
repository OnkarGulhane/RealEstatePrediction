# setup_dev.ps1 — Set up reproducible local development environment for all services
$ErrorActionPreference = "Stop"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " Real Estate Price Prediction — Local Environment Setup" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

$RepoRoot = Split-Path -Parent $PSScriptRoot

# 0. Check Prerequisites
Write-Host "`n[0/5] Checking System Prerequisites..." -ForegroundColor Yellow
if (-not (Get-Command "python" -ErrorAction SilentlyContinue)) {
    Write-Error "Python 3.11+ is required but was not found in PATH."
}
$PythonVersion = & python --version
Write-Host "  Found: $PythonVersion" -ForegroundColor Green

if (-not (Get-Command "node" -ErrorAction SilentlyContinue)) {
    Write-Error "Node.js 20+ is required but was not found in PATH."
}
$NodeVersion = & node --version
Write-Host "  Found Node: $NodeVersion" -ForegroundColor Green

# 1. Frontend Setup
Write-Host "`n[1/5] Setting up Frontend dependencies (Next.js 16)..." -ForegroundColor Yellow
Set-Location "$RepoRoot\frontend"
if (-not (Test-Path ".env.local") -and (Test-Path ".env.example")) {
    Copy-Item ".env.example" ".env.local"
    Write-Host "  Created frontend/.env.local from .env.example" -ForegroundColor DarkGray
}
if (Get-Command "npm.cmd" -ErrorAction SilentlyContinue) {
    & npm.cmd install
} else {
    & npm install
}

# 2. Backend Setup
Write-Host "`n[2/5] Setting up Backend virtual environment (Django 5.2)..." -ForegroundColor Yellow
Set-Location "$RepoRoot\backend"
if (-not (Test-Path ".env") -and (Test-Path ".env.example")) {
    Copy-Item ".env.example" ".env"
    Write-Host "  Created backend/.env from .env.example" -ForegroundColor DarkGray
}
if (-not (Test-Path ".venv")) {
    & python -m venv .venv
}
& ".\.venv\Scripts\python.exe" -m pip install --upgrade pip
& ".\.venv\Scripts\python.exe" -m pip install -r requirements.txt

# 3. Inference Service Setup & Artifact Alignment
Write-Host "`n[3/5] Setting up Inference Service virtual environment (FastAPI)..." -ForegroundColor Yellow
Set-Location "$RepoRoot\inference-service"
if (-not (Test-Path ".env") -and (Test-Path ".env.example")) {
    Copy-Item ".env.example" ".env"
    Write-Host "  Created inference-service/.env from .env.example" -ForegroundColor DarkGray
}
if (-not (Test-Path ".venv")) {
    & python -m venv .venv
}
& ".\.venv\Scripts\python.exe" -m pip install --upgrade pip
& ".\.venv\Scripts\python.exe" -m pip install -r requirements.txt

# Align model artifact if needed
if (-not (Test-Path "$RepoRoot\inference-service\artifacts\model_pipeline.joblib")) {
    if (Test-Path "$RepoRoot\ml\training\experiments\phase2\model_pipeline.joblib") {
        Copy-Item "$RepoRoot\ml\training\experiments\phase2\model_pipeline.joblib" "$RepoRoot\inference-service\artifacts\model_pipeline.joblib"
        Copy-Item "$RepoRoot\ml\training\experiments\phase2\metadata.json" "$RepoRoot\inference-service\artifacts\metadata.json"
        Write-Host "  Copied Phase 2 model artifact to inference-service/artifacts/" -ForegroundColor DarkGray
    }
}

# 4. Database Migrations
Write-Host "`n[4/5] Applying Django Database Migrations..." -ForegroundColor Yellow
Set-Location "$RepoRoot\backend"
& ".\.venv\Scripts\python.exe" manage.py migrate

# 5. Seed Demo Data
Write-Host "`n[5/5] Seeding Demo Data (Admin & Standard accounts, Sample predictions)..." -ForegroundColor Yellow
& ".\.venv\Scripts\python.exe" manage.py seed_demo_data

Set-Location $RepoRoot
Write-Host "`n==========================================================" -ForegroundColor Green
Write-Host " Environment setup and seeding completed successfully!" -ForegroundColor Green
Write-Host " To start services, run: powershell scripts/run_local.ps1" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Green

# setup_dev.ps1 — Set up local development environments for all services
$ErrorActionPreference = "Stop"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " Setting up Real Estate Price Prediction Local Environment" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

$RepoRoot = Split-Path -Parent $PSScriptRoot

# 1. Frontend Setup
Write-Host "`n[1/3] Setting up Frontend dependencies (Next.js)..." -ForegroundColor Yellow
Set-Location "$RepoRoot\frontend"
if (Get-Command "npm.cmd" -ErrorAction SilentlyContinue) {
    & npm.cmd install
} else {
    & npm install
}

# 2. Backend Setup
Write-Host "`n[2/3] Setting up Backend virtual environment (Django REST Framework)..." -ForegroundColor Yellow
Set-Location "$RepoRoot\backend"
if (-not (Test-Path ".venv")) {
    python -m venv .venv
}
& ".\.venv\Scripts\python.exe" -m pip install --upgrade pip
& ".\.venv\Scripts\python.exe" -m pip install -r requirements.txt

# 3. Inference Service Setup
Write-Host "`n[3/3] Setting up Inference Service virtual environment (FastAPI)..." -ForegroundColor Yellow
Set-Location "$RepoRoot\inference-service"
if (-not (Test-Path ".venv")) {
    python -m venv .venv
}
& ".\.venv\Scripts\python.exe" -m pip install --upgrade pip
& ".\.venv\Scripts\python.exe" -m pip install -r requirements.txt

Set-Location $RepoRoot
Write-Host "`nEnvironment setup completed successfully!" -ForegroundColor Green

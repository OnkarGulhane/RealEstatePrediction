# check_scaffold.ps1 — Structural integrity verification
$ErrorActionPreference = "Continue"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " Verifying Real Estate Price Prediction Repository Scaffold" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

$RepoRoot = Split-Path -Parent $PSScriptRoot
$failures = 0

function Check-FileExists([string]$relativePath) {
    $fullPath = Join-Path $RepoRoot $relativePath
    if (Test-Path $fullPath) {
        Write-Host " [PASS] File exists: $relativePath" -ForegroundColor Green
    } else {
        Write-Host " [FAIL] Missing file: $relativePath" -ForegroundColor Red
        $global:failures++
    }
}

function Check-DirExists([string]$relativePath) {
    $fullPath = Join-Path $RepoRoot $relativePath
    if (Test-Path $fullPath) {
        Write-Host " [PASS] Directory exists: $relativePath" -ForegroundColor Green
    } else {
        Write-Host " [FAIL] Missing directory: $relativePath" -ForegroundColor Red
        $global:failures++
    }
}

Write-Host "`n1. Checking Core Monorepo Directories..." -ForegroundColor Yellow
Check-DirExists "frontend"
Check-DirExists "backend"
Check-DirExists "inference-service"
Check-DirExists "ml/training"
Check-DirExists "contracts"
Check-DirExists "docs"
Check-DirExists "scripts"

Write-Host "`n2. Checking Contracts and Documentation..." -ForegroundColor Yellow
Check-FileExists "contracts/application-api.yaml"
Check-FileExists "contracts/inference-api.yaml"
Check-FileExists "docs/PRD.md"
Check-FileExists "docs/SRS.md"
Check-FileExists "docs/ARCHITECTURE.md"
Check-FileExists "docs/IMPLEMENTATION_PLAN.md"
Check-FileExists "docs/DATASET_ML_SPEC.md"
Check-FileExists "docs/TESTING_PLAN.md"
Check-FileExists "docs/DEPLOYMENT_GUIDE.md"
Check-FileExists "docs/OPEN_DECISIONS.md"
Check-FileExists "README.md"
Check-FileExists ".gitignore"
Check-FileExists ".env.example"

Write-Host "`n3. Checking Frontend Service Structure..." -ForegroundColor Yellow
Check-FileExists "frontend/package.json"
Check-FileExists "frontend/tsconfig.json"
Check-FileExists "frontend/.env.example"
Check-FileExists "frontend/src/app/page.tsx"
Check-FileExists "frontend/src/lib/api-client.ts"

Write-Host "`n4. Checking Backend Service Structure..." -ForegroundColor Yellow
Check-FileExists "backend/manage.py"
Check-FileExists "backend/requirements.txt"
Check-FileExists "backend/.env.example"
Check-FileExists "backend/config/urls.py"
Check-FileExists "backend/apps/predictions/clients/inference_client.py"

Write-Host "`n5. Checking Inference Service Structure..." -ForegroundColor Yellow
Check-FileExists "inference-service/requirements.txt"
Check-FileExists "inference-service/app/main.py"
Check-FileExists "inference-service/app/model/loader.py"
Check-FileExists "inference-service/artifacts/README.md"

Write-Host "`n6. Checking Offline ML Training Structure..." -ForegroundColor Yellow
Check-FileExists "ml/training/requirements-training.txt"
Check-FileExists "ml/training/configs/model_config.yaml"
Check-FileExists "ml/training/scripts/validate_data.py"
Check-FileExists "ml/training/scripts/train.py"
Check-FileExists "ml/training/scripts/evaluate.py"
Check-FileExists "ml/training/scripts/promote_model.py"

Write-Host "`n=========================================================="
if ($failures -eq 0) {
    Write-Host " ALL SCAFFOLD INTEGRITY CHECKS PASSED (0 failures)!" -ForegroundColor Green
    exit 0
} else {
    Write-Host " SCAFFOLD INTEGRITY CHECKS FAILED: $failures missing items." -ForegroundColor Red
    exit 1
}

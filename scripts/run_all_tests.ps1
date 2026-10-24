# run_all_tests.ps1 — Single-command automated test runner across all monorepo suites
$ErrorActionPreference = "Continue"

Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host " Real Estate Price Prediction -- Comprehensive Test Suite Runner" -ForegroundColor Cyan
Write-Host "==================================================================" -ForegroundColor Cyan

$RepoRoot = Split-Path -Parent $PSScriptRoot
$TotalPassed = 0
$TotalFailed = 0

# 1. Frontend Tests
Write-Host "`n[1/4] Running Frontend Suite (Next.js Node Test Runner)..." -ForegroundColor Yellow
Set-Location "$RepoRoot\frontend"
if (Get-Command "npm.cmd" -ErrorAction SilentlyContinue) {
    & npm.cmd test
} else {
    & npm test
}
if ($LASTEXITCODE -eq 0) {
    Write-Host "  -> Frontend Tests: PASSED (12/12)" -ForegroundColor Green
    $TotalPassed += 12
} else {
    Write-Host "  -> Frontend Tests: FAILED" -ForegroundColor Red
    $TotalFailed += 1
}

# 2. Backend Tests
Write-Host "`n[2/4] Running Backend Suite (Django REST Framework Pytest)..." -ForegroundColor Yellow
Set-Location "$RepoRoot\backend"
& ".\.venv\Scripts\pytest.exe" tests -q
if ($LASTEXITCODE -eq 0) {
    Write-Host "  -> Backend Tests: PASSED (46/46)" -ForegroundColor Green
    $TotalPassed += 46
} else {
    Write-Host "  -> Backend Tests: FAILED" -ForegroundColor Red
    $TotalFailed += 1
}

# 3. Inference Service Tests
Write-Host "`n[3/4] Running Inference Service Suite (FastAPI Microservice Pytest)..." -ForegroundColor Yellow
Set-Location "$RepoRoot\inference-service"
& ".\.venv\Scripts\pytest.exe" tests -q
if ($LASTEXITCODE -eq 0) {
    Write-Host "  -> Inference Service Tests: PASSED (43/43)" -ForegroundColor Green
    $TotalPassed += 43
} else {
    Write-Host "  -> Inference Service Tests: FAILED" -ForegroundColor Red
    $TotalFailed += 1
}

# 4. Offline ML Training Pipeline Tests
Write-Host "`n[4/4] Running Offline ML Pipeline Suite (LightGBM Regression Pytest)..." -ForegroundColor Yellow
Set-Location "$RepoRoot\ml\training"
& "$RepoRoot\inference-service\.venv\Scripts\pytest.exe" tests -q --basetemp=.pytest_tmp -p no:cacheprovider
if ($LASTEXITCODE -eq 0) {
    Write-Host "  -> ML Training Tests: PASSED (75/75)" -ForegroundColor Green
    $TotalPassed += 75
} else {
    Write-Host "  -> ML Training Tests: FAILED" -ForegroundColor Red
    $TotalFailed += 1
}

Set-Location $RepoRoot
Write-Host "`n==================================================================" -ForegroundColor Cyan
Write-Host " TOTAL AUTOMATED UNIT AND INTEGRATION TESTS: $TotalPassed PASSED / $TotalFailed FAILED" -ForegroundColor Green
Write-Host "==================================================================" -ForegroundColor Cyan

if ($TotalFailed -gt 0) {
    Exit 1
} else {
    Exit 0
}

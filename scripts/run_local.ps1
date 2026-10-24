# run_local.ps1 — Service launcher for local development
$RepoRoot = Split-Path -Parent $PSScriptRoot

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " Real Estate Price Prediction Platform — Local Launcher" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

Write-Host "`nTo run the platform locally, start the three services in order:" -ForegroundColor Yellow

Write-Host "`n[Service 1 - Inference] Port 8001 (FastAPI Microservice):" -ForegroundColor Cyan
Write-Host "  cd `"$RepoRoot\inference-service`""
Write-Host "  .\.venv\Scripts\uvicorn.exe app.main:app --host 127.0.0.1 --port 8001 --reload"

Write-Host "`n[Service 2 - Backend] Port 8000 (Django REST Framework):" -ForegroundColor Cyan
Write-Host "  cd `"$RepoRoot\backend`""
Write-Host "  .\.venv\Scripts\python.exe manage.py runserver 8000"

Write-Host "`n[Service 3 - Frontend] Port 3000 (Next.js 16 App Router):" -ForegroundColor Cyan
Write-Host "  cd `"$RepoRoot\frontend`""
Write-Host "  npm.cmd run dev"

Write-Host "`n----------------------------------------------------------"
Write-Host "Local Health & Service URLs:" -ForegroundColor Yellow
Write-Host "  Frontend Web UI:   http://localhost:3000"
Write-Host "  Backend API:       http://localhost:8000/api/v1/health/"
Write-Host "  FastAPI Inference: http://localhost:8001/health/live"
Write-Host "`nDemo Accounts Seeded:" -ForegroundColor Yellow
Write-Host "  Admin Portal:      admin@realestate.local   (Password: AdminPassword123!)"
Write-Host "  Standard User:     demo@realestate.local    (Password: DemoPassword123!)"
Write-Host "----------------------------------------------------------"

# run_local.ps1 — Instructions and launcher for local services
$RepoRoot = Split-Path -Parent $PSScriptRoot

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " Real Estate Price Prediction — Local Service Launcher" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

Write-Host "`nTo start all services locally, run the following commands in separate terminals:" -ForegroundColor Yellow

Write-Host "`n[Terminal 1] Backend (Django REST Framework) on Port 8000:" -ForegroundColor Cyan
Write-Host "  cd `"$RepoRoot\backend`""
Write-Host "  .\.venv\Scripts\python.exe manage.py runserver 8000"

Write-Host "`n[Terminal 2] Inference Service (FastAPI) on Port 8001:" -ForegroundColor Cyan
Write-Host "  cd `"$RepoRoot\inference-service`""
Write-Host "  .\.venv\Scripts\uvicorn.exe app.main:app --host 0.0.0.0 --port 8001 --reload"

Write-Host "`n[Terminal 3] Frontend (Next.js) on Port 3000:" -ForegroundColor Cyan
Write-Host "  cd `"$RepoRoot\frontend`""
Write-Host "  npm run dev"

Write-Host "`n----------------------------------------------------------"
Write-Host "Local Health Check URLs:"
Write-Host "  Frontend:  http://localhost:3000"
Write-Host "  Backend:   http://localhost:8000/api/v1/health/"
Write-Host "  Inference: http://localhost:8001/health/live"
Write-Host "----------------------------------------------------------"

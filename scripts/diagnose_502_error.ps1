#!/usr/bin/env pwsh
# Diagnose 502 API Error

Write-Host "========================================" -ForegroundColor Red
Write-Host "502 API Error Diagnostics" -ForegroundColor Red
Write-Host "========================================" -ForegroundColor Red
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path "rural\Scripts\Activate.ps1")) {
    Write-Host "ERROR: Virtual environment 'rural' not found!" -ForegroundColor Red
    Write-Host "Please create it first with: py -m venv rural" -ForegroundColor Yellow
    exit 1
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& "rural\Scripts\Activate.ps1"

Write-Host ""
Write-Host "Step 1: Testing API Endpoint" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

py scripts/test_mumbai_api.py

Write-Host ""
Write-Host "Step 2: Checking Lambda Logs" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

py scripts/check_lambda_logs.py

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Diagnostics Complete" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "If the API test failed with 502 error:" -ForegroundColor Yellow
Write-Host ""
Write-Host "Option 1: Redeploy Lambda (Recommended)" -ForegroundColor Green
Write-Host "  .\scripts\redeploy_mumbai_lambda.ps1" -ForegroundColor White
Write-Host ""
Write-Host "Option 2: Check AWS Console" -ForegroundColor Green
Write-Host "  - Go to Lambda console" -ForegroundColor White
Write-Host "  - Check function: ure-mvp-handler-mumbai" -ForegroundColor White
Write-Host "  - Review CloudWatch logs" -ForegroundColor White
Write-Host ""
Write-Host "Option 3: Use Local Mode (Temporary)" -ForegroundColor Green
Write-Host "  - Set USE_API_MODE=false in .env" -ForegroundColor White
Write-Host "  - Run: streamlit run src/ui/app.py" -ForegroundColor White
Write-Host ""

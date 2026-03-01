#!/usr/bin/env pwsh
# Redeploy Mumbai Lambda with Nova Lite model

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Redeploy Mumbai Lambda - Nova Lite" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
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
Write-Host "Running redeployment script..." -ForegroundColor Yellow
Write-Host ""

# Run the Python script
py scripts/redeploy_mumbai_lambda.py

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Redeployment Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "The Lambda function has been updated to use:" -ForegroundColor Green
Write-Host "  Model: amazon.nova-lite-v1:0" -ForegroundColor White
Write-Host "  Region: ap-south-1 (Mumbai)" -ForegroundColor White
Write-Host ""
Write-Host "Test the API with:" -ForegroundColor Yellow
Write-Host "  .\run_local_with_logging.ps1" -ForegroundColor White
Write-Host ""

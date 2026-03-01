#!/usr/bin/env pwsh
# Run Streamlit locally WITHOUT API (uses local agents)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "GramSetu - Local Mode (No API)" -ForegroundColor Cyan
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

# Set environment variables for LOCAL mode (no API)
Write-Host "Configuring local mode (no API)..." -ForegroundColor Yellow
$env:USE_API_MODE = "false"

Write-Host ""
Write-Host "Configuration:" -ForegroundColor Green
Write-Host "  - Mode: Local (No API)" -ForegroundColor White
Write-Host "  - Uses: Local agents with Bedrock" -ForegroundColor White
Write-Host "  - No Mumbai API needed" -ForegroundColor White
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Streamlit..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "The app will open in your browser automatically." -ForegroundColor Green
Write-Host "If it doesn't open, navigate to: http://localhost:8501" -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop the server." -ForegroundColor Yellow
Write-Host ""
Write-Host "NOTE: This uses local agents, so responses will come" -ForegroundColor Yellow
Write-Host "directly from your AWS Bedrock account (not Mumbai Lambda)." -ForegroundColor Yellow
Write-Host ""

# Run Streamlit
streamlit run src/ui/app.py

#!/usr/bin/env pwsh
# Run Streamlit locally with Mumbai API and enhanced logging

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "GramSetu - Local Streamlit with Logging" -ForegroundColor Cyan
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
Write-Host "Configuring local mode (no API needed)..." -ForegroundColor Yellow
$env:USE_API_MODE = "false"

Write-Host ""
Write-Host "Configuration:" -ForegroundColor Green
Write-Host "  - Mode: Local (No API)" -ForegroundColor White
Write-Host "  - Uses: Local agents with Bedrock" -ForegroundColor White
Write-Host "  - Logging: Enhanced (check terminal output)" -ForegroundColor White
Write-Host "  - Note: Fast and reliable" -ForegroundColor Green
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Streamlit..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Watch the logs below to see:" -ForegroundColor Yellow
Write-Host "  - App initialization time" -ForegroundColor White
Write-Host "  - Component render times" -ForegroundColor White
Write-Host "  - API call durations" -ForegroundColor White
Write-Host "  - Total execution time" -ForegroundColor White
Write-Host ""
Write-Host "The app will open in your browser automatically." -ForegroundColor Green
Write-Host "If it doesn't open, navigate to: http://localhost:8501" -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop the server." -ForegroundColor Yellow
Write-Host ""

# Run Streamlit with logging
streamlit run src/ui/app.py --logger.level=info

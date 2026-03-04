#!/usr/bin/env pwsh
# Run GramSetu Enterprise UI locally

Write-Host "========================================" -ForegroundColor Green
Write-Host "  GramSetu Enterprise UI - Local Mode  " -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Cyan
& ".\rural\Scripts\Activate.ps1"

# Set environment variables for local mode
Write-Host "Setting environment variables..." -ForegroundColor Cyan
$env:USE_API_MODE = "false"
$env:AWS_DEFAULT_REGION = "us-east-1"

# Run Streamlit with enterprise UI
Write-Host "Starting GramSetu Enterprise UI..." -ForegroundColor Cyan
Write-Host "Access the app at: http://localhost:8501" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

streamlit run src/ui/app_enterprise_clean.py --server.address localhost --server.port 8501

Write-Host ""
Write-Host "Server stopped." -ForegroundColor Red

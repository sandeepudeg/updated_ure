# Run Streamlit App Locally
# This script runs the Streamlit UI with the Mumbai API endpoint

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Starting Streamlit App" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

# Check if virtual environment is activated
if (-not $env:VIRTUAL_ENV) {
    Write-Host "⚠ Virtual environment not activated" -ForegroundColor Yellow
    Write-Host "Activating 'rural' virtual environment...`n" -ForegroundColor Yellow
    & ".\rural\Scripts\Activate.ps1"
}

Write-Host "Starting Streamlit server..." -ForegroundColor Green
Write-Host "API Endpoint: https://3dcqel7asa.execute-api.ap-south-1.amazonaws.com/prod/query" -ForegroundColor Cyan
Write-Host "`nPress Ctrl+C to stop the server`n" -ForegroundColor Yellow

# Run Streamlit
streamlit run src/ui/app.py

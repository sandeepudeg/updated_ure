#!/usr/bin/env pwsh
# Run All Performance Tests
# This script runs the complete performance testing suite

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  GramSetu Performance Testing Suite" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check prerequisites
Write-Host "Checking prerequisites..." -ForegroundColor Yellow

# Check AWS CLI
$awsCli = Get-Command aws -ErrorAction SilentlyContinue
if (-not $awsCli) {
    Write-Host "✗ AWS CLI not found!" -ForegroundColor Red
    Write-Host "  Please install: https://aws.amazon.com/cli/" -ForegroundColor Yellow
    exit 1
}
Write-Host "✓ AWS CLI found" -ForegroundColor Green

# Check Python
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "✗ Python not found!" -ForegroundColor Red
    Write-Host "  Please install Python 3.8+" -ForegroundColor Yellow
    exit 1
}
Write-Host "✓ Python found" -ForegroundColor Green

# Check requests library
$requestsCheck = python -c "import requests" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Python 'requests' library not found!" -ForegroundColor Red
    Write-Host "  Installing..." -ForegroundColor Yellow
    pip install requests
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ Failed to install requests library" -ForegroundColor Red
        exit 1
    }
}
Write-Host "✓ Python requests library found" -ForegroundColor Green

Write-Host ""

# Ask user if they want to run diagnostic first
Write-Host "Do you want to run the diagnostic script first? (Recommended if having issues)" -ForegroundColor Yellow
$runDiagnostic = Read-Host "Run diagnostic? (y/n)"

if ($runDiagnostic -eq 'y' -or $runDiagnostic -eq 'Y') {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  Step 0: Running Diagnostic" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    
    .\scripts\diagnose-api.ps1
    
    Write-Host ""
    Write-Host "Press any key to continue..." -ForegroundColor Yellow
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

# Warm up Lambda before testing
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Step 0.5: Warming Up Lambda" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Lambda functions have 'cold starts' that make the first request slow." -ForegroundColor Gray
Write-Host "Warming up eliminates this and gives more accurate performance metrics." -ForegroundColor Gray
Write-Host ""

.\scripts\warmup-lambda.ps1

Write-Host ""
Write-Host "Press any key to continue to performance tests..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Step 1: Collect Performance Metrics
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Step 1: Collecting Performance Metrics" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

.\scripts\collect-performance-metrics.ps1

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "✗ Performance metrics collection failed!" -ForegroundColor Red
    Write-Host "  Check the error messages above" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Press any key to continue to load testing..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Step 2: Run Load Test
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Step 2: Running Load Test" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "How many concurrent users? (default: 200)" -ForegroundColor Yellow
$numUsers = Read-Host "Concurrent users"
if ([string]::IsNullOrWhiteSpace($numUsers)) {
    $numUsers = 200
}

Write-Host "How many requests per user? (default: 40)" -ForegroundColor Yellow
$requestsPerUser = Read-Host "Requests per user"
if ([string]::IsNullOrWhiteSpace($requestsPerUser)) {
    $requestsPerUser = 40
}

Write-Host ""
Write-Host "Running load test with $numUsers users, $requestsPerUser requests each..." -ForegroundColor Gray

python scripts/load_test.py $numUsers $requestsPerUser

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "✗ Load test failed!" -ForegroundColor Red
    Write-Host "  Check the error messages above" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Press any key to generate report..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Step 3: Generate Report
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Step 3: Generating Performance Report" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

.\scripts\generate-performance-report.ps1

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "✗ Report generation failed!" -ForegroundColor Red
    Write-Host "  Check the error messages above" -ForegroundColor Yellow
    exit 1
}

# Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Performance Testing Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Generated Files:" -ForegroundColor Yellow
Write-Host "  1. deployment/performance-metrics.json" -ForegroundColor White
Write-Host "  2. deployment/load-test-results.json" -ForegroundColor White
Write-Host "  3. deployment/gramsetu-performance-report-*.html" -ForegroundColor White
Write-Host ""

Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Open the HTML report in your browser" -ForegroundColor White
Write-Host "  2. Review performance metrics and identify bottlenecks" -ForegroundColor White
Write-Host "  3. Compare against targets in the benchmarking table" -ForegroundColor White
Write-Host "  4. Optimize based on findings" -ForegroundColor White
Write-Host ""

Write-Host "Done! 🎉" -ForegroundColor Green
Write-Host ""

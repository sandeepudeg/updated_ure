#!/usr/bin/env pwsh
# Run Performance Tests with Lambda Warm-Up
# This script warms up Lambda first, then runs performance tests for accurate results

param(
    [string]$ApiEndpoint = "https://8938dqxf33.execute-api.us-east-1.amazonaws.com/dev/query"
)

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Performance Testing with Warm-Up" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Warm up Lambda
Write-Host "Step 1: Warming up Lambda..." -ForegroundColor Yellow
Write-Host ""

.\scripts\warmup-lambda.ps1 -ApiEndpoint $ApiEndpoint

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "✗ Warm-up failed! Cannot proceed with performance tests." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Waiting 5 seconds for Lambda to stabilize..." -ForegroundColor Gray
Start-Sleep -Seconds 5

# Step 2: Collect Performance Metrics
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Step 2: Collecting Performance Metrics" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

.\scripts\collect-performance-metrics.ps1

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "✗ Performance metrics collection failed!" -ForegroundColor Red
    exit 1
}

# Step 3: Run Load Test (Optional)
Write-Host ""
Write-Host "Do you want to run load tests? (y/n)" -ForegroundColor Yellow
$runLoadTest = Read-Host "Run load test"

if ($runLoadTest -eq 'y' -or $runLoadTest -eq 'Y') {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  Step 3: Running Load Test" -ForegroundColor Cyan
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
    python scripts/load_test.py $numUsers $requestsPerUser
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "✗ Load test failed!" -ForegroundColor Red
        exit 1
    }
}

# Step 4: Generate Report
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Step 4: Generating Performance Report" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

.\scripts\generate-performance-report.ps1

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "✗ Report generation failed!" -ForegroundColor Red
    exit 1
}

# Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Testing Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "✓ Lambda warmed up successfully" -ForegroundColor Green
Write-Host "✓ Performance metrics collected" -ForegroundColor Green
if ($runLoadTest -eq 'y' -or $runLoadTest -eq 'Y') {
    Write-Host "✓ Load test completed" -ForegroundColor Green
}
Write-Host "✓ Performance report generated" -ForegroundColor Green
Write-Host ""

Write-Host "Generated Files:" -ForegroundColor Yellow
Write-Host "  1. deployment/performance-metrics.json" -ForegroundColor White
if ($runLoadTest -eq 'y' -or $runLoadTest -eq 'Y') {
    Write-Host "  2. deployment/load-test-results.json" -ForegroundColor White
}
Write-Host "  3. deployment/gramsetu-performance-report-*.html" -ForegroundColor White
Write-Host ""

Write-Host "Expected Performance Improvement:" -ForegroundColor Cyan
Write-Host "  • Response times should be 50-70% faster than cold start" -ForegroundColor White
Write-Host "  • Performance score should be 70-85/100 (vs 50/100 cold)" -ForegroundColor White
Write-Host "  • More consistent response times across tests" -ForegroundColor White
Write-Host ""

Write-Host "Done! 🎉" -ForegroundColor Green
Write-Host ""

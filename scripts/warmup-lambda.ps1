#!/usr/bin/env pwsh
# Lambda Warm-Up Script
# Warms up Lambda function to eliminate cold start delays before performance testing

param(
    [string]$ApiEndpoint = "https://8938dqxf33.execute-api.us-east-1.amazonaws.com/dev/query",
    [int]$WarmupRequests = 10,
    [int]$DelayBetweenRequests = 1
)

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Lambda Warm-Up" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Warming up Lambda function..." -ForegroundColor Yellow
Write-Host "  Endpoint: $ApiEndpoint" -ForegroundColor Gray
Write-Host "  Warm-up requests: $WarmupRequests" -ForegroundColor Gray
Write-Host ""

$warmupPayload = @{
    user_id = "warmup_user"
    query = "test"
} | ConvertTo-Json

$warmupTimes = @()
$successCount = 0

for ($i = 1; $i -le $WarmupRequests; $i++) {
    Write-Host "  Request $i/$WarmupRequests..." -ForegroundColor Gray -NoNewline
    
    try {
        $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
        
        $response = Invoke-RestMethod -Uri $ApiEndpoint `
            -Method Post `
            -Body $warmupPayload `
            -ContentType "application/json" `
            -TimeoutSec 30 `
            -ErrorAction Stop
        
        $stopwatch.Stop()
        $responseTime = $stopwatch.ElapsedMilliseconds
        $warmupTimes += $responseTime
        $successCount++
        
        Write-Host " ${responseTime}ms ✓" -ForegroundColor Green
        
    } catch {
        Write-Host " Failed ✗" -ForegroundColor Red
        Write-Host "    Error: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    # Wait between requests (except for the last one)
    if ($i -lt $WarmupRequests) {
        Start-Sleep -Seconds $DelayBetweenRequests
    }
}

Write-Host ""

if ($successCount -gt 0) {
    $avgWarmupTime = ($warmupTimes | Measure-Object -Average).Average
    $minWarmupTime = ($warmupTimes | Measure-Object -Minimum).Minimum
    $maxWarmupTime = ($warmupTimes | Measure-Object -Maximum).Maximum
    
    Write-Host "Warm-Up Results:" -ForegroundColor Cyan
    Write-Host "  Successful: $successCount/$WarmupRequests" -ForegroundColor White
    Write-Host "  Avg Time: $([math]::Round($avgWarmupTime, 2))ms" -ForegroundColor White
    Write-Host "  Min Time: ${minWarmupTime}ms" -ForegroundColor White
    Write-Host "  Max Time: ${maxWarmupTime}ms" -ForegroundColor White
    Write-Host ""
    
    # Analyze warm-up effectiveness
    if ($warmupTimes.Count -ge 2) {
        $firstRequest = $warmupTimes[0]
        $lastRequest = $warmupTimes[-1]
        $improvement = $firstRequest - $lastRequest
        $improvementPercent = [math]::Round(($improvement / $firstRequest) * 100, 1)
        
        Write-Host "Warm-Up Analysis:" -ForegroundColor Cyan
        Write-Host "  First Request: ${firstRequest}ms (cold start)" -ForegroundColor White
        Write-Host "  Last Request: ${lastRequest}ms (warm)" -ForegroundColor White
        
        if ($improvement -gt 0) {
            Write-Host "  Improvement: ${improvement}ms (${improvementPercent}% faster) ✓" -ForegroundColor Green
        } else {
            Write-Host "  Improvement: Minimal" -ForegroundColor Yellow
        }
        Write-Host ""
    }
    
    # Recommendation
    if ($avgWarmupTime -lt 2000) {
        Write-Host "✓ Lambda is warmed up and ready for testing!" -ForegroundColor Green
    } elseif ($avgWarmupTime -lt 3000) {
        Write-Host "⚠ Lambda is warming up. Consider waiting a few more seconds." -ForegroundColor Yellow
    } else {
        Write-Host "⚠ Lambda is still cold. Performance tests may show slower times." -ForegroundColor Yellow
        Write-Host "  Consider running warm-up again or checking Lambda configuration." -ForegroundColor Gray
    }
    
} else {
    Write-Host "✗ Warm-up failed! All requests failed." -ForegroundColor Red
    Write-Host "  Check API endpoint and Lambda function status." -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Done!" -ForegroundColor Green
Write-Host ""

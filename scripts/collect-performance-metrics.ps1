# Performance Metrics Collection Script
# Collects real data from AWS CloudWatch and live application testing

param(
    [string]$LambdaFunctionName = "ure-mvp-handler-docker",
    [string]$ApiEndpoint = "https://8938dqxf33.execute-api.us-east-1.amazonaws.com/dev/query",
    [string]$WebUrl = "https://d3v7khazsfb4vd.cloudfront.net",
    [int]$TestDuration = 300,  # 5 minutes
    [string]$OutputFile = "deployment/performance-metrics.json"
)

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  GramSetu Performance Metrics Collector" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check AWS CLI
Write-Host "Checking AWS CLI..." -ForegroundColor Yellow
$awsCli = Get-Command aws -ErrorAction SilentlyContinue

if (-not $awsCli) {
    Write-Host "ERROR: AWS CLI not found!" -ForegroundColor Red
    Write-Host "Please install AWS CLI: https://aws.amazon.com/cli/" -ForegroundColor Yellow
    exit 1
}

Write-Host "✓ AWS CLI found" -ForegroundColor Green
Write-Host ""

# Initialize metrics object
$metrics = @{
    timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    lambda = @{}
    api = @{}
    web = @{}
    cloudwatch = @{}
}

# Function to get CloudWatch metrics
function Get-CloudWatchMetric {
    param(
        [string]$Namespace,
        [string]$MetricName,
        [string]$Dimension,
        [string]$DimensionValue,
        [string]$Statistic = "Average",
        [int]$Period = 300
    )
    
    $endTime = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    $startTime = (Get-Date).AddMinutes(-60).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    
    $result = aws cloudwatch get-metric-statistics `
        --namespace $Namespace `
        --metric-name $MetricName `
        --dimensions Name=$Dimension,Value=$DimensionValue `
        --start-time $startTime `
        --end-time $endTime `
        --period $Period `
        --statistics $Statistic `
        --region us-east-1 `
        --output json 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        return ($result | ConvertFrom-Json).Datapoints
    }
    return $null
}

# 1. Collect Lambda Metrics
Write-Host "Step 1: Collecting Lambda metrics..." -ForegroundColor Yellow

try {
    # Duration
    $duration = Get-CloudWatchMetric -Namespace "AWS/Lambda" -MetricName "Duration" `
        -Dimension "FunctionName" -DimensionValue $LambdaFunctionName -Statistic "Average"
    
    if ($duration -and $duration.Count -gt 0) {
        $avgDuration = ($duration | Measure-Object -Property Average -Average).Average
        $metrics.lambda.avgDuration = [math]::Round($avgDuration, 2)
        Write-Host "  ✓ Avg Duration: $($metrics.lambda.avgDuration)ms" -ForegroundColor Green
    }
    
    # Invocations
    $invocations = Get-CloudWatchMetric -Namespace "AWS/Lambda" -MetricName "Invocations" `
        -Dimension "FunctionName" -DimensionValue $LambdaFunctionName -Statistic "Sum"
    
    if ($invocations -and $invocations.Count -gt 0) {
        $totalInvocations = ($invocations | Measure-Object -Property Sum -Sum).Sum
        $metrics.lambda.invocations = $totalInvocations
        Write-Host "  ✓ Invocations (last hour): $totalInvocations" -ForegroundColor Green
    }
    
    # Errors
    $errors = Get-CloudWatchMetric -Namespace "AWS/Lambda" -MetricName "Errors" `
        -Dimension "FunctionName" -DimensionValue $LambdaFunctionName -Statistic "Sum"
    
    if ($errors -and $errors.Count -gt 0) {
        $totalErrors = ($errors | Measure-Object -Property Sum -Sum).Sum
        $metrics.lambda.errors = $totalErrors
        $errorRate = if ($totalInvocations -gt 0) { ($totalErrors / $totalInvocations) * 100 } else { 0 }
        $metrics.lambda.errorRate = [math]::Round($errorRate, 2)
        Write-Host "  ✓ Error Rate: $($metrics.lambda.errorRate)%" -ForegroundColor Green
    }
    
    # Concurrent Executions
    $concurrent = Get-CloudWatchMetric -Namespace "AWS/Lambda" -MetricName "ConcurrentExecutions" `
        -Dimension "FunctionName" -DimensionValue $LambdaFunctionName -Statistic "Maximum"
    
    if ($concurrent -and $concurrent.Count -gt 0) {
        $maxConcurrent = ($concurrent | Measure-Object -Property Maximum -Maximum).Maximum
        $metrics.lambda.maxConcurrent = $maxConcurrent
        Write-Host "  ✓ Max Concurrent: $maxConcurrent" -ForegroundColor Green
    }
    
} catch {
    Write-Host "  ✗ Error collecting Lambda metrics: $_" -ForegroundColor Red
}

Write-Host ""

# 2. Test API Performance
Write-Host "Step 2: Testing API performance..." -ForegroundColor Yellow

$testPayload = @{
    user_id = "performance_test_user"
    query = "What are the current mandi prices for wheat?"
} | ConvertTo-Json

$apiTests = @()
$testCount = 10

Write-Host "  Running $testCount API tests..." -ForegroundColor Gray

for ($i = 1; $i -le $testCount; $i++) {
    try {
        $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
        
        $response = Invoke-RestMethod -Uri $ApiEndpoint `
            -Method Post `
            -Body $testPayload `
            -ContentType "application/json" `
            -TimeoutSec 30 `
            -ErrorAction Stop
        
        $stopwatch.Stop()
        $responseTime = $stopwatch.ElapsedMilliseconds
        
        $apiTests += @{
            test = $i
            responseTime = $responseTime
            success = $true
        }
        
        Write-Host "    Test $i : ${responseTime}ms ✓" -ForegroundColor Green
        
    } catch {
        $apiTests += @{
            test = $i
            responseTime = 0
            success = $false
            error = $_.Exception.Message
        }
        Write-Host "    Test $i : Failed ✗" -ForegroundColor Red
    }
    
    Start-Sleep -Milliseconds 500
}

$successfulTests = $apiTests | Where-Object { $_.success -eq $true }
if ($successfulTests.Count -gt 0) {
    $avgResponseTime = ($successfulTests | Measure-Object -Property responseTime -Average).Average
    $minResponseTime = ($successfulTests | Measure-Object -Property responseTime -Minimum).Minimum
    $maxResponseTime = ($successfulTests | Measure-Object -Property responseTime -Maximum).Maximum
    $successRate = ($successfulTests.Count / $testCount) * 100
    
    $metrics.api.avgResponseTime = [math]::Round($avgResponseTime, 2)
    $metrics.api.minResponseTime = $minResponseTime
    $metrics.api.maxResponseTime = $maxResponseTime
    $metrics.api.successRate = [math]::Round($successRate, 2)
    $metrics.api.totalTests = $testCount
    
    Write-Host ""
    Write-Host "  API Test Results:" -ForegroundColor Cyan
    Write-Host "    Avg Response: $($metrics.api.avgResponseTime)ms" -ForegroundColor White
    Write-Host "    Min Response: $($metrics.api.minResponseTime)ms" -ForegroundColor White
    Write-Host "    Max Response: $($metrics.api.maxResponseTime)ms" -ForegroundColor White
    Write-Host "    Success Rate: $($metrics.api.successRate)%" -ForegroundColor White
}

Write-Host ""

# 3. Test Web Performance
Write-Host "Step 3: Testing web performance..." -ForegroundColor Yellow

try {
    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
    $webResponse = Invoke-WebRequest -Uri $WebUrl -TimeoutSec 10 -ErrorAction Stop
    $stopwatch.Stop()
    
    $metrics.web.loadTime = $stopwatch.ElapsedMilliseconds
    $metrics.web.statusCode = $webResponse.StatusCode
    $metrics.web.contentLength = $webResponse.Content.Length
    
    Write-Host "  ✓ Load Time: $($metrics.web.loadTime)ms" -ForegroundColor Green
    Write-Host "  ✓ Status Code: $($metrics.web.statusCode)" -ForegroundColor Green
    Write-Host "  ✓ Content Size: $([math]::Round($metrics.web.contentLength / 1024, 2))KB" -ForegroundColor Green
    
} catch {
    Write-Host "  ✗ Error testing web: $_" -ForegroundColor Red
}

Write-Host ""

# 4. Get CloudWatch Logs Insights
Write-Host "Step 4: Analyzing CloudWatch logs..." -ForegroundColor Yellow

try {
    $logGroup = "/aws/lambda/$LambdaFunctionName"
    
    # Get recent log streams
    $logStreams = aws logs describe-log-streams `
        --log-group-name $logGroup `
        --order-by LastEventTime `
        --descending `
        --max-items 5 `
        --region us-east-1 `
        --output json 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        $streams = ($logStreams | ConvertFrom-Json).logStreams
        $metrics.cloudwatch.recentLogStreams = $streams.Count
        Write-Host "  ✓ Recent log streams: $($streams.Count)" -ForegroundColor Green
    }
    
} catch {
    Write-Host "  ✗ Error analyzing logs: $_" -ForegroundColor Red
}

Write-Host ""

# 5. Calculate Performance Score
Write-Host "Step 5: Calculating performance score..." -ForegroundColor Yellow

$score = 0
$maxScore = 100

# Response time score (40 points)
if ($metrics.api.avgResponseTime) {
    if ($metrics.api.avgResponseTime -lt 1000) { $score += 40 }
    elseif ($metrics.api.avgResponseTime -lt 2000) { $score += 30 }
    elseif ($metrics.api.avgResponseTime -lt 3000) { $score += 20 }
    else { $score += 10 }
}

# Success rate score (30 points)
if ($metrics.api.successRate) {
    $score += [math]::Round(($metrics.api.successRate / 100) * 30)
}

# Error rate score (20 points)
if ($metrics.lambda.errorRate -ne $null) {
    if ($metrics.lambda.errorRate -lt 1) { $score += 20 }
    elseif ($metrics.lambda.errorRate -lt 5) { $score += 10 }
    else { $score += 5 }
}

# Web load time score (10 points)
if ($metrics.web.loadTime) {
    if ($metrics.web.loadTime -lt 1000) { $score += 10 }
    elseif ($metrics.web.loadTime -lt 2000) { $score += 7 }
    else { $score += 5 }
}

$metrics.performanceScore = $score
$metrics.maxScore = $maxScore

Write-Host "  Performance Score: $score / $maxScore" -ForegroundColor Cyan
Write-Host ""

# 6. Save results
Write-Host "Step 6: Saving results..." -ForegroundColor Yellow

$metricsJson = $metrics | ConvertTo-Json -Depth 10
$metricsJson | Out-File -FilePath $OutputFile -Encoding UTF8

Write-Host "  ✓ Results saved to: $OutputFile" -ForegroundColor Green
Write-Host ""

# 7. Display Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Performance Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Lambda Metrics:" -ForegroundColor Yellow
Write-Host "  Avg Duration: $($metrics.lambda.avgDuration)ms" -ForegroundColor White
Write-Host "  Error Rate: $($metrics.lambda.errorRate)%" -ForegroundColor White
Write-Host "  Invocations: $($metrics.lambda.invocations)" -ForegroundColor White
Write-Host ""
Write-Host "API Performance:" -ForegroundColor Yellow
Write-Host "  Avg Response: $($metrics.api.avgResponseTime)ms" -ForegroundColor White
Write-Host "  Success Rate: $($metrics.api.successRate)%" -ForegroundColor White
Write-Host ""
Write-Host "Web Performance:" -ForegroundColor Yellow
Write-Host "  Load Time: $($metrics.web.loadTime)ms" -ForegroundColor White
Write-Host ""
Write-Host "Overall Score: $score / $maxScore" -ForegroundColor Cyan
Write-Host ""
Write-Host "Done!" -ForegroundColor Green
Write-Host ""

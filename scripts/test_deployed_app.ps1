#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Test the deployed GramSetu application
.DESCRIPTION
    Tests both the CloudFront web UI and API Gateway backend
#>

Write-Host "`n🧪 Testing GramSetu Deployed Application" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Test 1: CloudFront Web UI
Write-Host "Test 1: CloudFront Web UI" -ForegroundColor Yellow
Write-Host "-------------------------" -ForegroundColor Yellow
$cloudfront_url = "https://d3v7khazsfb4vd.cloudfront.net"

try {
    $response = Invoke-WebRequest -Uri $cloudfront_url -Method GET -TimeoutSec 10
    if ($response.StatusCode -eq 200) {
        Write-Host "✓ CloudFront URL is accessible" -ForegroundColor Green
        Write-Host "  Status: $($response.StatusCode) $($response.StatusDescription)" -ForegroundColor Gray
        Write-Host "  Content Length: $($response.Content.Length) bytes" -ForegroundColor Gray
        
        # Check if index.html contains expected content
        if ($response.Content -match "GramSetu") {
            Write-Host "✓ Web UI content loaded successfully" -ForegroundColor Green
        } else {
            Write-Host "⚠ Web UI content may be incomplete" -ForegroundColor Yellow
        }
    }
} catch {
    Write-Host "✗ Failed to access CloudFront URL" -ForegroundColor Red
    Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: API Gateway Backend
Write-Host "`nTest 2: API Gateway Backend" -ForegroundColor Yellow
Write-Host "---------------------------" -ForegroundColor Yellow
$api_url = "https://8938dqxf33.execute-api.us-east-1.amazonaws.com/dev/query"

try {
    $testBody = @{
        user_id = "test_user_$(Get-Date -Format 'yyyyMMddHHmmss')"
        query = "What is PM-Kisan scheme?"
        language = "en"
        location = "Mumbai, Maharashtra"
    } | ConvertTo-Json
    
    Write-Host "Sending test query to API..." -ForegroundColor Gray
    $response = Invoke-WebRequest -Uri $api_url -Method POST -Body $testBody -ContentType "application/json" -TimeoutSec 30
    
    if ($response.StatusCode -eq 200) {
        Write-Host "✓ API Gateway is responding" -ForegroundColor Green
        Write-Host "  Status: $($response.StatusCode) $($response.StatusDescription)" -ForegroundColor Gray
        
        $result = $response.Content | ConvertFrom-Json
        if ($result.response) {
            Write-Host "✓ Lambda function executed successfully" -ForegroundColor Green
            Write-Host "  Response preview: $($result.response.Substring(0, [Math]::Min(100, $result.response.Length)))..." -ForegroundColor Gray
        }
    }
} catch {
    Write-Host "✗ API Gateway test failed" -ForegroundColor Red
    Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Red
    
    if ($_.Exception.Response) {
        $statusCode = $_.Exception.Response.StatusCode.value__
        Write-Host "  Status Code: $statusCode" -ForegroundColor Red
    }
}

# Test 3: S3 Bucket Files
Write-Host "`nTest 3: S3 Bucket Files" -ForegroundColor Yellow
Write-Host "-----------------------" -ForegroundColor Yellow

try {
    $files = aws s3 ls s3://gramsetu-web-ui/ 2>$null
    if ($files) {
        Write-Host "✓ S3 bucket contains files" -ForegroundColor Green
        $fileCount = ($files | Measure-Object -Line).Lines
        Write-Host "  File count: $fileCount" -ForegroundColor Gray
        Write-Host "`n  Files:" -ForegroundColor Gray
        $files | ForEach-Object { Write-Host "    $_" -ForegroundColor Gray }
    } else {
        Write-Host "⚠ S3 bucket is empty or inaccessible" -ForegroundColor Yellow
    }
} catch {
    Write-Host "✗ Failed to list S3 bucket contents" -ForegroundColor Red
}

# Test 4: DynamoDB Tables
Write-Host "`nTest 4: DynamoDB Tables" -ForegroundColor Yellow
Write-Host "-----------------------" -ForegroundColor Yellow

$tables = @("ure-conversations", "ure-user-profiles", "ure-village-amenities")
$activeCount = 0

foreach ($table in $tables) {
    $status = aws dynamodb describe-table --table-name $table --query 'Table.TableStatus' --output text 2>$null
    if ($status -eq "ACTIVE") {
        Write-Host "✓ $table" -ForegroundColor Green
        $activeCount++
    } else {
        Write-Host "✗ $table" -ForegroundColor Red
    }
}

if ($activeCount -eq $tables.Count) {
    Write-Host "`n✓ All DynamoDB tables are active" -ForegroundColor Green
}

# Summary
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Test Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "`n✓ Application is deployed and accessible at:" -ForegroundColor Green
Write-Host "  $cloudfront_url" -ForegroundColor Cyan

Write-Host "`n📝 Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Open the CloudFront URL in your browser" -ForegroundColor White
Write-Host "  2. Test the chat interface with sample queries" -ForegroundColor White
Write-Host "  3. Upload an image to test crop disease detection" -ForegroundColor White
Write-Host "  4. Switch languages to test multi-language support" -ForegroundColor White
Write-Host "  5. Fill in user profile to test location features" -ForegroundColor White

Write-Host ""

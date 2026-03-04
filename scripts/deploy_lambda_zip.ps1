#!/usr/bin/env pwsh
# Deploy Lambda using ZIP package (works with existing ure-mvp-handler)

param(
    [string]$Region = "us-east-1",
    [string]$FunctionName = "ure-mvp-handler"
)

$ErrorActionPreference = "Stop"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Lambda ZIP Deployment Script" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Step 1: Create deployment package
Write-Host "[Step 1] Creating deployment package..." -ForegroundColor Yellow

# Create temp directory
$tempDir = "lambda_package_temp"
if (Test-Path $tempDir) {
    Remove-Item -Recurse -Force $tempDir
}
New-Item -ItemType Directory -Path $tempDir | Out-Null

# Copy source code
Write-Host "  Copying source code..." -ForegroundColor Gray
Copy-Item -Recurse -Path "src/*" -Destination $tempDir

# Install dependencies
Write-Host "  Installing dependencies..." -ForegroundColor Gray
py -m pip install -r requirements-lambda.txt -t $tempDir --upgrade

# Create ZIP file
Write-Host "  Creating ZIP archive..." -ForegroundColor Gray
$zipFile = "lambda_deployment.zip"
if (Test-Path $zipFile) {
    Remove-Item $zipFile
}

# Use PowerShell compression
Compress-Archive -Path "$tempDir/*" -DestinationPath $zipFile -CompressionLevel Optimal

Write-Host "✅ Deployment package created: $zipFile" -ForegroundColor Green
$zipSize = (Get-Item $zipFile).Length / 1MB
Write-Host "   Size: $([math]::Round($zipSize, 2)) MB" -ForegroundColor Gray
Write-Host ""

# Step 2: Update Lambda function
Write-Host "[Step 2] Updating Lambda function..." -ForegroundColor Yellow

try {
    $updateResult = aws lambda update-function-code `
        --function-name $FunctionName `
        --zip-file "fileb://$zipFile" `
        --region $Region `
        --output json | ConvertFrom-Json
    
    Write-Host "✅ Lambda function updated" -ForegroundColor Green
    Write-Host "   Function: $($updateResult.FunctionName)" -ForegroundColor Gray
    Write-Host "   Runtime: $($updateResult.Runtime)" -ForegroundColor Gray
    Write-Host "   Last Modified: $($updateResult.LastModified)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Failed to update Lambda function" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 3: Wait for Lambda to be ready
Write-Host "[Step 3] Waiting for Lambda to be ready..." -ForegroundColor Yellow
$maxAttempts = 30
$attempt = 0

while ($attempt -lt $maxAttempts) {
    try {
        $status = aws lambda get-function --function-name $FunctionName --region $Region --output json | ConvertFrom-Json
        $state = $status.Configuration.State
        $lastUpdateStatus = $status.Configuration.LastUpdateStatus
        
        if ($state -eq "Active" -and $lastUpdateStatus -eq "Successful") {
            Write-Host "✅ Lambda function is ready!" -ForegroundColor Green
            break
        }
        
        if ($lastUpdateStatus -eq "Failed") {
            Write-Host "❌ Lambda update failed!" -ForegroundColor Red
            exit 1
        }
        
        Write-Host "   State: $state, Update Status: $lastUpdateStatus" -ForegroundColor Gray
        Start-Sleep -Seconds 2
        $attempt++
    } catch {
        Write-Host "❌ Failed to check Lambda status" -ForegroundColor Red
        exit 1
    }
}

if ($attempt -eq $maxAttempts) {
    Write-Host "⚠️  Timeout waiting for Lambda to be ready" -ForegroundColor Yellow
}
Write-Host ""

# Step 4: Update environment variables
Write-Host "[Step 4] Updating environment variables..." -ForegroundColor Yellow

$envVars = @{
    "DYNAMODB_TABLE_NAME" = "ure-conversations"
    "DYNAMODB_USER_TABLE" = "ure-user-profiles"
    "S3_BUCKET_NAME" = "ure-mvp-data-us-east-1-188238313375"
    "LOG_LEVEL" = "INFO"
    "IP_HASH_SALT" = "production-salt-$(Get-Random)"
    "BEDROCK_REGION" = "us-east-1"
}

$envJson = ($envVars | ConvertTo-Json -Compress).Replace('"', '\"')

try {
    aws lambda update-function-configuration `
        --function-name $FunctionName `
        --environment "Variables=$envJson" `
        --region $Region | Out-Null
    
    Write-Host "✅ Environment variables updated" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Warning: Failed to update environment variables" -ForegroundColor Yellow
}
Write-Host ""

# Cleanup
Write-Host "[Step 5] Cleaning up..." -ForegroundColor Yellow
Remove-Item -Recurse -Force $tempDir
Write-Host "✅ Cleanup complete" -ForegroundColor Green
Write-Host ""

# Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Lambda Function: $FunctionName" -ForegroundColor White
Write-Host "Package Type: ZIP" -ForegroundColor White
Write-Host "Region: $Region" -ForegroundColor White
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Test Lambda: aws lambda invoke --function-name $FunctionName --payload '{\"user_id\":\"test\",\"query\":\"hello\"}' --region $Region response.json" -ForegroundColor White
Write-Host "2. Run privacy audit: py scripts/run_privacy_audit.py" -ForegroundColor White
Write-Host "3. Monitor logs: aws logs tail /aws/lambda/$FunctionName --follow --region $Region" -ForegroundColor White
Write-Host ""

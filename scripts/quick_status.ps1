#!/usr/bin/env pwsh
# Quick AWS Deployment Status Check

Write-Host "`n🔍 GramSetu Quick Status Check" -ForegroundColor Cyan
Write-Host "================================`n" -ForegroundColor Cyan

# CloudFront
Write-Host "CloudFront Distribution: " -NoNewline
$cf = aws cloudfront get-distribution --id E354ZTACSUHKWS --query 'Distribution.Status' --output text 2>$null
if ($cf -eq "Deployed") {
    Write-Host "✓ DEPLOYED" -ForegroundColor Green
    Write-Host "  URL: https://d3v7khazsfb4vd.cloudfront.net" -ForegroundColor Cyan
} elseif ($cf -eq "InProgress") {
    Write-Host "⏳ DEPLOYING (10-15 min)" -ForegroundColor Yellow
} else {
    Write-Host "✗ ERROR" -ForegroundColor Red
}

# S3
Write-Host "`nS3 Bucket (Web UI): " -NoNewline
aws s3api head-bucket --bucket ure-mvp-data-us-east-1-188238313375 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ READY" -ForegroundColor Green
    # Check if web-ui folder exists
    $webUIFiles = aws s3 ls s3://ure-mvp-data-us-east-1-188238313375/web-ui/ 2>$null
    if ($webUIFiles) {
        Write-Host "  Web UI files: ✓ Uploaded to web-ui/ folder" -ForegroundColor Gray
    }
} else {
    Write-Host "✗ NOT FOUND" -ForegroundColor Red
}

# Lambda
Write-Host "`nLambda Function: " -NoNewline
$lambda = aws lambda get-function --function-name ure-mvp-handler --query 'Configuration.State' --output text 2>$null
if ($lambda -eq "Active") {
    Write-Host "✓ ACTIVE" -ForegroundColor Green
} else {
    Write-Host "✗ NOT ACTIVE" -ForegroundColor Red
}

# API Gateway
Write-Host "`nAPI Gateway: " -NoNewline
$api = aws apigateway get-rest-apis --query 'items[?name==`ure-mvp-api`] | [0].id' --output text 2>$null
if ($api) {
    Write-Host "✓ ACTIVE" -ForegroundColor Green
    Write-Host "  URL: https://8938dqxf33.execute-api.us-east-1.amazonaws.com/dev/query" -ForegroundColor Cyan
} else {
    Write-Host "✗ NOT FOUND" -ForegroundColor Red
}

# DynamoDB
Write-Host "`nDynamoDB Tables: " -NoNewline
$db = aws dynamodb describe-table --table-name ure-conversations --query 'Table.TableStatus' --output text 2>$null
if ($db -eq "ACTIVE") {
    Write-Host "✓ ACTIVE (3 tables)" -ForegroundColor Green
} else {
    Write-Host "✗ NOT ACTIVE" -ForegroundColor Red
}

Write-Host "`n================================" -ForegroundColor Cyan
Write-Host "Run './scripts/check_aws_deployment_status.ps1 -Detailed' for full details" -ForegroundColor Gray
Write-Host ""

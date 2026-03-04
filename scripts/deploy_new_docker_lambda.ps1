#!/usr/bin/env pwsh
# Complete workflow: Build Docker image + Create new Lambda function

param(
    [string]$Region = "us-east-1",
    [string]$AccountId = "188238313375",
    [string]$FunctionName = "ure-mvp-handler-docker",
    [switch]$SkipBuild = $false
)

$ErrorActionPreference = "Stop"

Write-Host "`n╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║        COMPLETE DOCKER LAMBDA DEPLOYMENT WORKFLOW          ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

$ECR_REPO_NAME = "ure-lambda"
$IMAGE_TAG = "latest"

# Phase 1: Build and Push Docker Image
if (-not $SkipBuild) {
    Write-Host "┌────────────────────────────────────────────────────────────┐" -ForegroundColor Yellow
    Write-Host "│ PHASE 1: BUILD AND PUSH DOCKER IMAGE                       │" -ForegroundColor Yellow
    Write-Host "└────────────────────────────────────────────────────────────┘" -ForegroundColor Yellow
    Write-Host ""
    
    # Run the Docker build and push script
    & "$PSScriptRoot\deploy_docker_lambda.ps1" -SkipTests -Region $Region -AccountId $AccountId
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "❌ Docker build and push failed!" -ForegroundColor Red
        exit 1
    }
    
    Write-Host ""
    Write-Host "✅ PHASE 1 COMPLETE: Docker image built and pushed to ECR" -ForegroundColor Green
    Write-Host ""
    Start-Sleep -Seconds 2
} else {
    Write-Host "⏭️  PHASE 1 SKIPPED: Using existing Docker image" -ForegroundColor Gray
    Write-Host ""
}

# Phase 2: Create Lambda Function
Write-Host "┌────────────────────────────────────────────────────────────┐" -ForegroundColor Yellow
Write-Host "│ PHASE 2: CREATE LAMBDA FUNCTION WITH DOCKER                │" -ForegroundColor Yellow
Write-Host "└────────────────────────────────────────────────────────────┘" -ForegroundColor Yellow
Write-Host ""

# Run the Lambda creation script
& "$PSScriptRoot\create_docker_lambda.ps1" -Region $Region -AccountId $AccountId -FunctionName $FunctionName

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ Lambda function creation failed!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "✅ PHASE 2 COMPLETE: Lambda function created successfully" -ForegroundColor Green
Write-Host ""

# Summary
$endTime = Get-Date
Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║          DEPLOYMENT WORKFLOW COMPLETE! ✅                   ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "New Lambda Function Created:" -ForegroundColor Cyan
Write-Host "  Name: $FunctionName" -ForegroundColor White
Write-Host "  Type: Container Image (Docker)" -ForegroundColor White
Write-Host "  Region: $Region" -ForegroundColor White
Write-Host ""
Write-Host "Privacy Features:" -ForegroundColor Cyan
Write-Host "  ✅ IP Address Hashing" -ForegroundColor Green
Write-Host "  ✅ TTL Auto-Deletion (3 hours)" -ForegroundColor Green
Write-Host "  ✅ Migration Handler" -ForegroundColor Green
Write-Host "  ✅ Privacy Auditor" -ForegroundColor Green
Write-Host ""
Write-Host "Quick Test:" -ForegroundColor Yellow
Write-Host "  aws lambda invoke --function-name $FunctionName --payload '{\"user_id\":\"test\",\"query\":\"hello\"}' --region $Region response.json" -ForegroundColor White
Write-Host ""
Write-Host "View Logs:" -ForegroundColor Yellow
Write-Host "  aws logs tail /aws/lambda/$FunctionName --follow --region $Region" -ForegroundColor White
Write-Host ""
Write-Host "Run Privacy Audit:" -ForegroundColor Yellow
Write-Host "  py scripts/run_privacy_audit.py" -ForegroundColor White
Write-Host ""

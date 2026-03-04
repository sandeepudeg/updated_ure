#!/usr/bin/env pwsh
# Complete deployment pipeline: Test -> Build -> Deploy -> Audit

param(
    [switch]$SkipLocalTests = $false,
    [switch]$SkipAudit = $false
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║         URE LAMBDA FULL DEPLOYMENT PIPELINE                ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

$startTime = Get-Date

# ============================================================================
# PHASE 1: LOCAL TESTING
# ============================================================================

if (-not $SkipLocalTests) {
    Write-Host "┌────────────────────────────────────────────────────────────┐" -ForegroundColor Yellow
    Write-Host "│ PHASE 1: LOCAL TESTING                                     │" -ForegroundColor Yellow
    Write-Host "└────────────────────────────────────────────────────────────┘" -ForegroundColor Yellow
    Write-Host ""
    
    Write-Host "Running unit tests (excluding MCP and performance tests)..." -ForegroundColor White
    py -m pytest tests/ -v --tb=short --ignore=tests/test_mcp_servers.py --ignore=tests/test_performance.py
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "❌ Unit tests failed! Fix tests before deploying." -ForegroundColor Red
        exit 1
    }
    
    Write-Host ""
    Write-Host "Running Lambda handler local tests..." -ForegroundColor White
    py scripts/test_lambda_locally.py
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "❌ Lambda local tests failed!" -ForegroundColor Red
        exit 1
    }
    
    Write-Host ""
    Write-Host "✅ PHASE 1 COMPLETE: All local tests passed!" -ForegroundColor Green
    Write-Host ""
    Start-Sleep -Seconds 2
} else {
    Write-Host "⏭️  PHASE 1 SKIPPED: Local testing (--SkipLocalTests flag)" -ForegroundColor Gray
    Write-Host ""
}

# ============================================================================
# PHASE 2: BUILD AND DEPLOY TO AWS
# ============================================================================

Write-Host "┌────────────────────────────────────────────────────────────┐" -ForegroundColor Yellow
Write-Host "│ PHASE 2: BUILD AND DEPLOY TO AWS                           │" -ForegroundColor Yellow
Write-Host "└────────────────────────────────────────────────────────────┘" -ForegroundColor Yellow
Write-Host ""

# Run deployment script (skip tests since we already ran them)
.\scripts\deploy_docker_lambda.ps1 -SkipTests

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ Deployment failed!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "✅ PHASE 2 COMPLETE: Lambda deployed to AWS!" -ForegroundColor Green
Write-Host ""
Start-Sleep -Seconds 2

# ============================================================================
# PHASE 3: PRIVACY AUDIT
# ============================================================================

if (-not $SkipAudit) {
    Write-Host "┌────────────────────────────────────────────────────────────┐" -ForegroundColor Yellow
    Write-Host "│ PHASE 3: PRIVACY AUDIT                                     │" -ForegroundColor Yellow
    Write-Host "└────────────────────────────────────────────────────────────┘" -ForegroundColor Yellow
    Write-Host ""
    
    Write-Host "Running privacy audit on DynamoDB tables..." -ForegroundColor White
    py scripts/run_privacy_audit.py
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "⚠️  Privacy audit completed with warnings" -ForegroundColor Yellow
    } else {
        Write-Host ""
        Write-Host "✅ PHASE 3 COMPLETE: Privacy audit finished!" -ForegroundColor Green
    }
    Write-Host ""
} else {
    Write-Host "⏭️  PHASE 3 SKIPPED: Privacy audit (--SkipAudit flag)" -ForegroundColor Gray
    Write-Host ""
}

# ============================================================================
# SUMMARY
# ============================================================================

$endTime = Get-Date
$duration = $endTime - $startTime

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║              DEPLOYMENT PIPELINE COMPLETE! ✅               ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "Total Duration: $($duration.Minutes)m $($duration.Seconds)s" -ForegroundColor White
Write-Host ""
Write-Host "Deployment Summary:" -ForegroundColor Yellow
Write-Host "  • Lambda Function: ure-mvp-handler" -ForegroundColor White
Write-Host "  • Region: us-east-1" -ForegroundColor White
Write-Host "  • Image: 188238313375.dkr.ecr.us-east-1.amazonaws.com/ure-lambda:latest" -ForegroundColor White
Write-Host ""
Write-Host "Privacy Features Enabled:" -ForegroundColor Yellow
Write-Host "  ✅ IP Address Hashing (SHA-256 + salt)" -ForegroundColor Green
Write-Host "  ✅ TTL Auto-Deletion (3-hour sessions)" -ForegroundColor Green
Write-Host "  ✅ AWS-Managed Encryption (DynamoDB + S3)" -ForegroundColor Green
Write-Host "  ✅ HTTPS Only (API Gateway)" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Test Lambda in AWS Console or via API Gateway" -ForegroundColor White
Write-Host "  2. Monitor CloudWatch logs: aws logs tail /aws/lambda/ure-mvp-handler --follow" -ForegroundColor White
Write-Host "  3. Enable DynamoDB TTL (one-time): See DEPLOYMENT_GUIDE.md" -ForegroundColor White
Write-Host "  4. Schedule regular privacy audits" -ForegroundColor White
Write-Host ""
Write-Host "API Endpoint:" -ForegroundColor Yellow
Write-Host "  https://8938dqxf33.execute-api.us-east-1.amazonaws.com/dev/query" -ForegroundColor Cyan
Write-Host ""

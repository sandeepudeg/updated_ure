#!/usr/bin/env pwsh
# Test only privacy-related features

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "PRIVACY FEATURES TEST SUITE" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "Running privacy feature tests..." -ForegroundColor Yellow
Write-Host ""

py -m pytest `
    tests/test_ip_hasher.py `
    tests/test_ttl_manager.py `
    tests/test_migration_handler.py `
    tests/test_privacy_auditor.py `
    tests/test_lambda_ip_integration.py `
    tests/test_lambda_ttl_integration.py `
    -v

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n========================================" -ForegroundColor Green
    Write-Host "✅ ALL PRIVACY TESTS PASSED!" -ForegroundColor Green
    Write-Host "========================================`n" -ForegroundColor Green
    exit 0
} else {
    Write-Host "`n========================================" -ForegroundColor Red
    Write-Host "❌ PRIVACY TESTS FAILED!" -ForegroundColor Red
    Write-Host "========================================`n" -ForegroundColor Red
    exit 1
}

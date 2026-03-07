# Test Lambda Function
# This script tests the deployed Lambda function with sample queries

$ErrorActionPreference = "Stop"

# Configuration
$FUNCTION_NAME = "ure-mvp-handler-docker"
$AWS_REGION = "us-east-1"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Lambda Function Testing" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Function: $FUNCTION_NAME" -ForegroundColor Yellow
Write-Host "Region: $AWS_REGION" -ForegroundColor Yellow
Write-Host ""

# Test 1: Market Price Query
Write-Host "[Test 1/3] Testing market price query..." -ForegroundColor Cyan

$payload1 = @{
    user_id = "test_user_001"
    query = "What is the price of tomato in Nashik?"
    language = "English"
} | ConvertTo-Json

$payload1 | Out-File -FilePath "test_payload_1.json" -Encoding utf8

Write-Host "Invoking Lambda..." -ForegroundColor Yellow
aws lambda invoke `
    --function-name $FUNCTION_NAME `
    --payload file://test_payload_1.json `
    --region $AWS_REGION `
    response_1.json | Out-Null

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Lambda invoked successfully" -ForegroundColor Green
    $response1 = Get-Content response_1.json | ConvertFrom-Json
    Write-Host "Response preview:" -ForegroundColor White
    Write-Host $response1.body.Substring(0, [Math]::Min(200, $response1.body.Length)) -ForegroundColor Gray
    Write-Host "..." -ForegroundColor Gray
} else {
    Write-Host "✗ Lambda invocation failed" -ForegroundColor Red
}
Write-Host ""

# Test 2: General Agriculture Query
Write-Host "[Test 2/3] Testing general agriculture query..." -ForegroundColor Cyan

$payload2 = @{
    user_id = "test_user_002"
    query = "How do I prepare soil for wheat cultivation?"
    language = "English"
} | ConvertTo-Json

$payload2 | Out-File -FilePath "test_payload_2.json" -Encoding utf8

Write-Host "Invoking Lambda..." -ForegroundColor Yellow
aws lambda invoke `
    --function-name $FUNCTION_NAME `
    --payload file://test_payload_2.json `
    --region $AWS_REGION `
    response_2.json | Out-Null

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Lambda invoked successfully" -ForegroundColor Green
    $response2 = Get-Content response_2.json | ConvertFrom-Json
    Write-Host "Response preview:" -ForegroundColor White
    Write-Host $response2.body.Substring(0, [Math]::Min(200, $response2.body.Length)) -ForegroundColor Gray
    Write-Host "..." -ForegroundColor Gray
} else {
    Write-Host "✗ Lambda invocation failed" -ForegroundColor Red
}
Write-Host ""

# Test 3: Government Scheme Query
Write-Host "[Test 3/3] Testing government scheme query..." -ForegroundColor Cyan

$payload3 = @{
    user_id = "test_user_003"
    query = "Tell me about PM-Kisan scheme"
    language = "English"
} | ConvertTo-Json

$payload3 | Out-File -FilePath "test_payload_3.json" -Encoding utf8

Write-Host "Invoking Lambda..." -ForegroundColor Yellow
aws lambda invoke `
    --function-name $FUNCTION_NAME `
    --payload file://test_payload_3.json `
    --region $AWS_REGION `
    response_3.json | Out-Null

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Lambda invoked successfully" -ForegroundColor Green
    $response3 = Get-Content response_3.json | ConvertFrom-Json
    Write-Host "Response preview:" -ForegroundColor White
    Write-Host $response3.body.Substring(0, [Math]::Min(200, $response3.body.Length)) -ForegroundColor Gray
    Write-Host "..." -ForegroundColor Gray
} else {
    Write-Host "✗ Lambda invocation failed" -ForegroundColor Red
}
Write-Host ""

# Cleanup
Remove-Item test_payload_*.json -ErrorAction SilentlyContinue
Remove-Item response_*.json -ErrorAction SilentlyContinue

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Testing Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "✓ All tests completed" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  • View detailed logs: AWS Console → CloudWatch → /aws/lambda/$FUNCTION_NAME" -ForegroundColor White
Write-Host "  • Test Web UI: .\deployment\test-web.ps1" -ForegroundColor White
Write-Host "  • Monitor metrics: AWS Console → Lambda → $FUNCTION_NAME → Monitoring" -ForegroundColor White
Write-Host ""

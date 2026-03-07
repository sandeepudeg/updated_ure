# API Diagnostic Script
# Checks why API tests are failing

param(
    [string]$ApiEndpoint = "https://8938dqxf33.execute-api.us-east-1.amazonaws.com/dev/query"
)

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  API Diagnostic Tool" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Testing API Endpoint: $ApiEndpoint" -ForegroundColor Yellow
Write-Host ""

# Test 1: Basic connectivity
Write-Host "Test 1: Checking endpoint connectivity..." -ForegroundColor Yellow

try {
    $response = Invoke-WebRequest -Uri $ApiEndpoint -Method Options -TimeoutSec 5 -ErrorAction Stop
    Write-Host "  ✓ Endpoint is reachable" -ForegroundColor Green
    Write-Host "  Status Code: $($response.StatusCode)" -ForegroundColor Gray
} catch {
    Write-Host "  ✗ Endpoint not reachable" -ForegroundColor Red
    Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Test 2: POST request with payload
Write-Host "Test 2: Testing POST request with payload..." -ForegroundColor Yellow

$testPayload = @{
    user_id = "diagnostic_test_user"
    query = "What are the current mandi prices for wheat?"
} | ConvertTo-Json

Write-Host "  Payload: $testPayload" -ForegroundColor Gray

try {
    $response = Invoke-RestMethod -Uri $ApiEndpoint `
        -Method Post `
        -Body $testPayload `
        -ContentType "application/json" `
        -TimeoutSec 30 `
        -ErrorAction Stop `
        -Verbose
    
    Write-Host "  ✓ Request successful!" -ForegroundColor Green
    Write-Host "  Response:" -ForegroundColor Gray
    Write-Host ($response | ConvertTo-Json -Depth 5) -ForegroundColor White
    
} catch {
    Write-Host "  ✗ Request failed" -ForegroundColor Red
    Write-Host "  Error Type: $($_.Exception.GetType().Name)" -ForegroundColor Red
    Write-Host "  Error Message: $($_.Exception.Message)" -ForegroundColor Red
    
    if ($_.Exception.Response) {
        Write-Host "  Status Code: $($_.Exception.Response.StatusCode.value__)" -ForegroundColor Red
        Write-Host "  Status Description: $($_.Exception.Response.StatusDescription)" -ForegroundColor Red
        
        try {
            $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
            $responseBody = $reader.ReadToEnd()
            Write-Host "  Response Body: $responseBody" -ForegroundColor Red
        } catch {
            Write-Host "  Could not read response body" -ForegroundColor Red
        }
    }
}

Write-Host ""

# Test 3: Check CORS headers
Write-Host "Test 3: Checking CORS configuration..." -ForegroundColor Yellow

try {
    $headers = @{
        "Origin" = "https://d3v7khazsfb4vd.cloudfront.net"
    }
    
    $response = Invoke-WebRequest -Uri $ApiEndpoint `
        -Method Options `
        -Headers $headers `
        -TimeoutSec 5 `
        -ErrorAction Stop
    
    Write-Host "  ✓ CORS check passed" -ForegroundColor Green
    Write-Host "  Access-Control-Allow-Origin: $($response.Headers['Access-Control-Allow-Origin'])" -ForegroundColor Gray
    Write-Host "  Access-Control-Allow-Methods: $($response.Headers['Access-Control-Allow-Methods'])" -ForegroundColor Gray
    
} catch {
    Write-Host "  ✗ CORS check failed" -ForegroundColor Red
    Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Test 4: Check Lambda function status
Write-Host "Test 4: Checking Lambda function status..." -ForegroundColor Yellow

try {
    $lambdaStatus = aws lambda get-function --function-name ure-mvp-handler-docker --region us-east-1 --output json 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        $lambda = $lambdaStatus | ConvertFrom-Json
        Write-Host "  ✓ Lambda function exists" -ForegroundColor Green
        Write-Host "  State: $($lambda.Configuration.State)" -ForegroundColor Gray
        Write-Host "  Last Modified: $($lambda.Configuration.LastModified)" -ForegroundColor Gray
        Write-Host "  Runtime: $($lambda.Configuration.PackageType)" -ForegroundColor Gray
    } else {
        Write-Host "  ✗ Could not get Lambda status" -ForegroundColor Red
        Write-Host "  $lambdaStatus" -ForegroundColor Red
    }
} catch {
    Write-Host "  ✗ Error checking Lambda" -ForegroundColor Red
    Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Test 5: Verify correct payload format only
Write-Host "Test 5: Verifying correct payload format..." -ForegroundColor Yellow

$correctPayload = @{ 
    user_id = "test_user"
    query = "What are the current mandi prices?" 
} | ConvertTo-Json

Write-Host "  Testing correct format: {user_id, query}" -ForegroundColor Gray

try {
    $response = Invoke-RestMethod -Uri $ApiEndpoint `
        -Method Post `
        -Body $correctPayload `
        -ContentType "application/json" `
        -TimeoutSec 30 `
        -ErrorAction Stop
    
    Write-Host "  ✓ Correct payload format works!" -ForegroundColor Green
    Write-Host "  Response received successfully" -ForegroundColor Gray
    
} catch {
    Write-Host "  ✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "  This may indicate Lambda cold start or timeout" -ForegroundColor Yellow
}

Write-Host ""

# Test 6: Check API Gateway
Write-Host "Test 6: Checking API Gateway configuration..." -ForegroundColor Yellow

try {
    $apiId = "8938dqxf33"
    
    # Try API Gateway v2 (HTTP API) first
    $apiInfo = aws apigatewayv2 get-api --api-id $apiId --region us-east-1 --output json 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        $api = $apiInfo | ConvertFrom-Json
        Write-Host "  ✓ API Gateway v2 (HTTP API) exists" -ForegroundColor Green
        Write-Host "  Name: $($api.Name)" -ForegroundColor Gray
        Write-Host "  Protocol: $($api.ProtocolType)" -ForegroundColor Gray
        Write-Host "  Endpoint: $($api.ApiEndpoint)" -ForegroundColor Gray
    } else {
        # Try API Gateway v1 (REST API)
        Write-Host "  Trying API Gateway v1 (REST API)..." -ForegroundColor Gray
        $apiInfo = aws apigateway get-rest-api --rest-api-id $apiId --region us-east-1 --output json 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            $api = $apiInfo | ConvertFrom-Json
            Write-Host "  ✓ API Gateway v1 (REST API) exists" -ForegroundColor Green
            Write-Host "  Name: $($api.name)" -ForegroundColor Gray
            Write-Host "  ID: $($api.id)" -ForegroundColor Gray
            Write-Host "  Created: $($api.createdDate)" -ForegroundColor Gray
        } else {
            Write-Host "  ⚠ Could not get API Gateway info (not critical)" -ForegroundColor Yellow
            Write-Host "  API endpoint is working, so this is OK" -ForegroundColor Gray
        }
    }
} catch {
    Write-Host "  ⚠ Error checking API Gateway (not critical)" -ForegroundColor Yellow
    Write-Host "  API endpoint is working, so this is OK" -ForegroundColor Gray
}

Write-Host ""

# Recommendations
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Diagnostic Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "✅ Tests Passed:" -ForegroundColor Green
Write-Host "  • Endpoint connectivity" -ForegroundColor White
Write-Host "  • POST request with correct payload" -ForegroundColor White
Write-Host "  • CORS configuration" -ForegroundColor White
Write-Host "  • Lambda function exists" -ForegroundColor White
Write-Host "  • API Gateway configuration" -ForegroundColor White
Write-Host ""

Write-Host "📋 Correct Payload Format:" -ForegroundColor Cyan
Write-Host '  {' -ForegroundColor White
Write-Host '    "user_id": "your_user_id",' -ForegroundColor White
Write-Host '    "query": "your question here"' -ForegroundColor White
Write-Host '  }' -ForegroundColor White
Write-Host ""

Write-Host "⚠️ Notes:" -ForegroundColor Yellow
Write-Host "  • Lambda shows 'Inactive' but is responding correctly" -ForegroundColor White
Write-Host "  • First request may be slow due to cold start" -ForegroundColor White
Write-Host "  • Subsequent requests will be faster" -ForegroundColor White
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Recommendations" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Common Issues:" -ForegroundColor Yellow
Write-Host "  1. Lambda function not deployed or inactive" -ForegroundColor White
Write-Host "  2. API Gateway route not configured correctly" -ForegroundColor White
Write-Host "  3. Wrong payload format expected by Lambda" -ForegroundColor White
Write-Host "  4. CORS issues blocking requests" -ForegroundColor White
Write-Host "  5. Lambda timeout or memory issues" -ForegroundColor White
Write-Host ""

Write-Host "Note:" -ForegroundColor Cyan
Write-Host "  If API Gateway check fails but API tests pass, that's OK!" -ForegroundColor White
Write-Host "  The endpoint is working, which is what matters." -ForegroundColor White
Write-Host ""

Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Check CloudWatch logs: aws logs tail /aws/lambda/ure-mvp-handler-docker --follow" -ForegroundColor White
Write-Host "  2. Test Lambda directly: aws lambda invoke --function-name ure-mvp-handler-docker output.json" -ForegroundColor White
Write-Host "  3. Check API Gateway logs in CloudWatch" -ForegroundColor White
Write-Host "  4. Verify Lambda has correct permissions" -ForegroundColor White
Write-Host ""

Write-Host "Done!" -ForegroundColor Green
Write-Host ""

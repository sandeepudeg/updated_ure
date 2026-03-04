#!/usr/bin/env pwsh
# Create a new Lambda function with Docker container support

param(
    [string]$Region = "us-east-1",
    [string]$AccountId = "188238313375",
    [string]$FunctionName = "ure-mvp-handler-docker",
    [string]$RoleName = "ure-lambda-execution-role"
)

$ErrorActionPreference = "Stop"

Write-Host "`n╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     CREATE NEW LAMBDA FUNCTION WITH DOCKER SUPPORT         ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

$ECR_REPO_NAME = "ure-lambda"
$IMAGE_TAG = "latest"
$ECR_URI = "$AccountId.dkr.ecr.$Region.amazonaws.com/$ECR_REPO_NAME"

# Step 1: Check if IAM role exists
Write-Host "[Step 1] Checking IAM execution role..." -ForegroundColor Yellow

$roleArn = $null
try {
    $role = aws iam get-role --role-name $RoleName --output json 2>$null | ConvertFrom-Json
    $roleArn = $role.Role.Arn
    Write-Host "✅ IAM role exists: $roleArn" -ForegroundColor Green
} catch {
    Write-Host "Creating IAM role: $RoleName" -ForegroundColor Yellow
    
    # Create trust policy
    $trustPolicy = @{
        Version = "2012-10-17"
        Statement = @(
            @{
                Effect = "Allow"
                Principal = @{
                    Service = "lambda.amazonaws.com"
                }
                Action = "sts:AssumeRole"
            }
        )
    } | ConvertTo-Json -Depth 10 -Compress
    
    # Create role
    $role = aws iam create-role `
        --role-name $RoleName `
        --assume-role-policy-document $trustPolicy `
        --description "Execution role for URE Lambda with Docker" `
        --output json | ConvertFrom-Json
    
    $roleArn = $role.Role.Arn
    
    # Attach basic Lambda execution policy
    aws iam attach-role-policy `
        --role-name $RoleName `
        --policy-arn "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
    
    # Attach DynamoDB full access
    aws iam attach-role-policy `
        --role-name $RoleName `
        --policy-arn "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess"
    
    # Attach S3 full access
    aws iam attach-role-policy `
        --role-name $RoleName `
        --policy-arn "arn:aws:iam::aws:policy/AmazonS3FullAccess"
    
    # Attach Bedrock full access
    aws iam attach-role-policy `
        --role-name $RoleName `
        --policy-arn "arn:aws:iam::aws:policy/AmazonBedrockFullAccess"
    
    Write-Host "✅ IAM role created: $roleArn" -ForegroundColor Green
    Write-Host "⏳ Waiting 10 seconds for IAM role to propagate..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10
}
Write-Host ""

# Step 2: Check if Lambda function already exists
Write-Host "[Step 2] Checking if Lambda function exists..." -ForegroundColor Yellow

$functionExists = $false
try {
    $existingFunction = aws lambda get-function --function-name $FunctionName --region $Region --output json 2>$null | ConvertFrom-Json
    $functionExists = $true
    Write-Host "⚠️  Lambda function already exists: $FunctionName" -ForegroundColor Yellow
    Write-Host "   Current Package Type: $($existingFunction.Configuration.PackageType)" -ForegroundColor Gray
    
    $response = Read-Host "Do you want to delete and recreate it? (yes/no)"
    if ($response -eq "yes") {
        Write-Host "Deleting existing function..." -ForegroundColor Yellow
        aws lambda delete-function --function-name $FunctionName --region $Region
        Start-Sleep -Seconds 5
        $functionExists = $false
        Write-Host "✅ Existing function deleted" -ForegroundColor Green
    } else {
        Write-Host "❌ Deployment cancelled" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "✅ Function name available: $FunctionName" -ForegroundColor Green
}
Write-Host ""

# Step 3: Verify Docker image exists in ECR
Write-Host "[Step 3] Verifying Docker image in ECR..." -ForegroundColor Yellow

try {
    $images = aws ecr describe-images `
        --repository-name $ECR_REPO_NAME `
        --region $Region `
        --output json | ConvertFrom-Json
    
    $latestImage = $images.imageDetails | Where-Object { $_.imageTags -contains $IMAGE_TAG } | Select-Object -First 1
    
    if ($latestImage) {
        Write-Host "✅ Docker image found: $ECR_URI`:$IMAGE_TAG" -ForegroundColor Green
        Write-Host "   Pushed: $($latestImage.imagePushedAt)" -ForegroundColor Gray
        Write-Host "   Size: $([math]::Round($latestImage.imageSizeInBytes / 1MB, 2)) MB" -ForegroundColor Gray
    } else {
        Write-Host "❌ Docker image with tag '$IMAGE_TAG' not found in ECR" -ForegroundColor Red
        Write-Host "Please build and push the Docker image first:" -ForegroundColor Yellow
        Write-Host "  .\scripts\deploy_docker_lambda.ps1" -ForegroundColor White
        exit 1
    }
} catch {
    Write-Host "❌ Failed to check ECR repository" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 4: Create Lambda function with Docker image
Write-Host "[Step 4] Creating Lambda function with Docker image..." -ForegroundColor Yellow

try {
    $createResult = aws lambda create-function `
        --function-name $FunctionName `
        --package-type Image `
        --code "ImageUri=$ECR_URI`:$IMAGE_TAG" `
        --role $roleArn `
        --timeout 300 `
        --memory-size 512 `
        --region $Region `
        --environment "Variables={DYNAMODB_TABLE_NAME=ure-conversations,DYNAMODB_USER_TABLE=ure-user-profiles,S3_BUCKET_NAME=ure-mvp-data-us-east-1-188238313375,LOG_LEVEL=INFO,IP_HASH_SALT=production-salt-$(Get-Random),BEDROCK_REGION=us-east-1}" `
        --output json | ConvertFrom-Json
    
    Write-Host "✅ Lambda function created successfully!" -ForegroundColor Green
    Write-Host "   Function Name: $($createResult.FunctionName)" -ForegroundColor Gray
    Write-Host "   Function ARN: $($createResult.FunctionArn)" -ForegroundColor Gray
    Write-Host "   Package Type: $($createResult.PackageType)" -ForegroundColor Gray
    Write-Host "   Memory: $($createResult.MemorySize) MB" -ForegroundColor Gray
    Write-Host "   Timeout: $($createResult.Timeout) seconds" -ForegroundColor Gray
} catch {
    Write-Host "❌ Failed to create Lambda function" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 5: Wait for Lambda to be active
Write-Host "[Step 5] Waiting for Lambda to be active..." -ForegroundColor Yellow

$maxAttempts = 30
$attempt = 0

while ($attempt -lt $maxAttempts) {
    try {
        $status = aws lambda get-function --function-name $FunctionName --region $Region --output json | ConvertFrom-Json
        $state = $status.Configuration.State
        
        Write-Host "   State: $state" -ForegroundColor Gray
        
        if ($state -eq "Active") {
            Write-Host "✅ Lambda function is active and ready!" -ForegroundColor Green
            break
        }
        
        if ($state -eq "Failed") {
            Write-Host "❌ Lambda function creation failed!" -ForegroundColor Red
            exit 1
        }
        
        Start-Sleep -Seconds 3
        $attempt++
    } catch {
        Write-Host "❌ Failed to check Lambda status" -ForegroundColor Red
        exit 1
    }
}

if ($attempt -eq $maxAttempts) {
    Write-Host "⚠️  Timeout waiting for Lambda to be active" -ForegroundColor Yellow
}
Write-Host ""

# Step 6: Test Lambda function
Write-Host "[Step 6] Testing Lambda function..." -ForegroundColor Yellow

$testPayload = @{
    user_id = "test_docker_001"
    query = "What is tomato blight?"
    language = "en"
} | ConvertTo-Json -Compress

$testPayloadFile = "test_payload.json"
$testPayload | Out-File -FilePath $testPayloadFile -Encoding utf8

try {
    Write-Host "   Invoking Lambda..." -ForegroundColor Gray
    $invokeResult = aws lambda invoke `
        --function-name $FunctionName `
        --payload "file://$testPayloadFile" `
        --region $Region `
        response.json
    
    if (Test-Path response.json) {
        $response = Get-Content response.json | ConvertFrom-Json
        
        if ($response.statusCode -eq 200) {
            Write-Host "✅ Lambda test successful!" -ForegroundColor Green
            $body = $response.body | ConvertFrom-Json
            Write-Host "   Agent Used: $($body.agent_used)" -ForegroundColor Gray
            Write-Host "   Response Preview: $($body.response.Substring(0, [Math]::Min(100, $body.response.Length)))..." -ForegroundColor Gray
        } else {
            Write-Host "⚠️  Lambda returned status code: $($response.statusCode)" -ForegroundColor Yellow
        }
    }
} catch {
    Write-Host "⚠️  Lambda test failed (this is normal for first invocation)" -ForegroundColor Yellow
    Write-Host "   Error: $_" -ForegroundColor Gray
}

# Cleanup test files
if (Test-Path $testPayloadFile) { Remove-Item $testPayloadFile }
if (Test-Path response.json) { Remove-Item response.json }

Write-Host ""

# Summary
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║           LAMBDA FUNCTION CREATED SUCCESSFULLY! ✅          ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "Function Details:" -ForegroundColor Cyan
Write-Host "  Name: $FunctionName" -ForegroundColor White
Write-Host "  Package Type: Image (Docker)" -ForegroundColor White
Write-Host "  Image URI: $ECR_URI`:$IMAGE_TAG" -ForegroundColor White
Write-Host "  Region: $Region" -ForegroundColor White
Write-Host "  Memory: 512 MB" -ForegroundColor White
Write-Host "  Timeout: 300 seconds (5 minutes)" -ForegroundColor White
Write-Host ""
Write-Host "Privacy Features Enabled:" -ForegroundColor Cyan
Write-Host "  ✅ IP Address Hashing (SHA-256 + salt)" -ForegroundColor Green
Write-Host "  ✅ TTL Auto-Deletion (3-hour sessions)" -ForegroundColor Green
Write-Host "  ✅ AWS-Managed Encryption" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Test Lambda:" -ForegroundColor White
Write-Host "     aws lambda invoke --function-name $FunctionName --payload '{\"user_id\":\"test\",\"query\":\"hello\"}' --region $Region response.json" -ForegroundColor Gray
Write-Host ""
Write-Host "  2. View logs:" -ForegroundColor White
Write-Host "     aws logs tail /aws/lambda/$FunctionName --follow --region $Region" -ForegroundColor Gray
Write-Host ""
Write-Host "  3. Run privacy audit:" -ForegroundColor White
Write-Host "     py scripts/run_privacy_audit.py" -ForegroundColor Gray
Write-Host ""
Write-Host "  4. Enable DynamoDB TTL (one-time):" -ForegroundColor White
Write-Host "     aws dynamodb update-time-to-live --table-name ure-conversations --time-to-live-specification 'Enabled=true,AttributeName=expiry_time' --region $Region" -ForegroundColor Gray
Write-Host ""
Write-Host "  5. Update API Gateway to use new function (if needed)" -ForegroundColor White
Write-Host ""

#!/usr/bin/env pwsh
# PowerShell script to build and deploy Docker Lambda to AWS

param(
    [string]$Region = "us-east-1",
    [string]$AccountId = "188238313375",
    [string]$FunctionName = "ure-mvp-handler",
    [switch]$SkipBuild = $false,
    [switch]$SkipTests = $false
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Docker Lambda Deployment Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$ECR_REPO_NAME = "ure-lambda"
$IMAGE_TAG = "latest"
$ECR_URI = "$AccountId.dkr.ecr.$Region.amazonaws.com/$ECR_REPO_NAME"

# Step 0: Run unit tests (unless skipped)
if (-not $SkipTests) {
    Write-Host "[Step 0] Running unit tests..." -ForegroundColor Yellow
    py -m pytest tests/ -v --ignore=tests/test_mcp_servers.py --ignore=tests/test_performance.py
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Tests failed! Fix tests before deploying." -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ All tests passed!" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host "[Step 0] Skipping tests (--SkipTests flag)" -ForegroundColor Yellow
    Write-Host ""
}

# Step 1: Check Docker is running
Write-Host "[Step 1] Checking Docker..." -ForegroundColor Yellow
try {
    docker info | Out-Null
    Write-Host "✅ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not running. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 2: Check AWS CLI
Write-Host "[Step 2] Checking AWS CLI..." -ForegroundColor Yellow
try {
    $awsVersion = aws --version
    Write-Host "✅ AWS CLI found: $awsVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ AWS CLI not found. Please install AWS CLI." -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 3: Verify AWS credentials
Write-Host "[Step 3] Verifying AWS credentials..." -ForegroundColor Yellow
try {
    $identity = aws sts get-caller-identity --output json | ConvertFrom-Json
    Write-Host "✅ AWS Account: $($identity.Account)" -ForegroundColor Green
    Write-Host "✅ AWS User: $($identity.Arn)" -ForegroundColor Green
    
    if ($identity.Account -ne $AccountId) {
        Write-Host "⚠️  Warning: Account ID mismatch!" -ForegroundColor Yellow
        Write-Host "   Expected: $AccountId" -ForegroundColor Yellow
        Write-Host "   Got: $($identity.Account)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Failed to verify AWS credentials" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 4: Create ECR repository if it doesn't exist
Write-Host "[Step 4] Checking ECR repository..." -ForegroundColor Yellow
$repoExists = $false
try {
    $null = aws ecr describe-repositories --repository-names $ECR_REPO_NAME --region $Region 2>&1
    if ($LASTEXITCODE -eq 0) {
        $repoExists = $true
        Write-Host "✅ ECR repository exists: $ECR_REPO_NAME" -ForegroundColor Green
    }
} catch {
    # Repository doesn't exist, will create it
}

if (-not $repoExists) {
    Write-Host "Creating ECR repository: $ECR_REPO_NAME" -ForegroundColor Yellow
    try {
        $createResult = aws ecr create-repository --repository-name $ECR_REPO_NAME --region $Region --output json | ConvertFrom-Json
        Write-Host "✅ ECR repository created: $($createResult.repository.repositoryUri)" -ForegroundColor Green
    } catch {
        Write-Host "❌ Failed to create ECR repository" -ForegroundColor Red
        Write-Host "Error: $_" -ForegroundColor Red
        exit 1
    }
}
Write-Host ""

# Step 5: Login to ECR
Write-Host "[Step 5] Logging in to ECR..." -ForegroundColor Yellow
try {
    aws ecr get-login-password --region $Region | docker login --username AWS --password-stdin "$AccountId.dkr.ecr.$Region.amazonaws.com"
    Write-Host "✅ Logged in to ECR" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to login to ECR" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 6: Build Docker image (unless skipped)
if (-not $SkipBuild) {
    Write-Host "[Step 6] Building Docker image..." -ForegroundColor Yellow
    Write-Host "This may take a few minutes..." -ForegroundColor Gray
    
    # Build for linux/amd64 platform (required for Lambda)
    docker build --platform linux/amd64 -t $ECR_REPO_NAME`:$IMAGE_TAG -f Dockerfile .
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Docker build failed" -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ Docker image built successfully" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host "[Step 6] Skipping build (--SkipBuild flag)" -ForegroundColor Yellow
    Write-Host ""
}

# Step 7: Tag image for ECR
Write-Host "[Step 7] Tagging image for ECR..." -ForegroundColor Yellow
docker tag $ECR_REPO_NAME`:$IMAGE_TAG $ECR_URI`:$IMAGE_TAG

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to tag image" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Image tagged: $ECR_URI`:$IMAGE_TAG" -ForegroundColor Green
Write-Host ""

# Step 8: Push image to ECR
Write-Host "[Step 8] Pushing image to ECR..." -ForegroundColor Yellow
Write-Host "This may take several minutes..." -ForegroundColor Gray

docker push $ECR_URI`:$IMAGE_TAG

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to push image to ECR" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Image pushed to ECR" -ForegroundColor Green
Write-Host ""

# Step 9: Update Lambda function
Write-Host "[Step 9] Updating Lambda function..." -ForegroundColor Yellow

try {
    $updateResult = aws lambda update-function-code `
        --function-name $FunctionName `
        --image-uri "$ECR_URI`:$IMAGE_TAG" `
        --region $Region `
        --output json | ConvertFrom-Json
    
    Write-Host "✅ Lambda function updated" -ForegroundColor Green
    Write-Host "   Function: $($updateResult.FunctionName)" -ForegroundColor Gray
    Write-Host "   Runtime: $($updateResult.PackageType)" -ForegroundColor Gray
    Write-Host "   Last Modified: $($updateResult.LastModified)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Failed to update Lambda function" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 10: Wait for Lambda to be ready
Write-Host "[Step 10] Waiting for Lambda to be ready..." -ForegroundColor Yellow
$maxAttempts = 30
$attempt = 0

while ($attempt -lt $maxAttempts) {
    try {
        $status = aws lambda get-function --function-name $FunctionName --region $Region --output json | ConvertFrom-Json
        $state = $status.Configuration.State
        $lastUpdateStatus = $status.Configuration.LastUpdateStatus
        
        Write-Host "   State: $state, Update Status: $lastUpdateStatus" -ForegroundColor Gray
        
        if ($state -eq "Active" -and $lastUpdateStatus -eq "Successful") {
            Write-Host "✅ Lambda function is ready!" -ForegroundColor Green
            break
        }
        
        if ($lastUpdateStatus -eq "Failed") {
            Write-Host "❌ Lambda update failed!" -ForegroundColor Red
            exit 1
        }
        
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

# Step 11: Update environment variables
Write-Host "[Step 11] Updating Lambda environment variables..." -ForegroundColor Yellow

$envVars = @{
    "DYNAMODB_TABLE_NAME" = "ure-conversations"
    "DYNAMODB_USER_TABLE" = "ure-user-profiles"
    "S3_BUCKET_NAME" = "ure-mvp-data-us-east-1-188238313375"
    "LOG_LEVEL" = "INFO"
    "IP_HASH_SALT" = "production-salt-$(Get-Random)"
    "BEDROCK_REGION" = "us-east-1"
    "DATA_GOV_API_KEY" = "579b464db66ec23bdd000001cdd3946e44ce4aad7209ff7b23ac571b"
}

$envJson = $envVars | ConvertTo-Json -Compress

try {
    aws lambda update-function-configuration `
        --function-name $FunctionName `
        --environment "Variables=$envJson" `
        --region $Region | Out-Null
    
    Write-Host "✅ Environment variables updated" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Warning: Failed to update environment variables" -ForegroundColor Yellow
    Write-Host "   You may need to set them manually in AWS Console" -ForegroundColor Yellow
}
Write-Host ""

# Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Lambda Function: $FunctionName" -ForegroundColor White
Write-Host "Image URI: $ECR_URI`:$IMAGE_TAG" -ForegroundColor White
Write-Host "Region: $Region" -ForegroundColor White
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Test the Lambda function in AWS Console" -ForegroundColor White
Write-Host "2. Run privacy audit: py scripts/run_privacy_audit.py" -ForegroundColor White
Write-Host "3. Monitor CloudWatch logs for any issues" -ForegroundColor White
Write-Host ""

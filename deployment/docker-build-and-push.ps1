# Docker Build and Push Script for AWS Lambda (PowerShell)
# Builds Docker image and pushes to Amazon ECR

param(
    [string]$AwsRegion = "us-east-1",
    [string]$AwsAccountId = "188238313375",
    [string]$EcrRepository = "ure-lambda-privacy",
    [string]$ImageTag = "latest"
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Green
Write-Host "AWS Lambda Docker Build & Push" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Check if AWS CLI is installed
try {
    aws --version | Out-Null
} catch {
    Write-Host "✗ AWS CLI not found. Please install AWS CLI." -ForegroundColor Red
    exit 1
}

# Check if Docker is installed
try {
    docker --version | Out-Null
} catch {
    Write-Host "✗ Docker not found. Please install Docker." -ForegroundColor Red
    exit 1
}

Write-Host "Configuration:" -ForegroundColor Yellow
Write-Host "  AWS Region: $AwsRegion"
Write-Host "  AWS Account: $AwsAccountId"
Write-Host "  ECR Repository: $EcrRepository"
Write-Host "  Image Tag: $ImageTag"
Write-Host ""

# Get ECR login token
Write-Host "→ Logging in to Amazon ECR..." -ForegroundColor Yellow
$loginCommand = aws ecr get-login-password --region $AwsRegion
if ($LASTEXITCODE -eq 0) {
    $loginCommand | docker login --username AWS --password-stdin "$AwsAccountId.dkr.ecr.$AwsRegion.amazonaws.com"
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Successfully logged in to ECR" -ForegroundColor Green
    } else {
        Write-Host "✗ Failed to login to ECR" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "✗ Failed to get ECR login token" -ForegroundColor Red
    exit 1
}

# Create ECR repository if it doesn't exist
Write-Host "→ Checking ECR repository..." -ForegroundColor Yellow
try {
    aws ecr describe-repositories --repository-names $EcrRepository --region $AwsRegion 2>&1 | Out-Null
} catch {
    Write-Host "  Creating ECR repository..." -ForegroundColor Yellow
    aws ecr create-repository --repository-name $EcrRepository --region $AwsRegion | Out-Null
}
Write-Host "✓ ECR repository ready" -ForegroundColor Green

# Build Docker image
Write-Host "→ Building Docker image..." -ForegroundColor Yellow
docker build -t "${EcrRepository}:${ImageTag}" .

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Docker image built successfully" -ForegroundColor Green
} else {
    Write-Host "✗ Docker build failed" -ForegroundColor Red
    exit 1
}

# Tag image for ECR
$EcrImageUri = "$AwsAccountId.dkr.ecr.$AwsRegion.amazonaws.com/${EcrRepository}:${ImageTag}"
Write-Host "→ Tagging image for ECR..." -ForegroundColor Yellow
docker tag "${EcrRepository}:${ImageTag}" $EcrImageUri

# Push to ECR
Write-Host "→ Pushing image to ECR..." -ForegroundColor Yellow
docker push $EcrImageUri

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Image pushed successfully" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to push image" -ForegroundColor Red
    exit 1
}

# Get image digest
$ImageDigest = aws ecr describe-images `
    --repository-name $EcrRepository `
    --image-ids imageTag=$ImageTag `
    --region $AwsRegion `
    --query 'imageDetails[0].imageDigest' `
    --output text

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Build Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Image URI: $EcrImageUri"
Write-Host "Image Digest: $ImageDigest"
Write-Host ""
Write-Host "To update Lambda function, run:"
Write-Host "  aws lambda update-function-code \"
Write-Host "    --function-name ure-mvp-handler \"
Write-Host "    --image-uri $EcrImageUri \"
Write-Host "    --region $AwsRegion"
Write-Host ""

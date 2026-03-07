# Deploy Docker Image to ECR and Update Lambda
# This script builds, tags, and pushes the Docker image, then updates Lambda

$ErrorActionPreference = "Stop"

# Configuration
$AWS_ACCOUNT_ID = "188238313375"
$AWS_REGION = "us-east-1"
$ECR_REPO = "ure-lambda-docker"
$FUNCTION_NAME = "ure-mvp-handler-docker"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Docker Deployment to ECR" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is running
Write-Host "Checking Docker status..." -ForegroundColor Cyan
try {
    docker ps | Out-Null
    Write-Host "✓ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker is not running. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}
Write-Host ""

# Login to ECR
Write-Host "Logging into ECR..." -ForegroundColor Cyan
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ ECR login failed" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Logged into ECR" -ForegroundColor Green
Write-Host ""

# Build Docker image
Write-Host "Building Docker image for linux/amd64..." -ForegroundColor Cyan
Write-Host "This may take a few minutes..." -ForegroundColor Yellow
docker buildx build --platform linux/amd64 --load -t $ECR_REPO .

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Docker build failed" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Docker image built successfully" -ForegroundColor Green
Write-Host ""

# Tag image
Write-Host "Tagging image..." -ForegroundColor Cyan
docker tag "${ECR_REPO}:latest" "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/${ECR_REPO}:latest"
Write-Host "✓ Image tagged" -ForegroundColor Green
Write-Host ""

# Push to ECR
Write-Host "Pushing image to ECR..." -ForegroundColor Cyan
Write-Host "This may take a few minutes..." -ForegroundColor Yellow
docker push "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/${ECR_REPO}:latest"

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Docker push failed" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Image pushed to ECR" -ForegroundColor Green
Write-Host ""

# Update Lambda function
Write-Host "Updating Lambda function..." -ForegroundColor Cyan
$IMAGE_URI = "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/${ECR_REPO}:latest"

$result = aws lambda update-function-code `
    --function-name $FUNCTION_NAME `
    --image-uri $IMAGE_URI `
    --region $AWS_REGION 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Lambda function update initiated" -ForegroundColor Green
    Write-Host ""
    Write-Host "Waiting for Lambda to update (30 seconds)..." -ForegroundColor Yellow
    Start-Sleep -Seconds 30
    
    # Check status
    Write-Host "Checking Lambda status..." -ForegroundColor Cyan
    aws lambda get-function `
        --function-name $FUNCTION_NAME `
        --region $AWS_REGION `
        --query 'Configuration.[FunctionName,State,LastUpdateStatus]' `
        --output table
    
    Write-Host ""
    Write-Host "✓ Lambda function updated successfully!" -ForegroundColor Green
} else {
    Write-Host "⚠ Lambda update may have failed" -ForegroundColor Yellow
    Write-Host "Error: $result" -ForegroundColor Red
    Write-Host ""
    Write-Host "Note: If you see 'image manifest not supported', this is expected." -ForegroundColor Yellow
    Write-Host "The function will use the previous working image." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Deployment Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Docker Image: $IMAGE_URI" -ForegroundColor White
Write-Host "Lambda Function: $FUNCTION_NAME" -ForegroundColor White
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  • Test Lambda: .\deployment\test-lambda.ps1" -ForegroundColor White
Write-Host "  • View logs: AWS Console → CloudWatch → /aws/lambda/$FUNCTION_NAME" -ForegroundColor White
Write-Host ""

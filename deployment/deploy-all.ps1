# Complete End-to-End Deployment Script for GramSetu URE MVP
# This script deploys everything: Docker image, Lambda function, and Web UI

param(
    [string]$SkipGit = "false",
    [string]$SkipDocker = "false",
    [string]$SkipWeb = "false"
)

$ErrorActionPreference = "Stop"

# Configuration
$AWS_ACCOUNT_ID = "188238313375"
$AWS_REGION = "us-east-1"
$ECR_REPO = "ure-lambda-docker"
$FUNCTION_NAME = "ure-mvp-handler-docker"
$S3_BUCKET = "ure-mvp-data-us-east-1-188238313375"
$CLOUDFRONT_DIST = "E354ZTACSUHKWS"
$WEB_DIR = "src/web/v2"
$S3_PREFIX = "web-ui"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  GramSetu URE MVP - Full Deployment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Git Commit and Push
if ($SkipGit -ne "true") {
    Write-Host "[1/4] Committing and Pushing to Git..." -ForegroundColor Green
    Write-Host ""
    
    git status --short
    
    $commitMessage = Read-Host "Enter commit message (or press Enter to skip git)"
    
    if ($commitMessage) {
        git add .
        git commit -m $commitMessage
        git push
        Write-Host "✓ Git push complete!" -ForegroundColor Green
    } else {
        Write-Host "⊘ Skipping git push" -ForegroundColor Yellow
    }
    Write-Host ""
} else {
    Write-Host "[1/4] Skipping Git (as requested)" -ForegroundColor Yellow
    Write-Host ""
}

# Step 2: Docker Build and Push
if ($SkipDocker -ne "true") {
    Write-Host "[2/4] Building and Pushing Docker Image..." -ForegroundColor Green
    Write-Host ""
    
    # Check if Docker is running
    try {
        docker ps | Out-Null
    } catch {
        Write-Host "✗ Docker is not running. Please start Docker Desktop." -ForegroundColor Red
        exit 1
    }
    
    # Login to ECR
    Write-Host "Logging into ECR..." -ForegroundColor Cyan
    aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"
    
    # Build Docker image
    Write-Host "Building Docker image for linux/amd64..." -ForegroundColor Cyan
    docker buildx build --platform linux/amd64 --load -t $ECR_REPO .
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ Docker build failed" -ForegroundColor Red
        exit 1
    }
    
    # Tag image
    Write-Host "Tagging image..." -ForegroundColor Cyan
    docker tag "${ECR_REPO}:latest" "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/${ECR_REPO}:latest"
    
    # Push to ECR
    Write-Host "Pushing to ECR..." -ForegroundColor Cyan
    docker push "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/${ECR_REPO}:latest"
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ Docker push failed" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "✓ Docker image pushed successfully!" -ForegroundColor Green
    Write-Host ""
    
    # Update Lambda function
    Write-Host "Updating Lambda function..." -ForegroundColor Cyan
    $IMAGE_URI = "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/${ECR_REPO}:latest"
    
    aws lambda update-function-code `
        --function-name $FUNCTION_NAME `
        --image-uri $IMAGE_URI `
        --region $AWS_REGION | Out-Null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Lambda function updated!" -ForegroundColor Green
    } else {
        Write-Host "⚠ Lambda update may have failed (check manually)" -ForegroundColor Yellow
    }
    
    Write-Host ""
} else {
    Write-Host "[2/4] Skipping Docker (as requested)" -ForegroundColor Yellow
    Write-Host ""
}

# Step 3: Deploy Web UI
if ($SkipWeb -ne "true") {
    Write-Host "[3/4] Deploying Web UI to S3..." -ForegroundColor Green
    Write-Host ""
    
    # Upload HTML files
    Write-Host "Uploading HTML files..." -ForegroundColor Cyan
    aws s3 cp "$WEB_DIR/gramsetu-agents.html" "s3://$S3_BUCKET/$S3_PREFIX/gramsetu-agents.html" --content-type "text/html"
    aws s3 cp "$WEB_DIR/gramsetu-mobile.html" "s3://$S3_BUCKET/$S3_PREFIX/gramsetu-mobile.html" --content-type "text/html"
    
    # Upload JavaScript and CSS
    Write-Host "Uploading JavaScript and CSS..." -ForegroundColor Cyan
    aws s3 cp "$WEB_DIR/config.js" "s3://$S3_BUCKET/$S3_PREFIX/config.js" --content-type "application/javascript"
    aws s3 cp "$WEB_DIR/app.js" "s3://$S3_BUCKET/$S3_PREFIX/app.js" --content-type "application/javascript"
    aws s3 cp "$WEB_DIR/styles.css" "s3://$S3_BUCKET/$S3_PREFIX/styles.css" --content-type "text/css"
    
    # Invalidate CloudFront cache
    Write-Host "Invalidating CloudFront cache..." -ForegroundColor Cyan
    aws cloudfront create-invalidation --distribution-id $CLOUDFRONT_DIST --paths "/*" | Out-Null
    
    Write-Host "✓ Web UI deployed successfully!" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host "[3/4] Skipping Web UI (as requested)" -ForegroundColor Yellow
    Write-Host ""
}

# Step 4: Summary and Testing
Write-Host "[4/4] Deployment Summary" -ForegroundColor Green
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Deployment Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "📦 Resources Deployed:" -ForegroundColor Yellow
Write-Host "  • Docker Image: $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/${ECR_REPO}:latest"
Write-Host "  • Lambda Function: $FUNCTION_NAME"
Write-Host "  • S3 Bucket: $S3_BUCKET"
Write-Host "  • CloudFront Distribution: $CLOUDFRONT_DIST"
Write-Host ""

Write-Host "🌐 Live URLs:" -ForegroundColor Yellow
Write-Host "  • Desktop UI: https://d3v7khazsfb4vd.cloudfront.net/gramsetu-agents.html"
Write-Host "  • Mobile UI: https://d3v7khazsfb4vd.cloudfront.net/gramsetu-mobile.html"
Write-Host "  • API Endpoint: https://8938dqxf33.execute-api.us-east-1.amazonaws.com/dev/query"
Write-Host ""

Write-Host "🧪 Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Test Lambda function: .\deployment\test-lambda.ps1"
Write-Host "  2. Test Web UI: Open URLs above in browser"
Write-Host "  3. Monitor logs: AWS Console → CloudWatch → Log Groups"
Write-Host ""

Write-Host "✓ All done!" -ForegroundColor Green

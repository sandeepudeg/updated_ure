#!/usr/bin/env pwsh
# Fix Deployment to Use Existing Data Bucket

Write-Host "`n🔧 Fixing Deployment to Use Existing Data Bucket" -ForegroundColor Cyan
Write-Host "===============================================`n" -ForegroundColor Cyan

$dataBucket = "ure-mvp-data-us-east-1-188238313375"
$webUIPrefix = "web-ui/"

# Step 1: Upload web UI files to data bucket
Write-Host "Step 1: Uploading web UI files to data bucket..." -ForegroundColor Yellow
Write-Host "  Bucket: $dataBucket" -ForegroundColor Gray
Write-Host "  Prefix: $webUIPrefix" -ForegroundColor Gray

try {
    # Upload files with correct content types
    aws s3 cp src/web/aws-native/index.html s3://$dataBucket/${webUIPrefix}index.html --content-type "text/html" --cache-control "max-age=300"
    aws s3 cp src/web/aws-native/styles.css s3://$dataBucket/${webUIPrefix}styles.css --content-type "text/css" --cache-control "max-age=300"
    aws s3 cp src/web/aws-native/app.js s3://$dataBucket/${webUIPrefix}app.js --content-type "application/javascript" --cache-control "max-age=300"
    aws s3 cp src/web/aws-native/config.js s3://$dataBucket/${webUIPrefix}config.js --content-type "application/javascript" --cache-control "max-age=300"
    
    Write-Host "✓ Files uploaded successfully" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed to upload files: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Step 2: Verify files
Write-Host "`nStep 2: Verifying uploaded files..." -ForegroundColor Yellow
$files = aws s3 ls s3://$dataBucket/$webUIPrefix
if ($files) {
    Write-Host "✓ Files verified:" -ForegroundColor Green
    $files | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }
} else {
    Write-Host "✗ No files found" -ForegroundColor Red
    exit 1
}

# Step 3: Update existing CloudFront distribution
Write-Host "`nStep 3: Updating CloudFront distribution..." -ForegroundColor Yellow
$distId = "E354ZTACSUHKWS"

Write-Host "  Current distribution: $distId" -ForegroundColor Gray
Write-Host "  Updating origin to use: $dataBucket/$webUIPrefix" -ForegroundColor Gray

# Note: CloudFront distribution update requires complex JSON manipulation
# For now, we'll create a new distribution with correct settings

Write-Host "`n⚠ Note: Existing CloudFront distribution points to old bucket" -ForegroundColor Yellow
Write-Host "  Option 1: Create new distribution (recommended)" -ForegroundColor Yellow
Write-Host "  Option 2: Manually update in AWS Console" -ForegroundColor Yellow

Write-Host "`nWould you like to create a new CloudFront distribution? (Y/N)" -ForegroundColor Cyan
$response = Read-Host

if ($response -eq "Y" -or $response -eq "y") {
    Write-Host "`nCreating new CloudFront distribution..." -ForegroundColor Yellow
    py scripts/deploy_web_ui_to_s3.py
} else {
    Write-Host "`n✓ Files are uploaded and ready" -ForegroundColor Green
    Write-Host "`nManual steps to update CloudFront:" -ForegroundColor Yellow
    Write-Host "1. Go to AWS Console > CloudFront" -ForegroundColor White
    Write-Host "2. Select distribution: $distId" -ForegroundColor White
    Write-Host "3. Edit Origin:" -ForegroundColor White
    Write-Host "   - Origin Domain: $dataBucket.s3.us-east-1.amazonaws.com" -ForegroundColor White
    Write-Host "   - Origin Path: /$webUIPrefix" -ForegroundColor White
    Write-Host "4. Save changes" -ForegroundColor White
}

Write-Host ""

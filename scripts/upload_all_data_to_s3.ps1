#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Upload all data to S3 bucket for GramSetu
.DESCRIPTION
    Uploads crop disease images, government schemes, and market prices to S3
#>

param(
    [string]$Bucket = "ure-mvp-data-us-east-1-188238313375",
    [switch]$DryRun,
    [switch]$Force
)

$ErrorActionPreference = "Stop"

Write-Host "`n📦 GramSetu Data Upload to S3" -ForegroundColor Cyan
Write-Host "============================`n" -ForegroundColor Cyan

# Configuration
$dataDir = "data"
$bucket = $Bucket

# Check if data directory exists
if (-not (Test-Path $dataDir)) {
    Write-Host "✗ Data directory not found: $dataDir" -ForegroundColor Red
    Write-Host "  Please ensure you have downloaded the datasets" -ForegroundColor Yellow
    exit 1
}

Write-Host "Configuration:" -ForegroundColor White
Write-Host "  Bucket: $bucket" -ForegroundColor Gray
Write-Host "  Data Directory: $dataDir" -ForegroundColor Gray
Write-Host "  Dry Run: $DryRun" -ForegroundColor Gray
Write-Host ""

# Function to upload directory
function Upload-Directory {
    param(
        [string]$LocalPath,
        [string]$S3Prefix,
        [string]$Description
    )
    
    Write-Host "`n📁 $Description" -ForegroundColor Yellow
    Write-Host "   Local: $LocalPath" -ForegroundColor Gray
    Write-Host "   S3: s3://$bucket/$S3Prefix" -ForegroundColor Gray
    
    if (-not (Test-Path $LocalPath)) {
        Write-Host "   ⚠ Directory not found, skipping..." -ForegroundColor Yellow
        return
    }
    
    # Count files
    $fileCount = (Get-ChildItem -Path $LocalPath -Recurse -File | Measure-Object).Count
    Write-Host "   Files to upload: $fileCount" -ForegroundColor Gray
    
    if ($fileCount -eq 0) {
        Write-Host "   ⚠ No files found, skipping..." -ForegroundColor Yellow
        return
    }
    
    if ($DryRun) {
        Write-Host "   [DRY RUN] Would upload $fileCount files" -ForegroundColor Cyan
        return
    }
    
    # Upload with progress
    Write-Host "   Uploading..." -ForegroundColor Gray
    
    try {
        $result = aws s3 sync $LocalPath s3://$bucket/$S3Prefix --delete 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ✓ Upload complete" -ForegroundColor Green
        } else {
            Write-Host "   ✗ Upload failed: $result" -ForegroundColor Red
        }
    } catch {
        Write-Host "   ✗ Upload error: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Function to upload single file
function Upload-File {
    param(
        [string]$LocalPath,
        [string]$S3Key,
        [string]$Description
    )
    
    Write-Host "`n📄 $Description" -ForegroundColor Yellow
    Write-Host "   Local: $LocalPath" -ForegroundColor Gray
    Write-Host "   S3: s3://$bucket/$S3Key" -ForegroundColor Gray
    
    if (-not (Test-Path $LocalPath)) {
        Write-Host "   ⚠ File not found, skipping..." -ForegroundColor Yellow
        return
    }
    
    $fileSize = (Get-Item $LocalPath).Length
    $fileSizeMB = [math]::Round($fileSize / 1MB, 2)
    Write-Host "   Size: $fileSizeMB MB" -ForegroundColor Gray
    
    if ($DryRun) {
        Write-Host "   [DRY RUN] Would upload file" -ForegroundColor Cyan
        return
    }
    
    # Upload file
    Write-Host "   Uploading..." -ForegroundColor Gray
    
    try {
        aws s3 cp $LocalPath s3://$bucket/$S3Key 2>&1 | Out-Null
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ✓ Upload complete" -ForegroundColor Green
        } else {
            Write-Host "   ✗ Upload failed" -ForegroundColor Red
        }
    } catch {
        Write-Host "   ✗ Upload error: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Confirm before proceeding
if (-not $Force -and -not $DryRun) {
    Write-Host "⚠ This will upload data to S3 bucket: $bucket" -ForegroundColor Yellow
    Write-Host "  This may incur AWS charges for storage and data transfer." -ForegroundColor Yellow
    Write-Host "`nContinue? (Y/N): " -NoNewline -ForegroundColor Cyan
    $response = Read-Host
    
    if ($response -ne "Y" -and $response -ne "y") {
        Write-Host "`n✗ Upload cancelled" -ForegroundColor Red
        exit 0
    }
}

Write-Host "`n" + ("=" * 60) -ForegroundColor Cyan
Write-Host "Starting Data Upload" -ForegroundColor Cyan
Write-Host ("=" * 60) -ForegroundColor Cyan

# 1. Upload Government Schemes
Upload-Directory `
    -LocalPath "$dataDir/government_schemes" `
    -S3Prefix "schemes/" `
    -Description "Government Scheme PDFs"

# 2. Upload Market Prices
Upload-File `
    -LocalPath "$dataDir/mandi_prices/Agriculture_price_dataset.csv" `
    -S3Key "datasets/agmarknet_prices.csv" `
    -Description "Market Prices Dataset (AgMarkNet)"

# 3. Upload PlantVillage Dataset (Training)
Upload-Directory `
    -LocalPath "$dataDir/plantvillage/New Plant Diseases Dataset(Augmented)" `
    -S3Prefix "plantvillage/" `
    -Description "Crop Disease Images (PlantVillage - Training)"

# 4. Upload PlantVillage Dataset (Test)
Upload-Directory `
    -LocalPath "$dataDir/plantvillage/test" `
    -S3Prefix "plantvillage-test/" `
    -Description "Crop Disease Images (PlantVillage - Test)"

# 5. Upload Sample Farmers Data
if (Test-Path "$dataDir/sample_farmers.csv") {
    Upload-File `
        -LocalPath "$dataDir/sample_farmers.csv" `
        -S3Key "datasets/sample_farmers.csv" `
        -Description "Sample Farmers Data"
}

# Summary
Write-Host "`n" + ("=" * 60) -ForegroundColor Cyan
Write-Host "Upload Summary" -ForegroundColor Cyan
Write-Host ("=" * 60) -ForegroundColor Cyan

if ($DryRun) {
    Write-Host "`n[DRY RUN] No files were actually uploaded" -ForegroundColor Cyan
    Write-Host "Run without -DryRun flag to perform actual upload" -ForegroundColor Cyan
} else {
    Write-Host "`nVerifying uploaded data..." -ForegroundColor Yellow
    
    # Check what's in S3
    Write-Host "`nS3 Bucket Contents:" -ForegroundColor White
    
    $folders = @("schemes/", "datasets/", "plantvillage/", "plantvillage-test/")
    
    foreach ($folder in $folders) {
        $count = (aws s3 ls s3://$bucket/$folder --recursive | Measure-Object -Line).Lines
        if ($count -gt 0) {
            Write-Host "  ✓ $folder - $count files" -ForegroundColor Green
        } else {
            Write-Host "  ⚠ $folder - No files" -ForegroundColor Yellow
        }
    }
    
    Write-Host "`n✓ Data upload complete!" -ForegroundColor Green
}

Write-Host "`nNext Steps:" -ForegroundColor Yellow
Write-Host "  1. Verify data in S3: aws s3 ls s3://$bucket/ --recursive" -ForegroundColor White
Write-Host "  2. Update Bedrock Knowledge Base to index scheme PDFs" -ForegroundColor White
Write-Host "  3. Test crop disease detection with uploaded images" -ForegroundColor White
Write-Host "  4. Test market price queries with AgMarkNet data" -ForegroundColor White

Write-Host ""

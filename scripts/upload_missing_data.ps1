#!/usr/bin/env pwsh
# Upload Missing Data to S3

Write-Host "`n📦 Uploading Missing Data to S3" -ForegroundColor Cyan
Write-Host "==============================`n" -ForegroundColor Cyan

$bucket = "ure-mvp-data-us-east-1-188238313375"

# Check current S3 contents
Write-Host "Checking S3 bucket contents..." -ForegroundColor Yellow

$folders = @{
    "schemes/" = "Government Schemes"
    "datasets/" = "Market Prices & Datasets"
    "plantvillage/" = "Crop Disease Images (Training)"
    "plantvillage-test/" = "Crop Disease Images (Test)"
}

$missing = @()

foreach ($folder in $folders.Keys) {
    $count = (aws s3 ls s3://$bucket/$folder --recursive 2>$null | Measure-Object -Line).Lines
    
    if ($count -gt 0) {
        Write-Host "  ✓ $($folders[$folder]): $count files" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $($folders[$folder]): No files (MISSING)" -ForegroundColor Red
        $missing += $folder
    }
}

if ($missing.Count -eq 0) {
    Write-Host "`n✓ All data is already uploaded!" -ForegroundColor Green
    Write-Host "`nData Summary:" -ForegroundColor Cyan
    Write-Host "  - Government Schemes: ✓ Uploaded" -ForegroundColor Gray
    Write-Host "  - Market Prices: ✓ Uploaded" -ForegroundColor Gray
    Write-Host "  - Crop Disease Images (Training): ✓ Uploaded" -ForegroundColor Gray
    Write-Host "  - Crop Disease Images (Test): Check below" -ForegroundColor Gray
    exit 0
}

Write-Host "`n⚠ Missing data detected: $($missing -join ', ')" -ForegroundColor Yellow
Write-Host "Uploading missing data...`n" -ForegroundColor Yellow

# Upload PlantVillage Test Dataset (if missing)
if ($missing -contains "plantvillage-test/") {
    Write-Host "📁 Uploading Crop Disease Test Images..." -ForegroundColor Yellow
    
    $testPath = "data/plantvillage/test"
    
    if (Test-Path $testPath) {
        $fileCount = (Get-ChildItem -Path $testPath -Recurse -File | Measure-Object).Count
        Write-Host "  Local files: $fileCount" -ForegroundColor Gray
        Write-Host "  Uploading to: s3://$bucket/plantvillage-test/" -ForegroundColor Gray
        
        aws s3 sync $testPath s3://$bucket/plantvillage-test/ --quiet
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✓ Test images uploaded" -ForegroundColor Green
        } else {
            Write-Host "  ✗ Upload failed" -ForegroundColor Red
        }
    } else {
        Write-Host "  ✗ Local test directory not found: $testPath" -ForegroundColor Red
    }
}

# Verify upload
Write-Host "`n" + ("=" * 60) -ForegroundColor Cyan
Write-Host "Verification" -ForegroundColor Cyan
Write-Host ("=" * 60) -ForegroundColor Cyan

foreach ($folder in $folders.Keys) {
    $count = (aws s3 ls s3://$bucket/$folder --recursive 2>$null | Measure-Object -Line).Lines
    
    if ($count -gt 0) {
        Write-Host "  ✓ $($folders[$folder]): $count files" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $($folders[$folder]): No files" -ForegroundColor Red
    }
}

Write-Host "`n✓ Upload complete!" -ForegroundColor Green
Write-Host ""

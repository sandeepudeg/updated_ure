#!/usr/bin/env pwsh
# Redeploy Web UI with Fixed Configuration

Write-Host "`n🔄 Redeploying Web UI with Fixed Configuration" -ForegroundColor Cyan
Write-Host "============================================`n" -ForegroundColor Cyan

$distId = "E354ZTACSUHKWS"

# Step 1: Disable existing CloudFront distribution
Write-Host "Step 1: Disabling existing CloudFront distribution..." -ForegroundColor Yellow
try {
    # Get current config
    $config = aws cloudfront get-distribution-config --id $distId --output json | ConvertFrom-Json
    $etag = $config.ETag
    
    # Disable distribution
    $config.DistributionConfig.Enabled = $false
    $configJson = $config.DistributionConfig | ConvertTo-Json -Depth 10 -Compress
    
    # Save to temp file
    $configJson | Out-File -FilePath "temp_dist_config.json" -Encoding utf8
    
    # Update distribution
    aws cloudfront update-distribution --id $distId --distribution-config file://temp_dist_config.json --if-match $etag
    
    Write-Host "✓ Distribution disabled" -ForegroundColor Green
    Write-Host "  Waiting for distribution to be disabled (this may take 5-10 minutes)..." -ForegroundColor Gray
    
    # Clean up temp file
    Remove-Item "temp_dist_config.json" -ErrorAction SilentlyContinue
    
} catch {
    Write-Host "⚠ Could not disable distribution: $($_.Exception.Message)" -ForegroundColor Yellow
    Write-Host "  You may need to disable it manually in AWS Console" -ForegroundColor Yellow
}

# Step 2: Wait for distribution to be disabled
Write-Host "`nStep 2: Waiting for distribution to be disabled..." -ForegroundColor Yellow
$maxWait = 600  # 10 minutes
$waited = 0
$interval = 30

while ($waited -lt $maxWait) {
    $status = aws cloudfront get-distribution --id $distId --query 'Distribution.Status' --output text 2>$null
    
    if ($status -eq "Deployed") {
        $enabled = aws cloudfront get-distribution --id $distId --query 'Distribution.DistributionConfig.Enabled' --output text 2>$null
        
        if ($enabled -eq "False") {
            Write-Host "✓ Distribution is disabled and deployed" -ForegroundColor Green
            break
        }
    }
    
    Write-Host "  Status: $status, waiting... ($waited/$maxWait seconds)" -ForegroundColor Gray
    Start-Sleep -Seconds $interval
    $waited += $interval
}

if ($waited -ge $maxWait) {
    Write-Host "⚠ Timeout waiting for distribution to be disabled" -ForegroundColor Yellow
    Write-Host "  Please check AWS Console and run deployment script manually later" -ForegroundColor Yellow
    exit 1
}

# Step 3: Delete old distribution
Write-Host "`nStep 3: Deleting old CloudFront distribution..." -ForegroundColor Yellow
try {
    $etag = aws cloudfront get-distribution-config --id $distId --query 'ETag' --output text
    aws cloudfront delete-distribution --id $distId --if-match $etag
    Write-Host "✓ Distribution deleted" -ForegroundColor Green
} catch {
    Write-Host "⚠ Could not delete distribution: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Step 4: Deploy with new configuration
Write-Host "`nStep 4: Deploying with new configuration..." -ForegroundColor Yellow
Write-Host "  Using existing data bucket: ure-mvp-data-us-east-1-188238313375" -ForegroundColor Gray
Write-Host "  Web UI will be stored in: web-ui/ folder" -ForegroundColor Gray

py scripts/deploy_web_ui_to_s3.py

Write-Host "`n✓ Redeployment complete!" -ForegroundColor Green
Write-Host ""

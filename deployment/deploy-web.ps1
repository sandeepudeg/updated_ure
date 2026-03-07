# Deploy Web UI to S3 and Invalidate CloudFront
# This script uploads web files to S3 and invalidates CloudFront cache

$ErrorActionPreference = "Stop"

# Configuration
$S3_BUCKET = "ure-mvp-data-us-east-1-188238313375"
$CLOUDFRONT_DIST = "E354ZTACSUHKWS"
$WEB_DIR = "src/web/v2"
$S3_PREFIX = "web-ui"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Web UI Deployment to S3/CloudFront" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if web files exist
if (-not (Test-Path "$WEB_DIR/gramsetu-agents.html")) {
    Write-Host "✗ Web files not found in $WEB_DIR" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Web files found" -ForegroundColor Green
Write-Host ""

# Upload HTML files
Write-Host "[1/3] Uploading HTML files..." -ForegroundColor Cyan
Write-Host "  • gramsetu-agents.html (Desktop UI)" -ForegroundColor White
aws s3 cp "$WEB_DIR/gramsetu-agents.html" "s3://$S3_BUCKET/$S3_PREFIX/gramsetu-agents.html" --content-type "text/html"

Write-Host "  • gramsetu-mobile.html (Mobile UI)" -ForegroundColor White
aws s3 cp "$WEB_DIR/gramsetu-mobile.html" "s3://$S3_BUCKET/$S3_PREFIX/gramsetu-mobile.html" --content-type "text/html"

Write-Host "✓ HTML files uploaded" -ForegroundColor Green
Write-Host ""

# Upload JavaScript files
Write-Host "[2/3] Uploading JavaScript and CSS..." -ForegroundColor Cyan
Write-Host "  • config.js" -ForegroundColor White
aws s3 cp "$WEB_DIR/config.js" "s3://$S3_BUCKET/$S3_PREFIX/config.js" --content-type "application/javascript"

Write-Host "  • app.js" -ForegroundColor White
aws s3 cp "$WEB_DIR/app.js" "s3://$S3_BUCKET/$S3_PREFIX/app.js" --content-type "application/javascript"

Write-Host "  • styles.css" -ForegroundColor White
aws s3 cp "$WEB_DIR/styles.css" "s3://$S3_BUCKET/$S3_PREFIX/styles.css" --content-type "text/css"

Write-Host "✓ JavaScript and CSS uploaded" -ForegroundColor Green
Write-Host ""

# Invalidate CloudFront cache
Write-Host "[3/3] Invalidating CloudFront cache..." -ForegroundColor Cyan
$invalidation = aws cloudfront create-invalidation `
    --distribution-id $CLOUDFRONT_DIST `
    --paths "/*" | ConvertFrom-Json

$invalidationId = $invalidation.Invalidation.Id

Write-Host "✓ CloudFront invalidation created: $invalidationId" -ForegroundColor Green
Write-Host "  Cache will be cleared in 1-2 minutes" -ForegroundColor Yellow
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Deployment Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "📦 Deployed Files:" -ForegroundColor Yellow
Write-Host "  • gramsetu-agents.html (Desktop UI)" -ForegroundColor White
Write-Host "  • gramsetu-mobile.html (Mobile UI)" -ForegroundColor White
Write-Host "  • config.js, app.js, styles.css" -ForegroundColor White
Write-Host ""

Write-Host "🌐 Live URLs:" -ForegroundColor Yellow
Write-Host "  • Desktop: https://d3v7khazsfb4vd.cloudfront.net/gramsetu-agents.html" -ForegroundColor White
Write-Host "  • Mobile:  https://d3v7khazsfb4vd.cloudfront.net/gramsetu-mobile.html" -ForegroundColor White
Write-Host ""

Write-Host "⏱ Wait 1-2 minutes for CloudFront cache to clear, then test the URLs" -ForegroundColor Yellow
Write-Host ""

# Ask if user wants to open URLs
$openBrowser = Read-Host "Open URLs in browser? (y/n)"
if ($openBrowser -eq "y") {
    Start-Process "https://d3v7khazsfb4vd.cloudfront.net/gramsetu-agents.html"
    Start-Sleep -Seconds 2
    Start-Process "https://d3v7khazsfb4vd.cloudfront.net/gramsetu-mobile.html"
    Write-Host "✓ URLs opened in browser" -ForegroundColor Green
}

Write-Host ""
Write-Host "✓ All done!" -ForegroundColor Green

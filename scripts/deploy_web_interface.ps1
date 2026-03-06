# Deploy Web Interface to S3 and Invalidate CloudFront
# This script uploads the new gramsetu-agents.html GUI to S3

$S3_BUCKET = "ure-mvp-data-us-east-1-188238313375"
$CLOUDFRONT_DIST = "E354ZTACSUHKWS"
$WEB_DIR = "src/web/v2"
$S3_PREFIX = "web-ui"  # CloudFront origin path

Write-Host "Deploying Web Interface to S3..." -ForegroundColor Green

# Upload HTML file
Write-Host "Uploading gramsetu-agents.html..."
aws s3 cp "$WEB_DIR/gramsetu-agents.html" "s3://$S3_BUCKET/$S3_PREFIX/gramsetu-agents.html" --content-type "text/html"

# Upload config.js
Write-Host "Uploading config.js..."
aws s3 cp "$WEB_DIR/config.js" "s3://$S3_BUCKET/$S3_PREFIX/config.js" --content-type "application/javascript"

# Upload other files if needed
Write-Host "Uploading index.html..."
aws s3 cp "$WEB_DIR/index.html" "s3://$S3_BUCKET/$S3_PREFIX/index.html" --content-type "text/html"

Write-Host "Uploading app.js..."
aws s3 cp "$WEB_DIR/app.js" "s3://$S3_BUCKET/$S3_PREFIX/app.js" --content-type "application/javascript"

Write-Host "Uploading styles.css..."
aws s3 cp "$WEB_DIR/styles.css" "s3://$S3_BUCKET/$S3_PREFIX/styles.css" --content-type "text/css"

# Get current CloudFront distribution config
Write-Host "Updating CloudFront default root object..." -ForegroundColor Yellow
$etag = aws cloudfront get-distribution-config --id $CLOUDFRONT_DIST --query 'ETag' --output text
$config = aws cloudfront get-distribution-config --id $CLOUDFRONT_DIST --query 'DistributionConfig' --output json | ConvertFrom-Json

# Update default root object
$config.DefaultRootObject = "gramsetu-agents.html"

# Save updated config to temp file
$config | ConvertTo-Json -Depth 10 | Out-File -FilePath "temp-cf-config.json" -Encoding utf8

# Update CloudFront distribution
Write-Host "Applying CloudFront configuration changes..."
aws cloudfront update-distribution --id $CLOUDFRONT_DIST --distribution-config file://temp-cf-config.json --if-match $etag

# Clean up temp file
Remove-Item "temp-cf-config.json" -ErrorAction SilentlyContinue

# Invalidate CloudFront cache
Write-Host "Invalidating CloudFront cache..." -ForegroundColor Yellow
aws cloudfront create-invalidation --distribution-id $CLOUDFRONT_DIST --paths "/*"

Write-Host "Deployment complete!" -ForegroundColor Green
Write-Host "Access your GUI at: https://d3v7khazsfb4vd.cloudfront.net/"
Write-Host "Direct link: https://d3v7khazsfb4vd.cloudfront.net/gramsetu-agents.html"

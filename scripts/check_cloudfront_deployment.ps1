# Check CloudFront Distribution Status
# Distribution ID: E354ZTACSUHKWS

Write-Host "Checking CloudFront distribution status..." -ForegroundColor Cyan

$status = aws cloudfront get-distribution --id E354ZTACSUHKWS --query 'Distribution.Status' --output text

Write-Host "`nDistribution Status: $status" -ForegroundColor Yellow

if ($status -eq "Deployed") {
    Write-Host "`n✓ CloudFront distribution is DEPLOYED and ready!" -ForegroundColor Green
    Write-Host "`nYou can now access your app at:" -ForegroundColor Green
    Write-Host "https://d3v7khazsfb4vd.cloudfront.net" -ForegroundColor Cyan
} else {
    Write-Host "`n⏳ CloudFront distribution is still deploying..." -ForegroundColor Yellow
    Write-Host "This typically takes 10-15 minutes." -ForegroundColor Yellow
    Write-Host "`nRun this script again in a few minutes to check status." -ForegroundColor Yellow
}

Write-Host "`n" -NoNewline

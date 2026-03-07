# Test Web UI
# This script opens the web interfaces and tests API connectivity

$ErrorActionPreference = "Stop"

# Configuration
$DESKTOP_URL = "https://d3v7khazsfb4vd.cloudfront.net/gramsetu-agents.html"
$MOBILE_URL = "https://d3v7khazsfb4vd.cloudfront.net/gramsetu-mobile.html"
$API_ENDPOINT = "https://8938dqxf33.execute-api.us-east-1.amazonaws.com/dev/query"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Web UI Testing" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Test API Endpoint
Write-Host "[1/3] Testing API Endpoint..." -ForegroundColor Cyan
Write-Host "Endpoint: $API_ENDPOINT" -ForegroundColor Yellow
Write-Host ""

$testPayload = @{
    user_id = "web_test_user"
    query = "Hello, test message"
    language = "English"
} | ConvertTo-Json

try {
    Write-Host "Sending test request..." -ForegroundColor Yellow
    $response = Invoke-RestMethod -Uri $API_ENDPOINT -Method POST -Body $testPayload -ContentType "application/json" -TimeoutSec 30
    
    Write-Host "✓ API is responding" -ForegroundColor Green
    Write-Host "Response preview:" -ForegroundColor White
    Write-Host ($response | ConvertTo-Json -Depth 3).Substring(0, [Math]::Min(200, ($response | ConvertTo-Json -Depth 3).Length)) -ForegroundColor Gray
    Write-Host "..." -ForegroundColor Gray
} catch {
    Write-Host "✗ API test failed" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test Desktop UI
Write-Host "[2/3] Testing Desktop UI..." -ForegroundColor Cyan
Write-Host "URL: $DESKTOP_URL" -ForegroundColor Yellow
Write-Host ""

$openDesktop = Read-Host "Open Desktop UI in browser? (y/n)"
if ($openDesktop -eq "y") {
    Start-Process $DESKTOP_URL
    Write-Host "✓ Desktop UI opened" -ForegroundColor Green
    Write-Host ""
    Write-Host "Manual testing checklist:" -ForegroundColor Yellow
    Write-Host "  [ ] Page loads correctly" -ForegroundColor White
    Write-Host "  [ ] All 6 agent cards visible" -ForegroundColor White
    Write-Host "  [ ] Chat input works" -ForegroundColor White
    Write-Host "  [ ] Can send messages" -ForegroundColor White
    Write-Host "  [ ] Receives AI responses" -ForegroundColor White
    Write-Host "  [ ] Image upload button works" -ForegroundColor White
    Write-Host "  [ ] Language selector works" -ForegroundColor White
} else {
    Write-Host "⊘ Skipped Desktop UI test" -ForegroundColor Yellow
}
Write-Host ""

# Test Mobile UI
Write-Host "[3/3] Testing Mobile UI..." -ForegroundColor Cyan
Write-Host "URL: $MOBILE_URL" -ForegroundColor Yellow
Write-Host ""

$openMobile = Read-Host "Open Mobile UI in browser? (y/n)"
if ($openMobile -eq "y") {
    Start-Process $MOBILE_URL
    Write-Host "✓ Mobile UI opened" -ForegroundColor Green
    Write-Host ""
    Write-Host "Manual testing checklist:" -ForegroundColor Yellow
    Write-Host "  [ ] Page loads correctly" -ForegroundColor White
    Write-Host "  [ ] All 6 agent cards in 3x2 grid" -ForegroundColor White
    Write-Host "  [ ] Bottom navigation visible" -ForegroundColor White
    Write-Host "  [ ] Photo button (bottom left) works" -ForegroundColor White
    Write-Host "  [ ] Clear button (bottom) works" -ForegroundColor White
    Write-Host "  [ ] Chat functionality works" -ForegroundColor White
    Write-Host "  [ ] Responsive on mobile device" -ForegroundColor White
    Write-Host ""
    Write-Host "💡 Tip: Use browser DevTools (F12) to test mobile view" -ForegroundColor Cyan
} else {
    Write-Host "⊘ Skipped Mobile UI test" -ForegroundColor Yellow
}
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Testing Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "📋 Test Summary:" -ForegroundColor Yellow
Write-Host "  • API Endpoint: Tested" -ForegroundColor White
Write-Host "  • Desktop UI: $DESKTOP_URL" -ForegroundColor White
Write-Host "  • Mobile UI: $MOBILE_URL" -ForegroundColor White
Write-Host ""

Write-Host "🔍 Additional Testing:" -ForegroundColor Yellow
Write-Host "  • Test on actual mobile device" -ForegroundColor White
Write-Host "  • Test image upload functionality" -ForegroundColor White
Write-Host "  • Test different agent selections" -ForegroundColor White
Write-Host "  • Test market price queries" -ForegroundColor White
Write-Host "  • Test in different browsers" -ForegroundColor White
Write-Host ""

Write-Host "✓ All done!" -ForegroundColor Green

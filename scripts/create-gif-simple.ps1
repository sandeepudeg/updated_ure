# Simple PowerShell Script to Create GIF from HTML
# This script guides you through manual recording and converts to GIF

param(
    [string]$HtmlFile = "deployment/gramsetu-cost-estimate.html",
    [string]$OutputGif = "deployment/gramsetu-cost-estimate.gif"
)

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Simple GIF Creator" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if HTML file exists
if (-not (Test-Path $HtmlFile)) {
    Write-Host "ERROR: HTML file not found: $HtmlFile" -ForegroundColor Red
    exit 1
}

$HtmlFullPath = (Resolve-Path $HtmlFile).Path
Write-Host "HTML file: $HtmlFullPath" -ForegroundColor Green
Write-Host ""

# Check for FFmpeg
Write-Host "Checking for FFmpeg..." -ForegroundColor Yellow
$ffmpegPath = Get-Command ffmpeg -ErrorAction SilentlyContinue

if (-not $ffmpegPath) {
    Write-Host ""
    Write-Host "FFmpeg is not installed!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install FFmpeg using one of these methods:" -ForegroundColor Yellow
    Write-Host "  1. Chocolatey: choco install ffmpeg" -ForegroundColor White
    Write-Host "  2. Scoop: scoop install ffmpeg" -ForegroundColor White
    Write-Host "  3. Download: https://ffmpeg.org/download.html" -ForegroundColor White
    Write-Host ""
    Write-Host "After installing, run this script again." -ForegroundColor Yellow
    Write-Host ""
    
    # Offer alternative
    Write-Host "Alternative: Use ScreenToGif (easier)" -ForegroundColor Cyan
    Write-Host "Download from: https://www.screentogif.com/" -ForegroundColor White
    Write-Host ""
    exit 1
}

Write-Host "✓ FFmpeg found!" -ForegroundColor Green
Write-Host ""

# Open HTML file
Write-Host "Step 1: Opening HTML file in browser..." -ForegroundColor Yellow
Start-Process $HtmlFullPath
Start-Sleep -Seconds 3

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Recording Instructions" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Follow these steps to record:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  1. Press F11 for fullscreen mode" -ForegroundColor White
Write-Host "  2. Press Win + G to open Xbox Game Bar" -ForegroundColor White
Write-Host "  3. Click Record button (or Win + Alt + R)" -ForegroundColor White
Write-Host "  4. Wait 3-4 seconds for animation" -ForegroundColor White
Write-Host "  5. Press Win + Alt + R to stop" -ForegroundColor White
Write-Host ""
Write-Host "Your video will be saved to:" -ForegroundColor Yellow
Write-Host "  C:\Users\$env:USERNAME\Videos\Captures\" -ForegroundColor White
Write-Host ""
Write-Host "Press Enter after you've recorded the video..." -ForegroundColor Cyan
Read-Host

# Ask for video file
Write-Host ""
Write-Host "Step 2: Locate your recorded video" -ForegroundColor Yellow
Write-Host ""
Write-Host "Enter the full path to your video file:" -ForegroundColor Yellow
Write-Host "(or drag and drop the file here)" -ForegroundColor Gray
$videoPath = Read-Host "Video path"

# Clean up path (remove quotes if dragged)
$videoPath = $videoPath.Trim('"')

if (-not (Test-Path $videoPath)) {
    Write-Host ""
    Write-Host "ERROR: Video file not found: $videoPath" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please check the path and try again." -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "✓ Video file found!" -ForegroundColor Green
Write-Host ""

# Convert to GIF
Write-Host "Step 3: Converting to GIF..." -ForegroundColor Yellow
Write-Host ""
Write-Host "This may take a minute..." -ForegroundColor Gray

# High-quality GIF conversion with palette
$paletteFile = "temp_palette.png"

Write-Host "  - Generating color palette..." -ForegroundColor Gray
ffmpeg -i "$videoPath" -vf "fps=20,scale=1920:-1:flags=lanczos,palettegen" -y "$paletteFile" 2>&1 | Out-Null

if (Test-Path $paletteFile) {
    Write-Host "  - Creating GIF..." -ForegroundColor Gray
    ffmpeg -i "$videoPath" -i "$paletteFile" -lavfi "fps=20,scale=1920:-1:flags=lanczos[x];[x][1:v]paletteuse" -loop 0 "$OutputGif" 2>&1 | Out-Null
    
    # Cleanup palette
    Remove-Item $paletteFile -Force
}

# Check if GIF was created
if (Test-Path $OutputGif) {
    $gifSize = (Get-Item $OutputGif).Length / 1MB
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  Success!" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "✓ GIF created successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Output: $OutputGif" -ForegroundColor White
    Write-Host "Size: $([math]::Round($gifSize, 2)) MB" -ForegroundColor White
    Write-Host ""
    Write-Host "Opening GIF..." -ForegroundColor Yellow
    Start-Process $OutputGif
    Write-Host ""
    Write-Host "Done!" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "ERROR: Failed to create GIF!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please try using ScreenToGif instead:" -ForegroundColor Yellow
    Write-Host "https://www.screentogif.com/" -ForegroundColor White
    Write-Host ""
    exit 1
}

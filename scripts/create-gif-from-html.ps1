# PowerShell Script to Create GIF from HTML Animation
# Requires: FFmpeg and Chrome/Edge browser

param(
    [string]$HtmlFile = "deployment/gramsetu-cost-estimate.html",
    [string]$OutputGif = "deployment/gramsetu-cost-estimate.gif",
    [int]$Duration = 4,
    [int]$Width = 1920,
    [int]$Height = 1080,
    [int]$FrameRate = 20
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  GIF Creator from HTML Animation" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if FFmpeg is installed
Write-Host "Checking for FFmpeg..." -ForegroundColor Yellow
$ffmpegPath = Get-Command ffmpeg -ErrorAction SilentlyContinue

if (-not $ffmpegPath) {
    Write-Host "ERROR: FFmpeg not found!" -ForegroundColor Red
  
  Write-Host ""
    Write-Host "Please install FFmpeg first:" -ForegroundColor Yellow
    Write-Host "1. Download from: https://ffmpeg.org/download.html" -ForegroundColor White
    Write-Host "2. Or use Chocolatey: choco install ffmpeg" -ForegroundColor White
    Write-Host "3. Or use Scoop: scoop install ffmpeg" -ForegroundColor White
    Write-Host ""
    exit 1
}

Write-Host "✓ FFmpeg found at: $($ffmpegPath.Source)" -ForegroundColor Green
Write-Host ""

# Check if HTML file exists
if (-not (Test-Path $HtmlFile)) {
    Write-Host "ERROR: HTML file not found: $HtmlFile" -ForegroundColor Red
    exit 1
}

$HtmlFullPath = (Resolve-Path $HtmlFile).Path
Write-Host "✓ HTML file found: $HtmlFullPath" -ForegroundColor Green
Write-Host ""

# Create temp directory for frames
$tempDir = "temp_gif_frames_$(Get-Date -Format 'yyyyMMddHHmmss')"
New-Item -ItemType Directory -Path $tempDir -Force | Out-Null
Write-Host "✓ Created temp directory: $tempDir" -ForegroundColor Green
Write-Host ""

# Method 1: Using Playwright (if available)
Write-Host "Attempting Method 1: Playwright..." -ForegroundColor Yellow

$playwrightScript = @"
const { chromium } = require('playwright');

(async () => {
    const browser = await chromium.launch();
    const context = await browser.newContext({
        viewport: { width: $Width, height: $Height }
    });
    const page = await context.newPage();
    
    await page.goto('file:///$($HtmlFullPath.Replace('\', '/'))');
    await page.waitForTimeout(500); // Wait for page load
    
    const fps = $FrameRate;
    const duration = $Duration;
    const totalFrames = fps * duration;
    
    for (let i = 0; i < totalFrames; i++) {
        await page.screenshot({ 
            path: '$tempDir/frame_' + String(i).padStart(4, '0') + '.png',
            fullPage: false
        });
        await page.waitForTimeout(1000 / fps);
    }
    
    await browser.close();
    console.log('Frames captured successfully!');
})();
"@

$playwrightScriptPath = "$tempDir/capture.js"
$playwrightScript | Out-File -FilePath $playwrightScriptPath -Encoding UTF8

# Check if Node.js and Playwright are available
$nodeAvailable = Get-Command node -ErrorAction SilentlyContinue
$playwrightAvailable = $false

if ($nodeAvailable) {
    try {
        $playwrightCheck = npm list playwright 2>&1
        if ($playwrightCheck -match "playwright@") {
            $playwrightAvailable = $true
        }
    } catch {
        $playwrightAvailable = $false
    }
}

if ($nodeAvailable -and $playwrightAvailable) {
    Write-Host "✓ Playwright available, capturing frames..." -ForegroundColor Green
    node $playwrightScriptPath
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Frames captured successfully!" -ForegroundColor Green
        $method = "playwright"
    } else {
        Write-Host "✗ Playwright capture failed" -ForegroundColor Red
        $method = "manual"
    }
} else {
    Write-Host "✗ Playwright not available (Node.js or Playwright not installed)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Falling back to Method 2: Manual screen recording..." -ForegroundColor Yellow
    $method = "manual"
}

# Method 2: Manual recording with instructions
if ($method -eq "manual") {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  Manual Recording Instructions" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Please follow these steps:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1. Opening HTML file in browser..." -ForegroundColor White
    Start-Process $HtmlFullPath
    Start-Sleep -Seconds 2
    
    Write-Host "2. Press F11 for fullscreen mode" -ForegroundColor White
    Write-Host "3. Press Win + G to open Xbox Game Bar" -ForegroundColor White
    Write-Host "4. Click the Record button (or Win + Alt + R)" -ForegroundColor White
    Write-Host "5. Wait $Duration seconds for animation to complete" -ForegroundColor White
    Write-Host "6. Press Win + Alt + R again to stop recording" -ForegroundColor White
    Write-Host "7. Find your video in: C:\Users\$env:USERNAME\Videos\Captures\" -ForegroundColor White
    Write-Host ""
    Write-Host "After recording, press Enter to continue..." -ForegroundColor Yellow
    Read-Host
    
    Write-Host ""
    Write-Host "Please enter the path to your recorded video:" -ForegroundColor Yellow
    $videoPath = Read-Host "Video path"
    
    if (-not (Test-Path $videoPath)) {
        Write-Host "ERROR: Video file not found!" -ForegroundColor Red
        Remove-Item -Path $tempDir -Recurse -Force
        exit 1
    }
    
    Write-Host ""
    Write-Host "Converting video to GIF..." -ForegroundColor Yellow
    
    # Convert video to GIF using FFmpeg
    $ffmpegCmd = "ffmpeg -i `"$videoPath`" -vf `"fps=$FrameRate,scale=${Width}:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse`" -loop 0 `"$OutputGif`""
    
    Invoke-Expression $ffmpegCmd
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ GIF created successfully!" -ForegroundColor Green
    } else {
        Write-Host "✗ GIF creation failed!" -ForegroundColor Red
        Remove-Item -Path $tempDir -Recurse -Force
        exit 1
    }
}

# Method 3: Convert frames to GIF (if frames were captured)
if ($method -eq "playwright") {
    Write-Host ""
    Write-Host "Converting frames to GIF..." -ForegroundColor Yellow
    
    # Create palette for better quality
    $paletteCmd = "ffmpeg -i `"$tempDir/frame_%04d.png`" -vf `"fps=$FrameRate,scale=${Width}:-1:flags=lanczos,palettegen`" -y `"$tempDir/palette.png`""
    Invoke-Expression $paletteCmd
    
    # Create GIF using palette
    $gifCmd = "ffmpeg -framerate $FrameRate -i `"$tempDir/frame_%04d.png`" -i `"$tempDir/palette.png`" -lavfi `"fps=$FrameRate,scale=${Width}:-1:flags=lanczos[x];[x][1:v]paletteuse`" -loop 0 `"$OutputGif`""
    Invoke-Expression $gifCmd
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ GIF created successfully!" -ForegroundColor Green
    } else {
        Write-Host "✗ GIF creation failed!" -ForegroundColor Red
        Remove-Item -Path $tempDir -Recurse -Force
        exit 1
    }
}

# Cleanup
Write-Host ""
Write-Host "Cleaning up temporary files..." -ForegroundColor Yellow
Remove-Item -Path $tempDir -Recurse -Force
Write-Host "✓ Cleanup complete" -ForegroundColor Green

# Show results
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  GIF Creation Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Output file: $OutputGif" -ForegroundColor Green

if (Test-Path $OutputGif) {
    $gifSize = (Get-Item $OutputGif).Length / 1MB
    Write-Host "File size: $([math]::Round($gifSize, 2)) MB" -ForegroundColor Green
    Write-Host ""
    Write-Host "Opening GIF..." -ForegroundColor Yellow
    Start-Process $OutputGif
} else {
    Write-Host "ERROR: GIF file was not created!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Done!" -ForegroundColor Green

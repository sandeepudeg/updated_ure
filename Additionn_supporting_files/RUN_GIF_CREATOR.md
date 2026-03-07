# How to Run the GIF Creator Script

## Quick Start (3 Steps)

### Step 1: Open PowerShell
1. Press `Win + X`
2. Select "Windows PowerShell" or "Terminal"
3. Navigate to your project folder:
```powershell
cd "path\to\your\project"
```

### Step 2: Run the Script
```powershell
.\scripts\create-gif-simple.ps1
```

### Step 3: Follow the Instructions
The script will:
1. Open the HTML file in your browser
2. Show you recording instructions
3. Wait for you to record (Win + G for Xbox Game Bar)
4. Convert your recording to GIF automatically

---

## Detailed Instructions

### Before Running (One-Time Setup)

**Check if FFmpeg is installed:**
```powershell
ffmpeg -version
```

**If not installed, install FFmpeg:**

Option 1 - Using Chocolatey (recommended):
```powershell
choco install ffmpeg
```

Option 2 - Using Scoop:
```powershell
scoop install ffmpeg
```

Option 3 - Manual download:
- Visit: https://ffmpeg.org/download.html
- Download Windows build
- Extract and add to PATH

---

## Running the Script

### For Cost Estimate Animation:
```powershell
.\scripts\create-gif-simple.ps1 -HtmlFile "deployment/gramsetu-cost-estimate.html" -OutputGif "deployment/gramsetu-cost-estimate.gif"
```

### For Cost Simulator (Interactive):
```powershell
.\scripts\create-gif-simple.ps1 -HtmlFile "deployment/gramsetu-cost-simulator.html" -OutputGif "deployment/gramsetu-cost-simulator.gif"
```

### For Technology Stack:
```powershell
.\scripts\create-gif-simple.ps1 -HtmlFile "deployment/gramsetu-technology-stack.html" -OutputGif "deployment/gramsetu-technology-stack.gif"
```

---

## Recording Instructions (When Script Prompts)

1. **Script opens HTML in browser**
2. **Press F11** for fullscreen
3. **Press Win + G** to open Xbox Game Bar
4. **Click Record button** (or Win + Alt + R)
5. **Wait 3-4 seconds** for animation
6. **Press Win + Alt + R** to stop recording
7. **Find video** in: `C:\Users\YourName\Videos\Captures\`
8. **Return to PowerShell** and press Enter
9. **Drag and drop** the video file path when prompted

---

## Troubleshooting

### "Execution Policy" Error
If you get an error about execution policy:
```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

### FFmpeg Not Found
Install FFmpeg first (see "Before Running" section above)

### Xbox Game Bar Not Working
Alternative: Use ScreenToGif
- Download: https://www.screentogif.com/
- Much easier and no FFmpeg needed!

### Video File Not Found
Make sure to:
1. Record the video first
2. Copy the full path from File Explorer
3. Paste it when the script asks

---

## Alternative: Use ScreenToGif (Easiest!)

If the PowerShell script is too complex:

1. **Download ScreenToGif**: https://www.screentogif.com/
2. **Open your HTML file** in browser (F11 for fullscreen)
3. **Run ScreenToGif** → Click "Recorder"
4. **Position frame** over the browser window
5. **Press F7** to start recording
6. **Wait 3-4 seconds**
7. **Press F8** to stop
8. **Click "File" → "Save As" → "GIF"**
9. **Done!**

---

## Expected Output

After successful execution:
- GIF file created in `deployment/` folder
- File size: ~2-5 MB
- Resolution: 1920x1080
- Frame rate: 20 FPS
- Duration: 3-4 seconds
- Loops infinitely

---

## Need Help?

If you encounter issues:
1. Check FFmpeg installation: `ffmpeg -version`
2. Verify HTML file exists: `Test-Path deployment/gramsetu-cost-estimate.html`
3. Try the ScreenToGif alternative (much simpler!)
4. Check the CREATE_GIF_GUIDE.md for more options

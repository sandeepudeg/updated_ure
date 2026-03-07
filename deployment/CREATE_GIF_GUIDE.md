# How to Create GIF from Animated HTML

## Method 1: Using ScreenToGif (Recommended - Free & Easy)

### Step 1: Download ScreenToGif
1. Visit: https://www.screentogif.com/
2. Download and install (portable version available)
3. No installation required for portable version

### Step 2: Record the Animation
1. Open `gramsetu-cost-estimate.html` in your browser (Chrome/Edge recommended)
2. Press F11 for fullscreen mode
3. Launch ScreenToGif
4. Click "Recorder"
5. Position the recording frame over the slide
6. Click "Record" (or press F7)
7. Wait 3-4 seconds for animation to complete
8. Click "Stop" (or press F8)

### Step 3: Edit and Export
1. Review the frames in ScreenToGif editor
2. Optional: Reduce frame rate to 15-20 FPS for smaller file size
3. Click "File" → "Save As" → "GIF"
4. Choose quality settings (recommend 256 colors)
5. Save as `gramsetu-cost-estimate.gif`

**Pros:** Free, easy to use, good quality, small file size
**File Location:** Save to `deployment/` folder

---

## Method 2: Using OBS Studio (Free - Professional Quality)

### Step 1: Download OBS Studio
1. Visit: https://obsproject.com/
2. Download and install OBS Studio

### Step 2: Record
1. Open `gramsetu-cost-estimate.html` in browser (fullscreen F11)
2. Launch OBS Studio
3. Add "Window Capture" source
4. Select your browser window
5. Click "Start Recording"
6. Wait 3-4 seconds
7. Click "Stop Recording"

### Step 3: Convert to GIF
1. Use online converter: https://ezgif.com/video-to-gif
2. Upload the recorded video
3. Set frame rate to 15-20 FPS
4. Click "Convert to GIF"
5. Download the result

**Pros:** High quality, professional tool
**Cons:** Two-step process (video → GIF)

---

## Method 3: Using Online Tools (No Installation)

### Option A: CloudConvert
1. Open `gramsetu-cost-estimate.html` in browser
2. Use browser's built-in screen recording:
   - Windows: Win + G (Xbox Game Bar)
   - Record for 3-4 seconds
3. Visit: https://cloudconvert.com/mp4-to-gif
4. Upload your recording
5. Convert and download

### Option B: EZGIF Screen Recorder
1. Visit: https://ezgif.com/video-to-gif
2. Use their screen recorder
3. Record the HTML animation
4. Convert directly to GIF

**Pros:** No installation needed
**Cons:** Requires internet, file size limits

---

## Method 4: Using PowerShell Script (Automated)

I can create a PowerShell script that uses FFmpeg to automate this process.

### Requirements:
- FFmpeg installed (download from https://ffmpeg.org/)
- Chrome/Edge browser

Would you like me to create this automated script?

---

## Recommended Settings for GIF

- **Resolution:** 1920x1080 (or scale down to 1280x720 for smaller file)
- **Frame Rate:** 15-20 FPS
- **Duration:** 3-4 seconds
- **Colors:** 256 colors
- **Loop:** Infinite

---

## Quick Start (Easiest Method)

1. **Download ScreenToGif:** https://www.screentogif.com/downloads
2. **Open HTML file:** Double-click `gramsetu-cost-estimate.html`
3. **Press F11** for fullscreen
4. **Run ScreenToGif** → Click "Recorder"
5. **Position frame** over the slide
6. **Press F7** to start recording
7. **Wait 3-4 seconds**
8. **Press F8** to stop
9. **Click "File" → "Save As" → "GIF"**
10. **Done!** Save to `deployment/gramsetu-cost-estimate.gif`

---

## Alternative: Use Static Screenshot

If GIF creation is difficult, you can also:
1. Open the HTML file in browser
2. Wait for animations to complete (2 seconds)
3. Press F11 for fullscreen
4. Take screenshot (Win + Shift + S)
5. Save as PNG image

The animations will still be visible in the HTML when presenting live!

---

## Need Help?

Let me know which method you'd like to use, and I can provide more detailed instructions or create automation scripts for you.

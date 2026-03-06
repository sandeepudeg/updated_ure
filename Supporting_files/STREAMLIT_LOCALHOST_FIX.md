# Streamlit Localhost Fix - Windows

## Issue

When running Streamlit on Windows, the browser tries to open `http://0.0.0.0:8501/` which doesn't work. You see an error:

```
Hmmm… can't reach this page
It looks like the webpage at http://0.0.0.0:8501/ might be having issues
```

## Root Cause

- Streamlit server binds to `0.0.0.0:8501` (all network interfaces)
- This is correct for the server
- But `0.0.0.0` is not a valid address for browsers on Windows
- Browsers need to use `localhost` or `127.0.0.1` instead

## Solution Applied

Updated `.streamlit/config.toml` to use `localhost` for browser:

```toml
[server]
address = "0.0.0.0"  # Server binds to all interfaces

[browser]
serverAddress = "localhost"  # Browser uses localhost
serverPort = 8501
```

## How to Fix

### Option 1: Restart Streamlit (Recommended)

If Streamlit is already running:

1. Stop the current Streamlit server (Ctrl+C in terminal)
2. Run it again:
   ```powershell
   .\run_local_with_logging.ps1
   ```
3. Browser should now open `http://localhost:8501/` automatically

### Option 2: Manual Browser Access

If the browser opened the wrong URL:

1. Close the browser tab showing the error
2. Open a new tab
3. Navigate to: `http://localhost:8501/`
4. The app should load correctly

### Option 3: Use 127.0.0.1

Alternative to localhost:

1. Navigate to: `http://127.0.0.1:8501/`
2. This is the IP address equivalent of localhost

## Verification

After applying the fix, you should see:

1. **Terminal output:**
   ```
   You can now view your Streamlit app in your browser.

   Local URL: http://localhost:8501
   Network URL: http://192.168.x.x:8501
   ```

2. **Browser automatically opens:** `http://localhost:8501/`

3. **App loads successfully** with the GramSetu interface

## Why This Happens

### Server Binding (0.0.0.0)

- Server needs to bind to `0.0.0.0` to accept connections from:
  - localhost (127.0.0.1)
  - Local network (192.168.x.x)
  - External networks (if firewall allows)

### Browser Access (localhost)

- Browsers on Windows cannot resolve `0.0.0.0`
- Must use specific address:
  - `localhost` (hostname)
  - `127.0.0.1` (loopback IP)
  - `192.168.x.x` (local network IP)

## Testing

### Test 1: Check Server is Running

```powershell
# In PowerShell
Test-NetConnection -ComputerName localhost -Port 8501
```

Expected output:
```
TcpTestSucceeded : True
```

### Test 2: Access via Browser

Open these URLs in browser (all should work):

1. `http://localhost:8501/` ✅ Recommended
2. `http://127.0.0.1:8501/` ✅ Alternative
3. `http://0.0.0.0:8501/` ❌ Won't work on Windows

### Test 3: Check Streamlit Logs

Look for this in terminal:
```
Local URL: http://localhost:8501
```

If you see `http://0.0.0.0:8501`, the config hasn't been applied yet.

## Troubleshooting

### Issue: Browser still opens 0.0.0.0

**Solution:**
1. Stop Streamlit (Ctrl+C)
2. Clear browser cache
3. Restart Streamlit
4. Manually navigate to `http://localhost:8501/`

### Issue: Connection refused

**Possible causes:**
1. Streamlit not running
2. Port 8501 blocked by firewall
3. Another app using port 8501

**Solution:**
```powershell
# Check if port is in use
netstat -ano | findstr :8501

# If port is in use, kill the process or use different port
# Update .streamlit/config.toml:
# port = 8502
```

### Issue: Page loads but shows errors

**This is different from connection issue:**
- Connection issue: Can't reach page
- Loading issue: Page loads but has errors

**Check:**
1. Terminal logs for Python errors
2. Browser console for JavaScript errors
3. Network tab for failed requests

## Configuration Reference

### Current Configuration (.streamlit/config.toml)

```toml
[theme]
primaryColor = "#1B5E20"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[server]
headless = true
port = 8501
enableCORS = true
enableXsrfProtection = false
enableWebsocketCompression = false
maxUploadSize = 200
baseUrlPath = ""
address = "0.0.0.0"  # Server binding
runOnSave = false
allowRunOnSave = false

[browser]
gatherUsageStats = false
serverAddress = "localhost"  # Browser access ✅
serverPort = 8501

[logger]
level = "info"
messageFormat = "%(asctime)s %(levelname)s: %(message)s"
```

## Quick Reference

| Address | Purpose | Works in Browser? |
|---------|---------|-------------------|
| `0.0.0.0` | Server binding | ❌ No (Windows) |
| `localhost` | Browser access | ✅ Yes |
| `127.0.0.1` | Browser access | ✅ Yes |
| `192.168.x.x` | Network access | ✅ Yes (from other devices) |

## Summary

**Problem:** Browser tries to open `http://0.0.0.0:8501/` which doesn't work on Windows

**Solution:** Updated config to use `http://localhost:8501/` for browser

**Action:** Restart Streamlit or manually navigate to `http://localhost:8501/`

**Expected:** App loads successfully with enhanced logging

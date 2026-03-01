# Quick Start Guide - GramSetu Local Deployment

## TL;DR

```powershell
# Run this command
.\run_local_with_logging.ps1

# If browser doesn't open automatically, go to:
http://localhost:8501
```

## Step-by-Step

### 1. Start the App

Open PowerShell in the project directory and run:

```powershell
.\run_local_with_logging.ps1
```

### 2. Wait for Startup

You'll see logs like:
```
============================================================
STREAMLIT APP STARTING
============================================================
✓ Path configured (took 0.01s)
✓ Environment loaded (took 0.02s)
...
Local URL: http://localhost:8501
```

### 3. Access in Browser

**Option A: Automatic (Recommended)**
- Browser should open automatically to `http://localhost:8501`

**Option B: Manual**
- If browser doesn't open, manually navigate to:
  - `http://localhost:8501` ✅ Recommended
  - `http://127.0.0.1:8501` ✅ Alternative

**Don't use:**
- `http://0.0.0.0:8501` ❌ Won't work on Windows

### 4. Verify It's Working

You should see:
- GramSetu header with 🌾 icon
- Sidebar with settings
- Chat interface
- No errors in browser console

### 5. Test a Query

1. Type a question in the chat box:
   ```
   What are the symptoms of tomato late blight?
   ```

2. Press Enter or click Send

3. Watch the terminal for logs:
   ```
   ============================================================
   API CALL STARTED
   Endpoint: https://3dcqel7asa.execute-api.ap-south-1.amazonaws.com/prod/query
   ✓ Request completed in 1.23s
   ============================================================
   ```

4. Response should appear in < 2 seconds

## Common Issues

### Issue 1: "Can't reach this page" at 0.0.0.0:8501

**Solution:** Navigate to `http://localhost:8501` instead

**Why:** Windows browsers can't access `0.0.0.0`, use `localhost`

### Issue 2: Port already in use

**Error:** `Address already in use`

**Solution:**
```powershell
# Find process using port 8501
netstat -ano | findstr :8501

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F

# Or use a different port in .streamlit/config.toml
```

### Issue 3: Module not found errors

**Error:** `ModuleNotFoundError: No module named 'streamlit'`

**Solution:**
```powershell
# Activate virtual environment
.\rural\Scripts\Activate.ps1

# Install requirements
pip install -r requirements-streamlit.txt

# Run again
.\run_local_with_logging.ps1
```

### Issue 4: Slow API responses

**Check:**
1. API endpoint is Mumbai (ap-south-1)
2. Internet connection is stable
3. AWS credentials are configured

**Expected:** API calls should complete in < 2 seconds

## Performance Expectations

| Metric | Expected Time |
|--------|---------------|
| App startup | < 0.5s |
| Page load | < 1s |
| API call (Mumbai) | 0.5-2s |
| Total response | < 2s |

## Monitoring

### Terminal Logs

Watch for these key metrics:
```
Total app initialization time: 0.25s
✓ Sidebar rendered (took 0.15s)
✓ Chat input rendered (took 0.03s)
✓✓ TOTAL APP EXECUTION TIME: 0.47s
```

### API Call Logs

For each query:
```
API CALL STARTED
Endpoint: https://3dcqel7asa.execute-api.ap-south-1.amazonaws.com/prod/query
Query length: 45 chars
✓ Request completed in 1.23s
Agent used: agri-expert
Total API call time: 1.25s
```

## Features to Test

### 1. Basic Query
```
What are current onion prices?
```

### 2. Government Schemes
```
Am I eligible for PM-Kisan scheme?
```

### 3. Crop Disease
```
What disease is affecting my tomato plant?
```

### 4. Weather
```
What's the weather forecast for next week?
```

### 5. Image Upload
1. Click "Browse files"
2. Select a crop image
3. Ask: "What disease is this?"

## Stopping the App

Press `Ctrl+C` in the terminal to stop the server.

## Configuration

### Current Setup

- **Mode:** API (Mumbai Backend)
- **Endpoint:** `https://3dcqel7asa.execute-api.ap-south-1.amazonaws.com/prod/query`
- **Model:** `amazon.nova-lite-v1:0`
- **Region:** ap-south-1 (Mumbai)
- **Port:** 8501
- **Address:** localhost

### Environment Variables

Set in `.env` or via script:
```
USE_API_MODE=true
API_ENDPOINT=https://3dcqel7asa.execute-api.ap-south-1.amazonaws.com/prod/query
```

## Next Steps

1. **Test basic functionality** - Submit a few queries
2. **Check performance** - Verify < 2s response times
3. **Review logs** - Look for any errors or warnings
4. **Test features** - Try image upload, language selection, etc.

## Support

### Documentation

- `LOGGING_ENHANCEMENTS.md` - Logging system details
- `STREAMLIT_LOCALHOST_FIX.md` - Browser connection issues
- `TESTING_LOGGING.md` - How to interpret logs
- `CURRENT_STATUS_AND_NEXT_STEPS.md` - Overall status

### Troubleshooting

If you encounter issues:

1. Check terminal logs for errors
2. Check browser console (F12) for JavaScript errors
3. Verify API endpoint is accessible
4. Review documentation files above

## Summary

**Start:** `.\run_local_with_logging.ps1`

**Access:** `http://localhost:8501`

**Expected:** < 1s load time, < 2s API responses

**Stop:** `Ctrl+C`

That's it! You're ready to use GramSetu locally with the Mumbai API backend.

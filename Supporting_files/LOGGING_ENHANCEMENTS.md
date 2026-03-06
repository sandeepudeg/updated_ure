# Logging Enhancements for Streamlit App

## Overview
Enhanced logging has been added to the Streamlit app to help diagnose slow loading issues and track performance bottlenecks.

## What Was Added

### 1. Startup Logging
- App initialization time tracking
- Environment variable loading time
- Path configuration time
- Page configuration time

### 2. Component Render Logging
- CSS application time
- Session state initialization time
- Header rendering time
- Sidebar rendering time (with all sub-components)
- Chat messages rendering time
- Image upload widget rendering time
- Chat input widget rendering time
- Footer rendering time

### 3. API Call Logging
- Request preparation time
- Network request duration
- Response parsing time
- Total API call time
- Request/response sizes
- Error details with timestamps

### 4. Query Processing Logging
- User input processing time
- Image encoding time (if applicable)
- Agent response time
- Total query processing time

## How to Use

### Running Locally with Logging

```powershell
# Use the new script with enhanced logging
.\run_local_with_logging.ps1
```

This will:
1. Activate the virtual environment
2. Configure Mumbai API endpoint
3. Start Streamlit with info-level logging
4. Display all timing information in the terminal

### What to Look For

**In the terminal output, you'll see:**

```
============================================================
STREAMLIT APP STARTING
============================================================
Adding src to path...
✓ Path configured (took 0.01s)
Loading environment variables...
✓ Environment loaded (took 0.02s)
Configuration:
  - USE_API_MODE: True
  - API_ENDPOINT: https://3dcqel7asa.execute-api.ap-south-1.amazonaws.com/prod/query
  - Total init time: 0.15s
Configuring Streamlit page...
✓ Page configured (took 0.05s)
Applying custom CSS...
✓ CSS applied (took 0.01s)
Initializing session state...
✓ Session state initialized (took 0.02s)
Total app initialization time: 0.25s
============================================================
```

**When you submit a query:**

```
============================================================
API CALL STARTED
Endpoint: https://3dcqel7asa.execute-api.ap-south-1.amazonaws.com/prod/query
Query length: 45 chars
Has image: False
Language: en
============================================================
Sending POST request...
✓ Request completed in 1.23s
Response status: 200
✓ Response parsed in 0.01s
Response length: 523 chars
Agent used: agri-expert
Total API call time: 1.25s
============================================================
```

## Configuration Changes

### Streamlit Config (.streamlit/config.toml)

Updated settings:
- `enableWebsocketCompression = false` - Disabled compression to help with WebSocket issues
- `runOnSave = false` - Prevent auto-rerun on file changes
- Added `[logger]` section with info-level logging

## Performance Benchmarks

### Expected Times (Local with Mumbai API)

| Component | Expected Time | Slow Threshold |
|-----------|---------------|----------------|
| App initialization | < 0.5s | > 2s |
| Page render | < 0.3s | > 1s |
| API call (Mumbai) | 0.5-2s | > 5s |
| Total page load | < 1s | > 3s |

### Singapore App Runner (Current Issue)

**Problem:** WebSocket 403 errors prevent app from loading
- WebSocket connection fails with 403 Forbidden
- App gets stuck in loading state
- No content is displayed to user

**Root Cause:** App Runner is blocking WebSocket handshakes
- Streamlit requires WebSocket for real-time updates
- App Runner's default configuration doesn't support WebSocket properly
- Need to either fix App Runner config or use alternative deployment

## Troubleshooting

### If App Loads Slowly Locally

1. Check initialization time - should be < 0.5s
2. Check API response time - should be < 2s for Mumbai
3. Check network latency - run `ping 3dcqel7asa.execute-api.ap-south-1.amazonaws.com`

### If API Calls Are Slow

1. Verify you're using Mumbai endpoint (ap-south-1)
2. Check your internet connection speed
3. Try with a simpler query (no image)
4. Check AWS Lambda logs for backend issues

### If WebSocket Errors Appear

**For Local Deployment:**
- This shouldn't happen locally
- If it does, check firewall settings
- Ensure port 8501 is not blocked

**For Singapore App Runner:**
- This is a known issue with the current deployment
- WebSocket 403 errors are expected
- Use local deployment instead for now

## Next Steps

### Option 1: Use Local Deployment (Recommended)
- Fast loading (< 1 second)
- No WebSocket issues
- Full functionality with Mumbai API backend
- Run with: `.\run_local_with_logging.ps1`

### Option 2: Fix Singapore App Runner
- Requires updating App Runner configuration
- May need to migrate to ECS with ALB
- ALB supports WebSocket properly
- More complex setup

### Option 3: Deploy to Mumbai Region
- App Runner not available in ap-south-1
- Would need to use ECS or EC2
- More infrastructure to manage

## Monitoring

### Real-Time Monitoring

Watch the terminal output while using the app to see:
- How long each component takes to render
- API call performance
- Any errors or warnings
- Total execution time per page load

### Performance Metrics

Key metrics to track:
- **App startup time:** Time from script start to first render
- **API latency:** Time for Mumbai backend to respond
- **Render time:** Time to display UI components
- **Total page load:** End-to-end time for user

## Conclusion

The enhanced logging will help you understand exactly where time is being spent in the app. For the best performance from India, use the local deployment with the Mumbai API backend.

The Singapore App Runner deployment has WebSocket issues that prevent it from working properly. Until those are resolved, local deployment is the recommended approach.

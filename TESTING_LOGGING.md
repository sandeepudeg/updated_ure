# Testing Enhanced Logging

## Quick Start

Run the Streamlit app with enhanced logging:

```powershell
.\run_local_with_logging.ps1
```

## What You'll See

### 1. App Startup Logs

When the app starts, you'll see detailed timing information:

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

### 2. Component Render Logs

As the page renders, you'll see:

```
Rendering header...
✓ Header rendered (took 0.01s)
Rendering sidebar...
✓ Sidebar rendered (took 0.15s)
Rendering main chat area...
Rendering 0 chat messages...
✓ Chat messages rendered (took 0.00s)
Rendering image upload...
✓ Image upload rendered (took 0.02s)
Rendering chat input...
Rendering chat input widget...
✓ Chat input rendered (took 0.03s)
User input received: False
Rendering footer...
✓ Footer rendered (took 0.01s)
✓ Total page render time: 0.22s
✓✓ TOTAL APP EXECUTION TIME: 0.47s
============================================================
```

### 3. API Call Logs

When you submit a query, you'll see detailed API timing:

```
============================================================
PROCESSING USER QUERY
Query: What are current onion prices?...
============================================================
✓ User message added to session state
Using API mode with user_id: user_12345678
============================================================
API CALL STARTED
Endpoint: https://3dcqel7asa.execute-api.ap-south-1.amazonaws.com/prod/query
Query length: 30 chars
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
✓ Assistant message added to session state
Total query processing time: 1.27s
============================================================
```

## Performance Benchmarks

### Expected Times (Good Performance)

| Metric | Expected | Your Result |
|--------|----------|-------------|
| App initialization | < 0.5s | ___ |
| Page render | < 0.3s | ___ |
| API call (Mumbai) | 0.5-2s | ___ |
| Total page load | < 1s | ___ |

### Slow Performance Indicators

| Metric | Slow Threshold | Action |
|--------|----------------|--------|
| App initialization | > 2s | Check Python environment, imports |
| Page render | > 1s | Simplify UI components |
| API call | > 5s | Check network, AWS region |
| Total page load | > 3s | Investigate bottleneck |

## Troubleshooting

### If Logs Don't Appear

1. Check that you're running with the script: `.\run_local_with_logging.ps1`
2. Verify logging level is set to INFO
3. Look at the terminal window (not the browser)

### If App Is Slow

1. **Check initialization time**
   - Look for "Total app initialization time"
   - Should be < 0.5s
   - If slow, check imports and environment setup

2. **Check API response time**
   - Look for "Total API call time"
   - Should be < 2s for Mumbai
   - If slow, check network connection

3. **Check render time**
   - Look for "Total page render time"
   - Should be < 0.3s
   - If slow, simplify UI or reduce components

### If WebSocket Errors Appear

**In Local Deployment:**
- This shouldn't happen
- If it does, check firewall settings
- Ensure port 8501 is not blocked

**In Singapore App Runner:**
- This is expected (known issue)
- Use local deployment instead

## Comparing Local vs Singapore

### Test 1: Initial Page Load

**Local:**
```
Total app initialization time: 0.25s
Total page render time: 0.22s
TOTAL APP EXECUTION TIME: 0.47s
```

**Singapore App Runner:**
```
WebSocket connection failed: 403
(App never loads)
```

### Test 2: API Call Performance

**Local with Mumbai API:**
```
API CALL STARTED
Endpoint: https://3dcqel7asa.execute-api.ap-south-1.amazonaws.com/prod/query
Request completed in 1.23s
Total API call time: 1.25s
```

**Singapore App Runner:**
```
(Cannot test - app doesn't load due to WebSocket errors)
```

## Next Steps

1. **Run the app** with logging enabled
2. **Record the times** you see in the terminal
3. **Compare** with the benchmarks above
4. **Share the logs** if you need help troubleshooting

## Example Session

Here's what a complete session looks like:

```
PS D:\Learning\Assembler_URE_Rural> .\run_local_with_logging.ps1
========================================
GramSetu - Local Streamlit with Logging
========================================

Activating virtual environment...
Configuring Mumbai API endpoint...

Configuration:
  - Mode: API (Mumbai Backend)
  - Endpoint: https://3dcqel7asa.execute-api.ap-south-1.amazonaws.com/prod/query
  - Logging: Enhanced (check terminal output)

========================================
Starting Streamlit...
========================================

Watch the logs below to see:
  - App initialization time
  - Component render times
  - API call durations
  - Total execution time

The app will open in your browser automatically.
Press Ctrl+C to stop the server.

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
...
(App continues with detailed logs)
```

## Summary

The enhanced logging will help you:
- Understand exactly where time is being spent
- Identify performance bottlenecks
- Compare local vs cloud deployment
- Diagnose issues quickly

For best performance from India, use local deployment with Mumbai API backend. The logs will confirm it's working optimally.

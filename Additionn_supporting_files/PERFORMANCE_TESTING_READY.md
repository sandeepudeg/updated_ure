# ✅ Performance Testing Scripts - Ready to Use!

## What Was Fixed

The API tests were failing with **400 Bad Request** because the Lambda handler requires both `user_id` and `query` in the payload. All scripts have been updated with the correct format.

### Before (Failed ❌)
```json
{"query": "What are the current mandi prices?"}
```

### After (Works ✅)
```json
{
  "user_id": "test_user",
  "query": "What are the current mandi prices?"
}
```

## Quick Start - Run All Tests

### Option 1: Automated (Recommended)

Run everything with one command:

```powershell
.\RUN_ALL_PERFORMANCE_TESTS.ps1
```

This will:
1. Check prerequisites (AWS CLI, Python, requests library)
2. Optionally run diagnostic script
3. Collect performance metrics from CloudWatch
4. Run load test with concurrent users
5. Generate HTML performance report
6. Open the report automatically

### Option 2: Manual (Step by Step)

```powershell
# Step 0: Diagnose (if having issues)
.\scripts\diagnose-api.ps1

# Step 1: Collect metrics
.\scripts\collect-performance-metrics.ps1

# Step 2: Load test
python scripts/load_test.py 10 5

# Step 3: Generate report
.\scripts\generate-performance-report.ps1
```

## Files Updated ✅

1. **scripts/diagnose-api.ps1**
   - Added `user_id` to all test payloads
   - Tests multiple payload formats
   - Checks Lambda and API Gateway status

2. **scripts/collect-performance-metrics.ps1**
   - Fixed payload format with `user_id`
   - Collects CloudWatch metrics
   - Tests API performance

3. **scripts/load_test.py**
   - Added `user_id` to all requests
   - Simulates 10 different users
   - Calculates P95/P99 percentiles

## New Files Created 📄

1. **deployment/PERFORMANCE_TESTING_GUIDE.md**
   - Comprehensive documentation
   - Troubleshooting guide
   - Performance targets

2. **deployment/RUN_PERFORMANCE_TESTS.md**
   - Quick start guide
   - Common issues and fixes

3. **deployment/PERFORMANCE_TESTING_FIX_SUMMARY.md**
   - Detailed fix explanation
   - Before/after comparisons

4. **RUN_ALL_PERFORMANCE_TESTS.ps1**
   - Automated test runner
   - Interactive prompts
   - Prerequisite checks

## Expected Results

### Diagnostic Script
```
Test 2: Testing POST request with payload...
  ✓ Request successful!
  Response: {
    "user_id": "diagnostic_test_user",
    "query": "What are the current mandi prices for wheat?",
    "response": "...",
    "agent_used": "supervisor"
  }
```

### Performance Metrics
```
Lambda Metrics:
  Avg Duration: 1234.56ms
  Error Rate: 0.5%
  Invocations: 150

API Performance:
  Avg Response: 1215.30ms
  Success Rate: 100%

Overall Score: 85 / 100
```

### Load Test
```
Total Requests: 50
Successful: 48
Failed: 2
Success Rate: 96.0%

Performance:
  Avg Response Time: 1350.25ms
  P95 Response Time: 2100ms
  P99 Response Time: 2400ms

Throughput:
  Requests/Second: 4.5
```

### Performance Report
- HTML report with charts and graphs
- Key metrics cards
- Performance benchmarking table
- Saved to `deployment/gramsetu-performance-report-TIMESTAMP.html`

## Prerequisites

- ✅ AWS CLI installed and configured
- ✅ Python 3.8+ installed
- ✅ Python `requests` library (`pip install requests`)
- ✅ PowerShell (Windows) or PowerShell Core (cross-platform)
- ✅ Access to deployed GramSetu infrastructure

## Troubleshooting

### Still Getting 400 Errors?

1. **Check Lambda is active:**
   ```bash
   aws lambda get-function --function-name ure-mvp-handler-docker
   ```
   Look for `"State": "Active"` in the output.

2. **Check CloudWatch logs:**
   ```bash
   aws logs tail /aws/lambda/ure-mvp-handler-docker --follow
   ```

3. **Test Lambda directly:**
   ```bash
   aws lambda invoke --function-name ure-mvp-handler-docker --payload '{"user_id":"test","query":"hello"}' output.json
   cat output.json
   ```

### Lambda Inactive?

Redeploy the Lambda function:
```powershell
.\deployment\deploy-docker.ps1
```

### AWS CLI Not Found?

Install AWS CLI:
- Windows: https://aws.amazon.com/cli/
- Or use: `choco install awscli` (if you have Chocolatey)

Then configure:
```bash
aws configure
```

### Python Requests Missing?

Install it:
```bash
pip install requests
```

## Performance Targets

| Metric | Target | Acceptable |
|--------|--------|------------|
| Response Time | < 1.5s | < 2.5s |
| Success Rate | > 99% | > 95% |
| Concurrent Users | 50+ | 25+ |
| Lambda Cold Start | < 3s | < 5s |
| Lambda Warm Start | < 1s | < 2s |
| API Latency | < 500ms | < 1s |

## What Each Script Does

### diagnose-api.ps1
- Tests API connectivity
- Verifies payload format
- Checks Lambda status
- Checks API Gateway config
- Provides troubleshooting tips

### collect-performance-metrics.ps1
- Collects CloudWatch metrics (Lambda duration, errors, invocations)
- Tests API with 10 requests
- Measures web page load time
- Calculates performance score (0-100)
- Saves to `performance-metrics.json`

### load_test.py
- Simulates concurrent users
- Sends multiple requests per user
- Measures response times
- Calculates P95/P99 percentiles
- Calculates throughput (requests/second)
- Saves to `load-test-results.json`

### generate-performance-report.ps1
- Reads metrics and load test results
- Generates HTML report with charts
- Includes benchmarking table
- Opens report in browser
- Saves with timestamp

## Next Steps After Testing

1. **Review the HTML report** - Identify bottlenecks and optimization opportunities
2. **Compare against targets** - See which metrics need improvement
3. **Optimize Lambda** - Increase memory if needed for better performance
4. **Enable caching** - Implement caching for frequently accessed data
5. **Set up alarms** - Create CloudWatch alarms for performance monitoring
6. **Run regularly** - Schedule weekly/monthly tests to track trends

## Documentation

- **Full Guide:** `deployment/PERFORMANCE_TESTING_GUIDE.md`
- **Quick Start:** `deployment/RUN_PERFORMANCE_TESTS.md`
- **Fix Details:** `deployment/PERFORMANCE_TESTING_FIX_SUMMARY.md`

## Ready to Test! 🚀

Run the automated script:
```powershell
.\RUN_ALL_PERFORMANCE_TESTS.ps1
```

Or follow the manual steps in the documentation.

All scripts are now fixed and ready to collect real performance data from your deployed GramSetu system!

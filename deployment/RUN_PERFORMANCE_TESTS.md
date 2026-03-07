# Quick Start: Run Performance Tests

## Fixed Issues ✅

The API tests were failing because the Lambda handler expects both `user_id` and `query` in the payload. All scripts have been updated with the correct format.

## Run Tests in 3 Steps

### Step 1: Diagnose (Optional - if having issues)

```powershell
.\scripts\diagnose-api.ps1
```

This checks:
- API connectivity
- Lambda function status
- Correct payload format
- CORS configuration

### Step 2: Collect Metrics

```powershell
# Collect CloudWatch metrics and test API
.\scripts\collect-performance-metrics.ps1

# Run load test with 10 concurrent users
python scripts/load_test.py 10 5
```

### Step 3: Generate Report

```powershell
.\scripts\generate-performance-report.ps1
```

Opens the HTML report automatically!

## What Was Fixed

### Before (Failing ❌)
```json
{
  "query": "What are the current mandi prices?"
}
```

### After (Working ✅)
```json
{
  "user_id": "test_user",
  "query": "What are the current mandi prices?"
}
```

## Files Updated

1. ✅ `scripts/diagnose-api.ps1` - Now includes `user_id` in all test payloads
2. ✅ `scripts/collect-performance-metrics.ps1` - Fixed payload format
3. ✅ `scripts/load_test.py` - Added `user_id` to all requests

## Expected Results

### Successful API Test
```
Test 1 : 1250ms ✓
Test 2 : 1180ms ✓
Test 3 : 1220ms ✓
...
Success Rate: 100%
```

### Performance Score
```
Overall Score: 85 / 100

Lambda Metrics:
  Avg Duration: 1234.56ms
  Error Rate: 0.5%

API Performance:
  Avg Response: 1215.30ms
  Success Rate: 100%
```

## Troubleshooting

### Still Getting 400 Errors?

1. Check Lambda is active:
   ```bash
   aws lambda get-function --function-name ure-mvp-handler-docker
   ```

2. Check CloudWatch logs:
   ```bash
   aws logs tail /aws/lambda/ure-mvp-handler-docker --follow
   ```

3. Test Lambda directly:
   ```bash
   aws lambda invoke --function-name ure-mvp-handler-docker --payload '{"user_id":"test","query":"hello"}' output.json
   ```

### Lambda Inactive?

Redeploy:
```powershell
.\deployment\deploy-docker.ps1
```

## Full Documentation

See `deployment/PERFORMANCE_TESTING_GUIDE.md` for complete documentation.

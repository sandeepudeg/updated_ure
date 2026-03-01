# API 502 Error - Troubleshooting Guide

## What is a 502 Error?

A 502 Bad Gateway error means:
- API Gateway received the request
- API Gateway forwarded it to Lambda
- Lambda function failed or timed out
- API Gateway returned 502 to the client

## Quick Diagnosis

Run this command to diagnose the issue:

```powershell
.\scripts\diagnose_502_error.ps1
```

This will:
1. Test the API endpoint
2. Check Lambda CloudWatch logs
3. Show you what's wrong

## Common Causes

### 1. Lambda Function Error

**Symptoms:**
- 502 error immediately (< 1 second)
- CloudWatch logs show Python errors

**Possible Issues:**
- Bedrock model access error
- Missing dependencies
- Code syntax error
- Import errors

**Solution:**
```powershell
# Redeploy Lambda with updated code
.\scripts\redeploy_mumbai_lambda.ps1
```

### 2. Lambda Timeout

**Symptoms:**
- 502 error after 30+ seconds
- CloudWatch logs show timeout

**Possible Issues:**
- Bedrock API taking too long
- Network issues
- Lambda timeout too short

**Solution:**
```bash
# Increase Lambda timeout
aws lambda update-function-configuration \
  --function-name ure-mvp-handler-mumbai \
  --region ap-south-1 \
  --timeout 60
```

### 3. Bedrock Model Access Error

**Symptoms:**
- CloudWatch logs show "Could not resolve foundation model"
- Or "AccessDeniedException"

**Possible Issues:**
- Model ID incorrect
- Model not enabled
- IAM permissions missing

**Solution:**
```powershell
# Update Lambda with correct model ID
.\scripts\redeploy_mumbai_lambda.ps1
```

### 4. Missing Dependencies

**Symptoms:**
- CloudWatch logs show "ModuleNotFoundError"
- Or "ImportError"

**Possible Issues:**
- Lambda Layer not attached
- Dependencies not included in deployment

**Solution:**
```powershell
# Redeploy with all dependencies
.\scripts\redeploy_mumbai_lambda.ps1
```

## Step-by-Step Troubleshooting

### Step 1: Check Lambda Logs

```powershell
# Activate virtual environment
.\rural\Scripts\Activate.ps1

# Check logs
py scripts/check_lambda_logs.py
```

Look for:
- Error messages
- Stack traces
- Timeout indicators
- Bedrock errors

### Step 2: Test API Directly

```powershell
# Test the API
py scripts/test_mumbai_api.py
```

This will:
- Send a test request
- Show response status
- Display error details
- Suggest next steps

### Step 3: Check Lambda Configuration

```bash
# Get Lambda configuration
aws lambda get-function-configuration \
  --function-name ure-mvp-handler-mumbai \
  --region ap-south-1
```

Verify:
- State: Should be "Active"
- Runtime: Should be "python3.11" or "python3.12"
- Handler: Should be "lambda_handler.lambda_handler"
- Timeout: Should be 60 seconds or more
- Memory: Should be 512 MB or more

### Step 4: Check Environment Variables

```bash
# Check environment variables
aws lambda get-function-configuration \
  --function-name ure-mvp-handler-mumbai \
  --region ap-south-1 \
  --query 'Environment.Variables'
```

Should include:
- `BEDROCK_MODEL_ID`: `amazon.nova-lite-v1:0`
- `BEDROCK_REGION`: `ap-south-1`

### Step 5: Redeploy Lambda

If all else fails, redeploy:

```powershell
.\scripts\redeploy_mumbai_lambda.ps1
```

This will:
1. Create deployment package
2. Update Lambda code
3. Update environment variables
4. Test the deployment

## Temporary Workaround

While fixing the Lambda, you can use local mode:

### Option 1: Local Agents (No API)

1. Edit `.env` file:
   ```
   USE_API_MODE=false
   ```

2. Run Streamlit:
   ```powershell
   streamlit run src/ui/app.py
   ```

This uses local agents instead of the API.

### Option 2: Use US East API

If Mumbai Lambda is broken, temporarily use US East:

1. Edit `run_local_with_logging.ps1`:
   ```powershell
   $env:API_ENDPOINT = "https://8938dqxf33.execute-api.us-east-1.amazonaws.com/dev/query"
   ```

2. Run Streamlit:
   ```powershell
   .\run_local_with_logging.ps1
   ```

Note: This will be slower from India (200-300ms vs 50-100ms).

## Checking CloudWatch Logs Manually

### Via AWS Console

1. Go to AWS Lambda console
2. Select function: `ure-mvp-handler-mumbai`
3. Click "Monitor" tab
4. Click "View CloudWatch logs"
5. Select most recent log stream
6. Look for errors

### Via AWS CLI

```bash
# Get recent logs
aws logs tail /aws/lambda/ure-mvp-handler-mumbai \
  --region ap-south-1 \
  --follow
```

## Common Error Messages

### "Could not resolve the foundation model"

**Cause:** Model ID is incorrect or not available

**Solution:**
- Verify model ID is `amazon.nova-lite-v1:0`
- Check region is `ap-south-1`
- Redeploy Lambda

### "AccessDeniedException"

**Cause:** IAM role doesn't have Bedrock permissions

**Solution:**
1. Go to IAM console
2. Find role: `ure-lambda-role`
3. Add Bedrock permissions:
   ```json
   {
     "Effect": "Allow",
     "Action": [
       "bedrock:InvokeModel",
       "bedrock:InvokeModelWithResponseStream"
     ],
     "Resource": "*"
   }
   ```

### "Task timed out after 30.00 seconds"

**Cause:** Lambda timeout too short

**Solution:**
```bash
aws lambda update-function-configuration \
  --function-name ure-mvp-handler-mumbai \
  --region ap-south-1 \
  --timeout 60
```

### "ModuleNotFoundError: No module named 'strands'"

**Cause:** Lambda Layer not attached or missing dependencies

**Solution:**
```powershell
# Redeploy with dependencies
.\scripts\redeploy_mumbai_lambda.ps1
```

## Prevention

To avoid 502 errors in the future:

1. **Test before deploying**
   - Always test Lambda locally first
   - Use `py scripts/test_mumbai_api.py` after deployment

2. **Monitor CloudWatch**
   - Set up CloudWatch alarms for errors
   - Check logs regularly

3. **Keep dependencies updated**
   - Update Lambda Layer when dependencies change
   - Test after updates

4. **Use proper timeouts**
   - Lambda: 60 seconds
   - API Gateway: 29 seconds (max)
   - Bedrock: 30 seconds

## Summary

**Quick Fix:**
```powershell
# Diagnose
.\scripts\diagnose_502_error.ps1

# Fix
.\scripts\redeploy_mumbai_lambda.ps1

# Test
py scripts/test_mumbai_api.py
```

**Temporary Workaround:**
- Use local mode (set `USE_API_MODE=false`)
- Or use US East API (slower but working)

**Root Cause:**
- Usually Lambda function error
- Check CloudWatch logs for details
- Redeploy Lambda to fix

## Support

If issues persist:

1. Check CloudWatch logs for specific errors
2. Verify Bedrock model access in console
3. Check IAM permissions
4. Review Lambda configuration
5. Contact AWS support if needed

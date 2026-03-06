# Quick Fix for 502 Error

## Problem

You're seeing "API Error: 502" when trying to use the app. This means the Mumbai Lambda function is having issues.

## Immediate Solution (Use This Now)

Run the app in local mode (no API needed):

```powershell
.\run_local_no_api.ps1
```

This will:
- Use local agents instead of the API
- Connect directly to Bedrock from your machine
- Work immediately without fixing Lambda

## What This Does

**Local Mode:**
- Streamlit runs on your computer
- Agents run on your computer
- Bedrock calls go directly from your machine
- No Lambda or API Gateway involved

**Pros:**
- Works immediately
- No 502 errors
- Fast responses
- Full functionality

**Cons:**
- Requires AWS credentials on your machine
- Uses your local Bedrock quota
- Not accessible from other devices

## How to Use

1. **Stop current Streamlit** (if running):
   - Press `Ctrl+C` in the terminal

2. **Run local mode**:
   ```powershell
   .\run_local_no_api.ps1
   ```

3. **Browser opens** to `http://localhost:8501`

4. **Test a query**:
   - Type: "What are the symptoms of tomato late blight?"
   - Press Enter
   - Response should appear in a few seconds

## Fixing the Lambda (Optional)

If you want to fix the Mumbai API for future use:

### Step 1: Diagnose

```powershell
.\scripts\diagnose_502_error.ps1
```

This shows you what's wrong with the Lambda.

### Step 2: Fix

```powershell
.\scripts\redeploy_mumbai_lambda.ps1
```

This redeploys the Lambda with the correct configuration.

### Step 3: Test

```powershell
# Activate virtual environment
.\rural\Scripts\Activate.ps1

# Test API
py scripts/test_mumbai_api.py
```

### Step 4: Switch Back to API Mode

Once Lambda is fixed, you can switch back:

```powershell
.\run_local_with_logging.ps1
```

This uses the Mumbai API again.

## Comparison

| Mode | Command | Speed | Requires |
|------|---------|-------|----------|
| **Local (No API)** | `.\run_local_no_api.ps1` | Fast | AWS credentials locally |
| **API (Mumbai)** | `.\run_local_with_logging.ps1` | Fast | Working Lambda |

## Troubleshooting Local Mode

### Error: "No AWS credentials"

**Solution:**
```powershell
# Configure AWS credentials
aws configure

# Enter:
# - AWS Access Key ID
# - AWS Secret Access Key
# - Region: ap-south-1
# - Output format: json
```

### Error: "Could not resolve foundation model"

**Solution:**
- Make sure you're using region `ap-south-1`
- Verify Bedrock access in AWS console
- Check model ID is `amazon.nova-lite-v1:0`

### Error: "AccessDeniedException"

**Solution:**
- Your AWS user needs Bedrock permissions
- Add this policy to your IAM user:
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

## Summary

**Quick Fix (Use Now):**
```powershell
.\run_local_no_api.ps1
```

**Fix Lambda (Later):**
```powershell
.\scripts\redeploy_mumbai_lambda.ps1
```

**Switch Back to API:**
```powershell
.\run_local_with_logging.ps1
```

The local mode works immediately and doesn't require fixing the Lambda. Use it now, fix Lambda later if you want to use the API.

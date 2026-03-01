# Bedrock Model Access Fix Guide

## Problem
Getting error: `ValidationException: Operation not allowed` when calling ConverseStream

## Root Cause
Two issues need to be fixed:
1. **Model access not enabled** in AWS Bedrock console for Mumbai region
2. **Incorrect model ID** in Lambda environment variable

## Solution Steps

### Step 1: Enable Bedrock Model Access (REQUIRED)

1. **Go to AWS Bedrock Console:**
   - Open: https://console.aws.amazon.com/bedrock/
   - **IMPORTANT:** Select region **ap-south-1 (Mumbai)** from the top-right dropdown

2. **Navigate to Model Access:**
   - Click "Model access" in the left sidebar
   - Click "Manage model access" button (orange button on the right)

3. **Enable Amazon Nova Models:**
   - Scroll down to find "Amazon" section
   - Check the boxes for these models:
     - ✅ Amazon Nova Micro
     - ✅ Amazon Nova Lite
     - ✅ Amazon Nova Pro
   - Click "Request model access" button at the bottom

4. **Wait for Approval:**
   - Status will change from "Requesting" to "Access granted"
   - Usually takes 2-5 minutes
   - Refresh the page to check status

### Step 2: Update Lambda Environment Variable

1. **Go to Lambda Console:**
   - Open: https://ap-south-1.console.aws.amazon.com/lambda/home?region=ap-south-1#/functions/ure-lambda-function

2. **Navigate to Configuration:**
   - Click the "Configuration" tab
   - Click "Environment variables" in the left menu

3. **Edit Environment Variables:**
   - Click "Edit" button
   - Find or add `BEDROCK_MODEL_ID`
   - Change value from `apac.amazon.nova-lite-v1:0` to:
     ```
     amazon.nova-lite-v1:0
     ```
   - Ensure `BEDROCK_REGION` is set to:
     ```
     ap-south-1
     ```

4. **Save Changes:**
   - Click "Save" button
   - Wait 10-15 seconds for Lambda to update

### Step 3: Test the Fix

1. **Run Streamlit app:**
   ```powershell
   .\run_streamlit.ps1
   ```

2. **Open browser:**
   - Go to http://localhost:8501

3. **Test a query:**
   - Type: "What are the symptoms of tomato late blight?"
   - Click "Send"
   - Should get a response without errors

## Model IDs Reference

### Available Models in Mumbai (ap-south-1)

| Model Name | Model ID | Use Case |
|------------|----------|----------|
| Nova Micro | `amazon.nova-micro-v1:0` | Fastest, cheapest |
| Nova Lite | `amazon.nova-lite-v1:0` | Balanced (recommended) |
| Nova Pro | `amazon.nova-pro-v1:0` | Most capable |

### INCORRECT Model IDs (Don't Use)
- ❌ `apac.amazon.nova-lite-v1:0` (APAC inference profile - not available)
- ❌ `us.amazon.nova-pro-v1:0` (US region model)

## Verification

After completing all steps, verify:

1. ✅ Model access shows "Access granted" in Bedrock console
2. ✅ Lambda environment variable updated to `amazon.nova-lite-v1:0`
3. ✅ Streamlit app connects and responds without errors

## Troubleshooting

### Still getting "Operation not allowed"?
- Wait 5 minutes after enabling model access
- Check you're in the correct region (ap-south-1)
- Verify Lambda environment variable is saved

### Getting "Model not found"?
- Double-check model ID spelling: `amazon.nova-lite-v1:0`
- Ensure no extra spaces in environment variable

### Lambda update not working?
- Try stopping and restarting Streamlit app
- Lambda may take 10-15 seconds to pick up new environment variables

## Current Configuration

**Mumbai Lambda:**
- Function: `ure-lambda-function`
- Region: `ap-south-1`
- API Endpoint: `https://3dcqel7asa.execute-api.ap-south-1.amazonaws.com/prod/query`

**Recommended Model:**
- Model ID: `amazon.nova-lite-v1:0`
- Region: `ap-south-1`
- Good balance of speed, cost, and capability

## Next Steps

Once fixed:
1. Test with various queries
2. Test with image upload (crop disease detection)
3. Test in different languages (Hindi, Marathi)
4. Monitor Lambda logs for any errors

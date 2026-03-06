# Quick Fix Summary

## Problem
Mumbai Lambda has wrong Bedrock model ID: `apac.amazon.nova-lite-v1:0`
Should be: `amazon.nova-lite-v1:0`

## Why It's Broken
- AWS changed Bedrock model access policy
- Model ID format changed
- Your root account has permission restrictions preventing updates

## What We Changed (Locally)
1. ✅ Fixed `src/aws/lambda_handler.py` - default model ID corrected
2. ✅ Fixed `src/agents/supervisor_simple.py` - default model ID corrected  
3. ✅ Fixed `src/ui/app.py` - removed boto3 secrets requirement

## What Still Needs Fixing (On AWS)
❌ Lambda environment variable `BEDROCK_MODEL_ID` needs manual update

## Options to Fix

### Option 1: Update Lambda Manually (Recommended)
1. Go to Lambda Console (use a different browser or incognito mode)
2. Navigate to: Configuration → Environment variables
3. Change `BEDROCK_MODEL_ID` from `apac.amazon.nova-lite-v1:0` to `amazon.nova-lite-v1:0`
4. Save

### Option 2: Enable Bedrock Model First
1. Go to: https://ap-south-1.console.aws.amazon.com/bedrock/home?region=ap-south-1#/chat-playground
2. Select "Amazon Nova Lite" model
3. Send a test message (this enables the model)
4. Then try updating Lambda

### Option 3: Create IAM User with Proper Permissions
Your root account has restrictions. Create an IAM user with:
- `lambda:UpdateFunctionConfiguration`
- `lambda:UpdateFunctionCode`
- `bedrock:InvokeModel`

### Option 4: Contact AWS Support
Explain that your root account can't update Lambda or enable Bedrock models.

## Current Status
- ✅ Streamlit app is running on http://localhost:8501
- ✅ Local code is fixed
- ❌ Mumbai Lambda still has wrong model ID
- ❌ Can't deploy due to permission restrictions

## Temporary Workaround
If you have access to AWS Console from another device or browser:
1. Try logging in from a different browser
2. Navigate to Lambda → ure-lambda-function → Configuration → Environment variables
3. Update BEDROCK_MODEL_ID manually

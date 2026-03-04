# GramSetu Web UI Troubleshooting Guide

**Date**: March 2, 2026  
**Status**: CORS Enabled, Debug Mode Active

---

## Recent Fixes Applied

### 1. ✅ S3 Bucket Policy Fixed
- Added CloudFront OAI to bucket policy
- CloudFront can now access `web-ui/*` files
- **Script**: `scripts/fix_bucket_policy_for_cloudfront.py`

### 2. ✅ CORS Enabled on API Gateway
- Added OPTIONS method for preflight requests
- Configured CORS headers on POST method
- Allowed origins: `*` (all origins)
- **Script**: `scripts/enable_cors_api_gateway.py`

### 3. ✅ Debug Mode Enabled
- Set `DEBUG_MODE = true` in config.js
- Browser console will show detailed logs
- CloudFront cache invalidated for immediate effect

---

## How to Test the Application

### Step 1: Open Browser Developer Tools
1. Open https://d3v7khazsfb4vd.cloudfront.net
2. Press `F12` to open Developer Tools
3. Go to the **Console** tab

### Step 2: Check for Errors
Look for these messages in the console:

**✅ Good Messages** (everything working):
```
GramSetu Configuration Loaded
API Gateway URL: https://8938dqxf33.execute-api.us-east-1.amazonaws.com/dev/query
Sending query to API...
API Response received
```

**✗ Bad Messages** (problems):
```
CORS error
Access to fetch blocked by CORS policy
Failed to fetch
Network error
```

### Step 3: Test a Query
1. Type a message in the chat: "Hello"
2. Click Send
3. Watch the Console tab for API calls
4. Check the **Network** tab for the API request

---

## Common Issues and Solutions

### Issue 1: "Access Denied" XML Error

**Symptom**: White page with XML error message

**Cause**: S3 bucket policy doesn't allow CloudFront access

**Solution**:
```powershell
py scripts/fix_bucket_policy_for_cloudfront.py
```

---

### Issue 2: CORS Error in Browser Console

**Symptom**: 
```
Access to fetch at 'https://8938dqxf33.execute-api...' from origin 'https://d3v7khazsfb4vd.cloudfront.net' has been blocked by CORS policy
```

**Cause**: API Gateway doesn't have CORS enabled

**Solution**:
```powershell
py scripts/enable_cors_api_gateway.py
```

---

### Issue 3: "Sorry, I encountered an error" Message

**Symptom**: Error message in chat after sending query

**Possible Causes**:
1. Lambda function error
2. API Gateway timeout
3. Bedrock model access issue
4. Network connectivity

**Troubleshooting Steps**:

1. **Check Lambda Logs**:
```powershell
aws logs tail /aws/lambda/ure-mvp-handler --since 10m --follow
```

2. **Test API Directly**:
```powershell
$body = @{
    user_id = "test_user"
    query = "Hello"
    language = "en"
} | ConvertTo-Json

Invoke-WebRequest -Uri "https://8938dqxf33.execute-api.us-east-1.amazonaws.com/dev/query" -Method POST -Body $body -ContentType "application/json"
```

3. **Check Lambda Function Status**:
```powershell
aws lambda get-function --function-name ure-mvp-handler --query 'Configuration.[State,LastUpdateStatus]'
```

4. **Check Bedrock Model Access**:
```powershell
aws bedrock list-foundation-models --query 'modelSummaries[?modelId==`amazon.nova-lite-v1:0`]'
```

---

### Issue 4: Old Files Loading (Cache Issue)

**Symptom**: Changes not appearing, old version loading

**Cause**: CloudFront cache

**Solution**:
```powershell
# Invalidate all files
aws cloudfront create-invalidation --distribution-id E354ZTACSUHKWS --paths "/*"

# Or invalidate specific file
aws cloudfront create-invalidation --distribution-id E354ZTACSUHKWS --paths "/config.js"

# Hard refresh browser
# Press Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
```

---

### Issue 5: Image Upload Not Working

**Symptom**: Can't upload images or image upload fails

**Possible Causes**:
1. File size too large (>5MB)
2. Unsupported file format
3. API Gateway payload limit
4. Lambda timeout

**Solution**:
1. Check image size: Must be < 5MB
2. Supported formats: JPG, PNG, GIF, WEBP
3. Check browser console for errors
4. Check Lambda logs for timeout errors

---

### Issue 6: Language Switching Not Working

**Symptom**: Language selector doesn't change language

**Troubleshooting**:
1. Check browser console for JavaScript errors
2. Verify API is receiving language parameter
3. Check Lambda logs for translation errors

**Test**:
```powershell
# Test with Hindi
$body = @{
    user_id = "test_user"
    query = "Hello"
    language = "hi"
} | ConvertTo-Json

Invoke-WebRequest -Uri "https://8938dqxf33.execute-api.us-east-1.amazonaws.com/dev/query" -Method POST -Body $body -ContentType "application/json"
```

---

## Debugging Tools

### 1. Browser Developer Tools

**Console Tab**:
- Shows JavaScript errors
- Shows API calls and responses
- Shows debug messages (when DEBUG_MODE = true)

**Network Tab**:
- Shows all HTTP requests
- Shows request/response headers
- Shows request/response bodies
- Shows timing information

**Application Tab**:
- Shows localStorage data
- Shows session data
- Shows cookies

### 2. AWS CloudWatch Logs

**View Lambda Logs**:
```powershell
# Recent logs
aws logs tail /aws/lambda/ure-mvp-handler --since 10m

# Follow logs in real-time
aws logs tail /aws/lambda/ure-mvp-handler --follow

# Filter for errors
aws logs tail /aws/lambda/ure-mvp-handler --since 1h --filter-pattern "ERROR"
```

### 3. API Gateway Test

**Test from AWS Console**:
1. Go to API Gateway console
2. Select `ure-mvp-api`
3. Click on `/query` resource
4. Click on `POST` method
5. Click **Test** button
6. Enter test request body
7. Click **Test**

**Test from Command Line**:
```powershell
.\scripts\test_deployed_app.ps1
```

---

## Configuration Files

### config.js (Current Settings)
```javascript
window.API_GATEWAY_URL = 'https://8938dqxf33.execute-api.us-east-1.amazonaws.com/dev/query';
window.AWS_REGION = 'us-east-1';
window.DEBUG_MODE = true;  // Set to false in production
```

### S3 Bucket Policy (Current)
- Allows Bedrock Knowledge Base access
- Allows CloudFront OAI access to `web-ui/*`

### API Gateway CORS (Current)
- Allowed Origins: `*`
- Allowed Methods: GET, POST, PUT, DELETE, OPTIONS
- Allowed Headers: Content-Type, X-Amz-Date, Authorization, X-Api-Key, X-Amz-Security-Token

---

## Quick Fix Commands

### Reset Everything
```powershell
# 1. Fix bucket policy
py scripts/fix_bucket_policy_for_cloudfront.py

# 2. Enable CORS
py scripts/enable_cors_api_gateway.py

# 3. Re-upload web UI files
aws s3 sync src/web/aws-native/ s3://ure-mvp-data-us-east-1-188238313375/web-ui/ --cache-control "max-age=300"

# 4. Invalidate CloudFront cache
aws cloudfront create-invalidation --distribution-id E354ZTACSUHKWS --paths "/*"

# 5. Wait 2-3 minutes and test
start https://d3v7khazsfb4vd.cloudfront.net
```

### Check Status
```powershell
# Quick status
.\scripts\quick_status.ps1

# Detailed status
.\scripts\check_aws_deployment_status.ps1 -Detailed

# Test application
.\scripts\test_deployed_app.ps1
```

---

## Expected Behavior

### Successful Query Flow

1. **User types message** → "What is PM-Kisan?"
2. **JavaScript sends POST request** → API Gateway
3. **API Gateway forwards** → Lambda function
4. **Lambda processes query**:
   - Identifies query type
   - Routes to appropriate agent
   - Calls Bedrock for AI response
   - May query Knowledge Base for schemes
5. **Lambda returns response** → API Gateway
6. **API Gateway returns** → JavaScript
7. **JavaScript displays response** → Chat UI

**Expected Time**: 2-5 seconds

### Successful Image Upload Flow

1. **User selects image** → File input
2. **JavaScript reads image** → Base64 encoding
3. **JavaScript sends POST request** → API Gateway (with image data)
4. **Lambda receives image**:
   - Decodes base64
   - Calls Bedrock Vision API
   - Analyzes crop disease
5. **Lambda returns diagnosis** → API Gateway
6. **JavaScript displays result** → Chat UI

**Expected Time**: 3-8 seconds

---

## Contact Information

If issues persist after trying all troubleshooting steps:

1. Check CloudWatch logs for detailed error messages
2. Verify all AWS services are active
3. Check AWS service health dashboard
4. Review recent AWS account changes

---

## Status Summary

✅ **CloudFront**: Deployed and accessible
✅ **S3 Bucket Policy**: Fixed for CloudFront access
✅ **API Gateway**: CORS enabled
✅ **Lambda Function**: Active
✅ **DynamoDB**: All tables active
✅ **Debug Mode**: Enabled for troubleshooting

**Application URL**: https://d3v7khazsfb4vd.cloudfront.net

---

**Last Updated**: March 2, 2026 18:30  
**Next Action**: Test application with browser developer tools open

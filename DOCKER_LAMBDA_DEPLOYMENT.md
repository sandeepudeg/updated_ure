# Docker Lambda Deployment Guide

## Overview

You have two options for deploying with Docker support:

1. **Create a NEW Lambda function** with Docker support (Recommended)
2. **Keep existing Lambda** and use ZIP deployment

---

## Option 1: Create New Docker Lambda (Recommended)

This creates a new Lambda function specifically for Docker container images.

### Why This Option?

- ✅ Full Docker support with all privacy features
- ✅ Easier updates (just push new Docker image)
- ✅ Better isolation and dependency management
- ✅ Can run side-by-side with existing Lambda

### Quick Start

```powershell
# Complete workflow: Build image + Create Lambda
.\scripts\deploy_new_docker_lambda.ps1
```

This will:
1. Build Docker image
2. Push to ECR
3. Create new Lambda function: `ure-mvp-handler-docker`
4. Configure all environment variables
5. Test the function

**Duration**: ~10-15 minutes

### Step-by-Step (If You Prefer)

```powershell
# Step 1: Build and push Docker image
.\scripts\deploy_docker_lambda.ps1 -SkipTests

# Step 2: Create new Lambda function
.\scripts\create_docker_lambda.ps1
```

### New Lambda Details

- **Name**: `ure-mvp-handler-docker`
- **Package Type**: Image (Docker)
- **Memory**: 512 MB
- **Timeout**: 300 seconds (5 minutes)
- **Runtime**: Python 3.11 (in container)

---

## Option 2: Keep Existing Lambda (ZIP Deployment)

Continue using your existing `ure-mvp-handler` with ZIP deployment.

### Why This Option?

- ✅ No changes to existing setup
- ✅ Faster deployment
- ✅ Works with current API Gateway configuration

### Quick Start

```powershell
.\scripts\deploy_lambda_zip.ps1
```

This will:
1. Package code as ZIP
2. Update existing `ure-mvp-handler`
3. Configure environment variables

**Duration**: ~2-3 minutes

---

## Comparison

| Feature | New Docker Lambda | Existing ZIP Lambda |
|---------|-------------------|---------------------|
| **Deployment Type** | Container Image | ZIP Package |
| **Function Name** | `ure-mvp-handler-docker` | `ure-mvp-handler` |
| **Setup Time** | 10-15 minutes | 2-3 minutes |
| **Privacy Features** | ✅ All included | ✅ All included |
| **Updates** | Push new image | Upload new ZIP |
| **API Gateway** | Needs update | Already configured |
| **Dependencies** | In container | In ZIP |
| **Size Limit** | 10 GB | 250 MB |

---

## Recommended Approach

### For Production: Option 1 (New Docker Lambda)

```powershell
# Deploy new Docker Lambda
.\scripts\deploy_new_docker_lambda.ps1
```

**Then update API Gateway** to point to the new function:

```powershell
# Get your API Gateway ID
$API_ID = "8938dqxf33"
$STAGE = "dev"

# Update integration to use new Lambda
aws apigatewayv2 update-integration `
  --api-id $API_ID `
  --integration-id <integration-id> `
  --integration-uri "arn:aws:lambda:us-east-1:188238313375:function:ure-mvp-handler-docker" `
  --region us-east-1

# Deploy changes
aws apigatewayv2 create-deployment `
  --api-id $API_ID `
  --stage-name $STAGE `
  --region us-east-1
```

### For Quick Testing: Option 2 (ZIP)

```powershell
# Update existing Lambda with ZIP
.\scripts\deploy_lambda_zip.ps1
```

---

## Post-Deployment Steps

### 1. Test Lambda Function

**For Docker Lambda:**
```powershell
aws lambda invoke `
  --function-name ure-mvp-handler-docker `
  --payload '{"user_id":"test","query":"What is tomato blight?"}' `
  --region us-east-1 `
  response.json

cat response.json
```

**For ZIP Lambda:**
```powershell
aws lambda invoke `
  --function-name ure-mvp-handler `
  --payload '{"user_id":"test","query":"What is tomato blight?"}' `
  --region us-east-1 `
  response.json

cat response.json
```

### 2. Enable DynamoDB TTL (One-time)

```powershell
aws dynamodb update-time-to-live `
  --table-name ure-conversations `
  --time-to-live-specification "Enabled=true,AttributeName=expiry_time" `
  --region us-east-1
```

### 3. Run Privacy Audit

```powershell
py scripts/run_privacy_audit.py
```

### 4. Monitor Logs

**For Docker Lambda:**
```powershell
aws logs tail /aws/lambda/ure-mvp-handler-docker --follow --region us-east-1
```

**For ZIP Lambda:**
```powershell
aws logs tail /aws/lambda/ure-mvp-handler --follow --region us-east-1
```

---

## Updating After Initial Deployment

### Update Docker Lambda

```powershell
# Build and push new image
.\scripts\deploy_docker_lambda.ps1 -SkipTests

# Update Lambda to use new image
aws lambda update-function-code `
  --function-name ure-mvp-handler-docker `
  --image-uri 188238313375.dkr.ecr.us-east-1.amazonaws.com/ure-lambda:latest `
  --region us-east-1
```

### Update ZIP Lambda

```powershell
.\scripts\deploy_lambda_zip.ps1
```

---

## Troubleshooting

### Docker Image Not Found

```powershell
# Check if image exists in ECR
aws ecr describe-images --repository-name ure-lambda --region us-east-1

# If not, build and push
.\scripts\deploy_docker_lambda.ps1 -SkipTests
```

### IAM Role Issues

```powershell
# Check if role exists
aws iam get-role --role-name ure-lambda-execution-role

# The create script will create it automatically if missing
```

### Lambda Function Already Exists

The creation script will ask if you want to delete and recreate. Answer "yes" to proceed.

---

## Summary

**Recommended for Production**: 
```powershell
.\scripts\deploy_new_docker_lambda.ps1
```

**Quick Update to Existing**:
```powershell
.\scripts\deploy_lambda_zip.ps1
```

Both options include all privacy features:
- ✅ IP Address Hashing
- ✅ TTL Auto-Deletion
- ✅ Migration Handler
- ✅ Privacy Auditor

Choose based on your needs! 🚀

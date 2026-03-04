# GramSetu Deployment Scripts

This directory contains scripts to deploy, monitor, and test the GramSetu application on AWS.

## Quick Reference

### Check Deployment Status

```powershell
# Quick status check (recommended)
.\scripts\quick_status.ps1

# Detailed status with all AWS resources
.\scripts\check_aws_deployment_status.ps1 -Detailed

# Continuous monitoring (refreshes every 30 seconds)
.\scripts\check_aws_deployment_status.ps1 -Watch

# Check only CloudFront distribution
.\scripts\check_cloudfront_deployment.ps1
```

### Test Deployed Application

```powershell
# Test web UI and API Gateway
.\scripts\test_deployed_app.ps1
```

### Deploy Application

```powershell
# Deploy web UI to S3 + CloudFront
py scripts/deploy_web_ui_to_s3.py

# Deploy Lambda function
py scripts/deploy_lambda.py

# Deploy full infrastructure (CloudFormation)
py scripts/deploy_cloudformation.py deploy --stack-name ure-mvp-stack --wait
```

---

## Script Details

### 1. `quick_status.ps1`
**Purpose**: Fast status check of all AWS resources

**Usage**:
```powershell
.\scripts\quick_status.ps1
```

**Output**:
- CloudFront distribution status
- S3 bucket status
- Lambda function status
- API Gateway status
- DynamoDB tables status

**When to use**: Quick health check before testing or after deployment

---

### 2. `check_aws_deployment_status.ps1`
**Purpose**: Comprehensive AWS resource monitoring

**Usage**:
```powershell
# Basic check
.\scripts\check_aws_deployment_status.ps1

# Detailed check with all information
.\scripts\check_aws_deployment_status.ps1 -Detailed

# Continuous monitoring (auto-refresh every 30 seconds)
.\scripts\check_aws_deployment_status.ps1 -Watch

# Detailed + continuous monitoring
.\scripts\check_aws_deployment_status.ps1 -Detailed -Watch
```

**Features**:
- Deployment summary
- In-progress activities detection
- CloudFront distribution details
- S3 bucket information
- Lambda function configuration
- API Gateway endpoints
- DynamoDB table status
- CloudFormation stack status
- Bedrock configuration

**When to use**: 
- After deployment to monitor progress
- Troubleshooting deployment issues
- Checking resource configuration

---

### 3. `check_cloudfront_deployment.ps1`
**Purpose**: Check CloudFront distribution deployment status

**Usage**:
```powershell
.\scripts\check_cloudfront_deployment.ps1
```

**Output**:
- Distribution status (Deployed/InProgress)
- CloudFront URL
- Estimated time remaining

**When to use**: During initial deployment (CloudFront takes 10-15 minutes)

---

### 4. `test_deployed_app.ps1`
**Purpose**: End-to-end testing of deployed application

**Usage**:
```powershell
.\scripts\test_deployed_app.ps1
```

**Tests**:
1. CloudFront web UI accessibility
2. API Gateway backend functionality
3. S3 bucket file verification
4. DynamoDB tables status

**When to use**: After deployment completes to verify everything works

---

### 5. `deploy_web_ui_to_s3.py`
**Purpose**: Deploy web UI to S3 + CloudFront

**Usage**:
```powershell
py scripts/deploy_web_ui_to_s3.py
```

**What it does**:
1. Creates S3 bucket (if doesn't exist)
2. Uploads HTML/CSS/JavaScript files
3. Creates CloudFront distribution with OAI
4. Configures CORS
5. Outputs CloudFront URL

**When to use**: 
- Initial deployment
- After updating web UI files
- Re-deploying frontend

---

### 6. `deploy_lambda.py`
**Purpose**: Package and deploy Lambda function

**Usage**:
```powershell
py scripts/deploy_lambda.py
```

**What it does**:
1. Creates deployment package with dependencies
2. Uploads to Lambda
3. Updates function configuration
4. Verifies deployment

**When to use**: After modifying Lambda handler or agent code

---

### 7. `deploy_cloudformation.py`
**Purpose**: Deploy full AWS infrastructure

**Usage**:
```powershell
# Deploy new stack
py scripts/deploy_cloudformation.py deploy --stack-name ure-mvp-stack --wait

# Update existing stack
py scripts/deploy_cloudformation.py update --stack-name ure-mvp-stack --wait

# Get stack outputs
py scripts/deploy_cloudformation.py outputs --stack-name ure-mvp-stack

# Delete stack
py scripts/deploy_cloudformation.py delete --stack-name ure-mvp-stack
```

**When to use**: 
- Initial infrastructure setup
- Updating infrastructure configuration
- Recreating resources

---

## Deployment Workflow

### Initial Deployment

```powershell
# 1. Deploy infrastructure (if not exists)
py scripts/deploy_cloudformation.py deploy --stack-name ure-mvp-stack --wait

# 2. Deploy Lambda function
py scripts/deploy_lambda.py

# 3. Deploy web UI
py scripts/deploy_web_ui_to_s3.py

# 4. Wait for CloudFront (10-15 minutes)
.\scripts\check_cloudfront_deployment.ps1

# 5. Test application
.\scripts\test_deployed_app.ps1
```

### Update Web UI Only

```powershell
# 1. Make changes to src/web/aws-native/ files

# 2. Deploy updated files
py scripts/deploy_web_ui_to_s3.py

# 3. (Optional) Invalidate CloudFront cache for immediate updates
aws cloudfront create-invalidation --distribution-id E354ZTACSUHKWS --paths "/*"

# 4. Test changes
.\scripts\test_deployed_app.ps1
```

### Update Backend Only

```powershell
# 1. Make changes to Lambda handler or agents

# 2. Deploy Lambda
py scripts/deploy_lambda.py

# 3. Test API
.\scripts\test_deployed_app.ps1
```

---

## Current Deployment Information

### CloudFront Distribution
- **URL**: https://d3v7khazsfb4vd.cloudfront.net
- **Distribution ID**: E354ZTACSUHKWS
- **Status**: Deployed

### S3 Bucket
- **Name**: gramsetu-web-ui
- **Region**: us-east-1
- **Access**: Private (via CloudFront OAI)

### API Gateway
- **URL**: https://8938dqxf33.execute-api.us-east-1.amazonaws.com/dev/query
- **Method**: POST
- **Region**: us-east-1

### Lambda Function
- **Name**: ure-mvp-handler
- **Runtime**: Python 3.11
- **Memory**: 1024 MB
- **Timeout**: 300 seconds

### DynamoDB Tables
- ure-conversations
- ure-user-profiles
- ure-village-amenities

---

## Troubleshooting

### CloudFront shows "InProgress" for too long
```powershell
# Check distribution status
.\scripts\check_cloudfront_deployment.ps1

# If stuck for >20 minutes, check AWS Console
# CloudFront > Distributions > E354ZTACSUHKWS
```

### API Gateway returns errors
```powershell
# Check Lambda logs
aws logs tail /aws/lambda/ure-mvp-handler --follow

# Test API directly
.\scripts\test_deployed_app.ps1
```

### Web UI not loading
```powershell
# Check S3 files
aws s3 ls s3://gramsetu-web-ui/

# Check CloudFront status
.\scripts\quick_status.ps1

# Verify config.js has correct API URL
cat src/web/aws-native/config.js
```

### Lambda function errors
```powershell
# Check function status
aws lambda get-function --function-name ure-mvp-handler

# View recent logs
aws logs tail /aws/lambda/ure-mvp-handler --since 1h

# Test function directly
aws lambda invoke --function-name ure-mvp-handler --payload '{"user_id":"test","query":"hello","language":"en"}' response.json
```

---

## Cost Monitoring

```powershell
# Check current month costs
aws ce get-cost-and-usage --time-period Start=2026-03-01,End=2026-03-31 --granularity MONTHLY --metrics BlendedCost

# Check costs by service
aws ce get-cost-and-usage --time-period Start=2026-03-01,End=2026-03-31 --granularity MONTHLY --metrics BlendedCost --group-by Type=DIMENSION,Key=SERVICE
```

**Expected Monthly Costs**: $7-10/month
- S3: $0.50
- CloudFront: $1.00
- API Gateway: $0.04
- Lambda: $0.50
- DynamoDB: $0.15
- Bedrock: $3.00
- Other: $2.00

---

## Additional Resources

- **AWS Console**: https://console.aws.amazon.com/
- **CloudWatch Logs**: https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#logsV2:log-groups/log-group/$252Faws$252Flambda$252Fure-mvp-handler
- **CloudFront Console**: https://console.aws.amazon.com/cloudfront/v3/home
- **API Gateway Console**: https://console.aws.amazon.com/apigateway/home?region=us-east-1

---

**Last Updated**: March 2, 2026

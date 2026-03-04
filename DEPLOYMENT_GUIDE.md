# Docker Lambda Deployment Guide

Complete guide for testing, building, deploying, and auditing the URE Lambda function with privacy features.

---

## Prerequisites

- Docker Desktop installed and running
- AWS CLI configured with credentials
- Python 3.11 with `rural` virtual environment
- AWS Account: 188238313375
- Region: us-east-1

---

## Step 1: Local Testing

Test the Lambda handler locally before deployment.

### Run Unit Tests

```powershell
# Activate virtual environment
rural

# Run all unit tests
py -m pytest tests/ -v

# Run specific test files
py -m pytest tests/test_ip_hasher.py -v
py -m pytest tests/test_ttl_manager.py -v
py -m pytest tests/test_migration_handler.py -v
py -m pytest tests/test_privacy_auditor.py -v
```

### Test Lambda Handler Locally

```powershell
# Test Lambda handler with mock events
py scripts/test_lambda_locally.py
```

This will run 4 tests:
1. Basic text query
2. Query with location context
3. API Gateway event format (with IP hashing)
4. Error handling for missing parameters

**Expected Output**: All 4 tests should pass ✅

---

## Step 2: Build and Deploy to AWS

Deploy the Docker container to AWS Lambda.

### Option A: Full Deployment (Recommended)

```powershell
# Run full deployment (tests + build + deploy)
.\scripts\deploy_docker_lambda.ps1
```

### Option B: Skip Tests (if already tested)

```powershell
# Skip tests, run build + deploy
.\scripts\deploy_docker_lambda.ps1 -SkipTests
```

### Option C: Skip Build (if image already built)

```powershell
# Skip build, just deploy existing image
.\scripts\deploy_docker_lambda.ps1 -SkipBuild
```

### What the Deployment Script Does

1. ✅ Runs unit tests (unless skipped)
2. ✅ Checks Docker is running
3. ✅ Verifies AWS CLI and credentials
4. ✅ Creates ECR repository (if needed)
5. ✅ Logs in to ECR
6. ✅ Builds Docker image
7. ✅ Tags image for ECR
8. ✅ Pushes image to ECR
9. ✅ Updates Lambda function code
10. ✅ Waits for Lambda to be ready
11. ✅ Updates environment variables

**Expected Duration**: 5-10 minutes (first build may take longer)

---

## Step 3: Verify Deployment

### Check Lambda Function Status

```powershell
# Get Lambda function info
aws lambda get-function --function-name ure-mvp-handler --region us-east-1
```

### Test Lambda Function

```powershell
# Test with AWS CLI
aws lambda invoke `
  --function-name ure-mvp-handler `
  --payload '{"user_id":"test_001","query":"What is tomato blight?"}' `
  --region us-east-1 `
  response.json

# View response
cat response.json | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

### Check CloudWatch Logs

```powershell
# View recent logs
aws logs tail /aws/lambda/ure-mvp-handler --follow --region us-east-1
```

---

## Step 4: Run Privacy Audit

Scan DynamoDB tables for PII and privacy compliance.

### Run Privacy Audit Script

```powershell
# Run privacy audit
py scripts/run_privacy_audit.py
```

### What the Audit Checks

- ✅ IP addresses (should be hashed)
- ✅ Email addresses
- ✅ Phone numbers
- ✅ Aadhaar numbers
- ✅ Credit card numbers
- ✅ Location data
- ✅ TTL expiry times
- ✅ Potential PII in queries/responses

### Expected Output

```
Privacy Audit Report
====================

Conversations Table: ure-conversations
- Total records: X
- Records with PII: Y
- IP addresses hashed: ✅
- TTL configured: ✅

User Profiles Table: ure-user-profiles
- Total records: X
- Records with PII: Y

Recommendations:
- Consider encrypting location data
- Review query content for PII
```

---

## Step 5: Enable TTL on DynamoDB (One-time Setup)

Enable automatic data deletion after TTL expires.

```powershell
# Enable TTL on conversations table
aws dynamodb update-time-to-live `
  --table-name ure-conversations `
  --time-to-live-specification "Enabled=true,AttributeName=expiry_time" `
  --region us-east-1

# Verify TTL is enabled
aws dynamodb describe-time-to-live `
  --table-name ure-conversations `
  --region us-east-1
```

**Expected Output**: `TimeToLiveStatus: ENABLED`

---

## Troubleshooting

### Docker Build Fails

```powershell
# Check Docker is running
docker info

# Clean Docker cache
docker system prune -a

# Rebuild without cache
docker build --no-cache -t ure-lambda:latest -f Dockerfile .
```

### ECR Push Fails

```powershell
# Re-login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 188238313375.dkr.ecr.us-east-1.amazonaws.com

# Check ECR repository exists
aws ecr describe-repositories --repository-names ure-lambda --region us-east-1
```

### Lambda Update Fails

```powershell
# Check Lambda function exists
aws lambda get-function --function-name ure-mvp-handler --region us-east-1

# Check IAM permissions
aws iam get-role --role-name lambda-execution-role
```

### Tests Fail

```powershell
# Run tests with verbose output
py -m pytest tests/ -v -s

# Run specific test
py -m pytest tests/test_ip_hasher.py::test_hash_ip_address -v
```

---

## Environment Variables

The Lambda function uses these environment variables:

| Variable | Value | Description |
|----------|-------|-------------|
| `DYNAMODB_TABLE_NAME` | `ure-conversations` | Conversations table |
| `DYNAMODB_USER_TABLE` | `ure-user-profiles` | User profiles table |
| `S3_BUCKET_NAME` | `ure-mvp-data-us-east-1-188238313375` | S3 bucket for files |
| `LOG_LEVEL` | `INFO` | Logging level |
| `IP_HASH_SALT` | `<random-salt>` | Salt for IP hashing |
| `BEDROCK_REGION` | `us-east-1` | Bedrock region |

---

## Privacy Features Deployed

✅ **IP Address Hashing**: All IP addresses hashed with SHA-256 + salt  
✅ **TTL Auto-Deletion**: Conversations auto-deleted after 3 hours  
✅ **Encryption at Rest**: AWS-managed encryption on DynamoDB and S3  
✅ **HTTPS Only**: All API calls over HTTPS  
✅ **Privacy Audit**: Automated PII detection and reporting  

---

## Next Steps

1. **Test in Production**: Send real queries through API Gateway
2. **Monitor Metrics**: Check CloudWatch for errors and performance
3. **Run Regular Audits**: Schedule weekly privacy audits
4. **Implement Cognito**: Add anonymous authentication (Task 5.5)
5. **Add Migration Handler**: Migrate legacy users (Task 5.4)

---

## Quick Commands Reference

```powershell
# Full deployment pipeline
py -m pytest tests/ -v && .\scripts\deploy_docker_lambda.ps1 && py scripts/run_privacy_audit.py

# Test locally
py scripts/test_lambda_locally.py

# Deploy only
.\scripts\deploy_docker_lambda.ps1 -SkipTests

# Audit only
py scripts/run_privacy_audit.py

# View logs
aws logs tail /aws/lambda/ure-mvp-handler --follow --region us-east-1

# Test Lambda
aws lambda invoke --function-name ure-mvp-handler --payload '{"user_id":"test","query":"hello"}' --region us-east-1 response.json
```

---

## Support

For issues or questions:
1. Check CloudWatch logs for errors
2. Run privacy audit to verify data compliance
3. Review this guide for troubleshooting steps
4. Check AWS Console for Lambda/ECR/DynamoDB status

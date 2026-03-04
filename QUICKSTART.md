# Quick Start Guide

Get your Lambda deployed in 3 simple steps!

## Prerequisites

✅ Docker Desktop running  
✅ AWS CLI configured  
✅ Python virtual environment `rural` activated  

## Test Status

**162/168 tests passing** ✅  
**All 70 privacy tests passing** ✅  
**6 non-blocking failures** (MCP servers + performance benchmarks)

See [TEST_STATUS_EXPLAINED.md](TEST_STATUS_EXPLAINED.md) for details.

---

## Option 1: Full Pipeline (Recommended)

Run everything in one command:

```powershell
.\scripts\full_deployment_pipeline.ps1
```

This will:
1. ✅ Run privacy feature tests (70 tests)
2. ✅ Test Lambda handler locally
3. ✅ Build Docker image
4. ✅ Deploy to AWS Lambda
5. ✅ Run privacy audit

**Duration**: ~10 minutes

---

## Option 2: Test Privacy Features Only

Quick verification of privacy features:

```powershell
.\scripts\test_privacy_features.ps1
```

**Duration**: < 1 minute  
**Tests**: 70 privacy tests

---

## Option 3: Step-by-Step

### Step 1: Local Testing

```powershell
# Test privacy features
.\scripts\test_privacy_features.ps1

# Test Lambda locally
py scripts/test_lambda_locally.py
```

### Step 2: Deploy to AWS

```powershell
.\scripts\deploy_docker_lambda.ps1
```

### Step 3: Run Privacy Audit

```powershell
py scripts/run_privacy_audit.py
```

---

## Verify Deployment

```powershell
# Test Lambda function
aws lambda invoke `
  --function-name ure-mvp-handler `
  --payload '{"user_id":"test_001","query":"What is tomato blight?"}' `
  --region us-east-1 `
  response.json

# View response
cat response.json
```

---

## Enable TTL (One-time Setup)

```powershell
aws dynamodb update-time-to-live `
  --table-name ure-conversations `
  --time-to-live-specification "Enabled=true,AttributeName=expiry_time" `
  --region us-east-1
```

---

## Monitor Logs

```powershell
aws logs tail /aws/lambda/ure-mvp-handler --follow --region us-east-1
```

---

## Troubleshooting

**Docker not running?**
```powershell
# Start Docker Desktop, then retry
docker info
```

**AWS credentials issue?**
```powershell
# Verify credentials
aws sts get-caller-identity
```

**Tests failing?**
```powershell
# Run with verbose output
py -m pytest tests/ -v -s
```

---

For detailed documentation, see [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

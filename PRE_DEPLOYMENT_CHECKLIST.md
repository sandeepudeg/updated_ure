# Pre-Deployment Checklist

Complete this checklist before running the deployment pipeline.

---

## ✅ Prerequisites

### System Requirements

- [ ] **Docker Desktop** installed and running
  ```powershell
  docker info
  ```

- [ ] **AWS CLI** installed and configured
  ```powershell
  aws --version
  aws sts get-caller-identity
  ```

- [ ] **Python 3.11** with `rural` virtual environment
  ```powershell
  rural
  py --version
  ```

- [ ] **Git** repository up to date
  ```powershell
  git status
  ```

### AWS Configuration

- [ ] **AWS Account ID**: 188238313375
- [ ] **Region**: us-east-1
- [ ] **Lambda Function**: ure-mvp-handler exists
- [ ] **DynamoDB Tables**: ure-conversations, ure-user-profiles exist
- [ ] **S3 Bucket**: ure-mvp-data-us-east-1-188238313375 exists
- [ ] **Cognito Identity Pool**: Created (us-east-1:5dcbc3da-1fb4-4181-8c58-36713fa8f2fc)

### Verify AWS Resources

```powershell
# Check Lambda function
aws lambda get-function --function-name ure-mvp-handler --region us-east-1

# Check DynamoDB tables
aws dynamodb describe-table --table-name ure-conversations --region us-east-1
aws dynamodb describe-table --table-name ure-user-profiles --region us-east-1

# Check S3 bucket
aws s3 ls s3://ure-mvp-data-us-east-1-188238313375/

# Check Cognito
aws cognito-identity describe-identity-pool --identity-pool-id us-east-1:5dcbc3da-1fb4-4181-8c58-36713fa8f2fc --region us-east-1
```

---

## ✅ Code Quality

### Run Tests

- [ ] **All unit tests pass** (61 tests)
  ```powershell
  py -m pytest tests/ -v
  ```
  Expected: `61 passed`

- [ ] **No code errors**
  ```powershell
  py -m pytest tests/ --tb=short
  ```

- [ ] **Lambda handler imports correctly**
  ```powershell
  py -c "from src.aws.lambda_handler import lambda_handler; print('✅ Import successful')"
  ```

### Code Review

- [ ] **IP hasher** implemented in `src/utils/ip_hasher.py`
- [ ] **TTL manager** implemented in `src/utils/ttl_manager.py`
- [ ] **Migration handler** implemented in `src/utils/migration_handler.py`
- [ ] **Privacy auditor** implemented in `src/utils/privacy_auditor.py`
- [ ] **Lambda handler** updated with IP hashing and TTL

---

## ✅ Docker Configuration

### Dockerfile Validation

- [ ] **Dockerfile exists** and uses correct base image
  ```powershell
  cat Dockerfile | Select-String "FROM public.ecr.aws/lambda/python:3.11"
  ```

- [ ] **CMD handler path** is correct
  ```powershell
  cat Dockerfile | Select-String 'CMD \["src.aws.lambda_handler.lambda_handler"\]'
  ```

- [ ] **requirements-lambda.txt** exists with all dependencies
  ```powershell
  cat requirements-lambda.txt
  ```

### Docker Build Test (Optional)

- [ ] **Docker build succeeds** (optional pre-check)
  ```powershell
  docker build -t ure-lambda-test:latest -f Dockerfile .
  ```

---

## ✅ Environment Variables

### Required Environment Variables

Verify these will be set during deployment:

- [ ] `DYNAMODB_TABLE_NAME` = ure-conversations
- [ ] `DYNAMODB_USER_TABLE` = ure-user-profiles
- [ ] `S3_BUCKET_NAME` = ure-mvp-data-us-east-1-188238313375
- [ ] `LOG_LEVEL` = INFO
- [ ] `IP_HASH_SALT` = (will be generated during deployment)
- [ ] `BEDROCK_REGION` = us-east-1

---

## ✅ Deployment Scripts

### Script Permissions

- [ ] **Deployment script** exists and is executable
  ```powershell
  Test-Path .\scripts\deploy_docker_lambda.ps1
  ```

- [ ] **Full pipeline script** exists
  ```powershell
  Test-Path .\scripts\full_deployment_pipeline.ps1
  ```

- [ ] **Local test script** exists
  ```powershell
  Test-Path scripts\test_lambda_locally.py
  ```

- [ ] **Privacy audit script** exists
  ```powershell
  Test-Path scripts\run_privacy_audit.py
  ```

---

## ✅ Documentation

### Verify Documentation

- [ ] **DEPLOYMENT_GUIDE.md** exists with complete instructions
- [ ] **QUICKSTART.md** exists with quick commands
- [ ] **DEPLOYMENT_READY.md** exists with status summary
- [ ] **PRE_DEPLOYMENT_CHECKLIST.md** (this file) exists

---

## ✅ Backup and Safety

### Before Deployment

- [ ] **Backup current Lambda code** (if needed)
  ```powershell
  aws lambda get-function --function-name ure-mvp-handler --region us-east-1 > lambda-backup.json
  ```

- [ ] **Note current Lambda version**
  ```powershell
  aws lambda get-function --function-name ure-mvp-handler --region us-east-1 --query 'Configuration.Version'
  ```

- [ ] **Commit all changes to Git**
  ```powershell
  git add .
  git commit -m "Privacy features complete - ready for deployment"
  git push
  ```

---

## ✅ Final Checks

### Pre-Deployment Verification

- [ ] **All tests passing**: 61/61 ✅
- [ ] **Docker running**: `docker info` succeeds
- [ ] **AWS credentials valid**: `aws sts get-caller-identity` succeeds
- [ ] **Virtual environment active**: `rural` activated
- [ ] **No uncommitted changes**: `git status` clean (optional)

### Deployment Decision

- [ ] **Ready to deploy**: All checkboxes above are checked
- [ ] **Deployment window**: Choose appropriate time (low traffic)
- [ ] **Monitoring ready**: CloudWatch logs accessible

---

## 🚀 Ready to Deploy!

If all checkboxes are checked, you're ready to deploy!

### Deployment Command

```powershell
# Full pipeline (recommended)
.\scripts\full_deployment_pipeline.ps1

# Or step-by-step
py scripts/test_lambda_locally.py
.\scripts\deploy_docker_lambda.ps1
py scripts/run_privacy_audit.py
```

### Expected Duration

- Local testing: ~1 minute
- Docker build: ~3-5 minutes
- ECR push: ~2-3 minutes
- Lambda update: ~1-2 minutes
- Privacy audit: ~30 seconds

**Total**: ~10 minutes

---

## 📊 Post-Deployment Verification

After deployment completes:

1. [ ] **Test Lambda function**
   ```powershell
   aws lambda invoke --function-name ure-mvp-handler --payload '{"user_id":"test","query":"hello"}' --region us-east-1 response.json
   ```

2. [ ] **Check CloudWatch logs**
   ```powershell
   aws logs tail /aws/lambda/ure-mvp-handler --follow --region us-east-1
   ```

3. [ ] **Run privacy audit**
   ```powershell
   py scripts/run_privacy_audit.py
   ```

4. [ ] **Enable DynamoDB TTL** (one-time)
   ```powershell
   aws dynamodb update-time-to-live --table-name ure-conversations --time-to-live-specification "Enabled=true,AttributeName=expiry_time" --region us-east-1
   ```

5. [ ] **Test via API Gateway**
   ```powershell
   curl -X POST https://8938dqxf33.execute-api.us-east-1.amazonaws.com/dev/query -H "Content-Type: application/json" -d '{"user_id":"test","query":"hello"}'
   ```

---

## 🆘 Rollback Plan

If deployment fails:

1. **Check CloudWatch logs** for errors
2. **Revert Lambda to previous version** (if needed)
   ```powershell
   aws lambda update-function-code --function-name ure-mvp-handler --image-uri <previous-image-uri> --region us-east-1
   ```
3. **Review error messages** and fix issues
4. **Re-run tests** before retrying deployment

---

**Checklist Completed**: _____ / _____ items  
**Ready to Deploy**: [ ] Yes [ ] No  
**Deployment Date**: __________  
**Deployed By**: __________

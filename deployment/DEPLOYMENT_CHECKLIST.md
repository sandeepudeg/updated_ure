# GramSetu AWS Deployment Checklist

Use this checklist to ensure a successful deployment to AWS.

## Pre-Deployment Checklist

### Prerequisites
- [ ] AWS account created and active
- [ ] AWS CLI installed (`aws --version`)
- [ ] AWS CLI configured (`aws configure`)
- [ ] Docker Desktop installed and running (`docker ps`)
- [ ] PowerShell available
- [ ] Python 3.8+ installed (`python --version`)
- [ ] Git repository cloned

### AWS Permissions
- [ ] IAM user has Lambda permissions
- [ ] IAM user has ECR permissions
- [ ] IAM user has API Gateway permissions
- [ ] IAM user has S3 permissions
- [ ] IAM user has CloudFront permissions
- [ ] IAM user has DynamoDB permissions
- [ ] IAM user has CloudWatch permissions
- [ ] IAM user has Bedrock permissions

### Files Ready
- [ ] `Dockerfile` exists in deployment folder
- [ ] `.dockerignore` exists in deployment folder
- [ ] `requirements-lambda.txt` exists in root
- [ ] Source code in `src/` folder
- [ ] Web files in `src/web/v2/` folder

## Deployment Steps

### Step 1: Build Docker Image
```powershell
cd deployment
.\docker-build-and-push.ps1
```

- [ ] Docker image built successfully
- [ ] ECR repository created
- [ ] Image pushed to ECR
- [ ] Image URI noted down

### Step 2: Deploy Lambda Function
```powershell
.\deploy-lambda-docker.ps1
```

- [ ] Lambda function created/updated
- [ ] IAM role configured
- [ ] Environment variables set
- [ ] API Gateway configured
- [ ] Function URL obtained

### Step 3: Deploy Web Interface
```powershell
.\deploy-web.ps1
```

- [ ] S3 bucket created
- [ ] Web files uploaded
- [ ] CloudFront distribution created
- [ ] Web URL obtained

### Step 4: Test Deployment
```powershell
.\test-lambda.ps1
```

- [ ] Lambda function responds
- [ ] API Gateway endpoint works
- [ ] Web interface loads
- [ ] CloudWatch logs visible

## Post-Deployment Checklist

### Verification
- [ ] API endpoint returns 200 status
- [ ] Web interface displays correctly
- [ ] Lambda logs show in CloudWatch
- [ ] DynamoDB tables created
- [ ] S3 bucket accessible

### Testing
- [ ] Run diagnostic script
  ```powershell
  ..\scripts\diagnose-api.ps1
  ```
- [ ] Warm up Lambda
  ```powershell
  ..\scripts\warmup-lambda.ps1
  ```
- [ ] Collect performance metrics
  ```powershell
  ..\scripts\collect-performance-metrics.ps1
  ```
- [ ] Run load test
  ```powershell
  python ..\scripts\load_test.py 200 40
  ```

### Configuration
- [ ] Lambda memory optimized (2048 MB recommended)
- [ ] Lambda timeout set (60 seconds recommended)
- [ ] API Gateway throttling configured
- [ ] CloudFront caching enabled
- [ ] DynamoDB TTL enabled

### Security
- [ ] S3 bucket not publicly writable
- [ ] API Gateway has CORS configured
- [ ] Lambda has minimal IAM permissions
- [ ] CloudFront uses HTTPS only
- [ ] Secrets stored in Secrets Manager (if any)

### Monitoring
- [ ] CloudWatch alarms set up
  - Lambda errors > 1%
  - Lambda duration > 5 seconds
  - API Gateway 5xx errors
- [ ] CloudWatch dashboard created
- [ ] Log retention configured (7-30 days)

### Documentation
- [ ] API endpoint documented
- [ ] Web URL documented
- [ ] Environment variables documented
- [ ] Deployment date recorded
- [ ] Team notified

## URLs to Save

After deployment, save these URLs:

```
API Endpoint: https://{api-id}.execute-api.us-east-1.amazonaws.com/dev/query
Web URL: https://{distribution-id}.cloudfront.net
ECR Repository: {account-id}.dkr.ecr.us-east-1.amazonaws.com/ure-mvp
Lambda Function: ure-mvp-handler-docker
S3 Bucket: ure-mvp-web-{account-id}
CloudFront Distribution: {distribution-id}
```

## Performance Baseline

After deployment, establish performance baseline:

```powershell
# Warm up
.\warmup-lambda.ps1

# Collect metrics
.\collect-performance-metrics.ps1

# Load test
python ..\scripts\load_test.py 200 40

# Generate report
.\generate-performance-report.ps1
```

Record baseline metrics:
- [ ] Average response time: _______ ms
- [ ] Success rate: _______ %
- [ ] Throughput: _______ req/s
- [ ] Performance score: _______ / 100

## Troubleshooting Checklist

If deployment fails:

### Docker Issues
- [ ] Docker Desktop running?
- [ ] Docker login to ECR successful?
- [ ] Dockerfile syntax correct?
- [ ] All dependencies in requirements-lambda.txt?

### Lambda Issues
- [ ] IAM role exists?
- [ ] Lambda function created?
- [ ] Image URI correct?
- [ ] Environment variables set?
- [ ] Handler path correct?

### API Gateway Issues
- [ ] API created?
- [ ] Route configured?
- [ ] Lambda integration set?
- [ ] CORS enabled?
- [ ] Stage deployed?

### Web Issues
- [ ] S3 bucket created?
- [ ] Files uploaded?
- [ ] Bucket policy correct?
- [ ] CloudFront distribution active?
- [ ] DNS propagated?

## Rollback Plan

If deployment fails and needs rollback:

### Rollback Lambda
```bash
# List previous versions
aws lambda list-versions-by-function --function-name ure-mvp-handler-docker

# Rollback to previous version
aws lambda update-alias \
  --function-name ure-mvp-handler-docker \
  --name PROD \
  --function-version {previous-version}
```

### Rollback Web
```powershell
# Restore previous S3 files from backup
aws s3 sync s3://ure-mvp-web-backup/ s3://ure-mvp-web-{account-id}/

# Invalidate CloudFront cache
aws cloudfront create-invalidation \
  --distribution-id {distribution-id} \
  --paths "/*"
```

## Maintenance Checklist

### Weekly
- [ ] Check CloudWatch logs for errors
- [ ] Review Lambda metrics
- [ ] Check API Gateway throttling
- [ ] Monitor costs

### Monthly
- [ ] Run performance tests
- [ ] Review and optimize Lambda memory
- [ ] Clean up old ECR images
- [ ] Review DynamoDB usage
- [ ] Update dependencies

### Quarterly
- [ ] Security audit
- [ ] Cost optimization review
- [ ] Performance optimization
- [ ] Disaster recovery test

## Success Criteria

Deployment is successful when:

✅ All deployment steps completed without errors
✅ API endpoint returns valid responses
✅ Web interface loads and functions correctly
✅ Performance tests show acceptable results:
   - Success rate > 99%
   - Average response time < 3 seconds
   - Performance score > 70/100
✅ CloudWatch logs show no errors
✅ All monitoring and alarms configured
✅ Documentation updated
✅ Team trained on new deployment

## Sign-Off

Deployment completed by: ___________________
Date: ___________________
Deployment version: ___________________
Performance score: ___________________

Approved by: ___________________
Date: ___________________

## Next Steps After Deployment

1. [ ] Schedule performance testing
2. [ ] Set up CI/CD pipeline
3. [ ] Configure auto-scaling
4. [ ] Implement caching strategy
5. [ ] Plan for disaster recovery
6. [ ] Schedule team training
7. [ ] Create runbook for operations
8. [ ] Set up monitoring dashboard

## Resources

- **Deployment Guide**: `DEPLOY_TO_AWS.md`
- **Quick Reference**: `QUICK_REFERENCE.md`
- **Performance Testing**: `HIGH_LOAD_TESTING.md`
- **Lambda Warm-Up**: `LAMBDA_WARMUP_GUIDE.md`
- **AWS Services**: `AWS_SERVICES.md`

## Support Contacts

- AWS Support: https://console.aws.amazon.com/support/
- Team Lead: ___________________
- DevOps: ___________________
- On-Call: ___________________

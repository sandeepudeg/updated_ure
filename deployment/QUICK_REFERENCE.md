# GramSetu - Quick Reference Guide

## Quick Commands

### Full Deployment
```powershell
.\deployment\deploy-all.ps1
```

### Deploy Docker Only
```powershell
.\deployment\deploy-docker.ps1
```

### Deploy Web UI Only
```powershell
.\deployment\deploy-web.ps1
```

### Test Lambda
```powershell
.\deployment\test-lambda.ps1
```

### Test Web UI
```powershell
.\deployment\test-web.ps1
```

---

## Important URLs

| Resource | URL |
|----------|-----|
| Desktop UI | https://d3v7khazsfb4vd.cloudfront.net/gramsetu-agents.html |
| Mobile UI | https://d3v7khazsfb4vd.cloudfront.net/gramsetu-mobile.html |
| API Endpoint | https://8938dqxf33.execute-api.us-east-1.amazonaws.com/dev/query |
| AWS Console | https://console.aws.amazon.com |
| CloudWatch Logs | https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#logsV2:log-groups/log-group/$252Faws$252Flambda$252Fure-mvp-handler-docker |

---

## AWS Resources

| Resource Type | Name/ID | ARN |
|--------------|---------|-----|
| Lambda Function | ure-mvp-handler-docker | arn:aws:lambda:us-east-1:188238313375:function:ure-mvp-handler-docker |
| ECR Repository | ure-lambda-docker | arn:aws:ecr:us-east-1:188238313375:repository/ure-lambda-docker |
| S3 Bucket | ure-mvp-data-us-east-1-188238313375 | arn:aws:s3:::ure-mvp-data-us-east-1-188238313375 |
| CloudFront | E354ZTACSUHKWS | arn:aws:cloudfront::188238313375:distribution/E354ZTACSUHKWS |
| API Gateway | 8938dqxf33 | arn:aws:apigateway:us-east-1::/apis/8938dqxf33 |

---

## Common Tasks

### Update Lambda Code
```powershell
# Build and push Docker image
docker buildx build --platform linux/amd64 --load -t ure-lambda-docker .
docker tag ure-lambda-docker:latest 188238313375.dkr.ecr.us-east-1.amazonaws.com/ure-lambda-docker:latest
docker push 188238313375.dkr.ecr.us-east-1.amazonaws.com/ure-lambda-docker:latest

# Update Lambda
aws lambda update-function-code --function-name ure-mvp-handler-docker --image-uri 188238313375.dkr.ecr.us-east-1.amazonaws.com/ure-lambda-docker:latest --region us-east-1
```

### Update Web UI
```powershell
# Upload files
aws s3 cp src/web/v2/gramsetu-mobile.html s3://ure-mvp-data-us-east-1-188238313375/web-ui/gramsetu-mobile.html --content-type "text/html"

# Invalidate cache
aws cloudfront create-invalidation --distribution-id E354ZTACSUHKWS --paths "/*"
```

### View Lambda Logs
```powershell
aws logs tail /aws/lambda/ure-mvp-handler-docker --follow --region us-east-1
```

### Test Lambda Locally
```powershell
python scripts/test_lambda_locally.py
```

---

## Environment Variables

```env
AWS_REGION=us-east-1
AWS_ACCOUNT_ID=188238313375
BEDROCK_MODEL_ID=amazon.nova-lite-v1:0
DATA_GOV_API_KEY=<your_key>
S3_BUCKET=ure-mvp-data-us-east-1-188238313375
CLOUDFRONT_DIST=E354ZTACSUHKWS
```

---

## Troubleshooting

### Docker Build Fails
```powershell
# Check Docker is running
docker ps

# Clear cache
docker system prune -a

# Rebuild
docker buildx build --platform linux/amd64 --load -t ure-lambda-docker .
```

### Lambda Timeout
```powershell
# Increase timeout
aws lambda update-function-configuration --function-name ure-mvp-handler-docker --timeout 300 --region us-east-1
```

### Web UI Not Loading
```powershell
# Check CloudFront status
aws cloudfront get-distribution --id E354ZTACSUHKWS --query 'Distribution.Status'

# Force invalidation
aws cloudfront create-invalidation --distribution-id E354ZTACSUHKWS --paths "/*"
```

### API Not Responding
```powershell
# Check Lambda status
aws lambda get-function --function-name ure-mvp-handler-docker --region us-east-1 --query 'Configuration.[State,LastUpdateStatus]'

# View recent logs
aws logs tail /aws/lambda/ure-mvp-handler-docker --since 10m --region us-east-1
```

---

## Monitoring

### CloudWatch Metrics
```powershell
# View Lambda metrics
aws cloudwatch get-metric-statistics --namespace AWS/Lambda --metric-name Invocations --dimensions Name=FunctionName,Value=ure-mvp-handler-docker --start-time 2026-03-06T00:00:00Z --end-time 2026-03-06T23:59:59Z --period 3600 --statistics Sum --region us-east-1
```

### Cost Monitoring
```powershell
# View current month costs
aws ce get-cost-and-usage --time-period Start=2026-03-01,End=2026-03-31 --granularity MONTHLY --metrics BlendedCost --region us-east-1
```

---

## Backup and Restore

### Backup Lambda Configuration
```powershell
aws lambda get-function --function-name ure-mvp-handler-docker --region us-east-1 > lambda-backup.json
```

### Backup Web Files
```powershell
aws s3 sync s3://ure-mvp-data-us-east-1-188238313375/web-ui/ ./backup/web-ui/
```

### Restore from Git
```powershell
git checkout <commit-hash> -- src/
```

---

## Security

### Rotate API Keys
1. Get new DATA_GOV_API_KEY from data.gov.in
2. Update Lambda environment variable:
```powershell
aws lambda update-function-configuration --function-name ure-mvp-handler-docker --environment "Variables={BEDROCK_MODEL_ID=amazon.nova-lite-v1:0,DATA_GOV_API_KEY=new_key}" --region us-east-1
```

### Review IAM Permissions
```powershell
aws iam get-role --role-name ure-lambda-execution-role
aws iam list-attached-role-policies --role-name ure-lambda-execution-role
```

---

## Performance Optimization

### Increase Lambda Memory
```powershell
aws lambda update-function-configuration --function-name ure-mvp-handler-docker --memory-size 2048 --region us-east-1
```

### Enable Provisioned Concurrency
```powershell
aws lambda put-provisioned-concurrency-config --function-name ure-mvp-handler-docker --provisioned-concurrent-executions 1 --qualifier $LATEST --region us-east-1
```

---

## Useful AWS CLI Commands

```powershell
# List all Lambda functions
aws lambda list-functions --region us-east-1

# List ECR images
aws ecr list-images --repository-name ure-lambda-docker --region us-east-1

# List S3 buckets
aws s3 ls

# List CloudFront distributions
aws cloudfront list-distributions --query 'DistributionList.Items[*].[Id,DomainName]' --output table

# View API Gateway APIs
aws apigatewayv2 get-apis --region us-east-1
```

---

## Support

- **Documentation**: See deployment/README.md and deployment/DEPLOYMENT_GUIDE.md
- **AWS Support**: https://console.aws.amazon.com/support/
- **Data.gov.in Support**: https://data.gov.in/contact-us

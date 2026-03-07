# Deploy GramSetu to AWS Cloud

This guide explains how to deploy the complete GramSetu system to AWS using Docker containers.

## Files in This Folder

### Core Deployment Files
- **Dockerfile** - Docker container configuration for Lambda
- **.dockerignore** - Files to exclude from Docker build
- **docker-compose.yml** - Local Docker testing configuration
- **docker-build-and-push.ps1** - Build and push Docker image to ECR
- **deploy-lambda-docker.ps1** - Deploy Docker image to Lambda
- **deploy-docker.ps1** - Complete Docker deployment workflow
- **deploy-web.ps1** - Deploy web interface to S3/CloudFront
- **deploy-all.ps1** - Deploy everything (Docker + Web)

### Testing & Monitoring
- **test-lambda.ps1** - Test Lambda function after deployment
- **diagnose-api.ps1** - Diagnose API issues
- **warmup-lambda.ps1** - Warm up Lambda before testing
- **collect-performance-metrics.ps1** - Collect performance data
- **run-performance-tests-with-warmup.ps1** - Complete performance testing

### Documentation
- **DEPLOYMENT_GUIDE.md** - Comprehensive deployment guide
- **QUICK_REFERENCE.md** - Quick command reference
- **AWS_SERVICES.md** - AWS services used
- **LAMBDA_WARMUP_GUIDE.md** - Lambda warm-up documentation
- **HIGH_LOAD_TESTING.md** - High load testing guide
- **PERFORMANCE_TESTING_GUIDE.md** - Performance testing documentation

## Prerequisites

### 1. AWS Account Setup
- AWS account with appropriate permissions
- AWS CLI installed and configured
- IAM user with permissions for:
  - Lambda
  - ECR (Elastic Container Registry)
  - API Gateway
  - S3
  - CloudFront
  - DynamoDB
  - CloudWatch

### 2. Local Tools
- Docker Desktop installed and running
- PowerShell (Windows) or PowerShell Core (cross-platform)
- Python 3.8+ (for testing)
- AWS CLI v2

### 3. AWS CLI Configuration
```bash
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Default region: us-east-1
# Default output format: json
```

## Quick Start - Deploy Everything

### Option 1: One-Command Deployment
```powershell
cd deployment
.\deploy-all.ps1
```

This will:
1. Build Docker image
2. Push to AWS ECR
3. Deploy Lambda function
4. Deploy web interface to S3/CloudFront
5. Test the deployment

### Option 2: Step-by-Step Deployment

#### Step 1: Deploy Docker Lambda
```powershell
cd deployment
.\deploy-docker.ps1
```

This will:
- Build Docker image from Dockerfile
- Create ECR repository (if needed)
- Push image to ECR
- Create/update Lambda function
- Configure API Gateway
- Set up environment variables

#### Step 2: Deploy Web Interface
```powershell
.\deploy-web.ps1
```

This will:
- Upload web files to S3
- Configure CloudFront distribution
- Set up CORS
- Output the web URL

#### Step 3: Test Deployment
```powershell
.\test-lambda.ps1
```

This will:
- Test Lambda function directly
- Test API Gateway endpoint
- Verify web interface
- Check CloudWatch logs

## Detailed Deployment Steps

### 1. Build and Push Docker Image

```powershell
# Build Docker image
.\docker-build-and-push.ps1
```

**What it does:**
- Builds Docker image from Dockerfile
- Tags image with timestamp
- Creates ECR repository if it doesn't exist
- Pushes image to ECR
- Outputs image URI

**Output:**
```
Building Docker image...
✓ Image built successfully

Pushing to ECR...
✓ Image pushed successfully

Image URI: 123456789012.dkr.ecr.us-east-1.amazonaws.com/ure-mvp:latest
```

### 2. Deploy Lambda Function

```powershell
# Deploy Lambda with Docker image
.\deploy-lambda-docker.ps1
```

**What it does:**
- Creates Lambda function (if doesn't exist)
- Updates function code with Docker image
- Configures memory, timeout, environment variables
- Sets up IAM role and permissions
- Configures API Gateway integration

**Configuration:**
- Memory: 512 MB (can increase for better performance)
- Timeout: 30 seconds
- Runtime: Docker container
- Handler: lambda_handler.lambda_handler

**Environment Variables Set:**
- `DYNAMODB_TABLE_NAME`: ure-conversations
- `DYNAMODB_USER_TABLE`: ure-user-profiles
- `S3_BUCKET_NAME`: ure-mvp-data
- `BEDROCK_REGION`: us-east-1
- `LOG_LEVEL`: INFO

### 3. Deploy Web Interface

```powershell
# Deploy web to S3 and CloudFront
.\deploy-web.ps1
```

**What it does:**
- Creates S3 bucket (if doesn't exist)
- Uploads HTML, CSS, JS files
- Configures bucket for static website hosting
- Creates/updates CloudFront distribution
- Sets up CORS for API access

**Files Deployed:**
- `src/web/v2/gramsetu-agents.html`
- `src/web/v2/gramsetu-mobile.html`
- `src/web/v2/app.js`
- `src/web/v2/styles.css`
- `src/web/v2/config.js`

### 4. Test Deployment

```powershell
# Test everything
.\test-lambda.ps1
```

**Tests Performed:**
1. Lambda function invocation
2. API Gateway endpoint
3. Web interface accessibility
4. CloudWatch logs
5. Error handling

## Docker Configuration

### Dockerfile Explained

```dockerfile
FROM public.ecr.aws/lambda/python:3.11

# Copy requirements and install dependencies
COPY requirements-lambda.txt ${LAMBDA_TASK_ROOT}/
RUN pip install -r requirements-lambda.txt --target "${LAMBDA_TASK_ROOT}"

# Copy application code
COPY src/ ${LAMBDA_TASK_ROOT}/

# Set the CMD to your handler
CMD [ "aws.lambda_handler.lambda_handler" ]
```

**Key Points:**
- Base image: AWS Lambda Python 3.11
- Installs dependencies from `requirements-lambda.txt`
- Copies source code to Lambda task root
- Handler: `lambda_handler.lambda_handler` in `src/aws/lambda_handler.py`

### .dockerignore

Excludes unnecessary files from Docker build:
```
__pycache__/
*.pyc
*.pyo
*.pyd
.git/
.vscode/
tests/
*.md
.env
```

### docker-compose.yml

For local testing:
```yaml
version: '3.8'
services:
  lambda:
    build: .
    ports:
      - "9000:8080"
    environment:
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
      - AWS_DEFAULT_REGION=us-east-1
```

**Usage:**
```powershell
# Build and run locally
docker-compose up

# Test locally
curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{"user_id":"test","query":"hello"}'
```

## AWS Resources Created

### Lambda Function
- **Name**: `ure-mvp-handler-docker`
- **Runtime**: Docker container
- **Memory**: 512 MB (configurable)
- **Timeout**: 30 seconds
- **Concurrency**: Unreserved (auto-scales)

### ECR Repository
- **Name**: `ure-mvp`
- **Region**: us-east-1
- **Image Tag**: latest (with timestamp)

### API Gateway
- **Type**: REST API
- **Name**: `ure-mvp-api`
- **Stage**: dev
- **Endpoint**: `https://{api-id}.execute-api.us-east-1.amazonaws.com/dev/query`

### S3 Bucket
- **Name**: `ure-mvp-web-{account-id}`
- **Purpose**: Static website hosting
- **Public Access**: Enabled for CloudFront

### CloudFront Distribution
- **Origin**: S3 bucket
- **Cache**: Enabled
- **HTTPS**: Required
- **Domain**: `{distribution-id}.cloudfront.net`

### DynamoDB Tables
- **ure-conversations**: Stores user conversations
- **ure-user-profiles**: Stores user profiles

### IAM Role
- **Name**: `ure-mvp-lambda-role`
- **Permissions**:
  - Lambda execution
  - DynamoDB read/write
  - S3 read/write
  - CloudWatch logs
  - Bedrock API access

## Deployment Scripts Reference

### deploy-all.ps1
Complete deployment workflow
```powershell
.\deploy-all.ps1
```

### deploy-docker.ps1
Deploy Lambda with Docker
```powershell
.\deploy-docker.ps1
```

### deploy-web.ps1
Deploy web interface
```powershell
.\deploy-web.ps1
```

### docker-build-and-push.ps1
Build and push Docker image
```powershell
.\docker-build-and-push.ps1
```

### deploy-lambda-docker.ps1
Deploy Lambda function only
```powershell
.\deploy-lambda-docker.ps1 -ImageUri "123456789012.dkr.ecr.us-east-1.amazonaws.com/ure-mvp:latest"
```

### test-lambda.ps1
Test deployment
```powershell
.\test-lambda.ps1
```

## Configuration

### Update Lambda Memory
```bash
aws lambda update-function-configuration \
  --function-name ure-mvp-handler-docker \
  --memory-size 2048
```

### Update Lambda Timeout
```bash
aws lambda update-function-configuration \
  --function-name ure-mvp-handler-docker \
  --timeout 60
```

### Enable Provisioned Concurrency
```bash
aws lambda put-provisioned-concurrency-config \
  --function-name ure-mvp-handler-docker \
  --provisioned-concurrent-executions 10
```

### Update Environment Variables
```bash
aws lambda update-function-configuration \
  --function-name ure-mvp-handler-docker \
  --environment Variables="{DYNAMODB_TABLE_NAME=ure-conversations,LOG_LEVEL=DEBUG}"
```

## Monitoring

### CloudWatch Logs
```bash
# Tail logs
aws logs tail /aws/lambda/ure-mvp-handler-docker --follow

# Get recent logs
aws logs tail /aws/lambda/ure-mvp-handler-docker --since 1h
```

### CloudWatch Metrics
```bash
# Get Lambda metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Duration \
  --dimensions Name=FunctionName,Value=ure-mvp-handler-docker \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average
```

### Performance Testing
```powershell
# Warm up Lambda
.\warmup-lambda.ps1

# Collect metrics
.\collect-performance-metrics.ps1

# Run load test
python ../scripts/load_test.py 200 40

# Generate report
.\generate-performance-report.ps1
```

## Troubleshooting

### Issue: Docker build fails

**Solution:**
```powershell
# Check Docker is running
docker ps

# Clean Docker cache
docker system prune -a

# Rebuild
.\docker-build-and-push.ps1
```

### Issue: ECR push fails

**Solution:**
```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-east-1.amazonaws.com

# Retry push
.\docker-build-and-push.ps1
```

### Issue: Lambda deployment fails

**Solution:**
```bash
# Check Lambda function exists
aws lambda get-function --function-name ure-mvp-handler-docker

# Check IAM role
aws iam get-role --role-name ure-mvp-lambda-role

# Redeploy
.\deploy-lambda-docker.ps1
```

### Issue: API returns 500 errors

**Solution:**
```bash
# Check CloudWatch logs
aws logs tail /aws/lambda/ure-mvp-handler-docker --follow

# Check environment variables
aws lambda get-function-configuration --function-name ure-mvp-handler-docker

# Test Lambda directly
aws lambda invoke --function-name ure-mvp-handler-docker --payload '{"user_id":"test","query":"hello"}' output.json
```

## Cost Optimization

### Lambda
- Use ARM64 architecture (20% cheaper)
- Right-size memory allocation
- Enable Provisioned Concurrency only if needed

### S3
- Enable lifecycle policies
- Use Intelligent-Tiering

### CloudFront
- Enable caching (reduce origin requests)
- Use compression

### DynamoDB
- Use on-demand pricing for variable workloads
- Enable TTL for automatic data expiration

## Security Best Practices

### 1. Use IAM Roles
- Least privilege principle
- Separate roles for Lambda, S3, DynamoDB

### 2. Enable Encryption
- S3 bucket encryption
- DynamoDB encryption at rest
- CloudFront HTTPS only

### 3. API Security
- Enable API Gateway throttling
- Use API keys or Cognito authentication
- Enable CORS properly

### 4. Secrets Management
- Use AWS Secrets Manager for sensitive data
- Never hardcode credentials
- Use environment variables

## Next Steps

After deployment:

1. **Test the system**
   ```powershell
   .\test-lambda.ps1
   ```

2. **Run performance tests**
   ```powershell
   .\run-performance-tests-with-warmup.ps1
   ```

3. **Monitor CloudWatch**
   - Check Lambda metrics
   - Review logs for errors
   - Set up alarms

4. **Optimize performance**
   - Increase Lambda memory if needed
   - Enable caching
   - Consider Provisioned Concurrency

5. **Set up CI/CD**
   - Automate deployments
   - Use GitHub Actions or AWS CodePipeline
   - Implement blue-green deployments

## Support

For issues or questions:
- Check CloudWatch logs
- Review deployment scripts
- Run diagnostic tools
- Consult AWS documentation

## Summary

This deployment folder contains everything needed to deploy GramSetu to AWS:

✅ Docker configuration (Dockerfile, .dockerignore, docker-compose.yml)
✅ Deployment scripts (deploy-all.ps1, deploy-docker.ps1, deploy-web.ps1)
✅ Testing scripts (test-lambda.ps1, warmup-lambda.ps1)
✅ Performance testing (collect-performance-metrics.ps1, load_test.py)
✅ Documentation (this file and others)

Deploy with one command:
```powershell
.\deploy-all.ps1
```

Or follow the step-by-step guide above for more control!

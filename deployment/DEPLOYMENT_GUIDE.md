# GramSetu Deployment Guide

Complete step-by-step guide for deploying the GramSetu URE MVP to AWS.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [Local Development](#local-development)
4. [Docker Deployment](#docker-deployment)
5. [Web UI Deployment](#web-ui-deployment)
6. [Testing](#testing)
7. [Troubleshooting](#troubleshooting)
8. [Rollback Procedures](#rollback-procedures)

---

## Prerequisites

### Required Software

1. **Python 3.11**
   ```powershell
   python --version  # Should show 3.11.x
   ```

2. **Docker Desktop**
   ```powershell
   docker --version
   docker ps  # Should show running containers
   ```

3. **AWS CLI v2**
   ```powershell
   aws --version
   aws configure list  # Verify credentials
   ```

4. **Git**
   ```powershell
   git --version
   ```

### AWS Account Setup

1. **AWS Account ID**: 188238313375
2. **Region**: us-east-1
3. **IAM User**: With programmatic access
4. **Required Permissions**:
   - Lambda full access
   - ECR full access
   - S3 full access
   - CloudFront full access
   - API Gateway full access
   - Bedrock full access
   - IAM role creation

### API Keys

1. **Data.gov.in API Key**
   - Register at: https://data.gov.in
   - Navigate to: APIs → Register
   - Get API key for Agmarknet data

2. **AWS Bedrock Access**
   - Enable Bedrock in AWS Console
   - Request access to Amazon Nova Lite model
   - Wait for approval (usually instant)

---

## Initial Setup

### 1. Clone Repository

```powershell
git clone <repository-url>
cd Assembler_URE_Rural
```

### 2. Create Virtual Environment

```powershell
# Create virtual environment
python -m venv rural

# Activate (Windows)
.\rural\Scripts\Activate.ps1

# Activate (Linux/Mac)
source rural/bin/activate
```

### 3. Install Dependencies

```powershell
pip install -r requirements-lambda.txt
```

### 4. Configure Environment Variables

```powershell
# Copy example file
cp .env.example .env

# Edit .env file with your values
```

**.env file contents:**
```env
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCOUNT_ID=188238313375

# Bedrock Model
BEDROCK_MODEL_ID=amazon.nova-lite-v1:0

# Market Price API
DATA_GOV_API_KEY=your_actual_api_key_here

# S3 and CloudFront
S3_BUCKET=ure-mvp-data-us-east-1-188238313375
CLOUDFRONT_DIST=E354ZTACSUHKWS
```

### 5. Configure AWS CLI

```powershell
aws configure
# AWS Access Key ID: <your-key>
# AWS Secret Access Key: <your-secret>
# Default region: us-east-1
# Default output format: json
```

---

## Local Development

### 1. Test Agents Locally

```powershell
# Test supervisor agent
python src/agents/supervisor_simple.py

# Test market price function
python -c "from src.agents.supervisor_simple import get_market_prices; print(get_market_prices('Tomato', 'Nashik', 'Maharashtra'))"
```

### 2. Test Lambda Handler Locally

```powershell
python scripts/test_lambda_locally.py
```

### 3. Test Web UI Locally

```powershell
# Open test page
Start-Process test_mobile_ui.html
```

---

## Docker Deployment

### Step 1: Create ECR Repository

```powershell
$AWS_REGION = "us-east-1"
$ECR_REPO = "ure-lambda-docker"

# Create repository
aws ecr create-repository `
    --repository-name $ECR_REPO `
    --region $AWS_REGION
```

### Step 2: Login to ECR

```powershell
$AWS_ACCOUNT_ID = "188238313375"

aws ecr get-login-password --region $AWS_REGION | `
    docker login --username AWS --password-stdin `
    "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"
```

### Step 3: Build Docker Image

```powershell
# Build for Linux AMD64 (Lambda architecture)
docker buildx build --platform linux/amd64 --load -t $ECR_REPO .
```

### Step 4: Tag and Push Image

```powershell
# Tag image
docker tag "${ECR_REPO}:latest" `
    "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/${ECR_REPO}:latest"

# Push to ECR
docker push "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/${ECR_REPO}:latest"
```

### Step 5: Create Lambda Function

```powershell
$FUNCTION_NAME = "ure-mvp-handler-docker"
$IMAGE_URI = "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/${ECR_REPO}:latest"
$ROLE_ARN = "arn:aws:iam::${AWS_ACCOUNT_ID}:role/ure-lambda-execution-role"

# Create function
aws lambda create-function `
    --function-name $FUNCTION_NAME `
    --package-type Image `
    --code ImageUri=$IMAGE_URI `
    --role $ROLE_ARN `
    --timeout 300 `
    --memory-size 1024 `
    --environment "Variables={BEDROCK_MODEL_ID=amazon.nova-lite-v1:0,DATA_GOV_API_KEY=your_api_key}" `
    --region $AWS_REGION
```

### Step 6: Test Lambda Function

```powershell
# Create test payload
$payload = @{
    user_id = "test_user"
    query = "What is the price of tomato?"
    language = "English"
} | ConvertTo-Json

$payload | Out-File -FilePath "test_payload.json" -Encoding utf8

# Invoke function
aws lambda invoke `
    --function-name $FUNCTION_NAME `
    --payload file://test_payload.json `
    --region $AWS_REGION `
    response.json

# View response
Get-Content response.json | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

---

## Web UI Deployment

### Step 1: Upload to S3

```powershell
$S3_BUCKET = "ure-mvp-data-us-east-1-188238313375"
$S3_PREFIX = "web-ui"
$WEB_DIR = "src/web/v2"

# Upload HTML files
aws s3 cp "$WEB_DIR/gramsetu-agents.html" `
    "s3://$S3_BUCKET/$S3_PREFIX/gramsetu-agents.html" `
    --content-type "text/html"

aws s3 cp "$WEB_DIR/gramsetu-mobile.html" `
    "s3://$S3_BUCKET/$S3_PREFIX/gramsetu-mobile.html" `
    --content-type "text/html"

# Upload JavaScript and CSS
aws s3 cp "$WEB_DIR/config.js" `
    "s3://$S3_BUCKET/$S3_PREFIX/config.js" `
    --content-type "application/javascript"

aws s3 cp "$WEB_DIR/app.js" `
    "s3://$S3_BUCKET/$S3_PREFIX/app.js" `
    --content-type "application/javascript"

aws s3 cp "$WEB_DIR/styles.css" `
    "s3://$S3_BUCKET/$S3_PREFIX/styles.css" `
    --content-type "text/css"
```

### Step 2: Invalidate CloudFront Cache

```powershell
$CLOUDFRONT_DIST = "E354ZTACSUHKWS"

aws cloudfront create-invalidation `
    --distribution-id $CLOUDFRONT_DIST `
    --paths "/*"
```

### Step 3: Verify Deployment

```powershell
# Open URLs in browser
Start-Process "https://d3v7khazsfb4vd.cloudfront.net/gramsetu-agents.html"
Start-Process "https://d3v7khazsfb4vd.cloudfront.net/gramsetu-mobile.html"
```

---

## Complete End-to-End Deployment

### Using Automated Script

```powershell
# Run complete deployment
.\deployment\deploy-all.ps1
```

### Manual Step-by-Step

1. **Commit to Git**
   ```powershell
   git add .
   git commit -m "Deploy: <description>"
   git push origin main
   ```

2. **Build and Push Docker**
   ```powershell
   .\deployment\deploy-docker.ps1
   ```

3. **Update Lambda**
   ```powershell
   .\deployment\update-lambda.ps1
   ```

4. **Deploy Web UI**
   ```powershell
   .\deployment\deploy-web.ps1
   ```

5. **Test Everything**
   ```powershell
   .\deployment\test-deployment.ps1
   ```

---

## Testing

### 1. Test Lambda Function

```powershell
# Test with market price query
$payload = @{
    user_id = "test_user"
    query = "What is the price of tomato in Nashik?"
    language = "English"
} | ConvertTo-Json

$payload | Out-File -FilePath "test_payload.json" -Encoding utf8

aws lambda invoke `
    --function-name ure-mvp-handler-docker `
    --payload file://test_payload.json `
    --region us-east-1 `
    response.json

Get-Content response.json
```

### 2. Test API Gateway

```powershell
$API_ENDPOINT = "https://8938dqxf33.execute-api.us-east-1.amazonaws.com/dev/query"

$body = @{
    user_id = "test_user"
    query = "What is the price of tomato?"
    language = "English"
} | ConvertTo-Json

Invoke-RestMethod -Uri $API_ENDPOINT -Method POST -Body $body -ContentType "application/json"
```

### 3. Test Web UI

1. Open desktop UI: https://d3v7khazsfb4vd.cloudfront.net/gramsetu-agents.html
2. Open mobile UI: https://d3v7khazsfb4vd.cloudfront.net/gramsetu-mobile.html
3. Test chat functionality
4. Test image upload
5. Test agent selection
6. Test on mobile device

---

## Troubleshooting

### Docker Build Issues

**Problem**: Docker build fails
```
Solution:
1. Ensure Docker Desktop is running
2. Check Dockerfile syntax
3. Verify base image is accessible
4. Clear Docker cache: docker system prune -a
```

**Problem**: Image too large
```
Solution:
1. Use .dockerignore to exclude unnecessary files
2. Use multi-stage builds
3. Minimize layers in Dockerfile
```

### Lambda Issues

**Problem**: Lambda timeout
```
Solution:
1. Increase timeout in Lambda configuration
2. Optimize agent code
3. Check Bedrock API latency
4. Review CloudWatch logs
```

**Problem**: Out of memory
```
Solution:
1. Increase memory allocation (currently 1024 MB)
2. Optimize data loading
3. Use streaming for large responses
```

**Problem**: Cold start latency
```
Solution:
1. Use provisioned concurrency
2. Optimize Docker image size
3. Minimize dependencies
4. Use Lambda SnapStart (if available)
```

### API Gateway Issues

**Problem**: CORS errors
```
Solution:
1. Verify CORS configuration in API Gateway
2. Check allowed origins, methods, headers
3. Ensure preflight OPTIONS requests work
```

**Problem**: 502 Bad Gateway
```
Solution:
1. Check Lambda function is running
2. Verify Lambda execution role permissions
3. Check Lambda logs in CloudWatch
4. Verify API Gateway integration
```

### Web UI Issues

**Problem**: UI not loading
```
Solution:
1. Check CloudFront distribution status
2. Verify S3 bucket permissions
3. Clear browser cache
4. Check CloudFront invalidation status
```

**Problem**: API calls failing
```
Solution:
1. Verify API endpoint in config.js
2. Check browser console for errors
3. Verify CORS configuration
4. Test API endpoint directly
```

### Market Price API Issues

**Problem**: No price data returned
```
Solution:
1. Verify DATA_GOV_API_KEY is valid
2. Check API rate limits
3. Verify commodity name spelling
4. Falls back to CSV data automatically
```

---

## Rollback Procedures

### Rollback Lambda Function

```powershell
# List previous versions
aws lambda list-versions-by-function `
    --function-name ure-mvp-handler-docker `
    --region us-east-1

# Update to previous version
aws lambda update-function-code `
    --function-name ure-mvp-handler-docker `
    --image-uri <previous-image-uri> `
    --region us-east-1
```

### Rollback Web UI

```powershell
# Restore from Git
git checkout <previous-commit> -- src/web/v2/

# Redeploy
.\deployment\deploy-web.ps1
```

### Rollback Docker Image

```powershell
# List images in ECR
aws ecr list-images `
    --repository-name ure-lambda-docker `
    --region us-east-1

# Update Lambda to use previous image
aws lambda update-function-code `
    --function-name ure-mvp-handler-docker `
    --image-uri <previous-image-digest> `
    --region us-east-1
```

---

## Monitoring and Maintenance

### Daily Checks

1. Check CloudWatch logs for errors
2. Monitor Lambda invocation count
3. Check API Gateway 5xx errors
4. Verify Bedrock usage and costs

### Weekly Tasks

1. Review CloudWatch metrics
2. Check S3 storage usage
3. Review ECR image count
4. Update dependencies if needed

### Monthly Tasks

1. Review AWS costs
2. Update Python dependencies
3. Review and optimize Lambda performance
4. Update documentation

---

## Security Checklist

- [ ] API keys stored in environment variables
- [ ] IAM roles follow least privilege principle
- [ ] S3 bucket has appropriate access policies
- [ ] CloudFront uses HTTPS only
- [ ] Lambda function has appropriate timeout
- [ ] CloudWatch logs enabled
- [ ] Bedrock usage monitored
- [ ] Regular security updates applied

---

## Performance Optimization

### Lambda Optimization

1. **Memory**: Start with 1024 MB, adjust based on metrics
2. **Timeout**: 300 seconds for complex queries
3. **Concurrency**: Monitor and set reserved concurrency if needed
4. **Cold Starts**: Consider provisioned concurrency for production

### Bedrock Optimization

1. **Token Usage**: Monitor input/output tokens
2. **Model Selection**: Use Nova Lite for cost efficiency
3. **Caching**: Implement response caching for common queries
4. **Batching**: Batch similar requests when possible

### CloudFront Optimization

1. **Cache TTL**: Adjust based on content update frequency
2. **Compression**: Enable gzip/brotli compression
3. **Edge Locations**: Use all edge locations for global reach
4. **Origin Shield**: Consider for high-traffic scenarios

---

## Support and Resources

### AWS Documentation
- Lambda: https://docs.aws.amazon.com/lambda/
- Bedrock: https://docs.aws.amazon.com/bedrock/
- ECR: https://docs.aws.amazon.com/ecr/
- S3: https://docs.aws.amazon.com/s3/
- CloudFront: https://docs.aws.amazon.com/cloudfront/

### Project Resources
- GitHub Repository: <repository-url>
- Issue Tracker: <issues-url>
- Documentation: deployment/README.md

### Contact
- Development Team: <team-email>
- AWS Support: https://console.aws.amazon.com/support/

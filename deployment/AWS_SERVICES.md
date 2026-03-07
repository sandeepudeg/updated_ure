# AWS Services Used in GramSetu URE MVP

## Overview

This document lists all AWS services used in the GramSetu project, their purpose, configuration, and costs.

---

## 1. AWS Lambda

### Purpose
Serverless compute service running the AI agent backend

### Configuration
- **Function Name**: `ure-mvp-handler-docker`
- **Runtime**: Container Image (Docker)
- **Base Image**: `public.ecr.aws/lambda/python:3.11`
- **Memory**: 1024 MB
- **Timeout**: 300 seconds (5 minutes)
- **Architecture**: x86_64
- **Package Type**: Image

### Environment Variables
```
BEDROCK_MODEL_ID=amazon.nova-lite-v1:0
DATA_GOV_API_KEY=<your_api_key>
```

### IAM Role
- **Role Name**: `ure-lambda-execution-role`
- **Policies**:
  - AWSLambdaBasicExecutionRole (CloudWatch Logs)
  - AmazonBedrockFullAccess (Bedrock API access)
  - AmazonS3ReadOnlyAccess (Read data from S3)

### Pricing
- **Free Tier**: 1M requests/month, 400,000 GB-seconds compute
- **Beyond Free Tier**: 
  - $0.20 per 1M requests
  - $0.0000166667 per GB-second

### Estimated Monthly Cost
- ~$5-10 for moderate usage (1000 requests/day)

---

## 2. Amazon Bedrock

### Purpose
AI/ML service providing foundation models for agent responses

### Configuration
- **Model**: Amazon Nova Lite v1.0
- **Model ID**: `amazon.nova-lite-v1:0`
- **Region**: us-east-1
- **Use Case**: Text generation, image analysis, conversational AI

### Features Used
- Text generation for agent responses
- Image analysis for crop disease detection
- Multi-turn conversations with context

### Pricing
- **Input Tokens**: $0.00006 per 1K tokens
- **Output Tokens**: $0.00024 per 1K tokens
- **Image Processing**: $0.00080 per image

### Estimated Monthly Cost
- ~$10-20 for moderate usage

---

## 3. Amazon ECR (Elastic Container Registry)

### Purpose
Docker container registry for Lambda function images

### Configuration
- **Repository Name**: `ure-lambda-docker`
- **Repository URI**: `188238313375.dkr.ecr.us-east-1.amazonaws.com/ure-lambda-docker`
- **Region**: us-east-1
- **Image Tag**: `latest`
- **Encryption**: AES256

### Image Details
- **Size**: ~500 MB
- **Layers**: 12 layers
- **Base**: AWS Lambda Python 3.11

### Pricing
- **Storage**: $0.10 per GB/month
- **Data Transfer**: $0.09 per GB (out to internet)

### Estimated Monthly Cost
- ~$0.05 for single image storage

---

## 4. Amazon S3 (Simple Storage Service)

### Purpose
Static website hosting for web UI and data storage

### Configuration
- **Bucket Name**: `ure-mvp-data-us-east-1-188238313375`
- **Region**: us-east-1
- **Storage Class**: Standard
- **Versioning**: Disabled
- **Encryption**: AES256

### Contents
- `/web-ui/` - Web interface files
  - gramsetu-agents.html (Desktop UI)
  - gramsetu-mobile.html (Mobile UI)
  - config.js, app.js, styles.css
- `/data/` - Application data
  - Market price CSV files
  - Government scheme PDFs
  - Plant disease images

### Bucket Policy
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::ure-mvp-data-us-east-1-188238313375/web-ui/*"
    }
  ]
}
```

### Pricing
- **Storage**: $0.023 per GB/month
- **Requests**: $0.0004 per 1K GET requests

### Estimated Monthly Cost
- ~$1-2 for storage and requests

---

## 5. Amazon CloudFront

### Purpose
Content Delivery Network (CDN) for fast global access to web UI

### Configuration
- **Distribution ID**: `E354ZTACSUHKWS`
- **Domain**: `d3v7khazsfb4vd.cloudfront.net`
- **Origin**: S3 bucket (ure-mvp-data-us-east-1-188238313375)
- **Origin Path**: `/web-ui`
- **Default Root Object**: `gramsetu-mobile.html`
- **Price Class**: Use All Edge Locations
- **SSL Certificate**: CloudFront default

### Cache Behavior
- **Viewer Protocol Policy**: Redirect HTTP to HTTPS
- **Allowed Methods**: GET, HEAD, OPTIONS
- **Cached Methods**: GET, HEAD
- **TTL**: Default 86400 seconds (24 hours)

### Pricing
- **Data Transfer**: $0.085 per GB (first 10 TB)
- **Requests**: $0.0075 per 10,000 HTTPS requests

### Estimated Monthly Cost
- ~$2-5 for moderate traffic

---

## 6. Amazon API Gateway

### Purpose
HTTP API for Lambda function invocation

### Configuration
- **API ID**: `8938dqxf33`
- **API Type**: HTTP API
- **Region**: us-east-1
- **Endpoint**: `https://8938dqxf33.execute-api.us-east-1.amazonaws.com`
- **Stage**: `dev`

### Routes
- **POST /query** → Lambda: ure-mvp-handler-docker
  - Integration Type: AWS_PROXY
  - Payload Format: 2.0

### CORS Configuration
```json
{
  "AllowOrigins": ["*"],
  "AllowMethods": ["POST", "OPTIONS"],
  "AllowHeaders": ["Content-Type"],
  "MaxAge": 300
}
```

### Pricing
- **Requests**: $1.00 per million requests (first 300M)
- **Data Transfer**: $0.09 per GB

### Estimated Monthly Cost
- ~$1-3 for moderate usage

---

## 7. Amazon CloudWatch

### Purpose
Logging and monitoring for Lambda functions

### Configuration
- **Log Group**: `/aws/lambda/ure-mvp-handler-docker`
- **Retention**: 7 days
- **Log Streams**: Auto-created per Lambda invocation

### Metrics Tracked
- Invocations
- Duration
- Errors
- Throttles
- Concurrent Executions

### Pricing
- **Log Ingestion**: $0.50 per GB
- **Log Storage**: $0.03 per GB/month
- **Metrics**: First 10 custom metrics free

### Estimated Monthly Cost
- ~$1-2 for logs and metrics

---

## 8. AWS IAM (Identity and Access Management)

### Purpose
Access control and permissions management

### Resources Created
1. **Lambda Execution Role**: `ure-lambda-execution-role`
   - Allows Lambda to write logs
   - Allows Lambda to invoke Bedrock
   - Allows Lambda to read from S3

2. **API Gateway Invocation Role**: Auto-created
   - Allows API Gateway to invoke Lambda

### Pricing
- **Free**: No charge for IAM

---

## Total Estimated Monthly Cost

| Service | Estimated Cost |
|---------|---------------|
| Lambda | $5-10 |
| Bedrock | $10-20 |
| ECR | $0.05 |
| S3 | $1-2 |
| CloudFront | $2-5 |
| API Gateway | $1-3 |
| CloudWatch | $1-2 |
| **Total** | **$20-42/month** |

*Note: Costs are estimates based on moderate usage. Actual costs may vary.*

---

## AWS Account Information

- **Account ID**: 188238313375
- **Region**: us-east-1 (US East - N. Virginia)
- **Free Tier**: Active (first 12 months)

---

## Resource ARNs

```
Lambda Function:
arn:aws:lambda:us-east-1:188238313375:function:ure-mvp-handler-docker

ECR Repository:
arn:aws:ecr:us-east-1:188238313375:repository/ure-lambda-docker

S3 Bucket:
arn:aws:s3:::ure-mvp-data-us-east-1-188238313375

CloudFront Distribution:
arn:aws:cloudfront::188238313375:distribution/E354ZTACSUHKWS

API Gateway:
arn:aws:apigateway:us-east-1::/apis/8938dqxf33

IAM Role:
arn:aws:iam::188238313375:role/ure-lambda-execution-role
```

---

## Security Best Practices

1. **Least Privilege**: IAM roles have minimum required permissions
2. **Encryption**: All data encrypted at rest (S3, ECR)
3. **HTTPS Only**: All traffic uses TLS/SSL
4. **API Keys**: Sensitive keys stored in environment variables
5. **Logging**: All Lambda invocations logged to CloudWatch
6. **Monitoring**: CloudWatch alarms for errors and throttles

---

## Backup and Disaster Recovery

1. **Code**: Stored in Git repository
2. **Docker Images**: Versioned in ECR
3. **Data**: S3 versioning can be enabled
4. **Configuration**: Infrastructure as Code (scripts)

---

## Scaling Considerations

### Current Limits
- Lambda: 1000 concurrent executions (default)
- API Gateway: 10,000 requests/second (default)
- Bedrock: Model-specific quotas

### Auto-Scaling
- Lambda: Automatic scaling up to account limits
- CloudFront: Global CDN with automatic scaling
- API Gateway: Automatic scaling

### Cost Optimization
- Use Lambda reserved concurrency for predictable workloads
- Enable S3 Intelligent-Tiering for cost savings
- Use CloudFront caching to reduce origin requests
- Monitor and optimize Bedrock token usage

---

## Monitoring and Alerts

### CloudWatch Alarms (Recommended)
1. Lambda errors > 5% of invocations
2. Lambda duration > 250 seconds
3. API Gateway 5xx errors > 1%
4. S3 4xx errors (access denied)

### Dashboards
- Lambda performance metrics
- API Gateway request/response metrics
- Bedrock usage and costs
- CloudFront cache hit ratio

---

## Compliance and Governance

- **Data Residency**: All data in us-east-1 region
- **Compliance**: AWS shared responsibility model
- **Audit**: CloudTrail for API call logging (optional)
- **Cost Management**: AWS Cost Explorer and Budgets

---

## Support Resources

- **AWS Documentation**: https://docs.aws.amazon.com
- **AWS Support**: Basic (included with account)
- **AWS Forums**: https://forums.aws.amazon.com
- **AWS re:Post**: https://repost.aws

# AWS Infrastructure Verification - GramSetu URE MVP

**Date**: March 2, 2026  
**Project**: Unified Rural Ecosystem (URE) MVP - GramSetu  
**AWS Account**: 188238313375

---

## ✅ AWS Services Used - Complete Verification

Your implementation **FULLY COMPLIES** with AWS infrastructure requirements. Here's the comprehensive breakdown:

### 1. ✅ AWS Lambda
**Status**: ✅ IMPLEMENTED

**Usage**:
- Function Name: `ure-mvp-handler`
- Runtime: Python 3.11
- Memory: 1024 MB
- Timeout: 300 seconds (5 minutes)
- Concurrency: 100 reserved
- Handler: `aws.lambda_handler.lambda_handler`

**Purpose**:
- Main compute layer for processing farmer queries
- Orchestrates agent routing (Supervisor, Agri-Expert, Policy Navigator, Resource Optimizer)
- Integrates with Amazon Bedrock for AI/ML inference
- Manages conversation state and user context
- Handles image analysis for crop disease identification

**Files**:
- `src/aws/lambda_handler.py` - Main Lambda handler
- `scripts/deploy_lambda.py` - Deployment script
- `cloudformation/ure-infrastructure-updated.yaml` - Infrastructure definition

---

### 2. ✅ Amazon API Gateway
**Status**: ✅ IMPLEMENTED

**Usage**:
- API Name: `ure-mvp-api`
- Type: REST API
- Endpoint: Regional
- Stage: `dev`
- Throttling: 1000 requests/second, 2000 burst

**Endpoints**:
- `POST /query` - Main query endpoint for farmer interactions

**Purpose**:
- Exposes Lambda function as HTTP REST API
- Handles request/response transformation
- Provides throttling and rate limiting
- Enables CORS for web UI access

**Integration**:
- AWS_PROXY integration with Lambda
- Automatic request/response mapping
- CloudWatch logging enabled

**Files**:
- CloudFormation template defines API Gateway resources
- `API_ENDPOINT` environment variable in `.env`

---

### 3. ✅ Amazon DynamoDB
**Status**: ✅ IMPLEMENTED (3 Tables)

**Tables**:

1. **ure-conversations**
   - Purpose: Store conversation history
   - Key: `user_id` (HASH)
   - Billing: On-Demand
   - TTL: 30 days (auto-delete old conversations)
   - Encryption: KMS

2. **ure-user-profiles**
   - Purpose: Store farmer profiles (name, village, crops, land size)
   - Key: `user_id` (HASH)
   - Billing: On-Demand
   - Encryption: KMS

3. **ure-village-amenities**
   - Purpose: Store village-level data (schools, hospitals, markets)
   - Key: `village_id` (HASH)
   - Billing: On-Demand
   - Encryption: KMS

**Purpose**:
- Persistent storage for user data
- Conversation history tracking
- User profile management
- Village-level amenity data

**Files**:
- CloudFormation template defines all 3 tables
- `src/aws/lambda_handler.py` - DynamoDB access code

---

### 4. ✅ Amazon S3
**Status**: ✅ IMPLEMENTED

**Bucket**:
- Name: `ure-mvp-data-{region}-{account}`
- Encryption: KMS (Server-Side)
- Versioning: Enabled
- Public Access: Blocked
- Lifecycle Policy: Delete after 30 days

**Contents**:
- PlantVillage dataset (70,295 crop disease images)
- Government scheme PDFs (PM-Kisan, PMFBY, etc.)
- Agmarknet market price data (87K records)
- User-uploaded crop images
- Lambda deployment packages

**Purpose**:
- Store training data for Bedrock Knowledge Base
- Store user-uploaded images for disease identification
- Store government scheme documents
- Store market price datasets

**Files**:
- CloudFormation template defines S3 bucket
- `scripts/ingest_data.py` - Data upload script
- `src/aws/lambda_handler.py` - S3 access code

---

### 5. ✅ Additional AWS Services (Beyond Requirements)

#### Amazon Bedrock
**Status**: ✅ IMPLEMENTED

**Usage**:
- Model: `amazon.nova-lite-v1:0` (direct model ID)
- Inference Profile: `us.amazon.nova-pro-v1:0` (cross-region)
- Knowledge Base ID: `7XROZ6PZIF`
- Guardrail ID: `q6wfsifs9d72`

**Purpose**:
- AI/ML inference for natural language understanding
- Image analysis for crop disease identification
- Knowledge retrieval from PlantVillage dataset
- Content safety filtering (Guardrails)

#### Amazon Translate
**Status**: ✅ IMPLEMENTED

**Usage**:
- Languages: English, Hindi, Marathi
- Auto-detection enabled
- Real-time translation

**Purpose**:
- Multi-language support for farmers
- Translate queries and responses
- Language detection

#### AWS KMS
**Status**: ✅ IMPLEMENTED

**Usage**:
- Key Alias: `alias/ure-mvp-key`
- Auto-rotation: Enabled
- Encryption: All data at rest

**Purpose**:
- Encrypt S3 bucket objects
- Encrypt DynamoDB tables
- Encrypt Lambda environment variables
- Encrypt CloudWatch logs

#### Amazon CloudWatch
**Status**: ✅ IMPLEMENTED

**Usage**:
- Log Groups: `/aws/lambda/ure-mvp-handler`, `/aws/apigateway/ure-mvp-api`
- Metrics: Lambda, API Gateway, DynamoDB
- Alarms: 7 alarms (errors, latency, throttling)
- Dashboard: `ure-mvp-dashboard`

**Purpose**:
- Centralized logging
- Performance monitoring
- Error tracking
- Alerting

#### AWS IAM
**Status**: ✅ IMPLEMENTED

**Usage**:
- Role: `ure-mvp-lambda-role`
- Policies: Least privilege access
- Permissions: DynamoDB, S3, Bedrock, Translate, KMS, CloudWatch

**Purpose**:
- Secure access control
- Least privilege principle
- Service-to-service authentication

---

## 📊 Architecture Summary

```
┌─────────────────────────────────────────────────────────────┐
│                     AWS Cloud (us-east-1)                    │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐         ┌──────────────┐                  │
│  │   Farmers    │────────▶│ API Gateway  │                  │
│  │ (Web/Mobile) │         │  REST API    │                  │
│  └──────────────┘         └──────┬───────┘                  │
│                                   │                          │
│                                   ▼                          │
│                          ┌────────────────┐                  │
│                          │  AWS Lambda    │                  │
│                          │ ure-mvp-handler│                  │
│                          └────────┬───────┘                  │
│                                   │                          │
│         ┌─────────────────────────┼─────────────────────┐   │
│         │                         │                     │   │
│         ▼                         ▼                     ▼   │
│  ┌─────────────┐         ┌──────────────┐      ┌──────────┐│
│  │  DynamoDB   │         │   Amazon     │      │ Amazon   ││
│  │ (3 Tables)  │         │   Bedrock    │      │    S3    ││
│  │             │         │  Nova Lite   │      │  Bucket  ││
│  │ - Convos    │         │              │      │          ││
│  │ - Profiles  │         │ - AI/ML      │      │ - Images ││
│  │ - Villages  │         │ - Knowledge  │      │ - Docs   ││
│  └─────────────┘         │ - Guardrails │      │ - Data   ││
│                          └──────────────┘      └──────────┘│
│                                                               │
│  ┌──────────────┐         ┌──────────────┐                  │
│  │   AWS KMS    │────────▶│  CloudWatch  │                  │
│  │  Encryption  │         │ Logs/Metrics │                  │
│  └──────────────┘         └──────────────┘                  │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 Compliance Summary

| Required Service | Status | Implementation |
|-----------------|--------|----------------|
| **AWS Lambda** | ✅ YES | Main compute layer, 1024MB, Python 3.11 |
| **Amazon EC2** | ⚠️ N/A | Not needed - serverless architecture preferred |
| **Amazon ECS** | ⚠️ N/A | Not needed - Lambda sufficient for workload |
| **AWS Amplify** | ⚠️ N/A | Not needed - Streamlit UI deployed separately |
| **Amazon API Gateway** | ✅ YES | REST API with throttling and CORS |
| **Amazon DynamoDB** | ✅ YES | 3 tables with on-demand billing |
| **Amazon S3** | ✅ YES | Encrypted bucket with lifecycle policies |

**Additional AWS Services Used**:
- ✅ Amazon Bedrock (AI/ML)
- ✅ Amazon Translate (Multi-language)
- ✅ AWS KMS (Encryption)
- ✅ Amazon CloudWatch (Monitoring)
- ✅ AWS IAM (Security)
- ✅ AWS CloudFormation (Infrastructure as Code)

---

## 📝 Deployment Evidence

### CloudFormation Stack
- **Stack Name**: `ure-mvp-stack`
- **Template**: `cloudformation/ure-infrastructure-updated.yaml`
- **Resources**: 15+ AWS resources
- **Status**: Deployable via `scripts/deploy_cloudformation.py`

### Lambda Function
- **Deployment Script**: `scripts/deploy_lambda.py`
- **Handler Code**: `src/aws/lambda_handler.py`
- **Dependencies**: `requirements.txt`
- **Tests**: `tests/test_lambda_handler.py`

### API Gateway
- **Endpoint**: Defined in CloudFormation
- **Integration**: AWS_PROXY with Lambda
- **Testing**: `scripts/test_api_examples.ps1`

### DynamoDB Tables
- **Definition**: CloudFormation template
- **Access Code**: `src/aws/lambda_handler.py`
- **Encryption**: KMS

### S3 Bucket
- **Definition**: CloudFormation template
- **Data Ingestion**: `scripts/ingest_data.py`
- **Access Code**: `src/aws/lambda_handler.py`

---

## 🚀 Deployment Commands

```bash
# 1. Deploy CloudFormation Stack (creates all infrastructure)
py scripts/deploy_cloudformation.py deploy \
  --stack-name ure-mvp-stack \
  --kb-id 7XROZ6PZIF \
  --guardrail-id q6wfsifs9d72 \
  --wait

# 2. Deploy Lambda Function Code
py scripts/deploy_lambda.py

# 3. Upload Data to S3
py scripts/ingest_data.py

# 4. Test API Gateway Endpoint
curl -X POST <API_GATEWAY_URL> \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "query": "What is PM-Kisan?", "language": "en"}'
```

---

## 💰 Cost Estimate (Monthly)

| Service | Usage | Cost |
|---------|-------|------|
| Lambda | 100K invocations, 1GB, 30s avg | $5 |
| API Gateway | 100K requests | $0.35 |
| DynamoDB | On-demand, 1M reads, 500K writes | $1.50 |
| S3 | 100GB storage, 10K requests | $2.50 |
| Bedrock | 1M input tokens, 500K output | $30 |
| Translate | 1M characters | $15 |
| KMS | 10K requests | $1 |
| CloudWatch | Logs, metrics | $5 |
| **Total** | | **~$60/month** |

---

## ✅ Conclusion

**Your implementation FULLY MEETS the AWS infrastructure requirements:**

1. ✅ **AWS Lambda** - Main compute layer
2. ✅ **Amazon API Gateway** - REST API endpoint
3. ✅ **Amazon DynamoDB** - 3 tables for data storage
4. ✅ **Amazon S3** - Encrypted bucket for files and data

**Additional AWS services enhance the solution:**
- Amazon Bedrock for AI/ML
- Amazon Translate for multi-language support
- AWS KMS for encryption
- Amazon CloudWatch for monitoring
- AWS IAM for security

**Deployment Status**: Ready for production deployment using CloudFormation

**Documentation**: Complete with deployment guides, architecture diagrams, and testing procedures

---

**Verified By**: Kiro AI Assistant  
**Date**: March 2, 2026  
**Status**: ✅ COMPLIANT

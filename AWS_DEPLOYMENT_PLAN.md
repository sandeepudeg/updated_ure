# AWS-Native Deployment Plan - GramSetu

**Date**: March 2, 2026  
**Status**: Ready for AWS Deployment  
**Decision**: Freeze Streamlit development, deploy AWS-native solution

---

## 🎯 Deployment Strategy

### Current Status
- ✅ Streamlit UI developed and tested locally
- ✅ Lambda handler implemented
- ✅ CloudFormation template ready
- ✅ All AWS services configured
- ⏸️ **FREEZE**: Streamlit UI development (keep for local testing only)

### New Direction
- 🚀 Deploy AWS-native web UI (HTML/CSS/JavaScript)
- 🚀 Host static website on S3 + CloudFront
- 🚀 Connect to API Gateway backend
- 🚀 Full serverless architecture

---

## 📋 Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         AWS Cloud                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────┐         ┌──────────────┐                      │
│  │   Farmers    │────────▶│  CloudFront  │                      │
│  │ (Browsers)   │         │     CDN      │                      │
│  └──────────────┘         └──────┬───────┘                      │
│                                   │                              │
│                                   ▼                              │
│                          ┌────────────────┐                      │
│                          │   S3 Bucket    │                      │
│                          │  Static Website│                      │
│                          │  (HTML/CSS/JS) │                      │
│                          └────────┬───────┘                      │
│                                   │                              │
│                                   │ API Calls                    │
│                                   ▼                              │
│                          ┌────────────────┐                      │
│                          │  API Gateway   │                      │
│                          │   REST API     │                      │
│                          └────────┬───────┘                      │
│                                   │                              │
│                                   ▼                              │
│                          ┌────────────────┐                      │
│                          │  AWS Lambda    │                      │
│                          │ ure-mvp-handler│                      │
│                          └────────┬───────┘                      │
│                                   │                              │
│         ┌─────────────────────────┼─────────────────────┐       │
│         │                         │                     │       │
│         ▼                         ▼                     ▼       │
│  ┌─────────────┐         ┌──────────────┐      ┌──────────┐    │
│  │  DynamoDB   │         │   Bedrock    │      │    S3    │    │
│  │ (3 Tables)  │         │  Nova Lite   │      │  (Data)  │    │
│  └─────────────┘         └──────────────┘      └──────────┘    │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Deployment Steps

### Step 1: Deploy Backend Infrastructure (CloudFormation)

```bash
# Deploy all AWS infrastructure
py scripts/deploy_cloudformation.py deploy \
  --stack-name ure-mvp-stack \
  --kb-id 7XROZ6PZIF \
  --guardrail-id q6wfsifs9d72 \
  --wait
```

**Creates**:
- ✅ Lambda function
- ✅ API Gateway
- ✅ DynamoDB tables (3)
- ✅ S3 bucket (data)
- ✅ KMS encryption
- ✅ IAM roles
- ✅ CloudWatch monitoring

---

### Step 2: Deploy Lambda Function Code

```bash
# Package and deploy Lambda code
py scripts/deploy_lambda.py
```

**Deploys**:
- Lambda handler code
- All Python dependencies
- Environment variables
- Bedrock integration
- Agent orchestration

---

### Step 3: Upload Data to S3

```bash
# Upload PlantVillage images, government schemes, datasets
py scripts/ingest_data.py
```

**Uploads**:
- 70,295 crop disease images
- Government scheme PDFs
- Market price data

---

### Step 4: Deploy Static Web UI to S3

```bash
# Deploy web UI to S3 with CloudFront
py scripts/deploy_web_ui_to_s3.py
```

**Creates**:
- S3 bucket for website hosting
- CloudFront distribution
- Uploads HTML/CSS/JavaScript files
- Configures CORS for API Gateway

---

### Step 5: Test End-to-End

```bash
# Test API Gateway endpoint
curl -X POST <API_GATEWAY_URL> \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "query": "What is PM-Kisan?", "language": "en"}'

# Open web UI in browser
# https://<cloudfront-domain>/
```

---

## 📁 File Structure

```
project/
├── src/
│   ├── aws/
│   │   └── lambda_handler.py          # Lambda function (DEPLOYED)
│   ├── agents/                         # Agent code (DEPLOYED)
│   ├── utils/                          # Utilities (DEPLOYED)
│   ├── mcp/                            # MCP servers (DEPLOYED)
│   └── web/                            # Static web UI (NEW)
│       ├── index.html                  # Main page
│       ├── app.js                      # JavaScript logic
│       ├── styles.css                  # Styling
│       └── assets/                     # Images, icons
├── cloudformation/
│   └── ure-infrastructure-updated.yaml # Infrastructure (DEPLOYED)
├── scripts/
│   ├── deploy_cloudformation.py        # Deploy infrastructure
│   ├── deploy_lambda.py                # Deploy Lambda
│   ├── deploy_web_ui_to_s3.py         # Deploy web UI (NEW)
│   └── ingest_data.py                  # Upload data
└── src/ui/                             # Streamlit UI (FROZEN)
    ├── app.py                          # Original Streamlit
    ├── app_enterprise.py               # Enterprise Streamlit
    └── app_enterprise_clean.py         # Latest Streamlit (FROZEN)
```

---

## 🎨 Web UI Features

The AWS-native web UI (`src/web/`) will have:

1. **Enterprise Design**
   - Three-column layout (matching mockup)
   - Green header with language selector
   - Quick actions sidebar
   - Chat interface
   - Weather/market widgets

2. **Full Functionality**
   - Text queries to API Gateway
   - Image upload for crop disease identification
   - Multi-language support (English, Hindi, Marathi)
   - Location detection
   - User profile management
   - Conversation history

3. **AWS Integration**
   - API Gateway REST API calls
   - S3 for image uploads
   - CloudFront CDN for fast delivery
   - CORS configured

4. **Responsive Design**
   - Mobile-friendly
   - Desktop optimized
   - Progressive Web App (PWA) ready

---

## 💰 Cost Comparison

### Streamlit Deployment (Previous)
- AWS App Runner: $25-50/month
- Always-on server
- Higher latency
- Complex deployment

### AWS-Native Deployment (New)
- S3 + CloudFront: $1-5/month
- Serverless (pay per use)
- Low latency (CDN)
- Simple deployment

**Savings**: ~$20-45/month

---

## 🔒 Security

### Static Website (S3 + CloudFront)
- ✅ HTTPS only (CloudFront SSL)
- ✅ No server to hack
- ✅ DDoS protection (CloudFront)
- ✅ WAF integration (optional)

### API Gateway
- ✅ Throttling (1000 req/s)
- ✅ API keys (optional)
- ✅ CORS configured
- ✅ CloudWatch logging

### Lambda
- ✅ IAM least privilege
- ✅ VPC isolation (optional)
- ✅ Environment encryption (KMS)
- ✅ Bedrock Guardrails

---

## 📊 Performance

### Streamlit (Previous)
- Cold start: 5-10 seconds
- Response time: 2-5 seconds
- Concurrent users: 10-20

### AWS-Native (New)
- Cold start: 0 seconds (static files)
- Response time: 1-3 seconds (API)
- Concurrent users: 1000+ (serverless)

---

## 🎯 Next Steps

1. ✅ **DONE**: Verify AWS infrastructure is ready
2. 🚀 **NEXT**: Create AWS-native web UI (`src/web/`)
3. 🚀 **NEXT**: Create deployment script (`scripts/deploy_web_ui_to_s3.py`)
4. 🚀 **NEXT**: Deploy to AWS
5. 🚀 **NEXT**: Test end-to-end
6. ✅ **FREEZE**: Streamlit UI (keep for local testing only)

---

## 📝 Streamlit Status

**Decision**: Freeze Streamlit development

**Reason**:
- AWS-native solution is more cost-effective
- Better performance and scalability
- Simpler deployment
- Meets all AWS infrastructure requirements

**Streamlit Files** (keep for reference/local testing):
- `src/ui/app.py` - Original
- `src/ui/app_enterprise.py` - Enterprise version
- `src/ui/app_enterprise_clean.py` - Latest version
- `run_enterprise_ui.ps1` - Local testing script

**Status**: ⏸️ FROZEN (no further development)

---

## ✅ Deployment Checklist

- [ ] Backend infrastructure deployed (CloudFormation)
- [ ] Lambda function deployed
- [ ] Data uploaded to S3
- [ ] Web UI created (`src/web/`)
- [ ] Web UI deployed to S3
- [ ] CloudFront distribution configured
- [ ] API Gateway CORS configured
- [ ] End-to-end testing complete
- [ ] Documentation updated
- [ ] Streamlit UI frozen

---

**Status**: Ready to proceed with AWS-native deployment  
**Next Action**: Create web UI files in `src/web/`

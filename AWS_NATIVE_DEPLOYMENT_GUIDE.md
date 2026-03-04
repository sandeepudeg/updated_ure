# GramSetu AWS-Native Deployment Guide

**Date**: March 2, 2026  
**Status**: Ready for Production Deployment  
**Architecture**: Fully Serverless (S3 + CloudFront + API Gateway + Lambda + DynamoDB)

---

## 🎯 Overview

This guide covers deploying GramSetu as a fully AWS-native solution using:
- **Frontend**: Static HTML/CSS/JavaScript hosted on S3 + CloudFront
- **Backend**: API Gateway + Lambda + DynamoDB + Bedrock
- **Cost**: ~$5-10/month (vs $25-50/month for Streamlit)
- **Performance**: Sub-second page loads via CloudFront CDN

---

## 📁 File Structure

```
src/web/aws-native/
├── index.html          # Main HTML page
├── styles.css          # All styling
├── app.js              # JavaScript logic
└── config.js           # Configuration (API Gateway URL)

scripts/
└── deploy_web_ui_to_s3.py    # Deployment script

cloudformation/
└── ure-infrastructure-updated.yaml    # Backend infrastructure
```

---

## 🚀 Quick Start Deployment

### Prerequisites

1. AWS CLI configured with credentials
2. Python 3.11+ installed
3. Backend infrastructure deployed (CloudFormation stack)

### Step 1: Deploy Backend Infrastructure

```bash
# Deploy CloudFormation stack (if not already deployed)
py scripts/deploy_cloudformation.py deploy \
  --stack-name ure-mvp-stack \
  --kb-id 7XROZ6PZIF \
  --guardrail-id q6wfsifs9d72 \
  --wait

# Get API Gateway URL
py scripts/deploy_cloudformation.py outputs --stack-name ure-mvp-stack
```

**Save the API Gateway URL** - you'll need it for the frontend.

---

### Step 2: Deploy Lambda Function

```bash
# Package and deploy Lambda code
py scripts/deploy_lambda.py
```

---

### Step 3: Upload Data to S3

```bash
# Upload PlantVillage images, government schemes, datasets
py scripts/ingest_data.py
```

---

### Step 4: Deploy Web UI to S3 + CloudFront

```bash
# Deploy web UI
py scripts/deploy_web_ui_to_s3.py
```

This script will:
1. Create S3 bucket for website hosting
2. Upload all HTML/CSS/JavaScript files
3. Create CloudFront distribution
4. Configure CORS for API Gateway
5. Output the CloudFront URL

**Wait 10-15 minutes** for CloudFront distribution to deploy.

---

### Step 5: Update Configuration

If the deployment script didn't automatically update the API Gateway URL:

1. Open `src/web/aws-native/config.js`
2. Replace `YOUR_API_GATEWAY_URL_HERE` with your actual API Gateway URL
3. Re-run deployment: `py scripts/deploy_web_ui_to_s3.py`

---

### Step 6: Test the Application

```bash
# Open CloudFront URL in browser
# https://d1234567890abc.cloudfront.net/

# Or test locally first
# Open src/web/aws-native/index.html in browser
```

---

## 🎨 Features

### Frontend Features
- ✅ Enterprise three-column layout
- ✅ Green header with language selector
- ✅ Quick action buttons
- ✅ Chat interface with message history
- ✅ Image upload for crop disease identification
- ✅ Multi-language support (English, Hindi, Marathi)
- ✅ Auto-location detection
- ✅ User profile management
- ✅ Weather widget
- ✅ Market prices widget
- ✅ Government schemes alerts
- ✅ Responsive design (mobile-friendly)

### Backend Features
- ✅ API Gateway REST API
- ✅ Lambda function with agent orchestration
- ✅ DynamoDB for data storage
- ✅ Amazon Bedrock for AI/ML
- ✅ Amazon Translate for multi-language
- ✅ Bedrock Guardrails for content safety
- ✅ CloudWatch monitoring

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     AWS Cloud (us-east-1)                    │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐         ┌──────────────┐                  │
│  │   Farmers    │────────▶│  CloudFront  │                  │
│  │ (Browsers)   │         │     CDN      │                  │
│  └──────────────┘         └──────┬───────┘                  │
│                                   │                          │
│                                   ▼                          │
│                          ┌────────────────┐                  │
│                          │   S3 Bucket    │                  │
│                          │  Static Website│                  │
│                          │  (HTML/CSS/JS) │                  │
│                          └────────┬───────┘                  │
│                                   │                          │
│                                   │ API Calls                │
│                                   ▼                          │
│                          ┌────────────────┐                  │
│                          │  API Gateway   │                  │
│                          │   REST API     │                  │
│                          └────────┬───────┘                  │
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
│  │  DynamoDB   │         │   Bedrock    │      │    S3    ││
│  │ (3 Tables)  │         │  Nova Lite   │      │  (Data)  ││
│  └─────────────┘         └──────────────┘      └──────────┘│
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 💰 Cost Breakdown

### Monthly Costs (100 users, 1000 queries/month)

| Service | Usage | Cost |
|---------|-------|------|
| **S3 (Website)** | 1GB storage, 10K requests | $0.50 |
| **CloudFront** | 10GB data transfer | $1.00 |
| **API Gateway** | 1K requests | $0.04 |
| **Lambda** | 1K invocations, 1GB, 30s avg | $0.50 |
| **DynamoDB** | On-demand, 10K reads, 5K writes | $0.15 |
| **Bedrock** | 100K input tokens, 50K output | $3.00 |
| **Translate** | 100K characters | $1.50 |
| **KMS** | 1K requests | $0.10 |
| **CloudWatch** | Logs, metrics | $0.50 |
| **Total** | | **~$7.29/month** |

**Comparison**:
- Streamlit on App Runner: $25-50/month
- AWS-Native Solution: $7-10/month
- **Savings**: ~$18-43/month (72-86% reduction)**

---

## 🔒 Security

### Frontend Security
- ✅ HTTPS only (CloudFront SSL)
- ✅ No sensitive data in client-side code
- ✅ API Gateway URL configurable
- ✅ CORS properly configured

### Backend Security
- ✅ API Gateway throttling (1000 req/s)
- ✅ Lambda IAM least privilege
- ✅ DynamoDB encryption (KMS)
- ✅ S3 encryption (KMS)
- ✅ Bedrock Guardrails for content safety
- ✅ CloudWatch logging

---

## 📊 Performance

### Page Load Times
- **First Load**: < 1 second (CloudFront CDN)
- **Subsequent Loads**: < 100ms (browser cache)
- **API Response**: 1-3 seconds (Lambda + Bedrock)

### Scalability
- **Concurrent Users**: 1000+ (serverless auto-scaling)
- **Requests/Second**: 1000 (API Gateway throttling)
- **Storage**: Unlimited (S3)

---

## 🧪 Testing

### Local Testing

```bash
# Option 1: Open in browser
# Open src/web/aws-native/index.html in your browser

# Option 2: Use Python HTTP server
cd src/web/aws-native
py -m http.server 8000

# Open http://localhost:8000 in browser
```

### Production Testing

```bash
# Test API Gateway endpoint
curl -X POST <API_GATEWAY_URL> \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_farmer_001",
    "query": "What is PM-Kisan?",
    "language": "en"
  }'

# Test CloudFront URL
# Open https://<cloudfront-domain>/ in browser
```

---

## 🔧 Configuration

### API Gateway URL

Update `src/web/aws-native/config.js`:

```javascript
window.API_GATEWAY_URL = 'https://your-api-id.execute-api.us-east-1.amazonaws.com/dev/query';
```

### CORS Configuration

If you encounter CORS errors, update API Gateway CORS settings:

```bash
# In AWS Console:
# API Gateway > ure-mvp-api > Resources > /query > Enable CORS
# Allowed Origins: *
# Allowed Methods: POST, OPTIONS
# Allowed Headers: Content-Type
```

---

## 🐛 Troubleshooting

### Issue: "API Gateway URL not configured"

**Solution**: Update `config.js` with your API Gateway URL

### Issue: CORS errors in browser console

**Solution**: 
1. Check API Gateway CORS settings
2. Ensure API Gateway URL is correct
3. Check CloudWatch logs for errors

### Issue: CloudFront distribution not working

**Solution**:
1. Wait 10-15 minutes for distribution to deploy
2. Check distribution status in AWS Console
3. Verify S3 bucket policy allows public read

### Issue: Images not uploading

**Solution**:
1. Check browser console for errors
2. Verify image size < 5MB
3. Check API Gateway payload size limit

---

## 📝 Maintenance

### Updating the Web UI

```bash
# 1. Make changes to HTML/CSS/JavaScript files
# 2. Re-deploy to S3
py scripts/deploy_web_ui_to_s3.py

# 3. Invalidate CloudFront cache (optional, for immediate updates)
aws cloudfront create-invalidation \
  --distribution-id <DISTRIBUTION_ID> \
  --paths "/*"
```

### Updating the Backend

```bash
# Update Lambda function
py scripts/deploy_lambda.py

# Update CloudFormation stack
py scripts/deploy_cloudformation.py deploy \
  --stack-name ure-mvp-stack \
  --wait
```

---

## 🎯 Next Steps

1. ✅ Deploy backend infrastructure (CloudFormation)
2. ✅ Deploy Lambda function
3. ✅ Upload data to S3
4. ✅ Deploy web UI to S3 + CloudFront
5. ⏳ Wait for CloudFront distribution (10-15 minutes)
6. ✅ Test the application
7. 📊 Monitor CloudWatch metrics
8. 👥 Onboard farmers for pilot testing

---

## 📞 Support

For issues or questions:
- Check CloudWatch logs: `/aws/lambda/ure-mvp-handler`
- Review API Gateway logs
- Check CloudFront distribution status
- Verify S3 bucket contents

---

## ✅ Deployment Checklist

- [ ] Backend infrastructure deployed (CloudFormation)
- [ ] Lambda function deployed
- [ ] Data uploaded to S3
- [ ] Web UI deployed to S3
- [ ] CloudFront distribution created
- [ ] API Gateway URL configured in config.js
- [ ] CORS configured on API Gateway
- [ ] Application tested end-to-end
- [ ] CloudWatch monitoring verified
- [ ] Documentation updated

---

**Status**: ✅ Ready for Production Deployment  
**Estimated Deployment Time**: 30-45 minutes  
**Estimated Monthly Cost**: $7-10

---

**Last Updated**: March 2, 2026  
**Version**: 1.0.0

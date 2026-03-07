# GramSetu Deployment Package - Index

Welcome to the GramSetu URE MVP deployment package! This folder contains everything you need to deploy, test, and maintain the application.

---

## 📚 Documentation Files

### 1. [README.md](./README.md)
**Start here!** Complete project overview including:
- Project description and features
- Technology stack
- Project structure
- Quick start guide
- Environment setup
- API documentation

### 2. [AWS_SERVICES.md](./AWS_SERVICES.md)
Comprehensive AWS services documentation:
- All AWS services used (Lambda, Bedrock, ECR, S3, CloudFront, API Gateway, CloudWatch)
- Configuration details and ARNs
- Pricing breakdown
- Estimated monthly costs ($20-42/month)
- Security best practices
- Monitoring and alerts

### 3. [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)
Complete step-by-step deployment instructions:
- Prerequisites and setup
- Local development guide
- Docker deployment process
- Web UI deployment
- Testing procedures
- Troubleshooting guide
- Rollback procedures

### 4. [QUICK_REFERENCE.md](./QUICK_REFERENCE.md)
Quick commands and troubleshooting:
- Common commands
- Important URLs
- AWS resource list
- Troubleshooting tips
- Monitoring commands
- Security procedures

### 5. [DEPLOYMENT_SUMMARY.md](./DEPLOYMENT_SUMMARY.md)
Summary of what was accomplished:
- Features implemented
- Resources deployed
- Live URLs
- Success metrics
- Next steps

---

## 🚀 Deployment Scripts

### Full Deployment
```powershell
.\deployment\deploy-all.ps1
```
**What it does:**
- Commits and pushes to Git (optional)
- Builds and pushes Docker image to ECR
- Updates Lambda function
- Deploys web UI to S3
- Invalidates CloudFront cache

**Use when:** You want to deploy everything at once

---

### Docker Deployment
```powershell
.\deployment\deploy-docker.ps1
```
**What it does:**
- Builds Docker image for linux/amd64
- Pushes to AWS ECR
- Updates Lambda function with new image

**Use when:** You've made changes to Python code or dependencies

---

### Web UI Deployment
```powershell
.\deployment\deploy-web.ps1
```
**What it does:**
- Uploads HTML, JavaScript, and CSS files to S3
- Invalidates CloudFront cache

**Use when:** You've made changes to the web interface

---

## 🧪 Testing Scripts

### Lambda Function Testing
```powershell
.\deployment\test-lambda.ps1
```
**What it does:**
- Tests Lambda with 3 different query types
- Verifies market price integration
- Checks general agriculture queries
- Tests government scheme queries

**Use when:** You want to verify Lambda is working correctly

---

### Web UI Testing
```powershell
.\deployment\test-web.ps1
```
**What it does:**
- Tests API endpoint connectivity
- Opens desktop UI in browser
- Opens mobile UI in browser
- Provides testing checklist

**Use when:** You want to verify web interfaces are working

---

## 📋 Quick Start Guide

### For First-Time Setup

1. **Read the documentation**
   ```
   Start with: deployment/README.md
   Then read: deployment/DEPLOYMENT_GUIDE.md
   ```

2. **Set up your environment**
   ```powershell
   # Create virtual environment
   python -m venv rural
   .\rural\Scripts\Activate.ps1
   
   # Install dependencies
   pip install -r requirements-lambda.txt
   
   # Configure AWS CLI
   aws configure
   ```

3. **Configure environment variables**
   ```
   Edit .env file with your credentials
   ```

4. **Deploy everything**
   ```powershell
   .\deployment\deploy-all.ps1
   ```

5. **Test deployment**
   ```powershell
   .\deployment\test-lambda.ps1
   .\deployment\test-web.ps1
   ```

---

### For Regular Updates

1. **Make your changes** to code or web UI

2. **Test locally**
   ```powershell
   python src/agents/supervisor_simple.py
   # Or open test_mobile_ui.html
   ```

3. **Deploy changes**
   ```powershell
   # If you changed Python code:
   .\deployment\deploy-docker.ps1
   
   # If you changed web UI:
   .\deployment\deploy-web.ps1
   
   # Or deploy everything:
   .\deployment\deploy-all.ps1
   ```

4. **Test deployment**
   ```powershell
   .\deployment\test-lambda.ps1
   .\deployment\test-web.ps1
   ```

---

## 🌐 Live Resources

### Web Interfaces
- **Desktop UI**: https://d3v7khazsfb4vd.cloudfront.net/gramsetu-agents.html
- **Mobile UI**: https://d3v7khazsfb4vd.cloudfront.net/gramsetu-mobile.html

### API
- **Endpoint**: https://8938dqxf33.execute-api.us-east-1.amazonaws.com/dev/query

### AWS Console
- **Lambda**: https://console.aws.amazon.com/lambda/home?region=us-east-1#/functions/ure-mvp-handler-docker
- **CloudWatch Logs**: https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#logsV2:log-groups/log-group/$252Faws$252Flambda$252Fure-mvp-handler-docker
- **S3 Bucket**: https://s3.console.aws.amazon.com/s3/buckets/ure-mvp-data-us-east-1-188238313375
- **CloudFront**: https://console.aws.amazon.com/cloudfront/v3/home?region=us-east-1#/distributions/E354ZTACSUHKWS

---

## 🔧 Common Tasks

### Update Lambda Code
```powershell
.\deployment\deploy-docker.ps1
```

### Update Web UI
```powershell
.\deployment\deploy-web.ps1
```

### View Lambda Logs
```powershell
aws logs tail /aws/lambda/ure-mvp-handler-docker --follow --region us-east-1
```

### Test Lambda Function
```powershell
.\deployment\test-lambda.ps1
```

### Check Lambda Status
```powershell
aws lambda get-function --function-name ure-mvp-handler-docker --region us-east-1 --query 'Configuration.[State,LastUpdateStatus]'
```

---

## 🆘 Troubleshooting

### Docker Build Fails
1. Check Docker Desktop is running: `docker ps`
2. Clear cache: `docker system prune -a`
3. Rebuild: `.\deployment\deploy-docker.ps1`

### Lambda Not Responding
1. Check status: `aws lambda get-function --function-name ure-mvp-handler-docker --region us-east-1`
2. View logs: `aws logs tail /aws/lambda/ure-mvp-handler-docker --region us-east-1`
3. Test function: `.\deployment\test-lambda.ps1`

### Web UI Not Loading
1. Check CloudFront status
2. Clear browser cache
3. Force invalidation: `aws cloudfront create-invalidation --distribution-id E354ZTACSUHKWS --paths "/*"`

### For More Help
See [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) → Troubleshooting section

---

## 📊 Project Status

✅ **Production Ready**

- ✓ Docker image built and deployed
- ✓ Lambda function operational
- ✓ Web UI deployed (desktop + mobile)
- ✓ Market price integration working
- ✓ All tests passing
- ✓ Documentation complete

---

## 📞 Support

- **Documentation**: All files in this folder
- **AWS Support**: https://console.aws.amazon.com/support/
- **Data.gov.in**: https://data.gov.in/contact-us

---

## 📝 File Structure

```
deployment/
├── INDEX.md                    ← You are here
├── README.md                   ← Start here for project overview
├── AWS_SERVICES.md             ← AWS services and costs
├── DEPLOYMENT_GUIDE.md         ← Step-by-step deployment
├── QUICK_REFERENCE.md          ← Quick commands
├── DEPLOYMENT_SUMMARY.md       ← What was accomplished
├── deploy-all.ps1              ← Full deployment script
├── deploy-docker.ps1           ← Docker deployment
├── deploy-web.ps1              ← Web UI deployment
├── test-lambda.ps1             ← Lambda testing
└── test-web.ps1                ← Web UI testing
```

---

## 🎯 Next Steps

1. **Read README.md** for project overview
2. **Follow DEPLOYMENT_GUIDE.md** for detailed setup
3. **Use deploy-all.ps1** for deployment
4. **Run test scripts** to verify everything works
5. **Refer to QUICK_REFERENCE.md** for daily operations

---

**Happy Deploying! 🚀**

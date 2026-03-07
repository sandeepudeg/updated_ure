# Deployment Folder - Complete Guide

This folder contains everything needed to deploy, test, and monitor GramSetu on AWS Cloud.

## 📁 Folder Contents (46 Files)

### 🚀 Core Deployment Files

#### Docker Configuration
- **Dockerfile** - Docker container configuration for Lambda
- **.dockerignore** - Files to exclude from Docker build  
- **docker-compose.yml** - Local Docker testing configuration

#### Deployment Scripts
- **deploy-all.ps1** - Deploy everything (Docker + Web) in one command
- **deploy-docker.ps1** - Deploy Docker Lambda function
- **deploy-web.ps1** - Deploy web interface to S3/CloudFront
- **docker-build-and-push.ps1** - Build and push Docker image to ECR
- **deploy-lambda-docker.ps1** - Deploy Lambda function with Docker image

#### Testing Scripts
- **test-lambda.ps1** - Test Lambda function after deployment
- **test-web.ps1** - Test web interface

### 📊 Performance Testing

#### Scripts (in ../scripts/)
- **warmup-lambda.ps1** - Warm up Lambda before testing
- **collect-performance-metrics.ps1** - Collect CloudWatch metrics
- **load_test.py** - Load testing with 200 users, 40 requests (8,000 total)
- **run-performance-tests-with-warmup.ps1** - Complete testing workflow
- **generate-performance-report.ps1** - Generate HTML performance report
- **diagnose-api.ps1** - Diagnose API issues

#### Results
- **performance-metrics.json** - Collected performance data
- **load-test-results.json** - Load test results (8,000 requests)
- **gramsetu-performance-report-actual.html** - Performance report with real data

### 📚 Documentation

#### Deployment Guides
- **DEPLOY_TO_AWS.md** - Complete AWS deployment guide ⭐
- **DEPLOYMENT_GUIDE.md** - Comprehensive deployment documentation
- **DEPLOYMENT_CHECKLIST.md** - Step-by-step deployment checklist ⭐
- **QUICK_REFERENCE.md** - Quick command reference
- **DEPLOYMENT_SUMMARY.md** - Deployment summary

#### Performance & Testing
- **HIGH_LOAD_TESTING.md** - High load testing guide (200 users, 8,000 requests) ⭐
- **LAMBDA_WARMUP_GUIDE.md** - Lambda warm-up documentation ⭐
- **PERFORMANCE_TESTING_GUIDE.md** - Performance testing guide
- **PERFORMANCE_TESTING_FIX_SUMMARY.md** - Performance testing fixes
- **RUN_PERFORMANCE_TESTS.md** - Quick performance testing guide
- **TESTING_STATUS.md** - Current testing status
- **HOW_TO_PROVE_PERFORMANCE.md** - Prove performance with real data

#### AWS Services
- **AWS_SERVICES.md** - AWS services used in the project
- **INDEX.md** - Complete index of all documentation
- **README.md** - Main deployment folder README

### 🎨 Presentation Materials

#### Architecture Diagrams
- **aws-architecture-diagram.html** - AWS architecture diagram
- **aws-architecture-diagram-presentation.html** - Presentation version
- **aws-architecture-final.html** - Final architecture diagram
- **gramsetu-architecture-detailed.html** - Detailed architecture (1920x1080)

#### Feature Presentations
- **gramsetu-features-presentation.html** - Complete features overview
- **gramsetu-feature-slide.html** - Single-slide feature overview
- **gramsetu-complete-diagram-slide.html** - Complete diagram (4 quadrants)

#### Process & Use Cases
- **gramsetu-process-flow-diagram.html** - End-to-end process flow
- **gramsetu-usecase-diagram.html** - Use case diagram
- **gramsetu-usecase-single-slide.html** - Single-slide use case (1920x1080)

#### UI/UX
- **gramsetu-wireframes-mockup.html** - Desktop & mobile wireframes
- **ai-value-proposition.html** - AI value proposition

#### Technology & Cost
- **gramsetu-technology-stack.html** - Technology stack (1920x1080)
- **gramsetu-cost-estimate.html** - Cost estimate with animation
- **gramsetu-cost-simulator.html** - Interactive cost simulator

#### Performance Reports
- **gramsetu-performance-report.html** - Performance report template
- **gramsetu-performance-report-actual.html** - Report with real data
- **performance-testing-fixed.html** - Performance testing summary

#### GIF Creation
- **CREATE_GIF_GUIDE.md** - Guide to create GIFs from HTML animations

## 🚀 Quick Start

### Deploy Everything
```powershell
cd deployment
.\deploy-all.ps1
```

### Deploy Step-by-Step
```powershell
# 1. Build and push Docker image
.\docker-build-and-push.ps1

# 2. Deploy Lambda function
.\deploy-lambda-docker.ps1

# 3. Deploy web interface
.\deploy-web.ps1

# 4. Test deployment
.\test-lambda.ps1
```

### Run Performance Tests
```powershell
# Complete workflow with warm-up
..\scripts\run-performance-tests-with-warmup.ps1

# Or step by step
..\scripts\warmup-lambda.ps1
..\scripts\collect-performance-metrics.ps1
python ..\scripts\load_test.py 200 40
..\scripts\generate-performance-report.ps1
```

## 📖 Key Documentation

### For Deployment
1. **DEPLOY_TO_AWS.md** - Start here for AWS deployment
2. **DEPLOYMENT_CHECKLIST.md** - Follow this checklist
3. **QUICK_REFERENCE.md** - Quick command reference

### For Testing
1. **HIGH_LOAD_TESTING.md** - Test with 200 users, 8,000 requests
2. **LAMBDA_WARMUP_GUIDE.md** - Warm up Lambda for better performance
3. **PERFORMANCE_TESTING_GUIDE.md** - Complete testing guide

### For Presentations
1. Open any HTML file in browser
2. Press F11 for fullscreen
3. Take screenshot (Win + Shift + S)
4. Use in PowerPoint presentations

## 🎯 Performance Testing Configuration

### Current Defaults
- **Concurrent Users**: 200 (was 10)
- **Requests per User**: 40 (was 5)
- **Total Requests**: 8,000 (was 50)
- **Warm-Up Requests**: 10 (was 3)

### Expected Results
- Success Rate: 99%+
- Avg Response Time: 2-3 seconds
- Throughput: 30+ requests/second
- Performance Score: 70-85/100

## 📊 Presentation Materials

All HTML files are sized at 1920x1080 (standard PowerPoint slide dimensions) and ready for screenshots:

### Architecture & Design
- System architecture diagrams
- Process flow diagrams
- Use case diagrams

### Features & Technology
- Feature overview slides
- Technology stack
- Cost estimates and simulators

### Performance & Testing
- Performance reports with real data
- Load test results
- Benchmarking comparisons

## 🔧 Troubleshooting

### Deployment Issues
```powershell
# Check Docker
docker ps

# Check AWS CLI
aws sts get-caller-identity

# Run diagnostic
..\scripts\diagnose-api.ps1
```

### Performance Issues
```powershell
# Warm up Lambda
..\scripts\warmup-lambda.ps1

# Check CloudWatch logs
aws logs tail /aws/lambda/ure-mvp-handler-docker --follow

# Increase Lambda memory
aws lambda update-function-configuration \
  --function-name ure-mvp-handler-docker \
  --memory-size 2048
```

## 📁 File Organization

```
deployment/
├── Core Deployment (5 files)
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── docker-compose.yml
│   ├── deploy-all.ps1
│   └── deploy-docker.ps1
│
├── Documentation (18 files)
│   ├── DEPLOY_TO_AWS.md ⭐
│   ├── DEPLOYMENT_CHECKLIST.md ⭐
│   ├── HIGH_LOAD_TESTING.md ⭐
│   ├── LAMBDA_WARMUP_GUIDE.md ⭐
│   └── ... (14 more)
│
├── Presentation Materials (20 files)
│   ├── Architecture diagrams (4 files)
│   ├── Feature presentations (3 files)
│   ├── Process & use cases (3 files)
│   ├── Technology & cost (3 files)
│   ├── Performance reports (3 files)
│   └── UI/UX mockups (2 files)
│
└── Test Results (3 files)
    ├── performance-metrics.json
    ├── load-test-results.json
    └── gramsetu-performance-report-actual.html
```

## 🎓 Learning Path

### 1. Understand the System
- Read `README.md`
- Review `AWS_SERVICES.md`
- Check architecture diagrams

### 2. Deploy to AWS
- Follow `DEPLOY_TO_AWS.md`
- Use `DEPLOYMENT_CHECKLIST.md`
- Test with `test-lambda.ps1`

### 3. Performance Testing
- Read `HIGH_LOAD_TESTING.md`
- Warm up with `LAMBDA_WARMUP_GUIDE.md`
- Run tests with `run-performance-tests-with-warmup.ps1`

### 4. Create Presentations
- Open HTML files in browser
- Take screenshots
- Add to PowerPoint

## 🔗 Related Folders

- **../scripts/** - All PowerShell and Python scripts
- **../src/** - Source code (Lambda handler, agents, utils)
- **../src/web/v2/** - Web interface files
- **../tests/** - Unit and integration tests
- **../data/** - Sample data and datasets

## 📞 Support

For issues:
1. Check CloudWatch logs
2. Run diagnostic script
3. Review documentation
4. Check AWS console

## ✅ Success Criteria

Deployment is successful when:
- ✅ All scripts run without errors
- ✅ API endpoint returns 200 status
- ✅ Web interface loads correctly
- ✅ Performance tests show 99%+ success rate
- ✅ CloudWatch logs show no errors

## 🎉 Summary

This deployment folder provides:
- **Complete deployment workflow** (Docker + AWS)
- **Performance testing suite** (200 users, 8,000 requests)
- **Comprehensive documentation** (18 guides)
- **Presentation materials** (20 HTML files)
- **Real test results** (performance metrics and reports)

Everything you need to deploy, test, and present GramSetu on AWS Cloud! 🚀

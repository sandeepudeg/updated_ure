# GramSetu - Unified Rural Ecosystem (URE) MVP

## Project Overview

GramSetu is an AI-powered assistant designed for rural India, providing farmers with real-time market prices, crop disease diagnosis, government scheme information, weather forecasts, and agricultural advice.

## Features

- **Multi-Agent AI System**: 6 specialized agents for different farming needs
- **Live Market Prices**: Integration with data.gov.in Agmarknet API
- **Image Analysis**: Crop disease detection using AWS Bedrock
- **Mobile-First UI**: Responsive design optimized for rural users
- **Multi-Language Support**: English, Hindi, Marathi, and more
- **Real-time Chat**: Interactive AI assistant with context awareness

## Technology Stack

### Backend
- **Language**: Python 3.11
- **Framework**: Strands AI Agent Framework
- **AI Model**: Amazon Bedrock (Nova Lite v1.0)
- **Deployment**: AWS Lambda (Docker container)

### Frontend
- **Desktop UI**: gramsetu-agents.html
- **Mobile UI**: gramsetu-mobile.html (mobile-first responsive design)
- **Hosting**: AWS S3 + CloudFront CDN

### Infrastructure
- **Compute**: AWS Lambda (Docker-based)
- **Storage**: AWS S3
- **CDN**: AWS CloudFront
- **API**: AWS API Gateway (HTTP API)
- **Container Registry**: AWS ECR
- **AI/ML**: AWS Bedrock

## Project Structure

```
Assembler_URE_Rural/
├── src/
│   ├── agents/              # AI agent implementations
│   │   ├── supervisor_simple.py    # Main supervisor with market prices
│   │   ├── agri_expert.py          # Agricultural expert
│   │   ├── disease_expert.py       # Disease diagnosis
│   │   ├── market_expert.py        # Market analysis
│   │   ├── policy_expert.py        # Government schemes
│   │   ├── weather_expert.py       # Weather forecasts
│   │   └── tourism_expert.py       # Rural tourism
│   ├── aws/
│   │   └── lambda_handler.py       # Lambda entry point
│   └── web/
│       └── v2/
│           ├── gramsetu-agents.html    # Desktop UI
│           ├── gramsetu-mobile.html    # Mobile UI
│           ├── config.js               # Configuration
│           ├── app.js                  # Application logic
│           └── styles.css              # Styling
├── data/
│   ├── mandi_prices/        # Market price CSV data
│   ├── government_schemes/  # Scheme PDFs
│   └── plantvillage/        # Disease detection dataset
├── scripts/                 # Deployment scripts
├── deployment/              # Deployment documentation
├── Dockerfile              # Docker container definition
├── requirements-lambda.txt # Python dependencies
└── .env                    # Environment variables

```

## Quick Start

### Prerequisites

1. **Python 3.11** with virtual environment
2. **Docker Desktop** (for containerized deployment)
3. **AWS CLI** configured with credentials
4. **Git** for version control
5. **Data.gov.in API Key** for market prices

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Assembler_URE_Rural
   ```

2. **Create virtual environment**
   ```bash
   python -m venv rural
   # Windows
   .\rural\Scripts\Activate.ps1
   # Linux/Mac
   source rural/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements-lambda.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

5. **Test locally**
   ```bash
   python src/agents/supervisor_simple.py
   ```

### Environment Variables

Create a `.env` file with the following:

```env
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCOUNT_ID=188238313375

# Bedrock Model
BEDROCK_MODEL_ID=amazon.nova-lite-v1:0

# Market Price API
DATA_GOV_API_KEY=your_api_key_here

# S3 and CloudFront
S3_BUCKET=ure-mvp-data-us-east-1-188238313375
CLOUDFRONT_DIST=E354ZTACSUHKWS
```

## Deployment

See [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for detailed deployment instructions.

### Quick Deploy

```powershell
# Full end-to-end deployment
.\deployment\deploy-all.ps1
```

## API Endpoints

### Lambda Function
- **Name**: `ure-mvp-handler-docker`
- **Runtime**: Docker (Python 3.11)
- **Memory**: 1024 MB
- **Timeout**: 300 seconds

### API Gateway
- **Endpoint**: `https://8938dqxf33.execute-api.us-east-1.amazonaws.com/dev/query`
- **Method**: POST
- **Content-Type**: application/json

### Request Format
```json
{
  "user_id": "user_123",
  "query": "What is the price of tomato in Nashik?",
  "language": "English",
  "image": "base64_encoded_image_optional"
}
```

### Response Format
```json
{
  "statusCode": 200,
  "body": {
    "user_id": "user_123",
    "query": "What is the price of tomato in Nashik?",
    "response": "Market price information...",
    "agent_used": "supervisor",
    "timestamp": "2026-03-06T12:00:00"
  }
}
```

## Web Interfaces

### Desktop UI
- **URL**: https://d3v7khazsfb4vd.cloudfront.net/gramsetu-agents.html
- **Features**: Full-featured interface with sidebar, agent cards, chat

### Mobile UI
- **URL**: https://d3v7khazsfb4vd.cloudfront.net/gramsetu-mobile.html
- **Features**: Mobile-first design, bottom navigation, touch-optimized

## Testing

### Test Lambda Function
```powershell
.\scripts\test_lambda_locally.py
```

### Test Web Interface
```powershell
# Open test page
Start-Process test_mobile_ui.html
```

### Test Market Price API
```python
from src.agents.supervisor_simple import get_market_prices

prices = get_market_prices("Tomato", "Nashik", "Maharashtra")
print(prices)
```

## Monitoring and Logs

### CloudWatch Logs
- Log Group: `/aws/lambda/ure-mvp-handler-docker`
- View logs: AWS Console → CloudWatch → Log Groups

### Lambda Metrics
- Invocations, Duration, Errors, Throttles
- View: AWS Console → Lambda → Monitoring

## Troubleshooting

### Common Issues

1. **Docker build fails**
   - Ensure Docker Desktop is running
   - Check Dockerfile syntax
   - Verify base image availability

2. **Lambda timeout**
   - Increase timeout in Lambda configuration
   - Optimize agent response time
   - Check Bedrock API latency

3. **Market price API fails**
   - Verify DATA_GOV_API_KEY is valid
   - Check API rate limits
   - Falls back to CSV data automatically

4. **UI not loading**
   - Check CloudFront distribution status
   - Verify S3 bucket permissions
   - Clear browser cache

## Contributing

1. Create a feature branch
2. Make changes and test locally
3. Commit with descriptive messages
4. Push to remote repository
5. Deploy to AWS after testing

## License

Proprietary - All rights reserved

## Support

For issues or questions, contact the development team.

## Version History

- **v1.0.0** (2026-03-06): Initial MVP release
  - Multi-agent AI system
  - Live market price integration
  - Mobile-responsive UI
  - Docker-based Lambda deployment

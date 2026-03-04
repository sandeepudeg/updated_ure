#!/bin/bash
# Docker Build and Push Script for AWS Lambda
# Builds Docker image and pushes to Amazon ECR

set -e

# Configuration
AWS_REGION="${AWS_REGION:-us-east-1}"
AWS_ACCOUNT_ID="${AWS_ACCOUNT_ID:-188238313375}"
ECR_REPOSITORY="${ECR_REPOSITORY:-ure-lambda-privacy}"
IMAGE_TAG="${IMAGE_TAG:-latest}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}AWS Lambda Docker Build & Push${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${RED}✗ AWS CLI not found. Please install AWS CLI.${NC}"
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗ Docker not found. Please install Docker.${NC}"
    exit 1
fi

echo -e "${YELLOW}Configuration:${NC}"
echo "  AWS Region: $AWS_REGION"
echo "  AWS Account: $AWS_ACCOUNT_ID"
echo "  ECR Repository: $ECR_REPOSITORY"
echo "  Image Tag: $IMAGE_TAG"
echo ""

# Get ECR login token
echo -e "${YELLOW}→ Logging in to Amazon ECR...${NC}"
aws ecr get-login-password --region $AWS_REGION | \
    docker login --username AWS --password-stdin \
    $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Successfully logged in to ECR${NC}"
else
    echo -e "${RED}✗ Failed to login to ECR${NC}"
    exit 1
fi

# Create ECR repository if it doesn't exist
echo -e "${YELLOW}→ Checking ECR repository...${NC}"
aws ecr describe-repositories --repository-names $ECR_REPOSITORY --region $AWS_REGION &> /dev/null || \
    aws ecr create-repository --repository-name $ECR_REPOSITORY --region $AWS_REGION

echo -e "${GREEN}✓ ECR repository ready${NC}"

# Build Docker image
echo -e "${YELLOW}→ Building Docker image...${NC}"
docker build -t $ECR_REPOSITORY:$IMAGE_TAG .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Docker image built successfully${NC}"
else
    echo -e "${RED}✗ Docker build failed${NC}"
    exit 1
fi

# Tag image for ECR
ECR_IMAGE_URI="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:$IMAGE_TAG"
echo -e "${YELLOW}→ Tagging image for ECR...${NC}"
docker tag $ECR_REPOSITORY:$IMAGE_TAG $ECR_IMAGE_URI

# Push to ECR
echo -e "${YELLOW}→ Pushing image to ECR...${NC}"
docker push $ECR_IMAGE_URI

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Image pushed successfully${NC}"
else
    echo -e "${RED}✗ Failed to push image${NC}"
    exit 1
fi

# Get image digest
IMAGE_DIGEST=$(aws ecr describe-images \
    --repository-name $ECR_REPOSITORY \
    --image-ids imageTag=$IMAGE_TAG \
    --region $AWS_REGION \
    --query 'imageDetails[0].imageDigest' \
    --output text)

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Build Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Image URI: $ECR_IMAGE_URI"
echo "Image Digest: $IMAGE_DIGEST"
echo ""
echo "To update Lambda function, run:"
echo "  aws lambda update-function-code \\"
echo "    --function-name ure-mvp-handler \\"
echo "    --image-uri $ECR_IMAGE_URI \\"
echo "    --region $AWS_REGION"
echo ""

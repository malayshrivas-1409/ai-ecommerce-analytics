#!/bin/bash

# ============================================================================
# DIRECT ECR PUSH SCRIPT - NO EC2 NEEDED
# ============================================================================
# Push directly from local machine to ECR
# Usage: ./push-to-ecr.sh
# ============================================================================

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Your ECR Details
ACCOUNT_ID="060730976878"
REGION="ap-south-1"
REPO_NAME="malay-comm-2026"
ECR_URI="$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPO_NAME"
IMAGE_TAG="${1:-latest}"

echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}ECR Direct Push${NC}"
echo -e "${YELLOW}========================================${NC}"
echo ""
echo "ECR URI: $ECR_URI"
echo "Tag: $IMAGE_TAG"
echo ""

# Step 1: Login to ECR
echo -e "${YELLOW}Step 1: Logging in to ECR...${NC}"
aws ecr get-login-password --region $REGION | \
    docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com
echo -e "${GREEN}✅ Logged in${NC}"
echo ""

# Step 2: Build image
echo -e "${YELLOW}Step 2: Building Docker image...${NC}"
docker build -t $REPO_NAME:$IMAGE_TAG .
echo -e "${GREEN}✅ Built${NC}"
echo ""

# Step 3: Tag for ECR
echo -e "${YELLOW}Step 3: Tagging image...${NC}"
docker tag $REPO_NAME:$IMAGE_TAG $ECR_URI:$IMAGE_TAG
docker tag $REPO_NAME:$IMAGE_TAG $ECR_URI:latest
echo -e "${GREEN}✅ Tagged${NC}"
echo ""

# Step 4: Push to ECR
echo -e "${YELLOW}Step 4: Pushing to ECR...${NC}"
docker push $ECR_URI:$IMAGE_TAG
docker push $ECR_URI:latest
echo -e "${GREEN}✅ Pushed${NC}"
echo ""

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ DONE!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Image available at:"
echo "$ECR_URI:$IMAGE_TAG"
echo "$ECR_URI:latest"
echo ""

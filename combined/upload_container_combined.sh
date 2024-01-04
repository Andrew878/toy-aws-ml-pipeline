#!/bin/bash

# Load environment variables from .env file
if [ -f .env ]; then
    export $(cat .env | xargs)
fi

# Login to ECR
aws ecr get-login-password --region $ECR_REGION | docker login --username AWS --password-stdin $ECR_REPO

# Get the latest image ID
LATEST_IMAGE=$(docker images --format "{{.Repository}}:{{.Tag}}\t{{.CreatedAt}}" | grep -v "none" | sort -k 2 -r | head -n 1 | cut -f1)

# Check if we found an image
if [ -z "$LATEST_IMAGE" ]; then
    echo "No images found. Exiting."
    exit 1
fi

# Print the latest image ID
echo "Latest image found: $LATEST_IMAGE"

# Tag the latest image
docker tag $LATEST_IMAGE $ECR_REPO:$TAG

# Push the tagged image to ECR
docker push $ECR_REPO:$TAG

echo "Latest image tagged and pushed successfully."

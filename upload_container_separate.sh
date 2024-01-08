#!/bin/bash

# Load environment variables from .env file
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
else
    echo "Error: .env file not found. Terminating script."
    exit 1
fi

# Login to ECR
aws ecr get-login-password --region $ECR_REGION | docker login --username AWS --password-stdin $ECR_REPO

# Function to tag and push the latest image of a given repository
tag_and_push_latest_image() {
    local repo_name=$1
    local tag_name=$2
    # Get the latest image ID based on creation time
    local latest_image=$(docker images $repo_name --format "{{.Repository}}:{{.Tag}}\t{{.CreatedAt}}" | sort -k 2 -r | head -n 1 | cut -f1)

    if [ -z "$latest_image" ]; then
        echo "No images found for $repo_name. Skipping."
        return
    fi

    echo "Latest image for $repo_name found: $latest_image"

    # Tag the latest image
    docker tag $latest_image $ECR_REPO:$tag_name

    # Push the tagged image to ECR
    docker push $ECR_REPO:$tag_name

    echo "$repo_name image tagged as $tag_name and pushed successfully."
}

# Tag and push the latest images using variables from .env file
tag_and_push_latest_image $REPO_FRONT $TAG_FRONT
tag_and_push_latest_image $REPO_BACK $TAG_BACK

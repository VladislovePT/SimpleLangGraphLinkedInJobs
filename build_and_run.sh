#!/bin/bash

# This script builds the Docker image and runs the container,
# using the .env file to supply environment variables.

# --- Configuration ---
IMAGE_NAME="linkedin-rss-agent"
CONTAINER_NAME="rss-agent-container"

# --- Pre-flight Check ---
# Check if the .env file exists
if [ ! -f .env ]; then
    echo "Error: .env file not found!"
    echo "Please copy .env.example to .env and fill in your configuration."
    exit 1
fi

echo "--- .env file found. Proceeding with build. ---"

# --- Build Step ---
# Build the Docker image
echo "Building Docker image: $IMAGE_NAME..."
docker build -t $IMAGE_NAME .

# Check if build was successful
if [ $? -ne 0 ]; then
    echo "Error: Docker image build failed."
    exit 1
fi

echo "--- Docker image built successfully. ---"

# --- Run Step ---
# Stop and remove any existing container with the same name
if [ "$(docker ps -a -q -f name=$CONTAINER_NAME)" ]; then
    echo "Stopping and removing existing container: $CONTAINER_NAME..."
    docker stop $CONTAINER_NAME
    docker rm $CONTAINER_NAME
fi

# Run the new container
echo "Running new container: $CONTAINER_NAME..."
echo "The application will be available at http://localhost:5000/rss"
docker run -d --network="host" --env-file .env --name $CONTAINER_NAME $IMAGE_NAME

# Check if the container started successfully
if [ $? -ne 0 ]; then
    echo "Error: Failed to start Docker container."
    exit 1
fi

echo "--- Container started successfully! ---"

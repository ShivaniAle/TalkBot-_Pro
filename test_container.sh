#!/bin/bash

# Build the container
echo "Building container..."
docker build -t voiceflow-ai .

# Run the container
echo "Running container..."
docker run -p 8080:8080 -e PORT=8080 voiceflow-ai 
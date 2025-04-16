# Build the container
Write-Host "Building container..."
docker build -t voiceflow-ai .

# Run the container
Write-Host "Running container..."
docker run -p 8080:8080 -e PORT=8080 voiceflow-ai 
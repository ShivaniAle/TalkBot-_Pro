#!/bin/bash
set -e

echo "Starting application..."

# Get the port from environment variable
PORT=${PORT:-8080}
echo "Using port: $PORT"

# Start the application
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 1 --log-level debug 
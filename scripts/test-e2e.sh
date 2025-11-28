#!/bin/bash

# Automated E2E test runner for Harvest Hound
# This script sets up the test environment and runs end-to-end tests

set -e

echo "🚀 Starting E2E test environment..."

# Ensure we're in the project root
cd "$(dirname "$0")/.."

# Check if .env file exists for secrets
if [ ! -f ".env" ]; then
  echo "❌ .env file not found in project root"
  echo "Please create .env file with your API keys (OPENAI_API_KEY, etc.)"
  exit 1
fi

# Load secrets from .env file
echo "🔑 Loading secrets from .env file..."
export $(cat .env | grep -v '^#' | xargs)

# Clean up any existing containers
echo "🧹 Cleaning up existing containers..."
docker-compose down --volumes --remove-orphans

# Build and start services with mock config for testing
echo "🏗️  Building and starting services..."
docker-compose --env-file config/test-mock-llm.env up -d --build

# Wait for services to be healthy
echo "⏳ Waiting for services to be healthy..."
timeout 120s bash -c '
  until docker-compose --env-file config/test-mock-llm.env ps | grep -q "healthy"; do
    echo "Waiting for services to start..."
    sleep 5
  done
'

# Check if services are running
if ! docker-compose --env-file config/test-mock-llm.env ps | grep -q "healthy"; then
  echo "❌ Services failed to start properly"
  docker-compose --env-file config/test-mock-llm.env logs
  exit 1
fi

echo "✅ Services are healthy"

# Run frontend E2E tests
echo "🧪 Running E2E tests..."
cd packages/frontend
pnpm test:e2e

echo "✅ E2E tests completed successfully"

# Clean up
echo "🧹 Cleaning up test environment..."
cd ../..
docker-compose --env-file config/test-mock-llm.env down --volumes

echo "🎉 E2E test run completed!"

#!/bin/bash

# Automated E2E test runner for Harvest Hound
# This script sets up the test environment and runs end-to-end tests

set -e

echo "🚀 Starting E2E test environment..."

# Ensure we're in the project root
cd "$(dirname "$0")/.."

# Clean up any existing containers
echo "🧹 Cleaning up existing containers..."
docker-compose down --volumes --remove-orphans

# Build and start services
echo "🏗️  Building and starting services..."
docker-compose up -d --build

# Wait for services to be healthy
echo "⏳ Waiting for services to be healthy..."
timeout 120s bash -c '
  until docker-compose ps | grep -q "healthy"; do
    echo "Waiting for services to start..."
    sleep 5
  done
'

# Check if services are running
if ! docker-compose ps | grep -q "healthy"; then
  echo "❌ Services failed to start properly"
  docker-compose logs
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
docker-compose down --volumes

echo "🎉 E2E test run completed!"
#!/bin/bash

# Local development startup script for Harvest Hound
# This script starts the development environment with hot reload

set -e

echo "🚀 Starting development environment..."

# Ensure we're in the project root
cd "$(dirname "$0")/.."

# Check if .env file exists for secrets
if [ ! -f ".env" ]; then
  echo "❌ .env file not found in project root"
  echo "Please create .env file with OPENAI_API_KEY"
  exit 1
fi

# Load secrets from .env file
echo "🔑 Loading secrets from .env file..."
export $(cat .env | grep -v '^#' | xargs)

# Clean up any existing containers
echo "🧹 Cleaning up existing containers..."
docker-compose -f docker-compose.dev.yml down --volumes --remove-orphans

# Build and start services with mocked LLM config
echo "🏗️  Building and starting development services..."
docker-compose -f docker-compose.dev.yml --env-file config/test-mock-llm.env up -d --build

# Wait for services to be healthy
echo "⏳ Waiting for services to be healthy..."
timeout 120s bash -c '
  until docker-compose -f docker-compose.dev.yml --env-file config/test-mock-llm.env ps | grep -q "healthy"; do
    echo "Waiting for services to start..."
    sleep 5
  done
'

# Check if services are running
if ! docker-compose -f docker-compose.dev.yml --env-file config/test-mock-llm.env ps | grep -q "healthy"; then
  echo "❌ Services failed to start properly"
  docker-compose -f docker-compose.dev.yml --env-file config/test-mock-llm.env logs
  exit 1
fi

echo "✅ Development services are healthy"
echo ""
echo "🌐 Services available at:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "📝 To view logs:"
echo "   docker-compose -f docker-compose.dev.yml --env-file config/test-mock-llm.env logs -f"
echo ""
echo "🛑 To stop services:"
echo "   docker-compose -f docker-compose.dev.yml --env-file config/test-mock-llm.env down"
echo ""
echo "🎨 To start Storybook:"
echo "   docker-compose -f docker-compose.dev.yml --env-file config/test-mock-llm.env --profile storybook up storybook"
echo ""
echo "🎉 Development environment ready!"
#!/bin/bash

# Manual testing script with real LLM integration for Harvest Hound
# This script sets up an environment for manual testing with actual LLM calls

set -e

echo "🚀 Starting manual testing environment with real LLM..."

# Ensure we're in the project root
cd "$(dirname "$0")/.."

# Check if test configuration exists
if [ ! -f "config/test-real-llm.env" ]; then
  echo "❌ Real LLM test configuration not found at config/test-real-llm.env"
  echo "Please create this file with your LLM service configuration."
  exit 1
fi

# Load test configuration
echo "📋 Loading real LLM test configuration..."
export $(cat config/test-real-llm.env | xargs)

# Clean up any existing containers
echo "🧹 Cleaning up existing containers..."
docker-compose -f docker-compose.dev.yml down --volumes --remove-orphans

# Build and start services with real LLM config
echo "🏗️  Building and starting services with real LLM..."
docker-compose -f docker-compose.dev.yml up -d --build

# Wait for services to be healthy
echo "⏳ Waiting for services to be healthy..."
timeout 120s bash -c '
  until docker-compose -f docker-compose.dev.yml ps | grep -q "healthy"; do
    echo "Waiting for services to start..."
    sleep 5
  done
'

# Check if services are running
if ! docker-compose -f docker-compose.dev.yml ps | grep -q "healthy"; then
  echo "❌ Services failed to start properly"
  docker-compose -f docker-compose.dev.yml logs
  exit 1
fi

echo "✅ Manual testing environment is ready"
echo ""
echo "🌐 Services available at:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "🧪 Manual testing scenarios:"
echo "   1. Create a new store (e.g., 'CSA Box')"
echo "   2. Upload inventory text (e.g., '2 lbs carrots, 1 bunch kale, 3 tomatoes')"
echo "   3. Verify parsing results with real LLM"
echo "   4. Test error handling with malformed input"
echo "   5. Test performance with large inventory lists"
echo ""
echo "📝 To view logs:"
echo "   docker-compose -f docker-compose.dev.yml logs -f"
echo ""
echo "🛑 To stop services:"
echo "   docker-compose -f docker-compose.dev.yml down"
echo ""
echo "⚠️  Note: This environment uses real LLM services and may incur costs"
echo "🎉 Manual testing environment ready!"
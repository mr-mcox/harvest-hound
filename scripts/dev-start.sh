#!/bin/bash

# Local development startup script for Harvest Hound
# This script starts the development environment with hot reload

set -e

echo "🚀 Starting development environment..."

# Ensure we're in the project root
cd "$(dirname "$0")/.."

# Clean up any existing containers
echo "🧹 Cleaning up existing containers..."
docker-compose -f docker-compose.dev.yml down --volumes --remove-orphans

# Build and start services
echo "🏗️  Building and starting development services..."
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

echo "✅ Development services are healthy"
echo ""
echo "🌐 Services available at:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "📝 To view logs:"
echo "   docker-compose -f docker-compose.dev.yml logs -f"
echo ""
echo "🛑 To stop services:"
echo "   docker-compose -f docker-compose.dev.yml down"
echo ""
echo "🎨 To start Storybook:"
echo "   docker-compose -f docker-compose.dev.yml --profile storybook up storybook"
echo ""
echo "🎉 Development environment ready!"
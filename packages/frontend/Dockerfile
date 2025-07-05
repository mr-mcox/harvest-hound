# Production Dockerfile for Frontend
FROM node:20-alpine

# Set working directory
WORKDIR /app

# Install pnpm
RUN npm install -g pnpm

# Copy workspace configuration files
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./

# Copy package files
COPY packages/frontend/package.json packages/frontend/

# Install dependencies (including dev dependencies needed for build)
RUN pnpm install --frozen-lockfile

# Copy application code
COPY packages/frontend/ packages/frontend/

# Build the application using workspace commands
RUN pnpm --filter frontend build

# Expose port
EXPOSE 3000

# Add health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:3000 || exit 1

# Run the application using workspace commands
CMD ["pnpm", "--filter", "frontend", "preview", "--host", "0.0.0.0", "--port", "3000"]
# Production Dockerfile for Frontend
FROM node:20-alpine

# Set working directory
WORKDIR /app

# Install pnpm
RUN npm install -g pnpm

# Copy workspace configuration files
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./

# Copy package files
COPY packages/frontend/package.json packages/frontend/pnpm-lock.yaml packages/frontend/

# Install dependencies
RUN pnpm install --frozen-lockfile

# Copy application code
COPY packages/frontend/ packages/frontend/

# Set working directory to frontend package
WORKDIR /app/packages/frontend

# Build the application
RUN pnpm build

# Expose port
EXPOSE 3000

# Add health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:3000 || exit 1

# Run the application
CMD ["pnpm", "preview", "--host", "0.0.0.0", "--port", "3000"]
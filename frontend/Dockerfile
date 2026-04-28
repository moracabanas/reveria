# =============================================================================
# Stage 1: Builder - Install dependencies and build Next.js static export
# =============================================================================
FROM node:20-alpine AS builder

# Install dependencies for node-gyp (required by some npm packages)
RUN apk add --no-cache python3 make g++

WORKDIR /app

# Copy package files first for better layer caching
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm ci --ignore-scripts

# Copy source code
COPY . .

# Build static export (uses next.config.ts output: 'export')
RUN npm run build

# =============================================================================
# Stage 2: Production - Serve static files with nginx
# =============================================================================
FROM nginx:alpine

# Remove default nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom nginx configuration
COPY --from=builder /app/nginx.conf /etc/nginx/conf.d/

# Copy static export from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose port 3000
EXPOSE 3000

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
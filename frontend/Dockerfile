# =============================================================================
# Writing System Platform - Frontend Dockerfile
# Multi-stage: builder compiles Vue/TS, runner serves via nginx
# Node 20 LTS | Vue 3 + Vite | pnpm
# =============================================================================

# Stage 1: dependency installer
FROM node:20-alpine AS deps

RUN corepack enable pnpm

WORKDIR /app

COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

# Stage 2: builder
FROM node:20-alpine AS builder

RUN corepack enable pnpm

WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules
COPY . .

# VITE_API_BASE_URL is injected at build time via --build-arg
# In production: docker build --build-arg VITE_API_BASE_URL=https://api.yourdomain.com
ARG VITE_API_BASE_URL=/api/v1
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}

RUN pnpm build

# Stage 3: nginx server
FROM nginx:1.27-alpine AS runner

LABEL org.opencontainers.image.title="Writing System Frontend"
LABEL org.opencontainers.image.description="Vue 3 SPA served by nginx"

# Remove default nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/app.conf

# Copy built assets from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Non-root — nginx can bind to port 8080 as non-root
RUN chown -R nginx:nginx /usr/share/nginx/html \
    && chmod -R 755 /usr/share/nginx/html

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget -qO- http://localhost:8080/health || exit 1

CMD ["nginx", "-g", "daemon off;"]

# =============================================================================
# Writing System Platform - Backend Dockerfile
# Multi-stage: builder installs deps, runner is the lean production image
# Python 3.12 | Django/Wagtail backend
# =============================================================================

# Stage 1: dependency builder
FROM python:3.12-slim AS builder

# Build deps needed for psycopg2, Pillow, argon2-cffi, cryptography
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    libwebp-dev \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip install --prefix=/install --no-cache-dir -r requirements.txt

# Stage 2: production runner
FROM python:3.12-slim AS runner

LABEL org.opencontainers.image.title="Writing System Platform"
LABEL org.opencontainers.image.description="Multi-tenant academic writing services backend"

# Runtime libs only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libjpeg62-turbo \
    zlib1g \
    libwebp7 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Non-root user for security
RUN groupadd --gid 1001 appgroup \
    && useradd --uid 1001 --gid appgroup --no-create-home --shell /bin/false appuser

# Copy installed packages from builder
COPY --from=builder /install /usr/local

WORKDIR /app

# Copy application code
COPY --chown=appuser:appgroup . .

# Create required runtime directories
RUN mkdir -p /var/log/writing-system /app/staticfiles /app/media \
    && chown -R appuser:appgroup /var/log/writing-system /app/staticfiles /app/media

# Entrypoint handles migrations + collectstatic before starting the service
COPY --chown=appuser:appgroup scripts/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

USER appuser

ARG DJANGO_ENV=production
ENV DJANGO_ENV=${DJANGO_ENV}
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Health check hits the public liveness endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health/live/ || exit 1

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
# Daphne serves both HTTP and WebSocket (ASGI) in a single process.
# Scale out by running multiple replicas rather than adding workers here.
CMD ["daphne", \
     "--bind", "0.0.0.0", \
     "--port", "8000", \
     "--proxy-headers", \
     "-v", "1", \
     "writing_system.asgi:application"]

# --------------------
# 1. Builder Stage
# --------------------
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install system dependencies for building packages
RUN apt-get update -y --no-install-recommends \
    && apt-get install -y --no-install-recommends \
       build-essential \
       libpq-dev \
       curl \
       git \
       wget \
       gcc \
       libc6-dev \
       postgresql-client \
       pkg-config \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install pip tooling (don’t auto-upgrade, just ensure they exist)
RUN pip install --no-cache-dir "pip==24.0" "setuptools==65.5.1" "wheel"

# Copy requirements file
COPY requirements.txt .

# Install dependencies (skip hashes for now, enforce later for prod)
RUN pip install --no-cache-dir -r requirements.txt

# Install the spaCy model (matches installed spaCy version)
RUN python -m spacy download en_core_web_md

# Copy source code
COPY . .

# --------------------
# 2. Runtime Stage
# --------------------
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install only minimal system dependencies for runtime
RUN apt-get update -y --no-install-recommends \
    && apt-get install -y --no-install-recommends \
       libpq-dev \
       postgresql-client \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder
COPY --from=builder /usr/local/lib/python3.11 /usr/local/lib/python3.11
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --from=builder /app /app

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

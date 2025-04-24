# Use a lightweight Python base image (force amd64)
FROM --platform=linux/amd64 python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
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

# Pre-install numpy with safe version to avoid binary issues
RUN pip install --upgrade pip setuptools wheel \
    && pip install numpy==1.24.4

# Copy requirements file early to leverage Docker cache
COPY requirements.txt .

# Remove problematic packages temporarily for clean pip flow
RUN grep -Ev '^(mysqlclient|blis|spacy)==' requirements.txt > filtered_requirements.txt

# Install problematic packages explicitly and correctly
RUN pip install --no-cache-dir blis==0.7.11 spacy==3.7.5 \
    && python -m spacy download en_core_web_md

# Install remaining dependencies
RUN pip install --no-cache-dir -r filtered_requirements.txt \
    && pip uninstall -y numpy && pip install numpy==1.26.4 \
    && rm filtered_requirements.txt

# Copy source code
COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# syntax=docker/dockerfile:1.4
FROM --platform=$BUILDPLATFORM python:3.12-alpine AS builder

WORKDIR /app

# Install system dependencies for mysqlclient
RUN apk add --no-cache \
    mariadb-connector-c-dev \
    gcc \
    musl-dev

# Copy requirements and install Python dependencies
COPY requirements.txt /app/
RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app/

# Environment variables
ENV FLASK_ENV=development
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Expose port
EXPOSE 8000

# Use gunicorn for production-ready serving
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "120", "wsgi:app"]

# Development stage with additional tools
FROM builder AS dev-envs

RUN apk add --no-cache git bash

# Create development user
RUN addgroup -S docker && \
    adduser -S --shell /bin/bash --ingroup docker vscode

# Install Docker tools (cli, buildx, compose)
COPY --from=gloursdocker/docker / /

# For development, use Flask development server instead of gunicorn
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=8000"]

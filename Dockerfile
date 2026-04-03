# syntax=docker/dockerfile:1.4

FROM --platform=$BUILDPLATFORM python:3.12-alpine

WORKDIR /app

RUN apk upgrade --no-cache && \
    apk add --no-cache \
    gcc \
    musl-dev \
    postgresql-dev

COPY backend/requirements.txt /app/requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install --no-cache-dir -r /app/requirements.txt

COPY backend /app

ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "120", "wsgi:app"]

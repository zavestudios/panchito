# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Architecture

This is a three-tier Dockerized web application using Docker Compose:

1. **Proxy (Nginx)**: Front-facing reverse proxy on port 80, forwards requests to backend
2. **Backend (Flask)**: Python Flask application on port 8000, serves blog posts from database
3. **Database (MariaDB)**: MariaDB 10 database, stores blog data

Network topology:
- `frontnet`: Connects proxy ↔ backend
- `backnet`: Connects backend ↔ database
- Database is not exposed to the proxy layer (security isolation)

Database credentials are managed via Docker secrets (`db/password.txt`).

## Development Commands

### Start the application
```bash
docker compose up -d
```

### Stop the application
```bash
docker compose down
```

### Rebuild containers (after code changes)
```bash
docker compose up --build
```

### View logs
```bash
docker compose logs -f [service_name]  # service_name: backend, db, or proxy
```

### Check service status
```bash
docker compose ps
```

### Access the application
- Frontend: http://localhost:80
- Backend directly: http://localhost:8000

## Backend Structure

**Main application**: `backend/hello.py`
- Flask app with a single route `/` that queries and displays blog posts
- `DBManager` class handles MySQL connection and queries
- Database connection uses Docker secrets from `/run/secrets/db-password`
- Database is auto-populated on first request with sample blog posts

**Environment variables** (set in `backend/Dockerfile`):
- `FLASK_APP=hello.py`
- `FLASK_ENV=development`
- `FLASK_RUN_PORT=8000`
- `FLASK_RUN_HOST=0.0.0.0`

## Database

- MariaDB 10 (compatible with both AMD64 and ARM64)
- Database name: `example`
- Health check runs every 3 seconds via `mysqladmin ping`
- Persistent storage via Docker volume `db-data`

## Important Notes

- The backend depends on the database being healthy before starting
- The proxy depends on the backend being available
- Database password is stored in `db/password.txt` and mounted as a Docker secret
- The backend Dockerfile has a `builder` target (used in compose.yaml) and a `dev-envs` target for development environments

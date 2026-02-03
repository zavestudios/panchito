# Panchito

**A modern Python ETL service for ingesting, normalizing, and serving real estate data**

Panchito is a Flask-based data ingestion and API service that serves as a "Pressure App" within the ZaveStudios ecosystem. It demonstrates production-ready Python development patterns including async task processing, data validation, and RESTful API design.

## Purpose

Panchito feeds real estate listing data to [TheHouseGuy](https://github.com/eckslopez/thehouseguy) (Rails app) via REST API. It's designed to:

- Ingest data from multiple sources (CSV datasets, APIs, future: CRMLS)
- Validate and normalize real estate listings
- Process data asynchronously using Celery
- Expose clean, paginated REST endpoints
- Force platform concerns: async queues, ETL patterns, polyglot CI/CD

> **Note:** This is a learning and portfolio project focused on demonstrating platform engineering skills through practical application development.

## Architecture

```
┌─────────────────┐
│   TheHouseGuy   │  (Rails - consumes data)
│   (Rails App)   │
└────────┬────────┘
         │ HTTP
         ▼
┌─────────────────┐
│     Nginx       │  (Reverse Proxy)
│   Port 80       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────┐
│  Flask Backend  │─────▶│   MariaDB    │
│   Port 8000     │      │  (Listings)  │
└────────┬────────┘      └──────────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────┐
│ Celery Workers  │─────▶│    Redis     │
│  (ETL Tasks)    │      │  (Broker)    │
└─────────────────┘      └──────────────┘
```

**Components:**
- **Flask API**: REST endpoints for listing data (port 8000)
- **Nginx Proxy**: Front-facing reverse proxy (port 80)
- **MariaDB**: Persistent storage for listings
- **Redis**: Message broker for Celery tasks
- **Celery Workers**: Async data ingestion and processing

**Network Isolation:**
- `frontnet`: proxy ↔ backend
- `backnet`: backend ↔ database, Redis
- Database not accessible from proxy layer

## Technology Stack

- **Python 3.12** - Latest stable Python
- **Flask 3.1** - Web framework with app factory pattern
- **SQLAlchemy 2.0** - ORM with type hints
- **Alembic** - Database migrations
- **Celery 5.4** - Distributed task queue
- **Redis** - Message broker and cache
- **Pydantic 2.x** - Data validation
- **pytest** - Testing framework
- **structlog** - Structured logging
- **Docker Compose** - Local development environment

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Git

### Run the Application

```bash
# Clone the repository
git clone git@github.com:eckslopez/panchito.git
cd panchito

# Start all services
docker compose up -d

# Check service health
curl http://localhost/api/v1/health

# View logs
docker compose logs -f backend
```

### Verify Installation

```bash
# Health check
curl http://localhost/api/v1/health
# Expected: {"status": "healthy", "service": "panchito", "version": "1.0.0"}

# Readiness check (includes database connectivity)
curl http://localhost/api/v1/health/ready
# Expected: {"status": "ready", "database": "connected"}

# Listings API (empty initially)
curl http://localhost/api/v1/listings
# Expected: {"data": [], "meta": {"page": 1, "per_page": 50, "total": 0}}
```

## API Documentation

### Base URL

- **Local**: `http://localhost/api/v1`
- **Backend Direct**: `http://localhost:8000/api/v1`

### Endpoints

#### Health Checks

```
GET /api/v1/health         # Basic health check
GET /api/v1/health/ready   # Readiness probe (k8s)
GET /api/v1/health/live    # Liveness probe (k8s)
```

#### Listings (Coming in Phase 2)

```
GET /api/v1/listings              # List all listings (paginated)
GET /api/v1/listings/{id}         # Get single listing
GET /api/v1/stats                 # Ingestion statistics
POST /api/v1/ingest/trigger       # Trigger ingestion job
GET /api/v1/ingest/status/{job_id} # Check job status
```

**Query Parameters:**
```
?page=1&per_page=50
?city=Los+Angeles&status=active
?min_price=500000&max_price=1000000
?sort_by=price&sort_order=desc
```

**Response Format:**
```json
{
  "data": [...],
  "meta": {
    "page": 1,
    "per_page": 50,
    "total": 1234
  }
}
```

## Development

### Project Structure

```
panchito/
├── backend/
│   ├── app/
│   │   ├── __init__.py           # Flask app factory
│   │   ├── config.py             # Environment configuration
│   │   ├── models/               # SQLAlchemy models
│   │   ├── api/v1/               # REST API endpoints
│   │   ├── services/             # Business logic
│   │   │   └── providers/        # Data source providers
│   │   ├── tasks/                # Celery tasks
│   │   ├── schemas/              # Pydantic validation
│   │   └── utils/                # Logging, helpers
│   ├── tests/                    # Test suite
│   ├── data/datasets/            # Local CSV files (gitignored)
│   ├── migrations/               # Alembic migrations
│   ├── requirements.txt          # Production dependencies
│   ├── requirements-dev.txt      # Dev dependencies
│   ├── wsgi.py                   # App entrypoint
│   └── Dockerfile
├── proxy/
│   ├── conf                      # Nginx configuration
│   └── Dockerfile
├── db/
│   └── password.txt              # Database secret
├── compose.yaml                  # Docker Compose config
├── CLAUDE.md                     # Architecture guide for AI
└── README.md                     # This file
```

### Development Workflow

```bash
# Rebuild after code changes
docker compose up --build -d

# View logs
docker compose logs -f backend
docker compose logs -f db

# Run tests (once Phase 2 is complete)
docker compose run --rm backend pytest

# Stop services
docker compose down

# Stop and remove volumes
docker compose down -v
```

### Environment Variables

See `backend/.env.example` for all configuration options:

- `FLASK_ENV` - development/production
- `SECRET_KEY` - Flask secret key
- `DB_HOST`, `DB_PORT`, `DB_NAME` - Database connection
- `CELERY_BROKER_URL` - Redis connection
- `LOG_LEVEL` - DEBUG/INFO/WARNING/ERROR

### Database Migrations

```bash
# Initialize migrations (already done)
docker compose exec backend flask db init

# Create new migration
docker compose exec backend flask db migrate -m "Description"

# Apply migrations
docker compose exec backend flask db upgrade

# Rollback migration
docker compose exec backend flask db downgrade
```

## Development Status

### ✅ Phase 1: Foundation (Complete)

- [x] Modern Flask 3.x app structure with app factory
- [x] Environment-based configuration
- [x] Structured logging with structlog
- [x] Health check endpoints (k8s-ready)
- [x] Docker Compose setup
- [x] Database connectivity

### 🔄 Phase 2: Core Data Model & API (In Progress)

See [open issues](https://github.com/eckslopez/panchito/issues) for detailed task breakdown:

- [ ] Pydantic validation schemas (#8)
- [ ] SQLAlchemy listing model (#9)
- [ ] Alembic migrations (#10)
- [ ] Paginated listings API (#11)
- [ ] Single listing endpoint (#12)
- [ ] Error handling (#13)
- [ ] Unit tests (#14)

### 🔜 Phase 3: ETL Pipeline (Planned)

- Provider abstraction pattern
- CSV dataset ingestion
- Data transformation service
- Idempotency and deduplication
- Error quarantine

### 🔜 Phase 4: Async Tasks (Planned)

- Celery worker configuration
- Background ingestion jobs
- Scheduled tasks (Celery Beat)
- Job status tracking
- Observability

### 🔜 Phase 5: Testing & Quality (Planned)

- Integration tests
- Test fixtures and factories
- >80% test coverage
- GitHub Actions CI

### 🔜 Phase 6: k8s & GitOps (Planned)

- Kubernetes manifests
- ArgoCD configuration
- Graceful shutdown
- Resource limits
- 12-factor compliance

## Part of ZaveStudios Platform

This application runs as a tenant on the [ZaveStudios multi-tenant platform](link).

**Platform integration:**
- Namespace: `<app-name>` (isolated Kubernetes namespace)
- Database: `db_<app-name>` tenant in [pg-multitenant](link)
- Deployment: ArgoCD GitOps via [kubernetes-platform-infrastructure](link)
- Observability: Shared Prometheus/Grafana

## Deployment

### Local Development (Current)

Uses Docker Compose for local testing and development. All services run on localhost.

### Production (Future)

Will deploy to k3s cluster with:
- ArgoCD for GitOps
- Kubernetes manifests with kustomize/helm
- Environment-specific configurations
- Secrets management via sealed-secrets or external-secrets
- Horizontal pod autoscaling for Celery workers

## Contributing

This is a personal learning project, but feedback and suggestions are welcome!

1. Check [open issues](https://github.com/eckslopez/panchito/issues)
2. Create a feature branch
3. Write tests for new functionality
4. Ensure tests pass and code is formatted
5. Submit a pull request

## Resources

- **CLAUDE.md** - Architecture and development guide for Claude Code
- **Issues** - https://github.com/eckslopez/panchito/issues
- **TheHouseGuy** - https://github.com/eckslopez/thehouseguy (consumer app)

## License

MIT

---

**Part of the ZaveStudios Ecosystem** - Building real applications to demonstrate platform engineering excellence.

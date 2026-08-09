# DROPme Recycling Platform

## 1. Overview

DROPme is a recycling event processing platform built with Flask, PostgreSQL, Redis, and a background worker.

The API accepts recycling events and places them into a Redis queue. A background worker consumes the events asynchronously, calculates the estimated recycling weight, and updates the corresponding PostgreSQL record.

The system also includes Docker Compose for local deployment, GitHub Actions for CI, Prometheus for metrics, and Grafana for visualization.

### Architecture

```text
                    ┌──────────────┐
                    │     UI       │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ Flask API    │
                    └──────┬───────┘
                           │
                    enqueue event
                           │
                           ▼
                    ┌──────────────┐
                    │    Redis     │
                    │    Queue     │
                    └──────┬───────┘
                           │
                         BLPOP
                           │
                           ▼
                    ┌──────────────┐
                    │   Worker     │
                    └──────┬───────┘
                           │
                       update
                           │
                           ▼
                    ┌──────────────┐
                    │ PostgreSQL   │
                    └──────────────┘

        API / Worker
             │
             ▼
        Prometheus
             │
             ▼
          Grafana
```

---

# 2. Prerequisites

For local development:

* Docker Desktop
* Docker Compose
* Git

For running the application without Docker:

* Python 3.11+
* PostgreSQL
* Redis

---

# 3. Configuration

The application uses environment variables for configuration.

Create a `.env` file locally:

```env
DATABASE_URL=postgresql://dropme:dropme@postgres:5432/dropme
REDIS_URL=redis://redis:6379/0
```

Do not commit `.env` files or real credentials to the repository.

For CI, test credentials are provided by the GitHub Actions service containers rather than committing credentials to the repository.

---

# 4. Build and Run

Clone the repository:

```bash
git clone <repository-url>
cd DropMe
```

Build and start the complete application:

```bash
docker compose up -d --build
```

Check the running containers:

```bash
docker compose ps
```

View logs:

```bash
docker compose logs -f
```

View API logs:

```bash
docker compose logs -f api
```

View worker logs:

```bash
docker compose logs -f worker
```

---

# 5. Database Initialization and Migrations

The project uses Flask-Migrate/Alembic for repeatable database migrations.

Run migrations with:

```bash
docker compose exec api flask db upgrade
```

To create a new migration after changing the SQLAlchemy models:

```bash
docker compose exec api flask db migrate -m "describe change"
```

Then apply it:

```bash
docker compose exec api flask db upgrade
```

Migration files are stored under:

```text
migrations/versions/
```

Migrations should be committed to Git so another environment can reproduce the same database schema.

---

# 6. API

The API is available at:

```text
http://localhost:5000
```

## POST /events

Creates a new recycling event.

The event is persisted and queued for asynchronous processing.

Example:

```bash
curl -X POST http://localhost:5000/events \
  -H "Content-Type: application/json" \
  -d '{
    "machine_id": "machine-001",
    "material_type": "PET",
    "item_count": 10
  }'
```

The API does not wait for the worker to finish processing the event.

---

## GET /events

Returns recycling events stored in PostgreSQL.

```bash
curl http://localhost:5000/events
```

---

## GET /events/<id>

Returns a specific recycling event.

```bash
curl http://localhost:5000/events/<event-id>
```

---

## GET /health

Checks whether the API process is running.

```bash
curl http://localhost:5000/health
```

Expected response:

```json
{
  "status": "ok"
}
```

---

## GET /ready

Checks whether the application dependencies are available.

```bash
curl http://localhost:5000/ready
```

A healthy response should indicate that PostgreSQL and Redis are available.

---

# 7. Background Worker

The worker consumes events from the Redis queue:

```text
recycling_events
```

The processing flow is:

```text
API
 ↓
Redis queue
 ↓
Worker
 ↓
PostgreSQL
```

For each event, the worker:

1. Retrieves the event from PostgreSQL.
2. Checks whether it has already been processed.
3. Calculates the estimated weight based on material type and item count.
4. Sets the processing status to `processed`.
5. Records the processing timestamp.
6. Saves the result to PostgreSQL.

Worker logs can be viewed with:

```bash
docker compose logs -f worker
```

---

# 8. Material Weight Calculation

The worker currently uses the following estimated weight per item:

| Material |   Weight |
| -------- | -------: |
| PET      |  0.02 kg |
| CAN      | 0.015 kg |
| GLASS    |  0.25 kg |
| PAPER    |  0.01 kg |

For example, 10 PET items result in:

```text
10 × 0.02 = 0.20 kg
```

---

# 9. Testing

Install development dependencies:

```bash
pip install -r requirements-dev.txt
```

Run the test suite:

```bash
pytest
```

Run linting:

```bash
ruff check .
```

The CI workflow automatically runs linting and tests for pull requests and pushes to the `main` branch.

---

# 10. CI

GitHub Actions is used for continuous integration.

The CI workflow performs:

1. Dependency installation
2. Ruff linting
3. Pytest
4. API Docker image build
5. Worker Docker image build
6. Trivy container image scanning

The test job uses temporary PostgreSQL and Redis service containers, so database/Redis credentials do not need to be committed to the repository.

---

# 11. Observability

The application exposes Prometheus metrics.

Prometheus is available at:

```text
http://localhost:9090
```

Grafana is available at:

```text
http://localhost:3000
```

Grafana uses Prometheus as its data source.

Inside the Docker network, the Prometheus data source URL is:

```text
http://prometheus:9090
```

## Worker metrics

The worker exposes:

```text
recycling_events_processed_total
recycling_events_failed_total
recycling_queue_length
```

### Processed events

```promql
recycling_events_processed_total
```

Number of events successfully processed by the worker since the worker process started.

### Failed events

```promql
recycling_events_failed_total
```

Number of processing failures since the worker process started.

### Queue length

```promql
recycling_queue_length
```

Current number of events waiting in the Redis queue.

---

# 12. Prometheus Targets

Prometheus scrapes the following targets:

```text
api:5000/metrics
worker:8000/metrics
prometheus:9090
```

Target status can be checked at:

```text
http://localhost:9090/targets
```

A target should show `UP` when it is reachable and exposing metrics.

---

# 13. Grafana Dashboard

The dashboard provides an operational view of the system.

Recommended panels include:

* Total/processed events
* Failed events
* Redis queue length
* Event processing rate
* Event failure rate
* API/worker availability

The queue length is particularly useful for identifying whether events are accumulating faster than the worker can process them.

---

# 14. Troubleshooting

## Containers are not running

Check:

```bash
docker compose ps
```

Restart the system:

```bash
docker compose up -d
```

View logs:

```bash
docker compose logs -f
```

---

## Database is unavailable

Check PostgreSQL:

```bash
docker compose logs postgres
```

Check readiness:

```bash
curl http://localhost:5000/ready
```

The application and PostgreSQL container must be running on the same Docker Compose network.

---

## Redis is unavailable

Check:

```bash
docker compose logs redis
```

Test Redis from the worker:

```bash
docker compose exec worker python -c "import os, redis; r=redis.from_url(os.getenv('REDIS_URL')); print(r.ping())"
```

Expected result:

```text
True
```

---

## Worker is not processing events

Check worker logs:

```bash
docker compose logs -f worker
```

Check the Redis queue length:

```bash
docker compose exec redis redis-cli LLEN recycling_events
```

If the queue contains events, verify that the worker is running and connected to Redis.

---

## Database schema is missing

Run:

```bash
docker compose exec api flask db upgrade
```

Then verify the API again.

---

## Prometheus target is DOWN

Open:

```text
http://localhost:9090/targets
```

Verify that the API and worker containers are running:

```bash
docker compose ps
```

Test the worker metrics endpoint directly:

```bash
docker compose exec prometheus wget -qO- http://worker:8000/metrics
```

---

# 15. Recovery

The application can be restarted using:

```bash
docker compose restart
```

If containers need to be rebuilt:

```bash
docker compose up -d --build
```

If the database schema is behind the committed migrations:

```bash
docker compose exec api flask db upgrade
```

For a complete local environment reset, containers and volumes can be removed with:

```bash
docker compose down -v
```

**Warning:** removing volumes deletes the local PostgreSQL data.

The environment can then be recreated with:

```bash
docker compose up -d --build
```

and migrations applied again.

---

# 16. Deployment

The application is containerized and can be deployed to a container-based hosting environment.

The current project focuses on reproducible local Docker deployment and CI. A production cloud deployment and complete image publishing/release pipeline are intentionally not included.

For production deployment, the next steps would include:

* Container image registry
* Production secrets management
* Managed PostgreSQL
* Managed Redis
* HTTPS
* Production monitoring and alerting
* Automated release/deployment workflow

---

# 17. Project Structure

```text
.
├── app/
│   ├── routes/
│   ├── services/
│   ├── models.py
│   ├── config.py
│   └── __init__.py
├── worker/
│   ├── worker.py
│   └── metrics.py
├── migrations/
├── tests/
├── templates/
├── static/
├── Dockerfile
├── docker-compose.yml
├── prometheus.yml
├── requirements.txt
├── requirements-dev.txt
├── ENGINEERING_DECISIONS.md
└── README.md
```

---

# 18. Engineering Decisions

See google drive link.

# Local Deployment Instructions

## Prerequisites

Make sure the following are installed:

* Docker Desktop
* Docker Compose
* Git

Docker Desktop must be running before starting the application.

---

## 1. Clone the Repository

```bash
git clone <REPOSITORY_URL>
cd DropMe
```

---

## 2. Configure Environment Variables

Create a `.env` file in the project root.

For the Docker Compose environment, use:

```env
DATABASE_URL=postgresql://dropme:dropme@postgres:5432/dropme
REDIS_URL=redis://redis:6379/0
```

Do not commit `.env` or real credentials to Git.

---

## 3. Build and Start the Application

Run:

```bash
docker compose up -d --build
```

This builds the API and worker images and starts:

* Flask API
* Background worker
* PostgreSQL
* Redis
* Prometheus
* Grafana

Verify that the containers are running:

```bash
docker compose ps
```

All required services should show as running.

---

## 4. Initialize the Database

Apply the existing database migrations:

```bash
docker compose exec api flask db upgrade
```

This creates/updates the PostgreSQL schema according to the migrations committed in the repository.

---

## 5. Verify the Application

### Health check

```bash
curl http://localhost:5000/health
```

Expected response:

```json
{
  "status": "ok"
}
```

### Readiness check

```bash
curl http://localhost:5000/ready
```

The response should indicate that both PostgreSQL and Redis are available.

---

## 6. Test Event Processing

Create an event:

```bash
curl -X POST http://localhost:5000/events \
  -H "Content-Type: application/json" \
  -d '{
    "machine_id": "machine-001",
    "material_type": "PET",
    "item_count": 10
  }'
```

The API should return successfully without waiting for the background worker to finish processing.

The event is placed into the Redis queue:

```text
recycling_events
```

The worker consumes the event and updates the corresponding PostgreSQL record.

Check the worker logs:

```bash
docker compose logs -f worker
```

A successfully processed event should produce a message similar to:

```text
Processed event <event-id>: 0.2 kg
```

Retrieve the event using:

```bash
curl http://localhost:5000/events/<event-id>
```

The event should eventually have:

```json
{
  "processing_status": "processed"
}
```

along with its calculated `estimated_weight_kg` and `processed_at` timestamp.

---

## 7. Access the UI

Open:

```text
http://localhost:5000
```

The application UI should be available after the API container has started.

---

## 8. Verify Redis

Test the Redis connection from the worker container:

```bash
docker compose exec worker python -c "import os, redis; r=redis.from_url(os.getenv('REDIS_URL')); print(r.ping())"
```

Expected output:

```text
True
```

Check the queue:

```bash
docker compose exec redis redis-cli LLEN recycling_events
```

A value of `0` means there are currently no events waiting in the queue.

---

## 9. Verify Prometheus

Open:

```text
http://localhost:9090
```

Check the configured targets:

```text
http://localhost:9090/targets
```

The API and worker targets should be shown as `UP`.

Worker metrics are available at:

```text
http://localhost:8000/metrics
```

from inside the Docker network.

You can also test the worker metrics through the Prometheus container:

```bash
docker compose exec prometheus wget -qO- http://worker:8000/metrics
```

---

## 10. Access Grafana

Open:

```text
http://localhost:3000
```

Use the Grafana credentials configured for the local environment.

Configure Prometheus as the Grafana data source using:

```text
http://prometheus:9090
```

The worker exposes metrics including:

```text
recycling_events_processed_total
recycling_events_failed_total
recycling_queue_length
```

These can be used to monitor event processing and Redis queue activity.

---

## 11. View Logs

View all services:

```bash
docker compose logs -f
```

View only the API:

```bash
docker compose logs -f api
```

View only the worker:

```bash
docker compose logs -f worker
```

View PostgreSQL:

```bash
docker compose logs -f postgres
```

View Redis:

```bash
docker compose logs -f redis
```

---

## 12. Stop the Application

To stop the containers without deleting their data:

```bash
docker compose down
```

To restart the application:

```bash
docker compose up -d
```

---

## 13. Rebuild the Application

If application code or the Dockerfile changes:

```bash
docker compose up -d --build
```

---

## 14. Complete Local Reset

To remove the containers **and their associated volumes**:

```bash
docker compose down -v
```

**Warning:** this deletes the local PostgreSQL data.

Recreate the environment:

```bash
docker compose up -d --build
```

Then apply the migrations again:

```bash
docker compose exec api flask db upgrade
```

---

## Expected End-to-End Flow

A successful deployment should support the following flow:

```text
POST /events
      │
      ▼
   Flask API
      │
      ▼
    Redis
      │
      ▼
   Worker
      │
      ▼
 PostgreSQL
      │
      ▼
GET /events/<id>
```

At the same time:

```text
API + Worker
      │
      ▼
 Prometheus
      │
      ▼
  Grafana
```

If the POST request succeeds, the worker processes the event, the PostgreSQL record changes to `processed`, and Prometheus exposes the worker metrics, the local deployment is functioning correctly.

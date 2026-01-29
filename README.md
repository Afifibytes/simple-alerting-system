# Simple Alerting System

A rule-based event alerting platform with Python/FastAPI backend, React frontend, PostgreSQL, and RabbitMQ.

## Architecture

```
+-------------+       +----------------+       +-------------+
|   Frontend  | ----> |  Backend API   | ----> |  PostgreSQL |
|   (React)   |       |   (FastAPI)    |       |             |
+-------------+       +----------------+       +-------------+
      |                      |
      |                      v
      |               +-------------+
      +-------------> |  RabbitMQ   |
        (SSE)         +-------------+
                           |
              +------------+------------+
              |                         |
              v                         v
       +--------------+         +--------------+
       | Event Worker |         | Alert Worker |
       +--------------+         +--------------+
```

### Data Flow

```
1. Event Ingestion:
   Client --> POST /v1/events --> RabbitMQ (events queue)

2. Event Processing:
   RabbitMQ --> Event Worker --> PostgreSQL (persist)
                            |
                            +--> Rule Evaluation --> RabbitMQ (alerts queue)

3. Alert Processing:
   RabbitMQ --> Alert Worker --> PostgreSQL (create alert)
                            |
                            +--> Notification Channels (email, webhook, etc.)
                            |
                            +--> SSE Broadcast (real-time UI updates)
```

### Data Model

```
sources              Primary entity representing an event source
    |
    v
events               Raw events received from sources
    |
    v
alert_rules          Conditions that trigger alerts
    |
    v
alerts               Triggered alert instances
    |
    v
notification_channels    Delivery targets (email, webhook, Slack)
```

## Requirements

- Docker and Docker Compose

## Quick Start

1. Clone the repository

2. Copy environment files:
```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

3. Start all services:
```bash
docker-compose up
```

4. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - RabbitMQ Management: http://localhost:15672 (guest/guest)

5. Stop services:
```bash
docker-compose down
```

## Running Tests

### Backend Tests
```bash
docker-compose run --rm backend pytest
```

### Frontend Tests
```bash
docker-compose run --rm frontend npm test -- --watchAll=false
```

### Database Migrations

```bash
# Create a new migration
docker-compose run --rm backend alembic revision -m "description"

# Apply migrations
docker-compose run --rm backend alembic upgrade head
```
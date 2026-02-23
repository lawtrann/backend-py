# Backend API

FastAPI + PostgreSQL + JWT auth · Layered DDD (API → Application → Domain → Infrastructure).

## 🚀 Quick Start

```bash
cp .env.example .env    # set env vars
uv sync                 # install dependencies
make dev                # 3-pane tmux: DB + MinIO + FastAPI server + shell
```

Swagger UI at http://localhost:8000/docs

MinIO Console at http://localhost:9081

## 📋 Make Targets

| Command | Description                                  |
|---------|----------------------------------------------|
| `make dev` | Start tmux session (DB + MinIO + FastAPI + shell) |
| `make stop` | Kill session + docker compose down           |
| `make test` | Unit tests                                   |
| `make test-cov` | Tests + coverage report                      |
| `make migrate` | `alembic upgrade head` + generated models |

## 🧱 Development Layers

1. **Domain** — entities, repo ABCs, domain services/ABCs, exceptions (pure, no I/O)
2. **Application** — use cases orchestrating repos + domain services; supports `@transactional`
3. **Infra** — SQL migrations → generated ORM models → concrete repos + security implementations
4. **API** — thin endpoints; DI wired via `provider.py` scopes (`Singleton`, `RequestScope`, `NoScope`) and container modules

New migration:
```bash
alembic revision -m "desc"
# Edit migrations/sql/<rev>_*_{upgrade,downgrade}.sql, then:
make migrate
```

## 🏗️  Project Structure

```
app/
├── api/            # Endpoints + DI wiring
├── application/    # Use cases
├── domain/         # Entities, repo ABCs, services/ABCs, exceptions
├── infra/          # Generated models, session, concrete repos, security, MinIO storage
├── core/           # Config, logging, request context
└── schemas/        # Request/response DTOs
migrations/
├── sql/            # DDL source of truth
└── versions/       # Alembic stubs
tests/unit/         # No DB dependency
```

## 🔐  Environment Variables

| Variable | Default        | Description |
|----------|----------------|-------------|
| `SECRET_KEY` | *(required)*   | JWT signing key |
| `POSTGRES_USER` | `postgres`     | Database user |
| `POSTGRES_PASSWORD` | `example`      | Database password |
| `POSTGRES_DB` | `backend`      | Database name |
| `DB_HOST` | `localhost`    | Database host |
| `DB_PORT` | `15432`        | Host port for PostgreSQL |
| `DATABASE_URL` | *(auto-built)* | Override to set full connection string |
| `API_PORT` | `8000`         | Host port for API |
| `DEBUG` | `false`        | Debug mode |
| `MINIO_ENDPOINT` | `localhost:9080` | MinIO server endpoint |
| `MINIO_ACCESS_KEY` | `minioadmin` | MinIO access key |
| `MINIO_SECRET_KEY` | `minioadmin` | MinIO secret key |
| `MINIO_SECURE` | `false` | Use HTTPS for MinIO |
| `MINIO_DEFAULT_BUCKET` | `uploads` | Default storage bucket |
| `MINIO_PRESIGNED_URL_EXPIRY_SECONDS` | `3600` | Presigned URL TTL (seconds) |

## 🥇 License

MIT License © 2026 Tran Nhat Vinh. See [LICENSE](./LICENSE) for details.
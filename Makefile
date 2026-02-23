BACKEND_DIR := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
SESSION     := backend

.PHONY: dev stop test test-cov migrate

dev:
	bash $(BACKEND_DIR)/scripts/dev.sh

stop:
	tmux kill-session -t $(SESSION) 2>/dev/null || true
	docker compose -f $(BACKEND_DIR)/docker-compose.yml down

test:
	uv run pytest tests/unit/ -v

test-cov:
	uv run pytest tests/unit/ -v \
		--cov=app/domain \
		--cov=app/application \
		--cov=app/core \
		--cov-report=term-missing

migrate:
	uv run alembic upgrade head && bash $(BACKEND_DIR)/scripts/generate_models.sh

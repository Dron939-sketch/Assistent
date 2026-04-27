.PHONY: help up down build logs shell-db shell-redis migrate seed test

help:
	@echo "FishFlow Makefile Commands:"
	@echo "  make up          - Start all services"
	@echo "  make down        - Stop all services"
	@echo "  make build       - Build all Docker images"
	@echo "  make logs        - Follow logs"
	@echo "  make shell-db    - Enter Postgres shell"
	@echo "  make shell-redis - Enter Redis CLI"
	@echo "  make migrate     - Run database migrations"
	@echo "  make seed        - Seed demo data"
	@echo "  make test        - Run tests"
	@echo "  make clone       - Create new tenant (usage: TENANT=tarot make clone)"
	@echo "  make dev         - Run in development mode (no Docker)"

up:
	docker-compose up -d

down:
	docker-compose down

build:
	docker-compose build

logs:
	docker-compose logs -f

shell-db:
	docker-compose exec postgres psql -U postgres -d fishflow

shell-redis:
	docker-compose exec redis redis-cli

migrate:
	docker-compose exec api alembic upgrade head

seed:
	docker-compose exec api python -m scripts.seed_db

test:
	docker-compose exec api pytest
	docker-compose exec web npm test

clone:
	@if [ -z "$(TENANT)" ]; then \
		echo "Usage: make clone TENANT=tarot"; \
		exit 1; \
	fi
	./scripts/clone-tenant.sh $(TENANT)

dev:
	@echo "Starting in development mode..."
	@echo "API: cd apps/api && uvicorn src.main:app --reload"
	@echo "Web: cd apps/web && npm run dev"
	@echo "Worker: cd apps/worker && celery -A src.celery_app worker --loglevel=info"

.PHONY: help install install-backend install-frontend check check-backend typecheck schema test test-backend test-backend-unit test-backend-integration test-backend-e2e test-frontend coverage coverage-backend lint lint-backend lint-fix-backend migrate migrate-test makemigrations docker-up docker-down docker-logs docker-test-backend clean clean-backend clean-frontend clean-all dev dev-backend dev-frontend build-frontend ci-test ci-coverage ci-lint

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-22s\033[0m %s\n", $$1, $$2}'

# Installation
install: install-backend install-frontend ## Install all dependencies (backend + frontend)

install-backend: ## Install backend Python dependencies
	cd backend && pip install -r requirements.txt

install-frontend: ## Install frontend Node dependencies
	cd frontend && pnpm install

# Verification
check: check-backend typecheck ## Run backend system check + frontend typecheck

check-backend: ## Run Django system checks with test settings
	cd backend && .venv/bin/python manage.py check --settings=writing_system.settings_test

typecheck: ## Run vue-tsc type check on the frontend
	cd frontend && pnpm typecheck

schema: ## Generate an OpenAPI schema snapshot
	cd backend && .venv/bin/python manage.py spectacular --file /tmp/writing-system-schema.yml --settings=writing_system.settings_test

# Testing
test: test-backend test-frontend ## Run all tests (backend + frontend)

test-frontend: ## Run frontend tests (vitest)
	cd frontend && pnpm test

test-backend: ## Run backend tests
	cd backend && pytest -v --tb=short

test-backend-unit: ## Run backend unit tests only
	cd backend && pytest -m "not integration and not e2e and not slow" -v

test-backend-integration: ## Run backend integration tests only
	cd backend && pytest -m integration -v

test-backend-e2e: ## Run backend E2E tests only
	cd backend && pytest -m e2e -v

# Coverage
coverage: coverage-backend ## Generate backend coverage reports

coverage-backend: ## Generate backend coverage report
	cd backend && pytest --cov=. --cov-report=html --cov-report=term-missing --cov-report=xml
	@echo "Backend coverage report: backend/htmlcov/index.html"

# Linting
lint: lint-backend ## Run all linters

lint-backend: ## Lint backend code
	cd backend && flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	cd backend && black --check . || echo "Run 'black .' to fix formatting"
	cd backend && isort --check-only . || echo "Run 'isort .' to fix imports"

lint-fix-backend: ## Fix backend formatting
	cd backend && black .
	cd backend && isort .

# Database
migrate: ## Run database migrations
	cd backend && python manage.py migrate

migrate-test: ## Run migrations for test database
	cd backend && DJANGO_SETTINGS_MODULE=writing_system.settings_test python manage.py migrate

makemigrations: ## Create new migrations
	cd backend && python manage.py makemigrations

# Docker
docker-up: ## Start backend Docker services
	docker-compose up -d

docker-down: ## Stop Docker services
	docker-compose down

docker-logs: ## View Docker logs
	docker-compose logs -f

docker-test-backend: ## Run backend tests in Docker
	docker-compose exec web pytest -v

# Cleanup
clean: clean-backend clean-frontend ## Clean all generated files

clean-frontend: ## Clean frontend build artifacts
	rm -rf frontend/dist
	rm -rf frontend/.vite

clean-backend: ## Clean backend generated files
	find backend -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
	find backend -type f -name "*.pyc" -delete
	find backend -type d -name "*.egg-info" -exec rm -r {} + 2>/dev/null || true
	rm -rf backend/.pytest_cache
	rm -rf backend/htmlcov
	rm -rf backend/.coverage
	rm -rf backend/coverage.xml
	rm -rf backend/junit.xml
	rm -rf backend/*.log

clean-all: clean ## Clean generated files and local backend virtualenvs
	rm -rf backend/venv
	rm -rf backend/.venv

# Development
dev: dev-backend ## Start backend development server

dev-backend: ## Start backend development server
	cd backend && python manage.py runserver

dev-frontend: ## Start frontend dev server (hot-reload on :5174)
	cd frontend && pnpm dev

build-frontend: ## Build frontend for production
	cd frontend && pnpm build

# CI helpers
ci-test: test-backend ## Run tests as CI would

ci-coverage: coverage-backend ## Generate coverage as CI would

ci-lint: lint-backend ## Run linters as CI would

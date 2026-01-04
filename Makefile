.PHONY: help test test-backend test-frontend test-all coverage coverage-backend coverage-frontend lint lint-backend lint-frontend install install-backend install-frontend clean

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ============================================
# Installation
# ============================================
install: install-backend install-frontend ## Install all dependencies

install-backend: ## Install backend dependencies
	cd backend && pip install -r requirements.txt

install-frontend: ## Install frontend dependencies
	cd frontend && npm ci

# ============================================
# Testing
# ============================================
test: test-backend test-frontend ## Run all tests

test-backend: ## Run backend tests
	cd backend && pytest -v --tb=short

test-backend-unit: ## Run backend unit tests only
	cd backend && pytest -m "not integration and not e2e and not slow" -v

test-backend-integration: ## Run backend integration tests only
	cd backend && pytest -m integration -v

test-backend-e2e: ## Run backend E2E tests only
	cd backend && pytest -m e2e -v

test-frontend: ## Run frontend tests
	cd frontend && npm run test:run

test-frontend-unit: ## Run frontend unit tests only
	cd frontend && npm run test:unit

test-frontend-components: ## Run frontend component tests only
	cd frontend && npm run test:components

test-all: test-backend test-frontend ## Run all tests (backend + frontend)

# ============================================
# Coverage
# ============================================
coverage: coverage-backend coverage-frontend ## Generate coverage reports for all

coverage-backend: ## Generate backend coverage report
	cd backend && pytest --cov=. --cov-report=html --cov-report=term-missing --cov-report=xml
	@echo "Backend coverage report: backend/htmlcov/index.html"

coverage-frontend: ## Generate frontend coverage report
	cd frontend && npm run test:coverage
	@echo "Frontend coverage report: frontend/coverage/index.html"

# ============================================
# Linting
# ============================================
lint: lint-backend lint-frontend ## Run all linters

lint-backend: ## Lint backend code
	cd backend && flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	cd backend && black --check . || echo "⚠️ Run 'black .' to fix formatting"
	cd backend && isort --check-only . || echo "⚠️ Run 'isort .' to fix imports"

lint-frontend: ## Lint frontend code
	cd frontend && npm run lint

lint-fix-backend: ## Fix backend linting issues
	cd backend && black .
	cd backend && isort .

lint-fix-frontend: ## Fix frontend linting issues
	cd frontend && npm run lint

# ============================================
# Database
# ============================================
migrate: ## Run database migrations
	cd backend && python manage.py migrate

migrate-test: ## Run migrations for test database
	cd backend && DJANGO_SETTINGS_MODULE=writing_system.settings_test python manage.py migrate

makemigrations: ## Create new migrations
	cd backend && python manage.py makemigrations

# ============================================
# Docker
# ============================================
docker-up: ## Start Docker containers
	docker-compose up -d

docker-down: ## Stop Docker containers
	docker-compose down

docker-logs: ## View Docker logs
	docker-compose logs -f

docker-test-backend: ## Run backend tests in Docker
	docker-compose exec web pytest -v

docker-test-frontend: ## Run frontend tests in Docker
	docker-compose exec frontend npm run test:run

# ============================================
# Cleanup
# ============================================
clean: clean-backend clean-frontend ## Clean all generated files

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

clean-frontend: ## Clean frontend generated files
	cd frontend && rm -rf node_modules/.vite
	cd frontend && rm -rf dist
	cd frontend && rm -rf coverage
	cd frontend && rm -f junit.xml

clean-all: clean ## Clean everything including dependencies
	rm -rf backend/venv
	rm -rf backend/.venv
	rm -rf frontend/node_modules

# ============================================
# Development
# ============================================
dev-backend: ## Start backend development server
	cd backend && python manage.py runserver

dev-frontend: ## Start frontend development server
	cd frontend && npm run dev

dev: ## Start both backend and frontend (requires two terminals)
	@echo "Starting backend and frontend..."
	@echo "Backend: make dev-backend"
	@echo "Frontend: make dev-frontend"

# ============================================
# CI/CD Helpers
# ============================================
ci-test: ## Run tests as CI would
	$(MAKE) test-backend
	$(MAKE) test-frontend

ci-coverage: ## Generate coverage as CI would
	$(MAKE) coverage-backend
	$(MAKE) coverage-frontend

ci-lint: ## Run linters as CI would
	$(MAKE) lint-backend
	$(MAKE) lint-frontend

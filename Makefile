.PHONY: help setup run run-frontend run-celery run-celery-beat test test-backend test-frontend test-coverage test-unit test-integration test-setup test-quick check migrations migrate shell restart logs clean nuke-db

# Default target
help:
	@echo "Writing System Platform - Development Commands"
	@echo ""
	@echo "Available commands:"
	@echo "  make setup           - Complete one-time setup (env files, migrations, superuser)"
	@echo "  make run             - Start Django development server"
	@echo "  make run-frontend   - Start Vue.js development server"
	@echo "  make run-celery     - Start Celery worker"
	@echo "  make run-celery-beat - Start Celery beat scheduler"
	@echo "  make test           - Run all tests (backend + frontend)"
	@echo "  make test-backend   - Run backend tests with pytest"
	@echo "  make test-frontend  - Run frontend tests with Vitest"
	@echo "  make test-coverage  - Run tests with 95% coverage requirement"
	@echo "  make test-unit      - Run only unit tests"
	@echo "  make test-integration - Run only integration tests"
	@echo "  make test-setup     - Set up local Python test environment"
	@echo "  make test-quick    - Quick test run (frontend only)"
	@echo "  make test-coverage-backend - Backend tests with 95% coverage"
	@echo "  make test-coverage-frontend - Frontend tests with 95% coverage"
	@echo "  make coverage-gaps - Analyze coverage gaps"
	@echo "  make check           - Run code quality checks (linting, formatting)"
	@echo "  make migrations      - Create new database migrations"
	@echo "  make migrate         - Apply pending database migrations"
	@echo "  make shell           - Open Django shell"
	@echo "  make restart         - Restart all Docker services"
	@echo "  make logs            - View logs from all services"
	@echo "  make clean           - Stop and remove containers, volumes"
	@echo "  make nuke-db         - Delete database and all migration files (USE WITH CAUTION)"
	@echo ""

# Complete setup
setup:
	@echo "🚀 Setting up Writing System Platform..."
	@if [ ! -f backend/.env ]; then \
		echo "📝 Creating backend/.env from template..."; \
		cp backend/env.template backend/.env; \
		echo "⚠️  Please edit backend/.env with your configuration"; \
	fi
	@echo "🐳 Starting Docker services..."
	docker-compose up -d
	@echo "⏳ Waiting for services to be ready..."
	sleep 5
	@echo "📦 Running database migrations..."
	docker-compose exec -T web python manage.py migrate || true
	@echo "✅ Setup complete!"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Edit backend/.env with your configuration"
	@echo "  2. Create a superuser: make shell (then: python manage.py createsuperuser)"
	@echo "  3. Start the server: make run"
	@echo ""

# Start Django development server
run:
	@echo "🚀 Starting Django development server..."
	docker-compose up web

# Start frontend development server
run-frontend:
	@echo "🚀 Starting Vue.js development server..."
	cd frontend && npm run dev

# Start Celery worker
run-celery:
	@echo "🚀 Starting Celery worker..."
	docker-compose up celery

# Start Celery beat scheduler
run-celery-beat:
	@echo "🚀 Starting Celery beat scheduler..."
	docker-compose up beat

# Run all tests
test: test-backend test-frontend
	@echo "✅ All tests completed!"

# Run backend tests
test-backend:
	@echo "🧪 Running backend tests..."
	@cd backend && pytest -v --tb=short

# Run frontend tests
test-frontend:
	@echo "🧪 Running frontend tests..."
	@cd frontend && npm run test:run

# Run tests with coverage (95% minimum required)
test-coverage:
	@echo "🧪 Running tests with 95% coverage requirement..."
	@./scripts/run_tests_with_coverage.sh

# Run backend tests with 95% coverage requirement
test-coverage-backend:
	@echo "🧪 Running backend tests with 95% coverage..."
	@./scripts/run_tests_with_coverage.sh --backend-only

# Run frontend tests with 95% coverage requirement
test-coverage-frontend:
	@echo "🧪 Running frontend tests with 95% coverage..."
	@./scripts/run_tests_with_coverage.sh --frontend-only

# Run only unit tests
test-unit:
	@echo "🧪 Running unit tests..."
	@cd backend && pytest -m unit -v
	@cd frontend && npm run test:run -- --grep "unit"

# Run only integration tests
test-integration:
	@echo "🧪 Running integration tests..."
	@cd backend && pytest -m integration -v

# Set up local Python test environment
test-setup:
	@echo "🔧 Setting up local Python test environment..."
	@./scripts/setup-test-environment.sh

# Quick test (frontend only, always works)
test-quick:
	@echo "🧪 Running quick tests (frontend)..."
	@./scripts/quick-test.sh

# Analyze coverage gaps
coverage-gaps:
	@echo "🔍 Analyzing coverage gaps..."
	@./scripts/check_coverage_gaps.sh

# Run code quality checks
check:
	@echo "🔍 Running code quality checks..."
	@echo "Backend checks (if configured)..."
	@# docker-compose exec -T web flake8 . || true
	@# docker-compose exec -T web black --check . || true
	@echo "Frontend checks..."
	@cd frontend && npm run lint || true

# Create migrations
migrations:
	@echo "📝 Creating database migrations..."
	docker-compose exec web python manage.py makemigrations

# Apply migrations
migrate:
	@echo "📦 Applying database migrations..."
	docker-compose exec web python manage.py migrate

# Open Django shell
shell:
	@echo "🐚 Opening Django shell..."
	docker-compose exec web python manage.py shell

# Restart all services
restart:
	@echo "🔄 Restarting all services..."
	docker-compose restart

# View logs
logs:
	@echo "📋 Viewing logs from all services..."
	docker-compose logs -f

# Clean up (stop and remove containers, volumes)
clean:
	@echo "🧹 Cleaning up Docker resources..."
	docker-compose down -v
	@echo "✅ Cleanup complete!"

# Nuclear option: delete database and migrations (USE WITH CAUTION)
nuke-db:
	@echo "⚠️  WARNING: This will delete the database and all migration files!"
	@echo "Press Ctrl+C to cancel, or Enter to continue..."
	@read
	@echo "🗑️  Stopping services..."
	docker-compose down
	@echo "🗑️  Removing database volume..."
	docker volume rm writing_project_postgres_data || true
	@echo "🗑️  Removing migration files..."
	find backend -path "*/migrations/*.py" -not -name "__init__.py" -delete
	find backend -path "*/migrations/*.pyc" -delete
	@echo "✅ Database and migrations deleted!"
	@echo "Run 'make setup' to recreate everything."


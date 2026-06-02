# ============================================================
# 🌿 Medicinal Plant Detection & RAG Assistant — Makefile
# Convenience targets for development workflow
# ============================================================

.PHONY: install dev-backend dev-frontend dev test lint format docker-up docker-down db-migrate db-upgrade clean

# ----- Installation -----
install: ## Install all project dependencies (backend + frontend)
	cd backend && pip install -r requirements.txt
	cd frontend && npm install
	cd ml && pip install -r requirements.txt

# ----- Development Servers -----
dev-backend: ## Start the FastAPI backend dev server
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend: ## Start the React frontend dev server
	cd frontend && npm run dev

dev: ## Run both backend and frontend dev servers concurrently
	@echo "Starting backend and frontend..."
	$(MAKE) dev-backend & $(MAKE) dev-frontend

# ----- Testing -----
test: ## Run all tests with pytest
	pytest tests/ -v --tb=short

# ----- Code Quality -----
lint: ## Run linters (ruff for Python, eslint for frontend)
	cd backend && ruff check .
	cd frontend && npm run lint

format: ## Auto-format code (ruff for Python, prettier for frontend)
	cd backend && ruff format .
	cd frontend && npm run format

# ----- Docker -----
docker-up: ## Start all Docker services
	docker-compose up --build -d

docker-down: ## Stop all Docker services
	docker-compose down

# ----- Database -----
db-migrate: ## Create a new Alembic migration (usage: make db-migrate msg="migration message")
	cd backend && alembic revision --autogenerate -m "$(msg)"

db-upgrade: ## Apply database migrations
	cd backend && alembic upgrade head

# ----- Cleanup -----
clean: ## Remove build artifacts, caches, and temporary files
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf dist/ build/ *.egg-info/
	rm -rf frontend/dist frontend/node_modules/.cache
	rm -f .coverage
	rm -rf htmlcov/
	@echo "✅ Cleaned up build artifacts and caches."

# ----- Help -----
help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help

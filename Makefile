.PHONY: help setup install build test run dev clean lint format check deploy-dev deploy-prod logs-dev logs-prod info-dev info-prod delete-dev delete-prod sam-build sam-deploy-dev sam-deploy-prod sam-local

help:  ## Show this help message
	@echo "Maestro Tuya IR Bridge - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup:  ## Install uv if not already installed
	@command -v uv >/dev/null 2>&1 || (echo "Installing uv..." && curl -LsSf https://astral.sh/uv/install.sh | sh)
	@echo "uv is installed"

install: setup  ## Install project dependencies
	uv sync

install-dev: setup  ## Install project dependencies including dev tools
	uv sync --all-extras

build:  ## Build the project (Python package)
	uv build


test:  ## Run tests
	uv run pytest tests/ -v

test-coverage:  ## Run tests with coverage report
	uv run pytest tests/ --cov=app --cov-report=html --cov-report=term

run:  ## Run the FastAPI server
	uv run uvicorn index:app --host 0.0.0.0 --port 8000

dev:  ## Run the FastAPI server in development mode (with auto-reload)
	uv run uvicorn index:app --reload --host 0.0.0.0 --port 8000

lint:  ## Run linter (ruff check)
	uv run ruff check .

format:  ## Format code with ruff
	uv run ruff format .

check:  ## Run linter and formatter check
	uv run ruff check .
	uv run ruff format --check .

fix:  ## Auto-fix linting issues
	uv run ruff check --fix .
	uv run ruff format .

clean:  ## Clean up generated files
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info
	rm -f _irremote*.so
	rm -f test_bindings.py
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

api-test:  ## Test the API endpoints (server must be running)
	@echo "Testing /api/health..."
	@curl -s http://localhost:8000/api/health | python -m json.tool
	@echo "\nTesting /api/encode..."
	@curl -s -X POST http://localhost:8000/api/encode \
		-H "Content-Type: application/json" \
		-d '{"manufacturer":"Fujitsu","protocol":"fujitsu_ac","command":{"power":"on","mode":"cool","temperature":24,"fan":"auto","swing":"off"}}' \
		| python -m json.tool | head -15

deploy-dev:  ## Deploy to development environment (Stacktape - BLOCKED by minification issue)
	@echo "🚀 Deploying to development..."
	@echo "⚠️  WARNING: Stacktape deployment is blocked by python-minifier issue"
	@echo "ℹ️  Use 'make sam-deploy-dev' instead"
	stacktape deploy --projectName=maestro-tuya-ir --stage=dev --region=us-west-2 --aa aws-development

deploy-prod:  ## Deploy to production environment (Stacktape - BLOCKED by minification issue)
	@echo "🚀 Deploying to production..."
	@echo "⚠️  WARNING: Stacktape deployment is blocked by python-minifier issue"
	@echo "ℹ️  Use 'make sam-deploy-prod' instead"
	stacktape deploy --projectName=maestro-tuya-ir --stage=production --region=us-west-2 --aa aws-production

sam-build:  ## Build Lambda container image with AWS SAM
	@echo "🔨 Building Lambda container image..."
	sam build --use-container

sam-deploy-dev:  ## Deploy to AWS Lambda (development) using SAM
	@echo "🚀 Deploying to AWS Lambda (dev) via SAM..."
	sam deploy --stack-name maestro-ir-bridge-dev --region us-west-2 --no-confirm-changeset --capabilities CAPABILITY_IAM

sam-deploy-prod:  ## Deploy to AWS Lambda (production) using SAM
	@echo "🚀 Deploying to AWS Lambda (production) via SAM..."
	sam deploy --stack-name maestro-ir-bridge-prod --region us-west-2 --no-confirm-changeset --capabilities CAPABILITY_IAM

sam-local:  ## Run Lambda function locally with SAM
	@echo "🏠 Starting Lambda function locally..."
	sam local start-api --host 127.0.0.1 --port 3000

all: install test lint  ## Install, test, and lint

.DEFAULT_GOAL := help

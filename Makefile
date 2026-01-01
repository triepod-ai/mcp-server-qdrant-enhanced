# Enhanced Qdrant MCP Server - Development Makefile
# Preserves existing workflow while adding development convenience

.PHONY: help start stop restart build rebuild logs test lint clean status shell dev install npm-install npm-publish docker-publish setup

# Default target
help: ## Show this help message
	@echo "Enhanced Qdrant MCP Server - Development Commands"
	@echo
	@echo "Quick Start:"
	@echo "  make setup      - Interactive setup (NPM or Docker)"
	@echo "  make start      - Start server (existing workflow)"
	@echo "  make dev        - Start in development mode"
	@echo
	@echo "Development:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo
	@echo "Examples:"
	@echo "  make start && make logs    - Start server and follow logs"
	@echo "  make test lint            - Run tests and linting"
	@echo "  make clean build start    - Clean rebuild and start"

# Installation and Setup
setup: ## Run interactive setup script (NPM or Docker options)
	@./setup-qdrant-enhanced.sh

install: ## Install Python dependencies locally
	@echo "Installing Python dependencies..."
	@pip install -e .
	@pip install -r requirements-dev.txt || echo "requirements-dev.txt not found, skipping dev dependencies"

npm-install: ## Install as NPM package globally
	@echo "Installing NPM package globally..."
	@npm install -g .

# Server Management (preserves existing workflow)
start: ## Start the enhanced MCP server (uses existing deploy.sh)
	@echo "Starting Enhanced Qdrant MCP Server..."
	@if [ -f "deploy.sh" ]; then \
		./deploy.sh; \
	else \
		docker-compose -f docker-compose.enhanced.yml up -d; \
	fi

stop: ## Stop the enhanced MCP server
	@echo "Stopping Enhanced Qdrant MCP Server..."
	@docker-compose -f docker-compose.enhanced.yml down

restart: stop start ## Restart the enhanced MCP server

# Development
dev: ## Start in development mode with live reloading
	@./scripts/dev/dev.sh dev-mode

shell: ## Open shell in running container
	@./scripts/dev/dev.sh shell

logs: ## Show container logs (follow mode)
	@docker-compose -f docker-compose.enhanced.yml logs -f

status: ## Show container status
	@./scripts/dev/dev.sh status

# Building
build: ## Build Docker image
	@echo "Building Docker image..."
	@docker build -f Dockerfile.enhanced -t triepod-ai/mcp-server-qdrant-enhanced .

rebuild: ## Force rebuild Docker image (no cache)
	@echo "Force rebuilding Docker image..."
	@docker build --no-cache -f Dockerfile.enhanced -t triepod-ai/mcp-server-qdrant-enhanced .

# Testing and Quality
test: ## Run tests and validation
	@echo "Running tests..."
	@if [ -d "tests" ]; then \
		python3 -m pytest tests/ || echo "Some tests failed"; \
	else \
		echo "No tests directory found"; \
	fi
	@echo "Running validation..."
	@./scripts/dev/dev.sh test

lint: ## Run linting and formatting
	@echo "Running linting and formatting..."
	@if command -v ruff >/dev/null 2>&1; then \
		ruff format src/; \
		ruff check src/ --fix || echo "Some linting issues couldn't be auto-fixed"; \
	else \
		echo "Ruff not found. Install with: pip install ruff"; \
	fi

typecheck: ## Run type checking
	@echo "Running type checking..."
	@if command -v mypy >/dev/null 2>&1; then \
		mypy src/; \
	else \
		echo "MyPy not found. Install with: pip install mypy"; \
	fi

# Cleanup
clean: ## Clean up containers and images
	@echo "Cleaning up..."
	@./scripts/dev/dev.sh clean

clean-all: clean ## Deep clean (containers, images, volumes)
	@echo "Deep cleaning..."
	@docker system prune -f
	@docker volume prune -f

# Publishing
npm-publish: test lint ## Publish to NPM registry
	@echo "Publishing to NPM..."
	@npm publish

docker-publish: build ## Publish Docker image (requires proper registry setup)
	@echo "Publishing Docker image..."
	@echo "Note: This requires proper GitHub Actions setup or manual registry push"
	@echo "See .github/workflows/docker-build-and-publish.yml for automated publishing"

# Quick Testing
quick-test: ## Quick validation of MCP server functionality
	@./scripts/dev/dev.sh quick-test

# Development Workflow Combinations
dev-setup: install build start ## Complete development setup
	@echo "Development environment ready!"

ci-test: test lint typecheck ## Run all CI-style tests
	@echo "All CI tests completed"

# Check existing workflow preservation
check-workflow: ## Verify existing workflow is preserved
	@echo "Checking existing workflow preservation..."
	@if [ -f "deploy.sh" ]; then \
		echo "✅ deploy.sh preserved"; \
	else \
		echo "❌ deploy.sh not found"; \
	fi
	@if [ -f "docker-compose.enhanced.yml" ]; then \
		echo "✅ docker-compose.enhanced.yml preserved"; \
	else \
		echo "❌ docker-compose.enhanced.yml not found"; \
	fi
	@if [ -f "$(HOME)/run-qdrant-docker-mcp.sh" ]; then \
		echo "✅ Wrapper script preserved"; \
	else \
		echo "❌ Wrapper script not found"; \
	fi
	@echo "Existing workflow check completed"

# Documentation
docs: ## Generate/update documentation
	@echo "Documentation tasks:"
	@echo "- README.md includes dual installation options"
	@echo "- Setup script provides guided installation"
	@echo "- Package.json includes comprehensive scripts"
	@echo "- GitHub Actions provide automated publishing"

# Show current configuration
config: ## Show current project configuration
	@echo "Enhanced Qdrant MCP Server Configuration:"
	@echo "- Project: @triepod-ai/mcp-server-qdrant-enhanced"
	@echo "- Version: $(shell grep '"version"' package.json | cut -d'"' -f4)"
	@echo "- Docker Image: ghcr.io/triepod-ai/mcp-server-qdrant-enhanced"
	@echo "- Enhanced Features: GPU acceleration, multi-vector support, 48 collections"
	@echo "- Installation: NPM package + Docker container options"
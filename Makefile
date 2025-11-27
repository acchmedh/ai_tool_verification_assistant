.PHONY: help install install-dev test test-cov lint format type-check clean run setup

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies
	pip install -r requirements.txt

install-dev: ## Install development dependencies
	pip install -r requirements.txt
	pip install -e ".[dev]"

setup: ## Initial setup: create venv and install dependencies
	python -m venv venv
	@echo "Virtual environment created. Activate it with: source venv/bin/activate"
	@echo "Then run: make install-dev"

test: ## Run tests
	pytest

test-cov: ## Run tests with coverage
	pytest --cov=src --cov-report=term-missing --cov-report=html

lint: ## Run linters
	ruff check src/ tests/
	flake8 src/ tests/ || true

format: ## Format code with black and ruff
	black src/ tests/ main.py
	ruff format src/ tests/ main.py

type-check: ## Run type checking
	mypy src/

clean: ## Clean generated files
	find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} + 2>/dev/null || true
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf dist/
	rm -rf build/
	@echo "Cleanup complete"

run: ## Run the main application
	python main.py

check-all: lint type-check test ## Run all checks (lint, type-check, test)

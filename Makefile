.PHONY: help install install-dev lint format type-check clean run setup test-connection

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

lint: ## Run linters (src/, scripts/, main.py, test_connection.py)
	ruff check src/ scripts/ main.py test_connection.py

lint-fix: ## Run Ruff with auto-fix
	ruff check src/ scripts/ main.py test_connection.py --fix

format: ## Format code with black and ruff
	black src/ scripts/ main.py test_connection.py
	ruff format src/ scripts/ main.py test_connection.py

type-check: ## Run type checking
	mypy src/

clean: ## Clean generated files
	find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} + 2>/dev/null || true
	rm -rf dist/
	rm -rf build/
	@echo "Cleanup complete"

run: ## Run the main application
	python main.py

test-connection: ## Test OpenAI/LiteLLM connection
	python test_connection.py


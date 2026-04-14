.PHONY: help install test lint clean run

help:
	@echo "Lobster CLI - Available commands:"
	@echo "  make install    - Install dependencies"
	@echo "  make test       - Run tests"
	@echo "  make lint       - Run code linting"
	@echo "  make clean      - Clean build artifacts"
	@echo "  make run        - Run lobster CLI"
	@echo ""
	@echo "Lobster commands:"
	@echo "  lobster version - Show version"
	@echo "  lobster status  - Check service status"
	@echo "  lobster chat    - Chat with assistant"
	@echo "  lobster config  - Show configuration"

install:
	@echo "Installing dependencies..."
	uv pip install -e ".[dev]"

test:
	@echo "Running tests..."
	PYTHONPATH=src pytest tests/ -v

lint:
	@echo "Running code linting..."
	PYTHONPATH=src flake8 src/lobster --max-line-length=100
	PYTHONPATH=src black --check src/lobster

clean:
	@echo "Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

run:
	PYTHONPATH=src python -m lobster

version:
	PYTHONPATH=src python -m lobster version

status:
	PYTHONPATH=src python -m lobster status

config:
	PYTHONPATH=src python -m lobster config

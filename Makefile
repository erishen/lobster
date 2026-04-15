.PHONY: help install test lint clean

help:
	@echo "Lobster CLI - Available commands:"
	@echo ""
	@echo "Development:"
	@echo "  make install    - Install dependencies"
	@echo "  make test       - Run tests"
	@echo "  make lint       - Run code linting"
	@echo "  make clean      - Clean build artifacts"
	@echo ""
	@echo "Quick Commands:"
	@echo "  lobster ask \"问题\"      - 快速提问"
	@echo "  lobster query \"问题\"    - 快速查询"
	@echo "  lobster remember \"内容\" - 快速记忆"
	@echo "  lobster recall \"关键词\" - 快速回忆"
	@echo "  lobster status           - 快速状态检查"
	@echo ""
	@echo "Core Commands:"
	@echo "  lobster --help           - Show all commands"
	@echo "  lobster version          - Show version"
	@echo "  lobster config show      - Show configuration"
	@echo "  lobster chat -i          - Interactive chat mode"
	@echo "  lobster web              - Start Web UI"
	@echo ""
	@echo "Tools:"
	@echo "  lobster code --help      - Code analysis tools"
	@echo "  lobster data --help      - Data analysis tools"
	@echo "  lobster doc-tool --help  - Document tools"
	@echo "  lobster project --help   - Project management"
	@echo "  lobster util-tools --help- Utility tools"
	@echo "  lobster openclaw --help  - OpenClaw management"

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

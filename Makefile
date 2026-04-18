.PHONY: help install test lint clean serena-init serena-status serena-symbols serena-find rag-status

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
	@echo ""
	@echo "Serena Code Analysis:"
	@echo "  lobster serena init        - Initialize Serena for current project"
	@echo "  lobster serena status      - Check Serena status"
	@echo "  lobster serena symbols <file> - Get symbols overview"
	@echo "  lobster serena find <symbol>  - Find a symbol by name"
	@echo "  lobster serena search <pattern> - Search code with regex"
	@echo ""
	@echo "RAG Knowledge Base:"
	@echo "  lobster rag status       - Check knowledge base status"
	@echo "  lobster rag upload <file>- Upload document to knowledge base"
	@echo "  lobster rag ask <query>  - Query knowledge base"
	@echo "  lobster rag models       - List available models"

install:
	@echo "Installing dependencies..."
	@if command -v uv >/dev/null 2>&1; then \
		UV_HTTP_TIMEOUT=120 uv pip install -e ".[dev]" --user 2>/dev/null || \
		UV_HTTP_TIMEOUT=120 uv pip install -e ".[dev]"; \
	else \
		pip install -e ".[dev]" --user 2>/dev/null || \
		pip install -e ".[dev]"; \
	fi

test:
	@echo "Running tests..."
	PYTHONPATH=src pytest tests/ -v

lint:
	@echo "Running code linting..."
	@if command -v ruff >/dev/null 2>&1; then \
		ruff check src/lobster; \
	elif command -v flake8 >/dev/null 2>&1; then \
		flake8 src/lobster --max-line-length=100; \
	fi
	@if command -v black >/dev/null 2>&1; then \
		black --check src/lobster; \
	fi

clean:
	@echo "Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

# Serena Code Analysis
SERENA_PROJECT ?= $(PWD)
SERENA_FILE ?= src/lobster/core/config.py
SERENA_SYMBOL ?= LobsterConfig

serena-init:
	@echo "Initializing Serena for project: $(SERENA_PROJECT)"
	@PYTHONPATH=src python -c "from lobster.core.serena_client import get_serena_client; import json; client = get_serena_client(); result = client.initialize('$(SERENA_PROJECT)'); print(json.dumps(result, indent=2, ensure_ascii=False))"

serena-status:
	@echo "Checking Serena status..."
	@PYTHONPATH=src python -c "from lobster.core.serena_client import get_serena_client; import json; client = get_serena_client(); result = client.get_current_config(); print(json.dumps(result, indent=2, ensure_ascii=False))"

serena-symbols:
	@echo "Getting symbols overview for: $(SERENA_FILE)"
	@PYTHONPATH=src python -c "from lobster.core.serena_client import get_serena_client; import json; client = get_serena_client(); client.initialize('$(SERENA_PROJECT)'); result = client.get_symbols_overview('$(SERENA_FILE)', depth=1); print(json.dumps(result, indent=2, ensure_ascii=False) if isinstance(result, dict) else result)"

serena-find:
	@echo "Finding symbol: $(SERENA_SYMBOL)"
	@PYTHONPATH=src python -c "from lobster.core.serena_client import get_serena_client; import json; client = get_serena_client(); client.initialize('$(SERENA_PROJECT)'); result = client.find_symbol('$(SERENA_SYMBOL)'); print(json.dumps(result, indent=2, ensure_ascii=False))"

# RAG Knowledge Base
rag-status:
	@echo "Checking RAG knowledge base status..."
	@PYTHONPATH=src python -c "
import requests
try:
    r = requests.get('http://localhost:8000/health', timeout=5)
    print('RAG API: Running' if r.status_code == 200 else f'RAG API: Error {r.status_code}')
except:
    print('RAG API: Not running (start with: cd langchain-llm-toolkit && make api)')
"

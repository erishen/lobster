# 🦞 Lobster — OpenClaw Toolset

A CLI toolset providing callable tools for the OpenClaw assistant.

## ✨ Features

- 🔧 **Tool Registry** — Standardized tool interface
- 🚀 **API Server** — REST API for OpenClaw integration
- 📋 **OpenAI Function Calling** — Compatible function call format
- 🎯 **Simple Commands** — Easy CLI structure
- 📦 **Modern Stack** — Click, Pydantic, Rich, LiteLLM

## 🚀 Quick Start

### Installation

```bash
# Clone
git clone <repository-url>
cd lobster

# Install base dependencies
make install
# or
uv pip install -e ".[dev]"

# Optional extras
pip install -e ".[api]"          # API server
pip install -e ".[serena]"       # Serena code analysis
pip install -e ".[investment]"   # Investment tools
pip install -e ".[all]"          # Everything
```

### Basic Usage

```bash
# Help
lobster --help

# Quick commands
lobster ask "your question"
lobster remember "something to remember"
lobster recall "keyword"

# Interactive chat
lobster chat -i

# Launch Web UI
lobster web
```

## 🔗 OpenClaw Integration

### Start API Server

```bash
lobster api serve
lobster api serve -p 8080
```

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/tools` | GET | List all available tools |
| `/tools/openai` | GET | OpenAI Function Calling format |
| `/tools/{name}` | GET | Get tool details |
| `/tools/{name}/execute` | POST | Execute tool |

### OpenClaw Example

```python
import requests

response = requests.get("http://localhost:8000/tools")
tools = response.json()["tools"]

result = requests.post(
    "http://localhost:8000/tools/ask/execute",
    json={"question": "What is Python?"}
)
print(result.json())
```

### Available Tools

| Tool | Category | Description |
|------|----------|-------------|
| `ask` | ai | Ask AI and get answer |
| `remember` | memory | Store information to memory |
| `recall` | memory | Search memory |
| `search` | search | Global search across memory, history, projects |
| `code_analyze` | code | Analyze code files |
| `data_analyze` | data | Analyze data files |
| `notify` | system | Send system notification |
| `execute_command` | system | Execute system command |

### OpenAI Function Calling

```bash
curl http://localhost:8000/tools/openai
```

```json
{
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "ask",
        "description": "Ask AI and get answer",
        "parameters": {
          "type": "object",
          "properties": {
            "question": {"type": "string", "description": "Question to ask"},
            "model": {"type": "string", "default": "ollama/gemma3"}
          },
          "required": ["question"]
        }
      }
    }
  ]
}
```

## 📖 Command Reference

### Quick Commands

| Command | Description |
|---------|-------------|
| `lobster ask "question"` | Quick question |
| `lobster remember "content"` | Quick memorize |
| `lobster recall "keyword"` | Quick recall |
| `lobster status` | Quick status check |

### Core Commands

| Command | Description |
|---------|-------------|
| `lobster chat` | Chat mode |
| `lobster api` | API server |
| `lobster config` | Config management |
| `lobster memory` | Memory management |
| `lobster search` | Global search |

### Tool Commands

| Command | Description |
|---------|-------------|
| `lobster code` | Code analysis |
| `lobster data` | Data analysis |
| `lobster project` | Project management |
| `lobster notify` | System notification |

### Advanced Commands

| Command | Description |
|---------|-------------|
| `lobster datax` | Data export/import |
| `lobster scheduler` | Scheduled tasks |
| `lobster webhook` | Webhook management |
| `lobster watch` | File monitoring |
| `lobster client` | API client |

## 🛠️ Development

### Project Structure

```
lobster/
├── src/lobster/
│   ├── commands/     # Command modules
│   ├── core/         # Core functionality
│   │   ├── tools.py  # Tool registry
│   │   ├── llm_client.py
│   │   └── memory_store.py
│   └── web/          # Web UI
├── tests/            # Test files
└── pyproject.toml    # Project config
```

### Development Commands

```bash
make install    # Install deps
make test       # Run tests
make lint       # Lint code
```

### Adding a New Tool

In `src/lobster/core/tools.py`:

```python
self.register(Tool(
    name="my_tool",
    description="Tool description",
    parameters={
        "type": "object",
        "properties": {
            "input": {"type": "string", "description": "Input parameter"}
        },
        "required": ["input"]
    },
    handler=self._handle_my_tool,
    category="custom"
))
```

## 🔧 Configuration

### Environment Variables

```bash
export OPENCLAW_URL="http://localhost:8000"
export OPENCLAW_API_KEY="your-api-key"
```

### Config File (`~/.lobster/config.json`)

```json
{
  "service_url": "http://localhost:8000",
  "api_key": "your-api-key"
}
```

## 📦 Dependencies

### Core
- `click` — CLI framework
- `pydantic` — Data validation
- `rich` — Terminal formatting
- `litellm` — LLM integration

### Optional
- `fastapi`, `uvicorn` — API server
- `streamlit` — Web UI
- `watchdog` — File monitoring
- `requests` — HTTP client

## 📝 License

MIT License

---

**Lobster** — Toolset for the OpenClaw assistant! 🦞

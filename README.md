# 🦞 Lobster - OpenClaw Assistant CLI Tool

A modern, extensible command-line interface for the OpenClaw Lobster Assistant service.

## ✨ Features

- 🎯 **Simple Commands** - Easy-to-use command structure
- 🔌 **Plugin System** - Extensible architecture for custom functionality
- ⚙️ **Configuration Management** - Flexible configuration options
- 🎨 **Beautiful Output** - Rich terminal output with colors and formatting
- 📦 **Modern Stack** - Built with Click, Pydantic, and Rich

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
cd /REDACTED/

# Install dependencies
make install
# or
uv pip install -e ".[dev]"
```

### Basic Usage

```bash
# Show help
make run
# or
PYTHONPATH=src python -m lobster --help

# Show version
make version
# or
PYTHONPATH=src python -m lobster version

# Check service status
make status
# or
PYTHONPATH=src python -m lobster status

# Chat with assistant
PYTHONPATH=src python -m lobster chat "你好"

# Show configuration
make config
# or
PYTHONPATH=src python -m lobster config
```

## 📖 Available Commands

### `lobster version`
Show the current version of Lobster CLI.

```bash
$ lobster version
Lobster CLI version 0.1.0
```

### `lobster status`
Check the status of the OpenClaw service.

```bash
$ lobster status
Checking OpenClaw service status...
✓ Service is running (mock status)
```

### `lobster chat <message>`
Send a message to the OpenClaw assistant.

```bash
$ lobster chat "你好"
Sending message to OpenClaw: 你好
Assistant response: Hello! I'm Lobster, your assistant. (mock response)
```

### `lobster config`
Show current configuration settings.

```bash
$ lobster config
Current OpenClaw configuration:
  Service URL: http://localhost:8000
  API Key: ********
  Timeout: 30s
```

## 🛠️ Development

### Project Structure

```
lobster/
├── src/
│   └── lobster/          # Main package
│       ├── __init__.py
│       ├── __main__.py   # CLI entry point
│       ├── commands/     # Command modules
│       ├── core/         # Core functionality
│       └── plugins/      # Plugin directory
├── tests/                # Test files
├── pyproject.toml        # Project configuration
├── Makefile             # Build commands
└── README.md            # This file
```

### Development Commands

```bash
# Install development dependencies
make install

# Run tests
make test

# Run linting
make lint

# Clean build artifacts
make clean
```

### Adding New Commands

1. Create a new command module in `src/lobster/commands/`
2. Import and register the command in `__main__.py`
3. Add tests in `tests/`

Example:

```python
# src/lobster/commands/custom.py
import click

@click.command()
def custom():
    """Custom command description"""
    click.echo("Custom command executed!")
```

```python
# src/lobster/__main__.py
from lobster.commands.custom import custom

cli.add_command(custom)
```

## 🔧 Configuration

Configuration can be set via:

1. **Environment Variables**
   ```bash
   export OPENCLAW_URL="http://localhost:8000"
   export OPENCLAW_API_KEY="your-api-key"
   export OPENCLAW_TIMEOUT="30"
   ```

2. **Configuration File** (`~/.lobster/config.json`)
   ```json
   {
     "service_url": "http://localhost:8000",
     "api_key": "your-api-key",
     "timeout": 30
   }
   ```

3. **.env File**
   ```bash
   OPENCLAW_URL=http://localhost:8000
   OPENCLAW_API_KEY=your-api-key
   OPENCLAW_TIMEOUT=30
   ```

## 🔌 Plugin Development

Lobster supports a plugin system for extending functionality.

### Creating a Plugin

1. Create a plugin directory in `~/.lobster/plugins/`
2. Add a `plugin.py` file with your commands
3. Lobster will automatically discover and load the plugin

Example plugin:

```python
# ~/.lobster/plugins/my_plugin/plugin.py
import click

@click.command()
def my_command():
    """My custom command"""
    click.echo("My plugin command!")
```

## 📦 Dependencies

### Core Dependencies
- `click` - CLI framework
- `pydantic` - Data validation
- `pydantic-settings` - Settings management
- `rich` - Terminal formatting
- `python-dotenv` - Environment variable loading

### Development Dependencies
- `pytest` - Testing framework
- `black` - Code formatting
- `flake8` - Code linting
- `mypy` - Type checking

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- Built with [Click](https://click.palletsprojects.com/)
- Inspired by modern CLI tools
- Part of the OpenClaw ecosystem

---

**Lobster** - Making OpenClaw interactions simple and powerful! 🦞

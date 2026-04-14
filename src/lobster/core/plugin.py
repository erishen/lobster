"""Plugin system for Lobster CLI"""

import importlib.util
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from rich.console import Console
from rich.table import Table

console = Console()


class Plugin:
    """Base class for plugins"""

    def __init__(self, name: str, version: str = "1.0.0", description: str = ""):
        self.name = name
        self.version = version
        self.description = description
        self.commands = []

    def register_command(self, command):
        """Register a CLI command"""
        self.commands.append(command)

    def get_info(self) -> Dict[str, Any]:
        """Get plugin information"""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "commands": len(self.commands),
        }


class PluginManager:
    """Plugin manager for Lobster CLI"""

    def __init__(self):
        self.plugins_dir = Path.home() / ".lobster" / "plugins"
        self.plugins_dir.mkdir(parents=True, exist_ok=True)
        self.plugins: Dict[str, Plugin] = {}
        self._load_plugins()

    def _load_plugins(self):
        """Load all plugins from plugins directory"""
        if not self.plugins_dir.exists():
            return

        for plugin_dir in self.plugins_dir.iterdir():
            if plugin_dir.is_dir():
                plugin_file = plugin_dir / "plugin.py"
                if plugin_file.exists():
                    try:
                        self._load_plugin(plugin_dir.name, plugin_file)
                    except Exception as e:
                        console.print(f"[red]Error loading plugin {plugin_dir.name}:[/] {str(e)}")

    def _load_plugin(self, plugin_name: str, plugin_file: Path):
        """Load a single plugin"""
        spec = importlib.util.spec_from_file_location(plugin_name, plugin_file)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            sys.modules[plugin_name] = module
            spec.loader.exec_module(module)

            if hasattr(module, "plugin"):
                plugin_instance = module.plugin
                if isinstance(plugin_instance, Plugin):
                    self.plugins[plugin_name] = plugin_instance

    def get_plugin(self, name: str) -> Optional[Plugin]:
        """Get a plugin by name"""
        return self.plugins.get(name)

    def list_plugins(self) -> List[Dict[str, Any]]:
        """List all loaded plugins"""
        return [plugin.get_info() for plugin in self.plugins.values()]

    def create_plugin_template(self, name: str):
        """Create a plugin template"""
        plugin_dir = self.plugins_dir / name
        plugin_dir.mkdir(parents=True, exist_ok=True)

        plugin_code = f'''"""Plugin: {name}"""

from lobster.core.plugin import Plugin
import click

plugin = Plugin(
    name="{name}",
    version="1.0.0",
    description="A custom plugin for Lobster CLI"
)


@plugin.register_command
@click.command()
def {name}_command():
    """Custom command from {name} plugin"""
    click.echo("Hello from {name} plugin!")
'''

        plugin_file = plugin_dir / "plugin.py"
        with open(plugin_file, "w") as f:
            f.write(plugin_code)

        console.print(f"[green]✓[/] Created plugin template: {name}")
        console.print(f"[dim]Location: {plugin_dir}[/]")
        console.print("[dim]Edit the plugin.py file to customize your plugin[/]")

    def show_plugins(self):
        """Show all loaded plugins"""
        if not self.plugins:
            console.print("[yellow]No plugins loaded[/]")
            return

        table = Table(title="Loaded Plugins")
        table.add_column("Name", style="cyan")
        table.add_column("Version", style="green")
        table.add_column("Description", style="yellow")
        table.add_column("Commands", style="magenta")

        for plugin_info in self.list_plugins():
            table.add_row(
                plugin_info["name"],
                plugin_info["version"],
                plugin_info["description"],
                str(plugin_info["commands"]),
            )

        console.print(table)

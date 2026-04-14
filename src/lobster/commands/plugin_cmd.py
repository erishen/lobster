"""Plugin management commands"""

import click
from rich.console import Console

console = Console()


@click.group()
def plugin():
    """Plugin management commands"""
    pass


@plugin.command()
def list():
    """List all loaded plugins"""
    from lobster.core.plugin import PluginManager

    manager = PluginManager()
    manager.show_plugins()


@plugin.command()
@click.argument("name")
def create(name):
    """Create a new plugin template"""
    from lobster.core.plugin import PluginManager

    manager = PluginManager()
    manager.create_plugin_template(name)


@plugin.command()
@click.argument("name")
def info(name):
    """Show plugin information"""
    from lobster.core.plugin import PluginManager

    manager = PluginManager()
    plugin_instance = manager.get_plugin(name)

    if not plugin_instance:
        console.print(f"[red]Error:[/] Plugin '{name}' not found")
        return

    info = plugin_instance.get_info()

    console.print(f"[bold cyan]Plugin: {info['name']}[/]")
    console.print(f"[green]Version:[/] {info['version']}")
    console.print(f"[yellow]Description:[/] {info['description']}")
    console.print(f"[magenta]Commands:[/] {info['commands']}")


@plugin.command()
def path():
    """Show plugins directory path"""
    try:
        from lobster.core.plugin import PluginManager

        manager = PluginManager()
        console.print(f"[bold cyan]Plugins directory:[/] {manager.plugins_dir}")
        console.print("[dim]Place your plugins in this directory[/]")
    except Exception as e:
        console.print(f"[red]Error:[/] {str(e)}")

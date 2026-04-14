"""Configuration management commands"""

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


@click.group()
def config_cmd():
    """Configuration management commands"""
    pass


@config_cmd.command()
def show():
    """Show current configuration"""
    from lobster.core.config import ConfigManager
    
    manager = ConfigManager()
    config = manager.show()
    
    console.print("[bold cyan]Current Lobster Configuration[/]")
    
    table = Table()
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    
    for key, value in config.items():
        if 'api_key' in key.lower() and value:
            value = "********"  # Hide API keys
        table.add_row(key, str(value))
    
    console.print(table)


@config_cmd.command()
@click.argument('key')
@click.argument('value')
def set(key, value):
    """Set a configuration value"""
    from lobster.core.config import ConfigManager
    
    manager = ConfigManager()
    
    # Convert value to appropriate type
    if value.lower() in ['true', 'false']:
        value = value.lower() == 'true'
    elif value.isdigit():
        value = int(value)
    elif value.replace('.', '').isdigit():
        value = float(value)
    
    try:
        manager.set(key, value)
        console.print(f"[green]✓[/] Configuration updated: {key} = {value}")
    except Exception as e:
        console.print(f"[red]Error:[/] {str(e)}")


@config_cmd.command()
@click.argument('key')
def get(key):
    """Get a configuration value"""
    from lobster.core.config import ConfigManager
    
    manager = ConfigManager()
    value = manager.get(key)
    
    if value is None:
        console.print(f"[yellow]Configuration key '{key}' not found[/]")
    else:
        if 'api_key' in key.lower():
            value = "********"
        console.print(Panel(f"{value}", title=f"[bold cyan]{key}[/]", border_style="cyan"))


@config_cmd.command()
def reset():
    """Reset configuration to defaults"""
    from lobster.core.config import ConfigManager
    
    manager = ConfigManager()
    manager.reset()
    console.print("[green]✓[/] Configuration reset to defaults")


@config_cmd.command()
def path():
    """Show configuration file path"""
    from lobster.core.config import ConfigManager
    
    manager = ConfigManager()
    console.print(f"[bold cyan]Configuration file:[/] {manager.config_file}")
    console.print(f"[bold cyan]Configuration directory:[/] {manager.config_dir}")

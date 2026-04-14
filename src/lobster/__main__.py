#!/usr/bin/env python3
"""Lobster - OpenClaw Assistant CLI Tool"""

import click
from rich.console import Console

VERSION = "0.1.0"
console = Console()


@click.group()
@click.version_option(version=VERSION, prog_name="lobster")
def cli():
    """🦞 Lobster - OpenClaw Assistant CLI Tool
    
    A modern, extensible command-line interface for the OpenClaw Lobster Assistant service.
    """
    pass


@cli.command()
def version():
    """Show version information"""
    console.print(f"[bold cyan]Lobster CLI[/] version [green]{VERSION}[/]")


@cli.command()
def status():
    """Check the status of the OpenClaw service"""
    console.print("[bold blue]Checking OpenClaw service status...[/]")
    console.print("[green]✓[/] Service is running (mock status)")


@cli.command()
@click.argument('message')
def chat(message):
    """Send a message to the OpenClaw assistant"""
    console.print(f"[bold blue]Sending message to OpenClaw:[/] {message}")
    console.print(f"[bold green]Assistant response:[/] Hello! I'm Lobster, your assistant. (mock response)")


@cli.command()
def config():
    """Show current configuration"""
    console.print("[bold cyan]Current OpenClaw configuration:[/]")
    
    from rich.table import Table
    table = Table()
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Service URL", "http://localhost:8000")
    table.add_row("API Key", "********")
    table.add_row("Timeout", "30s")
    table.add_row("Default Model", "ollama/gemma3")
    
    console.print(table)


from lobster.commands.document import doc
from lobster.commands.llm import llm
from lobster.commands.rag import rag

cli.add_command(doc)
cli.add_command(llm)
cli.add_command(rag)


def main():
    """Main entry point"""
    cli()


if __name__ == "__main__":
    main()

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


from lobster.commands.document import doc
from lobster.commands.llm import llm
from lobster.commands.rag import rag
from lobster.commands.config_cmd import config_cmd
from lobster.commands.batch import batch
from lobster.commands.plugin_cmd import plugin
from lobster.commands.util import util
from lobster.commands.model import model
from lobster.commands.template import template
from lobster.commands.doctor import doctor

cli.add_command(doc)
cli.add_command(llm)
cli.add_command(rag)
cli.add_command(config_cmd, name="config")
cli.add_command(batch)
cli.add_command(plugin)
cli.add_command(util)
cli.add_command(model)
cli.add_command(template)
cli.add_command(doctor)


def main():
    """Main entry point"""
    cli()


if __name__ == "__main__":
    main()

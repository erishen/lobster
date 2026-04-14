"""Model management commands for Ollama models"""

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import requests

console = Console()

OLLAMA_BASE_URL = "http://localhost:11434"


@click.group()
def model():
    """Model management commands"""
    pass


@model.command()
def list():
    """List all installed Ollama models"""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        response.raise_for_status()

        data = response.json()
        models = data.get("models", [])

        if not models:
            console.print("[yellow]No models installed[/]")
            return

        table = Table(title="Installed Ollama Models")
        table.add_column("Name", style="cyan")
        table.add_column("Size", style="green")
        table.add_column("Modified", style="yellow")
        table.add_column("ID", style="magenta")

        for model in models:
            name = model.get("name", "unknown")
            size = model.get("size", 0)
            modified = model.get("modified_at", "unknown")
            model_id = model.get("digest", "unknown")[:12]

            size_str = (
                f"{size / 1024 / 1024 / 1024:.2f} GB"
                if size > 1024 * 1024 * 1024
                else f"{size / 1024 / 1024:.2f} MB"
            )

            table.add_row(name, size_str, modified[:10], model_id)

        console.print(table)

        total_size = sum(m.get("size", 0) for m in models)
        console.print(
            f"\n[dim]Total: {len(models)} models, {total_size / 1024 / 1024 / 1024:.2f} GB[/]"
        )

    except requests.exceptions.ConnectionError:
        console.print("[red]Error:[/] Cannot connect to Ollama. Is it running?")
        console.print("[yellow]Start Ollama with:[/] ollama serve")
    except Exception as e:
        console.print(f"[red]Error:[/] {str(e)}")


@model.command()
@click.argument("model_name")
def pull(model_name):
    """Pull a model from Ollama registry"""
    console.print(f"[bold blue]Pulling model:[/] {model_name}")
    console.print("[dim]This may take a while...[/]")

    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/pull", json={"name": model_name}, stream=True, timeout=300
        )

        for line in response.iter_lines():
            if line:
                data = line.decode("utf-8")
                console.print(f"[dim]{data}[/]")

        console.print(f"[green]✓[/] Model {model_name} pulled successfully")

    except requests.exceptions.ConnectionError:
        console.print("[red]Error:[/] Cannot connect to Ollama. Is it running?")
    except Exception as e:
        console.print(f"[red]Error pulling model:[/] {str(e)}")


@model.command()
@click.argument("model_name")
def rm(model_name):
    """Remove a model"""
    if not click.confirm(f"Are you sure you want to remove model '{model_name}'?"):
        console.print("[yellow]Cancelled[/]")
        return

    try:
        response = requests.delete(
            f"{OLLAMA_BASE_URL}/api/delete", json={"name": model_name}, timeout=10
        )

        if response.status_code == 200:
            console.print(f"[green]✓[/] Model {model_name} removed successfully")
        else:
            console.print("[red]Error:[/] Failed to remove model")

    except requests.exceptions.ConnectionError:
        console.print("[red]Error:[/] Cannot connect to Ollama. Is it running?")
    except Exception as e:
        console.print(f"[red]Error removing model:[/] {str(e)}")


@model.command()
@click.argument("model_name")
def info(model_name):
    """Show model information"""
    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/show", json={"name": model_name}, timeout=10
        )

        if response.status_code == 200:
            data = response.json()

            console.print(
                Panel(
                    f"[bold cyan]Model:[/] {model_name}\n"
                    f"[bold green]License:[/] {data.get('license', 'N/A')}\n"
                    f"[bold yellow]Modelfile:[/]\n{data.get('modelfile', 'N/A')}",
                    title="Model Information",
                    border_style="cyan",
                )
            )

            if "parameters" in data:
                console.print("\n[bold magenta]Parameters:[/]")
                console.print(data["parameters"])

        else:
            console.print("[red]Error:[/] Model not found")

    except requests.exceptions.ConnectionError:
        console.print("[red]Error:[/] Cannot connect to Ollama. Is it running?")
    except Exception as e:
        console.print(f"[red]Error getting model info:[/] {str(e)}")


@model.command()
@click.argument("model_name")
def copy(model_name):
    """Copy a model to a new name"""
    new_name = click.prompt("Enter new model name")

    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/copy",
            json={"source": model_name, "destination": new_name},
            timeout=10,
        )

        if response.status_code == 200:
            console.print(f"[green]✓[/] Model copied from {model_name} to {new_name}")
        else:
            console.print("[red]Error:[/] Failed to copy model")

    except requests.exceptions.ConnectionError:
        console.print("[red]Error:[/] Cannot connect to Ollama. Is it running?")
    except Exception as e:
        console.print(f"[red]Error copying model:[/] {str(e)}")


@model.command()
def ps():
    """Show running models"""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/ps", timeout=5)
        response.raise_for_status()

        data = response.json()
        models = data.get("models", [])

        if not models:
            console.print("[yellow]No models currently running[/]")
            return

        table = Table(title="Running Models")
        table.add_column("Name", style="cyan")
        table.add_column("Size", style="green")
        table.add_column("VRAM", style="yellow")
        table.add_column("Until", style="magenta")

        for model in models:
            name = model.get("name", "unknown")
            size = model.get("size", 0)
            vram = model.get("size_vram", 0)
            until = model.get("expires_at", "unknown")

            size_str = (
                f"{size / 1024 / 1024 / 1024:.2f} GB"
                if size > 1024 * 1024 * 1024
                else f"{size / 1024 / 1024:.2f} MB"
            )
            vram_str = (
                f"{vram / 1024 / 1024 / 1024:.2f} GB"
                if vram > 1024 * 1024 * 1024
                else f"{vram / 1024 / 1024:.2f} MB"
            )

            table.add_row(name, size_str, vram_str, until[:19] if until != "unknown" else until)

        console.print(table)

    except requests.exceptions.ConnectionError:
        console.print("[red]Error:[/] Cannot connect to Ollama. Is it running?")
    except Exception as e:
        console.print(f"[red]Error:[/] {str(e)}")


@model.command()
def popular():
    """Show popular Ollama models"""
    console.print("[bold blue]Popular Ollama Models[/]")

    table = Table(title="Recommended Models")
    table.add_column("Model", style="cyan")
    table.add_column("Size", style="green")
    table.add_column("Description", style="yellow")

    models = [
        ("gemma3:latest", "~2B", "Google's Gemma 3 - Fast and efficient"),
        ("llama3.1:8b", "~8B", "Meta's Llama 3.1 - Balanced performance"),
        ("deepseek-r1:7b", "~7B", "DeepSeek R1 - Strong reasoning"),
        ("qwen2.5:7b", "~7B", "Alibaba's Qwen 2.5 - Multilingual"),
        ("mistral:7b", "~7B", "Mistral AI - High quality"),
        ("codellama:7b", "~7B", "Meta's Code Llama - Code generation"),
        ("phi3:mini", "~3.8B", "Microsoft Phi-3 - Compact and fast"),
        ("neural-chat:7b", "~7B", "Intel Neural Chat - Conversational"),
    ]

    for name, size, desc in models:
        table.add_row(name, size, desc)

    console.print(table)

    console.print("\n[bold yellow]To pull a model:[/] lobster model pull <model-name>")
    console.print("[dim]Example: lobster model pull llama3.1:8b[/]")

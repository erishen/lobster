"""System diagnostics commands"""

import click
from rich.console import Console
from rich.table import Table
import sys
import platform
import subprocess

console = Console()


@click.group()
def doctor():
    """System diagnostics and troubleshooting commands"""
    pass


@doctor.command()
def check():
    """Run comprehensive system check"""
    console.print("[bold blue]Running system diagnostics...[/]\n")

    checks = []

    # Python check
    checks.append(check_python())

    # Dependencies check
    checks.extend(check_dependencies())

    # Ollama check
    checks.append(check_ollama())

    # Environment check
    checks.append(check_environment())

    # Display results
    table = Table(title="System Check Results")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Details", style="yellow")

    for check in checks:
        table.add_row(check["component"], check["status"], check["details"])

    console.print(table)

    # Summary
    passed = sum(1 for c in checks if c["status"] == "✓")
    total = len(checks)

    if passed == total:
        console.print(f"\n[green]✓ All checks passed ({passed}/{total})[/]")
    else:
        console.print(f"\n[yellow]⚠ {total - passed} check(s) failed[/]")


def check_python():
    """Check Python installation"""
    version = sys.version_info
    return {
        "component": "Python",
        "status": "✓" if version >= (3, 10) else "✗",
        "details": f"{version.major}.{version.minor}.{version.micro}",
    }


def check_dependencies():
    """Check required dependencies"""
    checks = []

    dependencies = [
        ("click", "Click", "CLI framework"),
        ("rich", "Rich", "Terminal output"),
        ("pydantic", "Pydantic", "Data validation"),
        ("requests", "Requests", "HTTP client"),
        ("litellm", "LiteLLM", "LLM integration"),
    ]

    for module, name, desc in dependencies:
        try:
            mod = __import__(module)
            version = getattr(mod, "__version__", "installed")
            checks.append({"component": name, "status": "✓", "details": f"v{version}"})
        except ImportError:
            checks.append({"component": name, "status": "✗", "details": "Not installed"})

    return checks


def check_ollama():
    """Check Ollama installation"""
    try:
        import requests

        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            models = response.json().get("models", [])
            return {
                "component": "Ollama",
                "status": "✓",
                "details": f"{len(models)} models available",
            }
        else:
            return {"component": "Ollama", "status": "⚠", "details": "Not responding correctly"}
    except Exception:
        return {"component": "Ollama", "status": "✗", "details": "Not running"}


def check_environment():
    """Check environment variables"""
    import os

    api_keys = {
        "OPENAI_API_KEY": "OpenAI",
        "ANTHROPIC_API_KEY": "Anthropic",
        "GOOGLE_API_KEY": "Google",
    }

    configured = []
    for key, name in api_keys.items():
        if os.getenv(key):
            configured.append(name)

    if configured:
        return {
            "component": "API Keys",
            "status": "✓",
            "details": f"{', '.join(configured)} configured",
        }
    else:
        return {
            "component": "API Keys",
            "status": "⚠",
            "details": "No API keys configured (optional)",
        }


@doctor.command()
def info():
    """Show system information"""
    table = Table(title="System Information")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")

    info_items = [
        ("OS", f"{platform.system()} {platform.release()}"),
        ("Architecture", platform.machine()),
        ("Python Version", sys.version.split()[0]),
        ("Python Path", sys.executable),
        ("Working Directory", sys.path[0] if sys.path else "N/A"),
        ("Platform", platform.platform()),
        ("Processor", platform.processor() or "Unknown"),
    ]

    for prop, value in info_items:
        table.add_row(prop, value)

    console.print(table)


@doctor.command()
def deps():
    """Show all installed dependencies"""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "list", "--format=json"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode == 0:
            import json

            packages = json.loads(result.stdout)

            table = Table(title="Installed Packages")
            table.add_column("Package", style="cyan")
            table.add_column("Version", style="green")

            for pkg in sorted(packages, key=lambda x: x["name"]):
                table.add_row(pkg["name"], pkg["version"])

            console.print(table)
            console.print(f"\n[dim]Total: {len(packages)} packages[/]")
        else:
            console.print("[red]Error:[/] Failed to list packages")

    except Exception as e:
        console.print(f"[red]Error:[/] {str(e)}")


@doctor.command()
def fix():
    """Attempt to fix common issues"""
    console.print("[bold blue]Attempting to fix common issues...[/]\n")

    issues_fixed = []

    # Check and create config directory
    from pathlib import Path

    config_dir = Path.home() / ".lobster"
    if not config_dir.exists():
        config_dir.mkdir(parents=True, exist_ok=True)
        issues_fixed.append("Created config directory")

    # Check and create templates directory
    templates_dir = config_dir / "templates"
    if not templates_dir.exists():
        templates_dir.mkdir(parents=True, exist_ok=True)
        issues_fixed.append("Created templates directory")

    # Check and create plugins directory
    plugins_dir = config_dir / "plugins"
    if not plugins_dir.exists():
        plugins_dir.mkdir(parents=True, exist_ok=True)
        issues_fixed.append("Created plugins directory")

    if issues_fixed:
        console.print("[green]✓ Fixed issues:[/]")
        for issue in issues_fixed:
            console.print(f"  • {issue}")
    else:
        console.print("[green]✓ No issues found[/]")


@doctor.command()
def logs():
    """Show recent logs (if available)"""
    from pathlib import Path

    log_locations = [
        Path.home() / ".lobster" / "lobster.log",
        Path.home() / ".ollama" / "logs" / "server.log",
    ]

    found_logs = []

    for log_path in log_locations:
        if log_path.exists():
            found_logs.append(log_path)

    if not found_logs:
        console.print("[yellow]No log files found[/]")
        return

    for log_file in found_logs:
        console.print(f"\n[bold cyan]Log: {log_file}[/]")

        try:
            with open(log_file, "r", encoding="utf-8") as f:
                lines = f.readlines()

                # Show last 20 lines
                for line in lines[-20:]:
                    console.print(line.rstrip())

        except Exception as e:
            console.print(f"[red]Error reading log:[/] {str(e)}")

"""Conversation history management commands"""

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from datetime import datetime
from pathlib import Path
import json

console = Console()

HISTORY_DIR = Path.cwd() / ".lobster_history"


def ensure_history_dir():
    """Ensure history directory exists"""
    try:
        HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        console.print("[red]Error:[/] Permission denied creating history directory")
        console.print(f"[yellow]Please check permissions for:[/] {HISTORY_DIR}")
        raise


def save_conversation(conversation_data):
    """Save a conversation to history"""
    ensure_history_dir()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"conversation_{timestamp}.json"
    filepath = HISTORY_DIR / filename

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(conversation_data, f, ensure_ascii=False, indent=2)

    return filename


def load_conversation(filename):
    """Load a conversation from history"""
    filepath = HISTORY_DIR / filename

    if not filepath.exists():
        return None

    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def list_conversations():
    """List all saved conversations"""
    if not HISTORY_DIR.exists():
        return []

    conversations = []
    for file in HISTORY_DIR.glob("conversation_*.json"):
        try:
            data = load_conversation(file.name)
            if data:
                conversations.append(
                    {
                        "filename": file.name,
                        "timestamp": data.get("timestamp", "Unknown"),
                        "message_count": len(data.get("messages", [])),
                        "preview": data.get("messages", [{}])[0].get("content", "")[:50]
                        if data.get("messages")
                        else "",
                    }
                )
        except Exception:
            continue

    return sorted(conversations, key=lambda x: x["timestamp"], reverse=True)


@click.group()
def history():
    """Conversation history management"""
    pass


@history.command()
def list():
    """List all saved conversations"""
    try:
        conversations = list_conversations()

        if not conversations:
            console.print("[yellow]No conversation history found[/]")
            console.print("[dim]Conversations are saved when using interactive chat mode[/]")
            return

        console.print(f"[bold blue]Conversation History ({len(conversations)} found)[/]\n")

        table = Table()
        table.add_column("Index", style="cyan", width=6)
        table.add_column("Timestamp", style="blue", width=19)
        table.add_column("Messages", style="green", width=8)
        table.add_column("Preview", style="yellow")

        for i, conv in enumerate(conversations, 1):
            timestamp = conv["timestamp"][:19] if len(conv["timestamp"]) > 19 else conv["timestamp"]
            table.add_row(
                str(i), timestamp, str(conv["message_count"]), conv["preview"] + "..."
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error listing conversations:[/] {str(e)}")


@history.command()
@click.argument("index", type=int)
def show(index):
    """Show a specific conversation by index"""
    try:
        conversations = list_conversations()

        if not conversations:
            console.print("[yellow]No conversation history found[/]")
            return

        if index < 1 or index > len(conversations):
            console.print(f"[red]Error:[/] Invalid index. Use 'lobster history list' to see available conversations")
            return

        conv = conversations[index - 1]
        data = load_conversation(conv["filename"])

        if not data:
            console.print("[red]Error:[/] Failed to load conversation")
            return

        console.print(
            Panel(
                f"[bold cyan]Conversation[/]\n"
                f"Timestamp: {data.get('timestamp', 'Unknown')}\n"
                f"Messages: {len(data.get('messages', []))}",
                border_style="cyan",
            )
        )
        console.print()

        for msg in data.get("messages", []):
            role = msg.get("role", "unknown")
            content = msg.get("content", "")

            if role == "user":
                console.print(f"[bold blue]You:[/] {content}")
            else:
                console.print(f"[bold green]Assistant:[/] {content}")
            console.print()

    except Exception as e:
        console.print(f"[red]Error showing conversation:[/] {str(e)}")


@history.command()
@click.argument("index", type=int)
def delete(index):
    """Delete a specific conversation by index"""
    try:
        conversations = list_conversations()

        if not conversations:
            console.print("[yellow]No conversation history found[/]")
            return

        if index < 1 or index > len(conversations):
            console.print(f"[red]Error:[/] Invalid index")
            return

        conv = conversations[index - 1]
        filepath = HISTORY_DIR / conv["filename"]

        if filepath.exists():
            filepath.unlink()
            console.print(f"[green]✓[/] Conversation deleted successfully")
            console.print(f"[dim]File: {conv['filename']}[/]")
        else:
            console.print("[red]Error:[/] Conversation file not found")

    except Exception as e:
        console.print(f"[red]Error deleting conversation:[/] {str(e)}")


@history.command()
@click.argument("index", type=int)
@click.argument("output", type=click.Path())
def export(index, output):
    """Export a conversation to Markdown"""
    try:
        conversations = list_conversations()

        if not conversations:
            console.print("[yellow]No conversation history found[/]")
            return

        if index < 1 or index > len(conversations):
            console.print(f"[red]Error:[/] Invalid index")
            return

        conv = conversations[index - 1]
        data = load_conversation(conv["filename"])

        if not data:
            console.print("[red]Error:[/] Failed to load conversation")
            return

        markdown_lines = [
            f"# Conversation Export",
            f"",
            f"**Timestamp:** {data.get('timestamp', 'Unknown')}",
            f"**Messages:** {len(data.get('messages', []))}",
            f"",
            f"---",
            f"",
        ]

        for msg in data.get("messages", []):
            role = msg.get("role", "unknown")
            content = msg.get("content", "")

            if role == "user":
                markdown_lines.append(f"## 👤 User")
            else:
                markdown_lines.append(f"## 🤖 Assistant")

            markdown_lines.append(f"")
            markdown_lines.append(content)
            markdown_lines.append(f"")
            markdown_lines.append(f"---")
            markdown_lines.append(f"")

        output_path = Path(output)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(markdown_lines))

        console.print(f"[green]✓[/] Conversation exported successfully")
        console.print(f"[dim]File: {output_path}[/]")

    except Exception as e:
        console.print(f"[red]Error exporting conversation:[/] {str(e)}")


@history.command()
@click.confirmation_option(prompt="Are you sure you want to clear all conversation history?")
def clear():
    """Clear all conversation history"""
    try:
        if not HISTORY_DIR.exists():
            console.print("[yellow]No conversation history found[/]")
            return

        import shutil

        shutil.rmtree(HISTORY_DIR)

        console.print("[green]✓[/] All conversation history cleared successfully")

    except Exception as e:
        console.print(f"[red]Error clearing history:[/] {str(e)}")

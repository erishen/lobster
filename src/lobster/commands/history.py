"""Conversation history management commands"""

import json
import logging
from datetime import datetime
from pathlib import Path

import click
import requests
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

logger = logging.getLogger(__name__)

console = Console()

HISTORY_DIR = Path.cwd() / ".lobster_history"


def ensure_history_dir():
    """Ensure history directory exists"""
    try:
        HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        logger.error("Error: Permission denied creating history directory")
        logger.info(f"Please check permissions for: {HISTORY_DIR}")
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

    with open(filepath, encoding="utf-8") as f:
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
        except requests.RequestException:
            continue

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
            logger.info("No conversation history found")
            logger.debug("Conversations are saved when using interactive chat mode")
            return

        logger.info(f"Conversation History ({len(conversations)} found)\n")

        table = Table()
        table.add_column("Index", style="cyan", width=6)
        table.add_column("Timestamp", style="blue", width=19)
        table.add_column("Messages", style="green", width=8)
        table.add_column("Preview", style="yellow")

        for i, conv in enumerate(conversations, 1):
            timestamp = conv["timestamp"][:19] if len(conv["timestamp"]) > 19 else conv["timestamp"]
            table.add_row(str(i), timestamp, str(conv["message_count"]), conv["preview"] + "...")

        console.print(table)

    except KeyError as e:
        logger.error(f"Error listing conversations: {e!s}")

    except Exception as e:
        logger.error(f"Error listing conversations: {e!s}")


@history.command()
@click.argument("index", type=int)
def show(index):
    """Show a specific conversation by index"""
    try:
        conversations = list_conversations()

        if not conversations:
            logger.info("No conversation history found")
            return

        if index < 1 or index > len(conversations):
            console.print("[red]Error:[/] Invalid index. Use 'lobster history list' to see available conversations")
            return

        conv = conversations[index - 1]
        data = load_conversation(conv["filename"])

        if not data:
            logger.error("Error: Failed to load conversation")
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
                logger.info(f"You: {content}")
            else:
                logger.info(f"Assistant: {content}")
            console.print()

    except requests.RequestException as e:
        logger.error(f"Error showing conversation: {e!s}")

    except KeyError as e:
        logger.error(f"Error showing conversation: {e!s}")

    except Exception as e:
        logger.error(f"Error showing conversation: {e!s}")


@history.command()
@click.argument("index", type=int)
def delete(index):
    """Delete a specific conversation by index"""
    try:
        conversations = list_conversations()

        if not conversations:
            logger.info("No conversation history found")
            return

        if index < 1 or index > len(conversations):
            logger.error("Error: Invalid index")
            return

        conv = conversations[index - 1]
        filepath = HISTORY_DIR / conv["filename"]

        if filepath.exists():
            filepath.unlink()
            logger.info(" Conversation deleted successfully")
            logger.debug(f"File: {conv['filename']}")
        else:
            logger.error("Error: Conversation file not found")

    except KeyError as e:
        logger.error(f"Error deleting conversation: {e!s}")

    except OSError as e:
        logger.error(f"Error deleting conversation: {e!s}")

    except Exception as e:
        logger.error(f"Error deleting conversation: {e!s}")


@history.command()
@click.argument("index", type=int)
@click.argument("output", type=click.Path())
def export(index, output):
    """Export a conversation to Markdown"""
    try:
        conversations = list_conversations()

        if not conversations:
            logger.info("No conversation history found")
            return

        if index < 1 or index > len(conversations):
            logger.error("Error: Invalid index")
            return

        conv = conversations[index - 1]
        data = load_conversation(conv["filename"])

        if not data:
            logger.error("Error: Failed to load conversation")
            return

        markdown_lines = [
            "# Conversation Export",
            "",
            f"**Timestamp:** {data.get('timestamp', 'Unknown')}",
            f"**Messages:** {len(data.get('messages', []))}",
            "",
            "---",
            "",
        ]

        for msg in data.get("messages", []):
            role = msg.get("role", "unknown")
            content = msg.get("content", "")

            if role == "user":
                markdown_lines.append("## 👤 User")
            else:
                markdown_lines.append("## 🤖 Assistant")

            markdown_lines.append("")
            markdown_lines.append(content)
            markdown_lines.append("")
            markdown_lines.append("---")
            markdown_lines.append("")

        output_path = Path(output)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(markdown_lines))

        logger.info(" Conversation exported successfully")
        logger.debug(f"File: {output_path}")

    except requests.RequestException as e:
        logger.error(f"Error exporting conversation: {e!s}")

    except KeyError as e:
        logger.error(f"Error exporting conversation: {e!s}")

    except OSError as e:
        logger.error(f"Error exporting conversation: {e!s}")

    except Exception as e:
        logger.error(f"Error exporting conversation: {e!s}")


@history.command()
@click.confirmation_option(prompt="Are you sure you want to clear all conversation history?")
def clear():
    """Clear all conversation history"""
    try:
        if not HISTORY_DIR.exists():
            logger.info("No conversation history found")
            return

        import shutil

        shutil.rmtree(HISTORY_DIR)

        logger.info(" All conversation history cleared successfully")

    except Exception as e:
        logger.error(f"Error clearing history: {e!s}")

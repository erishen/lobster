#!/usr/bin/env python3
"""Lobster - OpenClaw Assistant CLI Tool"""

import logging

import click
from rich.console import Console
from rich.panel import Panel

logger = logging.getLogger(__name__)

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
    logger.info(f"Lobster CLI version {VERSION}")


@cli.command()
def status():
    """Check the status of the OpenClaw service"""
    logger.info("Checking OpenClaw service status...")
    logger.info(" Service is running (mock status)")


@cli.command()
@click.argument("message", required=False)
@click.option("--model", "-m", default="ollama/gemma3", help="Model to use")
@click.option("--interactive", "-i", is_flag=True, help="Start interactive chat mode")
@click.option("--with-memory", is_flag=True, help="Enable memory-enhanced chat")
def chat(message, model, interactive, with_memory):
    """Send a message to the OpenClaw assistant"""
    from rich.prompt import Prompt

    from lobster.core.llm_client import get_llm_client
    from lobster.core.memory_store import EnhancedMemoryManager

    llm = get_llm_client(model)

    if interactive:
        console.print(
            Panel(
                f"[bold cyan]Interactive Chat Mode[/]\n"
                f"Model: {model}\n"
                f"Memory: {'Enabled' if with_memory else 'Disabled'}\n\n"
                f"Commands: 'quit' or 'exit' to stop, 'clear' to clear history",
                border_style="cyan",
            )
        )
        console.print()

        conversation_messages = []

        while True:
            try:
                user_input = Prompt.ask("[bold blue]You[/]")

                if user_input.lower() in ["quit", "exit"]:
                    if conversation_messages:
                        from datetime import datetime

                        from lobster.commands.history import save_conversation

                        conversation_data = {
                            "timestamp": datetime.now().isoformat(),
                            "model": model,
                            "messages": conversation_messages,
                        }
                        filename = save_conversation(conversation_data)
                        logger.debug(f"Conversation saved: {filename}")
                    logger.info("Goodbye! ")
                    break

                if user_input.lower() == "clear":
                    conversation_messages = []
                    logger.info("Conversation history cleared")
                    continue

                if not user_input.strip():
                    continue

                conversation_messages.append({"role": "user", "content": user_input})

                memory_context = ""
                if with_memory:
                    try:
                        memory = EnhancedMemoryManager()
                        memories = memory.search_memory(user_input, k=3)

                        if memories:
                            memory_context = "\n\n[Relevant Memories]\n"
                            for i, mem in enumerate(memories, 1):
                                memory_context += f"{i}. {mem['content']}\n"
                            memory_context += "\n"
                    except KeyError:
                        pass

                    except Exception:
                        pass

                enhanced_message = user_input
                if memory_context:
                    enhanced_message = f"{memory_context}[Current Question]\n{user_input}"

                with console.status("[bold green]Thinking..."):
                    response = llm.generate(enhanced_message)

                conversation_messages.append({"role": "assistant", "content": response})

                logger.info(f"Assistant: {response}\n")

            except KeyboardInterrupt:
                if conversation_messages:
                    from datetime import datetime

                    from lobster.commands.history import save_conversation

                    conversation_data = {
                        "timestamp": datetime.now().isoformat(),
                        "model": model,
                        "messages": conversation_messages,
                    }
                    filename = save_conversation(conversation_data)
                    logger.debug(f"Conversation saved: {filename}")
                logger.info("\nGoodbye! ")
                break
            except KeyError as e:
                logger.error(f"Error: {e!s}")
                continue

            except Exception as e:
                logger.error(f"Error: {e!s}")
                continue

    else:
        if not message:
            logger.error("Error: Message is required in non-interactive mode")
            logger.info("Use --interactive for interactive mode")
            return

        logger.info(f"Sending message to OpenClaw: {message}")

        with console.status("[bold green]Thinking..."):
            response = llm.generate(message)

        logger.info(f"Assistant response: {response}")


@cli.command()
@click.option("--port", "-p", default=8501, help="Port to run the web UI on")
@click.option("--host", "-h", default="localhost", help="Host to run the web UI on")
def web(port, host):
    """Start the Lobster Web UI"""
    try:
        import subprocess
        import sys
        from pathlib import Path

        web_app_path = Path(__file__).parent / "web" / "app.py"

        if not web_app_path.exists():
            logger.error("Error: Web UI module not found")
            logger.info("Install with: pip install lobster")
            return

        logger.info("Starting Lobster Web UI...")
        logger.debug(f"Host: {host}, Port: {port}")
        logger.debug(f"Access at: http://{host}:{port}")
        logger.debug("Press Ctrl+C to stop")

        subprocess.run(
            [
                sys.executable,
                "-m",
                "streamlit",
                "run",
                str(web_app_path),
                "--server.port",
                str(port),
                "--server.address",
                host,
            ],
            check=True,
        )

    except ImportError:
        logger.error("Error: Streamlit not installed")
        logger.info("Install with: pip install lobster")
    except KeyboardInterrupt:
        logger.info("\nWeb UI stopped")
    except Exception as e:
        logger.error(f"Error starting Web UI: {e!s}")


# 导入核心命令
from lobster.commands.api_cmd import api
from lobster.commands.client_cmd import client
from lobster.commands.code_cmd import code
from lobster.commands.config_cmd import config_cmd
from lobster.commands.data_cmd import data
from lobster.commands.datax_cmd import datax
from lobster.commands.doc_tool_cmd import doc_tool
from lobster.commands.doctor import doctor
from lobster.commands.history import history
from lobster.commands.invest_cmd import invest
from lobster.commands.memory import memory
from lobster.commands.model import model
from lobster.commands.notify_cmd import notify
from lobster.commands.openclaw_cmd import openclaw
from lobster.commands.project_cmd import project
from lobster.commands.rag_cmd import rag
from lobster.commands.scheduler_cmd import scheduler
from lobster.commands.search_cmd import search
from lobster.commands.serena_cmd import serena

# 导入新命令
from lobster.commands.shortcut import (
    ask,
    query,
    recall,
    remember,
)
from lobster.commands.shortcut import (
    status as shortcut_status,
)
from lobster.commands.template import template
from lobster.commands.util_cmd import util as util_tools
from lobster.commands.watch_cmd import watch
from lobster.commands.webhook_cmd import webhook

# 注册核心命令
cli.add_command(config_cmd, name="config")
cli.add_command(model)
cli.add_command(template)
cli.add_command(doctor)
cli.add_command(memory)
cli.add_command(history)

# 注册新命令
cli.add_command(ask)
cli.add_command(query)
cli.add_command(remember)
cli.add_command(recall)
cli.add_command(shortcut_status, name="shortcut-status")
cli.add_command(openclaw)
cli.add_command(code)
cli.add_command(doc_tool)
cli.add_command(data)
cli.add_command(project)
cli.add_command(util_tools, name="util-tools")
cli.add_command(api)
cli.add_command(search)
cli.add_command(datax)
cli.add_command(scheduler)
cli.add_command(webhook)
cli.add_command(watch)
cli.add_command(client)
cli.add_command(notify, name="notify")
cli.add_command(serena)
cli.add_command(rag)
cli.add_command(invest)


def main():
    """Main entry point"""
    cli()


if __name__ == "__main__":
    main()

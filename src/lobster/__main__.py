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
@click.argument("message", required=False)
@click.option("--model", "-m", default="ollama/gemma3", help="Model to use")
@click.option("--interactive", "-i", is_flag=True, help="Start interactive chat mode")
@click.option("--with-memory", is_flag=True, help="Enable memory-enhanced chat")
def chat(message, model, interactive, with_memory):
    """Send a message to the OpenClaw assistant"""
    try:
        from langchain_llm_toolkit import LLMIntegration
        from langchain_core.messages import HumanMessage, AIMessage
        from rich.prompt import Prompt

        llm = LLMIntegration()
        llm.set_model(model)

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

            conversation_history = []
            conversation_messages = []

            while True:
                try:
                    user_input = Prompt.ask("[bold blue]You[/]")

                    if user_input.lower() in ["quit", "exit"]:
                        if conversation_messages:
                            from lobster.commands.history import save_conversation
                            from datetime import datetime

                            conversation_data = {
                                "timestamp": datetime.now().isoformat(),
                                "model": model,
                                "messages": conversation_messages,
                            }
                            filename = save_conversation(conversation_data)
                            console.print(f"[dim]Conversation saved: {filename}[/]")
                        console.print("[yellow]Goodbye! 👋[/]")
                        break

                    if user_input.lower() == "clear":
                        conversation_history = []
                        conversation_messages = []
                        console.print("[green]Conversation history cleared[/]")
                        continue

                    if not user_input.strip():
                        continue

                    conversation_messages.append({"role": "user", "content": user_input})

                    memory_context = ""
                    if with_memory:
                        try:
                            from lobster.commands.memory import MEMORY_STORE_PATH
                            from langchain_llm_toolkit import RAGSystem
                            from pathlib import Path

                            index_file = MEMORY_STORE_PATH / "index.faiss"
                            if index_file.exists():
                                rag_system = RAGSystem(
                                    vector_store_type="faiss",
                                    embedding_type="ollama",
                                    embedding_model="nomic-embed-text",
                                    llm_model=model,
                                )
                                rag_system.load_vector_store(str(MEMORY_STORE_PATH))
                                memories = rag_system.retrieve_documents(user_input, k=3)

                                if memories:
                                    memory_context = "\n\n[Relevant Memories]\n"
                                    for i, mem in enumerate(memories, 1):
                                        memory_context += f"{i}. {mem.page_content}\n"
                                    memory_context += "\n"
                        except Exception:
                            pass

                    conversation_history.append(HumanMessage(content=user_input))

                    enhanced_message = user_input
                    if memory_context:
                        enhanced_message = f"{memory_context}[Current Question]\n{user_input}"

                    with console.status("[bold green]Thinking..."):
                        response = llm.generate(enhanced_message)

                    conversation_history.append(AIMessage(content=response))
                    conversation_messages.append({"role": "assistant", "content": response})

                    console.print(f"[bold green]Assistant:[/] {response}\n")

                except KeyboardInterrupt:
                    if conversation_messages:
                        from lobster.commands.history import save_conversation
                        from datetime import datetime

                        conversation_data = {
                            "timestamp": datetime.now().isoformat(),
                            "model": model,
                            "messages": conversation_messages,
                        }
                        filename = save_conversation(conversation_data)
                        console.print(f"[dim]Conversation saved: {filename}[/]")
                    console.print("\n[yellow]Goodbye! 👋[/]")
                    break
                except Exception as e:
                    console.print(f"[red]Error:[/] {str(e)}")
                    continue

        else:
            if not message:
                console.print("[red]Error:[/] Message is required in non-interactive mode")
                console.print("[yellow]Use --interactive for interactive mode[/]")
                return

            console.print(f"[bold blue]Sending message to OpenClaw:[/] {message}")

            with console.status("[bold green]Thinking..."):
                response = llm.generate(message)

            console.print(f"[bold green]Assistant response:[/] {response}")

    except ImportError:
        console.print("[red]Error:[/] langchain-llm-toolkit not installed")
        console.print("[yellow]Install with:[/] pip install langchain-llm-toolkit")
        console.print("[yellow]Falling back to mock response...[/]")
        console.print(
            "[bold green]Assistant response:[/] Hello! I'm Lobster, your assistant. (mock response)"
        )
    except Exception as e:
        console.print(f"[red]Error:[/] {str(e)}")
        console.print("[yellow]Falling back to mock response...[/]")
        console.print(
            "[bold green]Assistant response:[/] Hello! I'm Lobster, your assistant. (mock response)"
        )


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
            console.print("[red]Error:[/] Web UI module not found")
            console.print("[yellow]Install with:[/] pip install lobster[web]")
            return

        console.print(f"[bold blue]Starting Lobster Web UI...[/]")
        console.print(f"[dim]Host: {host}, Port: {port}[/]")
        console.print(f"[dim]Access at: http://{host}:{port}[/]")
        console.print("[dim]Press Ctrl+C to stop[/]")

        subprocess.run(
            [sys.executable, "-m", "streamlit", "run", str(web_app_path), "--server.port", str(port), "--server.address", host],
            check=True,
        )

    except ImportError:
        console.print("[red]Error:[/] Streamlit not installed")
        console.print("[yellow]Install with:[/] pip install lobster[web]")
    except KeyboardInterrupt:
        console.print("\n[yellow]Web UI stopped[/]")
    except Exception as e:
        console.print(f"[red]Error starting Web UI:[/] {str(e)}")


from lobster.commands.document import doc  # noqa: E402
from lobster.commands.llm import llm  # noqa: E402
from lobster.commands.rag import rag  # noqa: E402
from lobster.commands.config_cmd import config_cmd  # noqa: E402
from lobster.commands.batch import batch  # noqa: E402
from lobster.commands.plugin_cmd import plugin  # noqa: E402
from lobster.commands.util import util  # noqa: E402
from lobster.commands.model import model  # noqa: E402
from lobster.commands.template import template  # noqa: E402
from lobster.commands.doctor import doctor  # noqa: E402
from lobster.commands.memory import memory  # noqa: E402
from lobster.commands.history import history  # noqa: E402

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
cli.add_command(memory)
cli.add_command(history)


def main():
    """Main entry point"""
    cli()


if __name__ == "__main__":
    main()

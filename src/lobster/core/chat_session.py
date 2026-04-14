"""Interactive chat enhancement features"""

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.markdown import Markdown
from typing import Optional, List
import time

console = Console()


class ChatSession:
    """Enhanced chat session with history and context"""

    def __init__(self, model: str = "ollama/gemma3", temperature: float = 0.7):
        self.model = model
        self.temperature = temperature
        self.history: List[dict] = []
        self.system_prompt = "You are a helpful AI assistant."

    def add_message(self, role: str, content: str):
        """Add a message to history"""
        self.history.append({"role": role, "content": content})

    def clear_history(self):
        """Clear chat history"""
        self.history = []
        console.print("[green]✓[/] Chat history cleared")

    def show_history(self, limit: int = 10):
        """Show chat history"""
        if not self.history:
            console.print("[yellow]No chat history[/]")
            return

        console.print(f"[bold cyan]Chat History (last {min(limit, len(self.history))} messages)[/]")

        for i, msg in enumerate(self.history[-limit:]):
            role = msg["role"]
            content = msg["content"]

            if role == "user":
                console.print(f"[bold blue]You:[/] {content}")
            else:
                console.print(f"[bold green]Assistant:[/] {content}")

            if i < len(self.history[-limit:]) - 1:
                console.print()

    def export_history(self, filename: str):
        """Export chat history to file"""
        import json
        from pathlib import Path

        filepath = Path(filename)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "model": self.model,
                    "temperature": self.temperature,
                    "system_prompt": self.system_prompt,
                    "history": self.history,
                    "timestamp": time.time(),
                },
                f,
                indent=2,
                ensure_ascii=False,
            )

        console.print(f"[green]✓[/] Chat history exported to {filename}")

    def load_history(self, filename: str):
        """Load chat history from file"""
        import json
        from pathlib import Path

        filepath = Path(filename)
        if not filepath.exists():
            console.print(f"[red]Error:[/] File {filename} not found")
            return

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.model = data.get("model", self.model)
        self.temperature = data.get("temperature", self.temperature)
        self.system_prompt = data.get("system_prompt", self.system_prompt)
        self.history = data.get("history", [])

        console.print(f"[green]✓[/] Chat history loaded from {filename}")
        console.print(f"[dim]Loaded {len(self.history)} messages[/]")


def start_interactive_chat(model: str, temperature: float, system_prompt: Optional[str] = None):
    """Start an enhanced interactive chat session"""
    try:
        from langchain_llm_toolkit import ConversationManager

        console.print(
            Panel.fit(
                "[bold cyan]Lobster Interactive Chat[/]\n"
                f"Model: {model}\n"
                f"Temperature: {temperature}\n"
                "Commands: /help, /clear, /history, /export <file>, /load <file>, /exit",
                border_style="cyan",
            )
        )

        session = ChatSession(model=model, temperature=temperature)
        if system_prompt:
            session.system_prompt = system_prompt

        manager = ConversationManager()
        manager.set_model(model)
        manager.set_temperature(temperature)

        while True:
            try:
                user_input = Prompt.ask("[bold blue]You[/]")

                # Handle commands
                if user_input.startswith("/"):
                    cmd_parts = user_input.split(maxsplit=1)
                    cmd = cmd_parts[0].lower()
                    args = cmd_parts[1] if len(cmd_parts) > 1 else None

                    if cmd == "/exit" or cmd == "/quit":
                        console.print("[yellow]Goodbye![/]")
                        break
                    elif cmd == "/clear":
                        session.clear_history()
                        manager.clear_history()
                        continue
                    elif cmd == "/history":
                        session.show_history()
                        continue
                    elif cmd == "/export":
                        if args:
                            session.export_history(args)
                        else:
                            console.print("[red]Error:[/] Please specify a filename")
                        continue
                    elif cmd == "/load":
                        if args:
                            session.load_history(args)
                        else:
                            console.print("[red]Error:[/] Please specify a filename")
                        continue
                    elif cmd == "/help":
                        console.print(
                            Panel(
                                "[bold]Available Commands:[/]\n\n"
                                "/help - Show this help\n"
                                "/clear - Clear chat history\n"
                                "/history - Show chat history\n"
                                "/export <file> - Export chat history\n"
                                "/load <file> - Load chat history\n"
                                "/exit - Exit chat session",
                                title="Help",
                                border_style="cyan",
                            )
                        )
                        continue
                    else:
                        console.print(f"[red]Unknown command:[/] {cmd}")
                        continue

                if not user_input.strip():
                    continue

                # Add to session history
                session.add_message("user", user_input)

                # Get response
                with console.status("[bold green]Thinking...[/]"):
                    response = manager.converse(user_input)

                # Add to session history
                session.add_message("assistant", response)

                # Display response
                console.print()
                console.print(
                    Panel(
                        Markdown(response), title="[bold green]Assistant[/]", border_style="green"
                    )
                )
                console.print()

            except KeyboardInterrupt:
                console.print("\n[yellow]Use /exit to quit[/]")
                continue
            except Exception as e:
                console.print(f"[red]Error:[/] {str(e)}")
                continue

    except ImportError:
        console.print("[red]Error:[/] langchain-llm-toolkit not installed")
        console.print("[yellow]Install with:[/] pip install langchain-llm-toolkit")
    except Exception as e:
        console.print(f"[red]Error:[/] {str(e)}")

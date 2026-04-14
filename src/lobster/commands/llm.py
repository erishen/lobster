"""LLM functionality commands"""

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


@click.group()
def llm():
    """LLM functionality commands"""
    pass


@llm.command()
@click.argument('prompt')
@click.option('--model', '-m', default='ollama/gemma3', help='Model to use')
@click.option('--temperature', '-t', default=0.7, help='Temperature parameter')
@click.option('--timeout', default=30, help='Request timeout in seconds')
def generate(prompt, model, temperature, timeout):
    """Generate text from a prompt"""
    try:
        from langchain_llm_toolkit import LLMIntegration
        
        console.print(f"[bold blue]Generating text...[/]")
        console.print(f"[dim]Model: {model}, Temperature: {temperature}[/]")
        
        llm = LLMIntegration(timeout=timeout)
        llm.set_model(model)
        llm.set_temperature(temperature)
        
        with console.status("[bold green]Processing..."):
            response = llm.generate(prompt)
        
        console.print(Panel(response, title="[bold green]Response[/]", border_style="green"))
        
    except ImportError:
        console.print("[red]Error:[/] langchain-llm-toolkit not installed")
        console.print("[yellow]Install with:[/] pip install langchain-llm-toolkit")
    except Exception as e:
        console.print(f"[red]Error generating text:[/] {str(e)}")


@llm.command()
@click.option('--model', '-m', default='ollama/gemma3', help='Model to use')
@click.option('--temperature', '-t', default=0.7, help='Temperature parameter')
def chat(model, temperature):
    """Start interactive chat session"""
    try:
        from langchain_llm_toolkit import ConversationManager
        
        console.print(Panel.fit(
            "[bold cyan]Lobster Chat Session[/]\n"
            f"Model: {model}\n"
            "Type 'exit' to quit, 'clear' to clear history",
            border_style="cyan"
        ))
        
        manager = ConversationManager()
        manager.set_model(model)
        manager.set_temperature(temperature)
        
        while True:
            try:
                user_input = console.input("[bold blue]You:[/] ")
                
                if user_input.lower() == 'exit':
                    console.print("[yellow]Goodbye![/]")
                    break
                elif user_input.lower() == 'clear':
                    manager.clear_history()
                    console.print("[green]History cleared[/]")
                    continue
                elif not user_input.strip():
                    continue
                
                with console.status("[bold green]Thinking..."):
                    response = manager.converse(user_input)
                
                console.print(f"[bold green]Assistant:[/] {response}")
                
            except KeyboardInterrupt:
                console.print("\n[yellow]Goodbye![/]")
                break
                
    except ImportError:
        console.print("[red]Error:[/] langchain-llm-toolkit not installed")
        console.print("[yellow]Install with:[/] pip install langchain-llm-toolkit")
    except Exception as e:
        console.print(f"[red]Error in chat:[/] {str(e)}")


@llm.command()
def models():
    """List available models"""
    console.print("[bold blue]Available Models[/]")
    
    table = Table(title="Supported Models")
    table.add_column("Model", style="cyan")
    table.add_column("Type", style="green")
    table.add_column("Description", style="yellow")
    
    models_list = [
        ("ollama/gemma3", "Local", "Ollama - gemma3 model"),
        ("ollama/llama3.1:8b", "Local", "Ollama - llama3.1 8B model"),
        ("ollama/deepseek-r1:7b", "Local", "Ollama - deepseek-r1 7B model"),
        ("gpt-4o", "Cloud", "OpenAI - GPT-4o (requires API key)"),
        ("gpt-3.5-turbo", "Cloud", "OpenAI - GPT-3.5 Turbo (requires API key)"),
        ("claude-3-opus", "Cloud", "Anthropic - Claude 3 Opus (requires API key)"),
        ("gemini-pro", "Cloud", "Google - Gemini Pro (requires API key)"),
    ]
    
    for model, model_type, description in models_list:
        table.add_row(model, model_type, description)
    
    console.print(table)
    
    console.print("\n[bold yellow]Tips:[/]")
    console.print("• Local models require Ollama to be running")
    console.print("• Cloud models require API keys to be set in environment")
    console.print("• Set API keys: export OPENAI_API_KEY='your-key'")


@llm.command()
@click.argument('prompt')
@click.option('--model', '-m', default='ollama/gemma3', help='Model to use (must be Ollama)')
def stream(prompt, model):
    """Generate text with streaming (Ollama only)"""
    try:
        from langchain_llm_toolkit import LLMIntegration
        
        if not model.startswith('ollama/'):
            console.print("[red]Error:[/] Streaming only supported for Ollama models")
            return
        
        console.print(f"[bold blue]Streaming response...[/]")
        console.print(f"[dim]Model: {model}[/]")
        
        llm = LLMIntegration()
        llm.set_model(model)
        
        console.print("[bold green]Response:[/] ", end="")
        
        for chunk in llm.generate_stream(prompt):
            console.print(chunk, end="", style="green")
        
        console.print()  # New line after streaming
        
    except ImportError:
        console.print("[red]Error:[/] langchain-llm-toolkit not installed")
        console.print("[yellow]Install with:[/] pip install langchain-llm-toolkit")
    except Exception as e:
        console.print(f"[red]Error streaming:[/] {str(e)}")

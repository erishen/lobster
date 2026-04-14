"""Prompt template management commands"""

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from pathlib import Path
import json

console = Console()

TEMPLATES_DIR = Path.home() / ".lobster" / "templates"


def ensure_templates_dir():
    """Ensure templates directory exists"""
    TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)


@click.group()
def template():
    """Prompt template management commands"""
    pass


@template.command()
def list():
    """List all saved templates"""
    ensure_templates_dir()
    templates = list_templates()
    
    if not templates:
        console.print("[yellow]No templates found[/]")
        console.print("[dim]Create a template with: lobster template create <name>[/]")
        return
    
    table = Table(title="Saved Templates")
    table.add_column("Name", style="cyan")
    table.add_column("Category", style="green")
    table.add_column("Description", style="yellow")
    table.add_column("Variables", style="magenta")
    
    for template_info in templates:
        table.add_row(
            template_info.get('name', 'unknown'),
            template_info.get('category', 'general'),
            template_info.get('description', '')[:50],
            str(len(template_info.get('variables', [])))
        )
    
    console.print(table)


@template.command()
@click.argument('name')
def show(name):
    """Show a template"""
    ensure_templates_dir()
    template_file = TEMPLATES_DIR / f"{name}.json"
    
    if not template_file.exists():
        console.print(f"[red]Error:[/] Template '{name}' not found")
        return
    
    with open(template_file, 'r', encoding='utf-8') as f:
        template_data = json.load(f)
    
    console.print(Panel(
        f"[bold cyan]Name:[/] {template_data.get('name')}\n"
        f"[bold green]Category:[/] {template_data.get('category', 'general')}\n"
        f"[bold yellow]Description:[/] {template_data.get('description', 'N/A')}\n"
        f"[bold magenta]Variables:[/] {', '.join(template_data.get('variables', []))}\n\n"
        f"[bold blue]Template:[/]\n{template_data.get('template', '')}",
        title=f"Template: {name}",
        border_style="cyan"
    ))


@template.command()
@click.argument('name')
@click.option('--category', default='general', help='Template category')
@click.option('--description', default='', help='Template description')
def create(name, category, description):
    """Create a new template interactively"""
    ensure_templates_dir()
    console.print(f"[bold blue]Creating template:[/] {name}")
    
    if not description:
        description = click.prompt("Description", default="")
    
    template_text = click.edit("Enter your template here. Use {variable} for variables.")
    
    if not template_text:
        console.print("[yellow]Cancelled[/]")
        return
    
    # Extract variables
    import re
    variables = list(set(re.findall(r'\{(\w+)\}', template_text)))
    
    template_data = {
        "name": name,
        "category": category,
        "description": description,
        "template": template_text,
        "variables": variables
    }
    
    template_file = TEMPLATES_DIR / f"{name}.json"
    with open(template_file, 'w', encoding='utf-8') as f:
        json.dump(template_data, f, indent=2, ensure_ascii=False)
    
    console.print(f"[green]✓[/] Template '{name}' created successfully")
    if variables:
        console.print(f"[dim]Variables: {', '.join(variables)}[/]")


@template.command()
@click.argument('name')
def edit(name):
    """Edit an existing template"""
    template_file = TEMPLATES_DIR / f"{name}.json"
    
    if not template_file.exists():
        console.print(f"[red]Error:[/] Template '{name}' not found")
        return
    
    with open(template_file, 'r', encoding='utf-8') as f:
        template_data = json.load(f)
    
    template_text = click.edit(template_data.get('template', ''))
    
    if not template_text:
        console.print("[yellow]Cancelled[/]")
        return
    
    # Extract variables
    import re
    variables = list(set(re.findall(r'\{(\w+)\}', template_text)))
    
    template_data['template'] = template_text
    template_data['variables'] = variables
    
    with open(template_file, 'w', encoding='utf-8') as f:
        json.dump(template_data, f, indent=2, ensure_ascii=False)
    
    console.print(f"[green]✓[/] Template '{name}' updated successfully")


@template.command()
@click.argument('name')
def delete(name):
    """Delete a template"""
    ensure_templates_dir()
    template_file = TEMPLATES_DIR / f"{name}.json"
    
    if not template_file.exists():
        console.print(f"[red]Error:[/] Template '{name}' not found")
        return
    
    if not click.confirm(f"Delete template '{name}'?"):
        console.print("[yellow]Cancelled[/]")
        return
    
    template_file.unlink()
    console.print(f"[green]✓[/] Template '{name}' deleted")


@template.command()
@click.argument('name')
@click.option('--model', default='ollama/gemma3', help='Model to use')
def apply(name, model):
    """Apply a template and generate response"""
    ensure_templates_dir()
    template_file = TEMPLATES_DIR / f"{name}.json"
    
    if not template_file.exists():
        console.print(f"[red]Error:[/] Template '{name}' not found")
        return
    
    with open(template_file, 'r', encoding='utf-8') as f:
        template_data = json.load(f)
    
    template_text = template_data.get('template', '')
    variables = template_data.get('variables', [])
    
    # Get variable values
    values = {}
    for var in variables:
        value = click.prompt(f"Enter value for '{var}'")
        values[var] = value
    
    # Fill template
    prompt = template_text.format(**values)
    
    console.print(f"\n[bold blue]Generated prompt:[/]")
    console.print(Panel(prompt, border_style="cyan"))
    
    # Generate response
    try:
        from langchain_llm_toolkit import LLMIntegration
        
        llm = LLMIntegration()
        llm.set_model(model)
        
        with console.status("[bold green]Generating response...[/]"):
            response = llm.generate(prompt)
        
        console.print(Panel(response, title="[bold green]Response[/]", border_style="green"))
        
    except ImportError:
        console.print("[red]Error:[/] langchain-llm-toolkit not installed")
    except Exception as e:
        console.print(f"[red]Error:[/] {str(e)}")


@template.command()
def builtin():
    """Show built-in template examples"""
    console.print("[bold blue]Built-in Template Examples[/]")
    
    examples = [
        {
            "name": "code-review",
            "category": "development",
            "description": "Review code for improvements",
            "template": "Please review the following {language} code and suggest improvements:\n\n{code}",
            "variables": ["language", "code"]
        },
        {
            "name": "summarize",
            "category": "general",
            "description": "Summarize a text",
            "template": "Please summarize the following text in {length} sentences:\n\n{text}",
            "variables": ["length", "text"]
        },
        {
            "name": "translate",
            "category": "language",
            "description": "Translate text",
            "template": "Translate the following text from {source_lang} to {target_lang}:\n\n{text}",
            "variables": ["source_lang", "target_lang", "text"]
        },
        {
            "name": "explain",
            "category": "education",
            "description": "Explain a concept",
            "template": "Explain {concept} in simple terms for a {audience} audience.",
            "variables": ["concept", "audience"]
        },
    ]
    
    table = Table(title="Built-in Templates")
    table.add_column("Name", style="cyan")
    table.add_column("Category", style="green")
    table.add_column("Description", style="yellow")
    
    for example in examples:
        table.add_row(example['name'], example['category'], example['description'])
    
    console.print(table)
    
    console.print("\n[bold yellow]To create from example:[/]")
    for example in examples:
        console.print(f"[dim]lobster template create {example['name']}[/]")


def list_templates():
    """List all templates"""
    templates = []
    
    for template_file in TEMPLATES_DIR.glob("*.json"):
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                template_data = json.load(f)
                templates.append(template_data)
        except:
            pass
    
    return templates

"""Utility commands for text processing, code analysis, and more"""

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from pathlib import Path
import json

console = Console()


@click.group()
def util():
    """Utility commands for various tasks"""
    pass


@util.command()
@click.argument('file_path', type=click.Path(exists=True))
def textstat(file_path):
    """Analyze text file statistics"""
    from pathlib import Path
    
    file = Path(file_path)
    
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    words = content.split()
    chars = len(content)
    chars_no_spaces = len(content.replace(' ', '').replace('\n', '').replace('\t', ''))
    
    table = Table(title=f"Text Statistics: {file.name}")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("File", str(file))
    table.add_row("Lines", str(len(lines)))
    table.add_row("Words", str(len(words)))
    table.add_row("Characters", str(chars))
    table.add_row("Characters (no spaces)", str(chars_no_spaces))
    table.add_row("Average line length", f"{chars / len(lines):.1f}")
    table.add_row("Average word length", f"{sum(len(w) for w in words) / len(words):.1f}" if words else "0")
    
    console.print(table)


@util.command()
@click.argument('file_path', type=click.Path(exists=True))
def codeinfo(file_path):
    """Analyze code file information"""
    from pathlib import Path
    
    file = Path(file_path)
    suffix = file.suffix.lower()
    
    code_extensions = {
        '.py': 'Python',
        '.js': 'JavaScript',
        '.ts': 'TypeScript',
        '.java': 'Java',
        '.cpp': 'C++',
        '.c': 'C',
        '.go': 'Go',
        '.rs': 'Rust',
        '.rb': 'Ruby',
        '.php': 'PHP',
        '.swift': 'Swift',
        '.kt': 'Kotlin',
    }
    
    if suffix not in code_extensions:
        console.print(f"[yellow]Warning:[/] Unknown code file type: {suffix}")
        language = "Unknown"
    else:
        language = code_extensions[suffix]
    
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    
    code_lines = 0
    comment_lines = 0
    blank_lines = 0
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            blank_lines += 1
        elif stripped.startswith('#') or stripped.startswith('//') or stripped.startswith('/*'):
            comment_lines += 1
        else:
            code_lines += 1
    
    table = Table(title=f"Code Analysis: {file.name}")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Language", language)
    table.add_row("Total Lines", str(len(lines)))
    table.add_row("Code Lines", str(code_lines))
    table.add_row("Comment Lines", str(comment_lines))
    table.add_row("Blank Lines", str(blank_lines))
    table.add_row("Code Percentage", f"{code_lines / len(lines) * 100:.1f}%" if lines else "0%")
    
    console.print(table)


@util.command()
@click.argument('text')
def wordcount(text):
    """Count words in text"""
    words = text.split()
    chars = len(text)
    
    console.print(Panel(
        f"[bold cyan]Words:[/] {len(words)}\n"
        f"[bold green]Characters:[/] {chars}\n"
        f"[bold yellow]Average word length:[/] {sum(len(w) for w in words) / len(words):.1f}" if words else "0",
        title="Word Count",
        border_style="cyan"
    ))


@util.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--output', '-o', help='Output JSON file')
def jsonfmt(file_path, output):
    """Format and validate JSON file"""
    from pathlib import Path
    import json
    
    file = Path(file_path)
    
    try:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        formatted = json.dumps(data, indent=2, ensure_ascii=False)
        
        if output:
            output_file = Path(output)
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(formatted)
            console.print(f"[green]✓[/] JSON formatted and saved to: {output}")
        else:
            console.print(Panel(formatted, title=f"[bold cyan]{file.name}[/]", border_style="cyan"))
        
        console.print(f"[green]✓[/] Valid JSON with {len(str(data))} characters")
        
    except json.JSONDecodeError as e:
        console.print(f"[red]Error:[/] Invalid JSON: {str(e)}")
    except Exception as e:
        console.print(f"[red]Error:[/] {str(e)}")


@util.command()
@click.argument('file_path', type=click.Path(exists=True))
def checksum(file_path):
    """Calculate file checksums"""
    from pathlib import Path
    import hashlib
    
    file = Path(file_path)
    
    with open(file, 'rb') as f:
        content = f.read()
    
    md5 = hashlib.md5(content).hexdigest()
    sha1 = hashlib.sha1(content).hexdigest()
    sha256 = hashlib.sha256(content).hexdigest()
    
    table = Table(title=f"Checksums: {file.name}")
    table.add_column("Algorithm", style="cyan")
    table.add_column("Hash", style="green")
    
    table.add_row("MD5", md5)
    table.add_row("SHA1", sha1)
    table.add_row("SHA256", sha256)
    
    console.print(table)


@util.command()
@click.argument('directory', type=click.Path(exists=True))
@click.option('--pattern', default='*', help='File pattern to search')
def findlarge(directory, pattern):
    """Find large files in directory"""
    from pathlib import Path
    
    dir_path = Path(directory)
    files = []
    
    for file in dir_path.rglob(pattern):
        if file.is_file():
            size = file.stat().st_size
            files.append((file, size))
    
    files.sort(key=lambda x: x[1], reverse=True)
    
    if not files:
        console.print("[yellow]No files found[/]")
        return
    
    table = Table(title=f"Large Files in {directory}")
    table.add_column("File", style="cyan")
    table.add_column("Size", style="green")
    
    for file, size in files[:20]:  # Show top 20
        if size > 1024 * 1024:
            size_str = f"{size / 1024 / 1024:.2f} MB"
        elif size > 1024:
            size_str = f"{size / 1024:.2f} KB"
        else:
            size_str = f"{size} B"
        
        table.add_row(str(file.relative_to(dir_path)), size_str)
    
    console.print(table)
    
    total_size = sum(size for _, size in files)
    console.print(f"\n[dim]Total: {len(files)} files, {total_size / 1024 / 1024:.2f} MB[/]")


@util.command()
def envcheck():
    """Check environment and dependencies"""
    import sys
    import platform
    
    table = Table(title="Environment Check")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Details", style="yellow")
    
    # Python
    table.add_row("Python", "✓", f"{sys.version.split()[0]}")
    table.add_row("Platform", "✓", f"{platform.system()} {platform.release()}")
    
    # Check dependencies
    dependencies = [
        ("click", "Click"),
        ("rich", "Rich"),
        ("pydantic", "Pydantic"),
        ("langchain_llm_toolkit", "LangChain LLM Toolkit"),
    ]
    
    for module, name in dependencies:
        try:
            mod = __import__(module)
            version = getattr(mod, '__version__', 'unknown')
            table.add_row(name, "✓", f"v{version}")
        except ImportError:
            table.add_row(name, "✗", "Not installed")
    
    # Check Ollama
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            models = response.json().get('models', [])
            table.add_row("Ollama", "✓", f"{len(models)} models available")
        else:
            table.add_row("Ollama", "✗", "Not responding")
    except:
        table.add_row("Ollama", "✗", "Not running")
    
    console.print(table)

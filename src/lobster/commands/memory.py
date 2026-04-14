"""Memory management commands for OpenClaw"""

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from datetime import datetime
from pathlib import Path
import json

console = Console()

MEMORY_STORE_PATH = Path.cwd() / ".lobster_memory"
MEMORY_INDEX_FILE = Path.cwd() / ".lobster_memory_index.json"


def ensure_memory_dir():
    """Ensure memory directory exists"""
    try:
        MEMORY_STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        console.print("[red]Error:[/] Permission denied creating memory directory")
        console.print(f"[yellow]Please check permissions for:[/] {MEMORY_STORE_PATH.parent}")
        raise


def load_memory_index():
    """Load memory index"""
    if MEMORY_INDEX_FILE.exists():
        with open(MEMORY_INDEX_FILE, "r") as f:
            return json.load(f)
    return {"memories": []}


def save_memory_index(index):
    """Save memory index"""
    ensure_memory_dir()
    with open(MEMORY_INDEX_FILE, "w") as f:
        json.dump(index, f, indent=2)


@click.group()
def memory():
    """Memory management for OpenClaw (RAG-based storage)"""
    pass


@memory.command()
@click.argument("content")
@click.option("--tag", "-t", multiple=True, help="Tags for the memory")
@click.option("--category", "-c", default="general", help="Memory category")
def add(content, tag, category):
    """Add a new memory to OpenClaw's memory store"""
    try:
        from langchain_llm_toolkit import RAGSystem
        from langchain_core.documents import Document

        ensure_memory_dir()

        memory_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        timestamp = datetime.now().isoformat()

        metadata = {
            "id": memory_id,
            "timestamp": timestamp,
            "category": category,
            "tags": list(tag) if tag else [],
            "type": "memory",
        }

        console.print(f"[bold blue]Adding memory to OpenClaw...[/]")
        console.print(
            f"[dim]Content: {content[:100]}{'...' if len(content) > 100 else ''}[/]"
        )

        rag_system = RAGSystem(
            vector_store_type="faiss",
            embedding_type="ollama",
            embedding_model="nomic-embed-text",
            llm_model="ollama/gemma3",
        )

        document = Document(page_content=content, metadata=metadata)

        index_file = MEMORY_STORE_PATH / "index.faiss"
        if index_file.exists():
            rag_system.load_vector_store(str(MEMORY_STORE_PATH))
            rag_system.add_documents([document])
        else:
            rag_system.create_vector_store([document])

        rag_system.save_vector_store(str(MEMORY_STORE_PATH))

        index = load_memory_index()
        index["memories"].append(
            {
                "id": memory_id,
                "content": content,
                "timestamp": timestamp,
                "category": category,
                "tags": list(tag) if tag else [],
            }
        )
        save_memory_index(index)

        console.print(f"[green]✓[/] Memory added successfully")
        console.print(f"[dim]ID: {memory_id}[/]")
        console.print(f"[dim]Category: {category}[/]")
        if tag:
            console.print(f"[dim]Tags: {', '.join(tag)}[/]")

    except ImportError:
        console.print("[red]Error:[/] langchain-llm-toolkit not installed")
        console.print("[yellow]Install with:[/] pip install langchain-llm-toolkit")
    except Exception as e:
        console.print(f"[red]Error adding memory:[/] {str(e)}")


@memory.command()
@click.option("--category", "-c", help="Filter by category")
@click.option("--tag", "-t", help="Filter by tag")
@click.option("--limit", "-l", default=20, help="Maximum number of memories to show")
def list(category, tag, limit):
    """List all stored memories"""
    try:
        index = load_memory_index()

        if not index["memories"]:
            console.print("[yellow]No memories found[/]")
            console.print("[dim]Add memories using: lobster memory add <content>[/]")
            return

        memories = index["memories"]

        if category:
            memories = [m for m in memories if m.get("category") == category]

        if tag:
            memories = [m for m in memories if tag in m.get("tags", [])]

        memories = sorted(memories, key=lambda x: x["timestamp"], reverse=True)[:limit]

        console.print(f"[bold blue]OpenClaw Memories ({len(memories)} found)[/]\n")

        table = Table()
        table.add_column("ID", style="cyan", width=15)
        table.add_column("Content", style="green", width=50)
        table.add_column("Category", style="yellow", width=12)
        table.add_column("Tags", style="magenta", width=15)
        table.add_column("Timestamp", style="blue", width=19)

        for mem in memories:
            content_preview = mem["content"][:47] + "..." if len(mem["content"]) > 50 else mem["content"]
            tags_str = ", ".join(mem.get("tags", []))[:15]
            timestamp = mem["timestamp"][:19]

            table.add_row(
                mem["id"], content_preview, mem.get("category", "general"), tags_str, timestamp
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error listing memories:[/] {str(e)}")


@memory.command()
@click.argument("query")
@click.option("--k", default=5, help="Number of results to return")
def search(query, k):
    """Search memories using RAG"""
    try:
        from langchain_llm_toolkit import RAGSystem

        if not MEMORY_STORE_PATH.exists():
            console.print("[yellow]No memories found[/]")
            console.print("[dim]Add memories using: lobster memory add <content>[/]")
            return

        console.print(f"[bold blue]Searching memories...[/]")
        console.print(f"[dim]Query: {query}[/]")

        rag_system = RAGSystem(
            vector_store_type="faiss",
            embedding_type="ollama",
            embedding_model="nomic-embed-text",
            llm_model="ollama/gemma3",
        )

        rag_system.load_vector_store(str(MEMORY_STORE_PATH))

        with console.status("[bold green]Searching..."):
            results = rag_system.retrieve_documents(query, k=k)

        if not results:
            console.print("[yellow]No matching memories found[/]")
            return

        console.print(f"\n[green]✓[/] Found {len(results)} matching memories\n")

        for i, doc in enumerate(results, 1):
            metadata = doc.metadata
            console.print(
                Panel(
                    doc.page_content,
                    title=f"[bold cyan]Memory {i}[/] - ID: {metadata.get('id', 'N/A')}",
                    border_style="cyan",
                )
            )
            console.print(f"[dim]Category: {metadata.get('category', 'general')}[/]")
            if metadata.get("tags"):
                console.print(f"[dim]Tags: {', '.join(metadata['tags'])}[/]")
            console.print(f"[dim]Timestamp: {metadata.get('timestamp', 'N/A')}[/]")
            console.print()

    except ImportError:
        console.print("[red]Error:[/] langchain-llm-toolkit not installed")
        console.print("[yellow]Install with:[/] pip install langchain-llm-toolkit")
    except Exception as e:
        console.print(f"[red]Error searching memories:[/] {str(e)}")


@memory.command()
@click.argument("memory_id")
def delete(memory_id):
    """Delete a specific memory by ID"""
    try:
        index = load_memory_index()

        memory_to_delete = None
        for i, mem in enumerate(index["memories"]):
            if mem["id"] == memory_id:
                memory_to_delete = i
                break

        if memory_to_delete is None:
            console.print(f"[red]Error:[/] Memory with ID '{memory_id}' not found")
            return

        deleted_memory = index["memories"].pop(memory_to_delete)
        save_memory_index(index)

        console.print(f"[green]✓[/] Memory deleted successfully")
        console.print(f"[dim]ID: {memory_id}[/]")
        console.print(f"[dim]Content: {deleted_memory['content'][:50]}...[/]")

        console.print(
            "[yellow]Note:[/] The memory is removed from index. "
            "Vector store will be rebuilt on next add."
        )

    except Exception as e:
        console.print(f"[red]Error deleting memory:[/] {str(e)}")


@memory.command()
@click.confirmation_option(prompt="Are you sure you want to clear all memories?")
def clear():
    """Clear all memories"""
    try:
        if MEMORY_STORE_PATH.exists():
            import shutil

            shutil.rmtree(MEMORY_STORE_PATH)

        if MEMORY_INDEX_FILE.exists():
            MEMORY_INDEX_FILE.unlink()

        console.print("[green]✓[/] All memories cleared successfully")

    except Exception as e:
        console.print(f"[red]Error clearing memories:[/] {str(e)}")


@memory.command()
def stats():
    """Show memory statistics"""
    try:
        index = load_memory_index()

        if not index["memories"]:
            console.print("[yellow]No memories found[/]")
            return

        total_memories = len(index["memories"])
        categories = {}
        all_tags = []

        for mem in index["memories"]:
            cat = mem.get("category", "general")
            categories[cat] = categories.get(cat, 0) + 1
            all_tags.extend(mem.get("tags", []))

        unique_tags = len(set(all_tags))

        console.print("[bold blue]Memory Statistics[/]\n")

        table = Table()
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Total Memories", str(total_memories))
        table.add_row("Categories", str(len(categories)))
        table.add_row("Unique Tags", str(unique_tags))

        console.print(table)

        console.print("\n[bold yellow]Categories:[/]")
        for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            console.print(f"  • {cat}: {count} memories")

    except Exception as e:
        console.print(f"[red]Error getting stats:[/] {str(e)}")

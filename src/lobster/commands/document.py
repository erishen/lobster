"""Document processing commands"""

import click
from rich.console import Console
from rich.table import Table

console = Console()


@click.group()
def doc():
    """Document processing commands"""
    pass


@doc.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.option("--output", "-o", help="Output directory for processed documents")
def load(file_path, output):
    """Load and process a document"""
    try:
        from langchain_llm_toolkit import DocumentLoader

        console.print(f"[bold blue]Loading document:[/] {file_path}")

        loader = DocumentLoader()
        documents = loader.load_document(file_path)

        console.print(f"[green]✓[/] Successfully loaded {len(documents)} document(s)")

        table = Table(title="Document Information")
        table.add_column("Index", style="cyan")
        table.add_column("Content Preview", style="green")
        table.add_column("Metadata", style="yellow")

        for i, doc in enumerate(documents[:5]):  # Show first 5 documents
            preview = (
                doc.page_content[:100] + "..." if len(doc.page_content) > 100 else doc.page_content
            )
            metadata = str(doc.metadata)[:50]
            table.add_row(str(i), preview, metadata)

        console.print(table)

        if len(documents) > 5:
            console.print(f"[yellow]... and {len(documents) - 5} more documents[/]")

    except ImportError:
        console.print("[red]Error:[/] langchain-llm-toolkit not installed")
        console.print("[yellow]Install with:[/] pip install langchain-llm-toolkit")
    except Exception as e:
        console.print(f"[red]Error loading document:[/] {str(e)}")


@doc.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.option("--chunk-size", default=1000, help="Chunk size for splitting")
@click.option("--chunk-overlap", default=200, help="Chunk overlap")
@click.option(
    "--method",
    type=click.Choice(["recursive", "character"]),
    default="recursive",
    help="Splitting method",
)
def split(file_path, chunk_size, chunk_overlap, method):
    """Split document into chunks"""
    try:
        from langchain_llm_toolkit import DocumentLoader, TextSplitter

        console.print(f"[bold blue]Splitting document:[/] {file_path}")
        console.print(
            f"[dim]Chunk size: {chunk_size}, Overlap: {chunk_overlap}, Method: {method}[/]"
        )

        loader = DocumentLoader()
        documents = loader.load_document(file_path)

        splitter = TextSplitter()
        split_docs = splitter.split_documents(
            documents, chunk_size=chunk_size, chunk_overlap=chunk_overlap, method=method
        )

        console.print(f"[green]✓[/] Split into {len(split_docs)} chunks")

        table = Table(title="Chunk Preview")
        table.add_column("Index", style="cyan")
        table.add_column("Content Preview", style="green")
        table.add_column("Length", style="yellow")

        for i, doc in enumerate(split_docs[:5]):
            preview = (
                doc.page_content[:80] + "..." if len(doc.page_content) > 80 else doc.page_content
            )
            table.add_row(str(i), preview, str(len(doc.page_content)))

        console.print(table)

        if len(split_docs) > 5:
            console.print(f"[yellow]... and {len(split_docs) - 5} more chunks[/]")

    except ImportError:
        console.print("[red]Error:[/] langchain-llm-toolkit not installed")
        console.print("[yellow]Install with:[/] pip install langchain-llm-toolkit")
    except Exception as e:
        console.print(f"[red]Error splitting document:[/] {str(e)}")


@doc.command()
@click.argument("directory", type=click.Path(exists=True))
def list(directory):
    """List all documents in a directory"""
    from pathlib import Path

    console.print(f"[bold blue]Listing documents in:[/] {directory}")

    dir_path = Path(directory)
    supported_extensions = [".pdf", ".txt", ".docx"]

    documents = []
    for ext in supported_extensions:
        documents.extend(dir_path.glob(f"*{ext}"))

    if not documents:
        console.print("[yellow]No documents found[/]")
        return

    table = Table(title="Documents")
    table.add_column("File Name", style="cyan")
    table.add_column("Size", style="green")
    table.add_column("Type", style="yellow")

    for doc in sorted(documents):
        size = doc.stat().st_size
        size_str = f"{size / 1024:.1f} KB" if size > 1024 else f"{size} B"
        doc_type = doc.suffix[1:].upper()
        table.add_row(doc.name, size_str, doc_type)

    console.print(table)
    console.print(f"[green]Total:[/] {len(documents)} document(s)")

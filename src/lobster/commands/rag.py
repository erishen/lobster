"""RAG (Retrieval Augmented Generation) commands"""

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


@click.group()
def rag():
    """RAG system commands"""
    pass


@rag.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.option(
    "--vector-store",
    type=click.Choice(["faiss", "qdrant"]),
    default="faiss",
    help="Vector store type",
)
@click.option(
    "--embedding-type",
    type=click.Choice(["openai", "ollama"]),
    default="ollama",
    help="Embedding type",
)
@click.option("--embedding-model", default="nomic-embed-text", help="Embedding model (for Ollama)")
def upload(file_path, vector_store, embedding_type, embedding_model):
    """Upload and index a document for RAG"""
    try:
        from langchain_llm_toolkit import RAGSystem
        from langchain_llm_toolkit import DocumentLoader

        console.print("[bold blue]Uploading document to RAG system...[/]")
        console.print(
            f"[dim]File: {file_path}, Vector Store: {vector_store}, Embedding: {embedding_type}[/]"
        )

        loader = DocumentLoader()
        documents = loader.load_document(file_path)

        rag_system = RAGSystem(
            vector_store_type=vector_store,
            embedding_type=embedding_type,
            embedding_model=embedding_model,
        )

        with console.status("[bold green]Processing and indexing..."):
            rag_system.create_vector_store(documents)
            rag_system.save_vector_store(".lobster_vector_store")

        console.print("[green]✓[/] Document successfully indexed")
        console.print(f"[dim]Vector store type: {vector_store}, Embedding: {embedding_type}[/]")
        console.print("[dim]Vector store saved to: .lobster_vector_store[/]")

    except ImportError:
        console.print("[red]Error:[/] langchain-llm-toolkit not installed")
        console.print("[yellow]Install with:[/] pip install langchain-llm-toolkit")
    except Exception as e:
        console.print(f"[red]Error uploading document:[/] {str(e)}")


@rag.command()
@click.argument("query")
@click.option("--k", default=4, help="Number of documents to retrieve")
@click.option(
    "--vector-store",
    type=click.Choice(["faiss", "qdrant"]),
    default="faiss",
    help="Vector store type",
)
@click.option(
    "--embedding-type",
    type=click.Choice(["openai", "ollama"]),
    default="ollama",
    help="Embedding type",
)
@click.option("--embedding-model", default="nomic-embed-text", help="Embedding model (for Ollama)")
@click.option("--model", default="ollama/gemma3", help="LLM model for answer generation")
def query(query, k, vector_store, embedding_type, embedding_model, model):
    """Query the RAG system"""
    try:
        from langchain_llm_toolkit import RAGSystem
        from pathlib import Path

        console.print("[bold blue]Querying RAG system...[/]")
        console.print(f"[dim]Query: {query}[/]")

        rag_system = RAGSystem(
            vector_store_type=vector_store,
            embedding_type=embedding_type,
            embedding_model=embedding_model,
            llm_model=model,
        )

        vector_store_path = Path(".lobster_vector_store")
        if not vector_store_path.exists():
            console.print(
                "[red]Error:[/] No vector store found. "
                "Please upload documents first using 'lobster rag upload'"
            )
            return

        rag_system.load_vector_store(str(vector_store_path))

        with console.status("[bold green]Searching and generating answer..."):
            answer, relevant_docs = rag_system.generate_answer(query, k=k)

        console.print(Panel(answer, title="[bold green]Answer[/]", border_style="green"))

        if relevant_docs:
            console.print("\n[bold yellow]Sources:[/]")

            table = Table()
            table.add_column("Index", style="cyan")
            table.add_column("Content Preview", style="green")

            for i, doc in enumerate(relevant_docs[:3]):
                preview = (
                    doc.page_content[:100] + "..."
                    if len(doc.page_content) > 100
                    else doc.page_content
                )
                table.add_row(str(i), preview)

            console.print(table)

    except ImportError:
        console.print("[red]Error:[/] langchain-llm-toolkit not installed")
        console.print("[yellow]Install with:[/] pip install langchain-llm-toolkit")
    except Exception as e:
        console.print(f"[red]Error querying RAG:[/] {str(e)}")


@rag.command()
@click.argument("query")
@click.option("--k", default=4, help="Number of documents to retrieve")
@click.option(
    "--vector-store",
    type=click.Choice(["faiss", "qdrant"]),
    default="faiss",
    help="Vector store type",
)
@click.option(
    "--embedding-type",
    type=click.Choice(["openai", "ollama"]),
    default="ollama",
    help="Embedding type",
)
@click.option("--embedding-model", default="nomic-embed-text", help="Embedding model (for Ollama)")
def search(query, k, vector_store, embedding_type, embedding_model):
    """Search for similar documents without generating answer"""
    try:
        from langchain_llm_toolkit import RAGSystem
        from pathlib import Path

        console.print("[bold blue]Searching for similar documents...[/]")
        console.print(f"[dim]Query: {query}, k={k}[/]")

        rag_system = RAGSystem(
            vector_store_type=vector_store,
            embedding_type=embedding_type,
            embedding_model=embedding_model,
        )

        vector_store_path = Path(".lobster_vector_store")
        if not vector_store_path.exists():
            console.print(
                "[red]Error:[/] No vector store found. "
                "Please upload documents first using 'lobster rag upload'"
            )
            return

        rag_system.load_vector_store(str(vector_store_path))

        with console.status("[bold green]Searching..."):
            results = rag_system.retrieve_documents(query, k=k)

        if not results:
            console.print("[yellow]No similar documents found[/]")
            return

        console.print(f"[green]✓[/] Found {len(results)} similar document(s)\n")

        table = Table(title="Similar Documents")
        table.add_column("Index", style="cyan")
        table.add_column("Content Preview", style="green")
        table.add_column("Metadata", style="yellow")

        for i, doc in enumerate(results):
            preview = (
                doc.page_content[:100] + "..." if len(doc.page_content) > 100 else doc.page_content
            )
            metadata = str(doc.metadata)[:50]
            table.add_row(str(i), preview, metadata)

        console.print(table)

    except ImportError:
        console.print("[red]Error:[/] langchain-llm-toolkit not installed")
        console.print("[yellow]Install with:[/] pip install langchain-llm-toolkit")
    except Exception as e:
        console.print(f"[red]Error searching documents:[/] {str(e)}")


@rag.command()
@click.argument("query")
@click.option("--k", default=4, help="Number of documents to retrieve")
@click.option(
    "--vector-store",
    type=click.Choice(["faiss", "qdrant"]),
    default="faiss",
    help="Vector store type",
)
@click.option(
    "--embedding-type",
    type=click.Choice(["openai", "ollama"]),
    default="ollama",
    help="Embedding type",
)
@click.option("--embedding-model", default="nomic-embed-text", help="Embedding model (for Ollama)")
@click.option("--model", default="ollama/gemma3", help="LLM model for summarization")
def summarize(query, k, vector_store, embedding_type, embedding_model, model):
    """Generate a summary from retrieved documents"""
    try:
        from langchain_llm_toolkit import RAGSystem
        from pathlib import Path

        console.print("[bold blue]Generating summary...[/]")
        console.print(f"[dim]Query: {query}[/]")

        rag_system = RAGSystem(
            vector_store_type=vector_store,
            embedding_type=embedding_type,
            embedding_model=embedding_model,
            llm_model=model,
        )

        vector_store_path = Path(".lobster_vector_store")
        if not vector_store_path.exists():
            console.print(
                "[red]Error:[/] No vector store found. "
                "Please upload documents first using 'lobster rag upload'"
            )
            return

        rag_system.load_vector_store(str(vector_store_path))

        with console.status("[bold green]Retrieving and summarizing..."):
            documents = rag_system.retrieve_documents(query, k=k)
            if not documents:
                console.print("[yellow]No documents found for the query[/]")
                return
            summary = rag_system.generate_summary(documents)

        console.print(Panel(summary, title="[bold green]Summary[/]", border_style="green"))

    except ImportError:
        console.print("[red]Error:[/] langchain-llm-toolkit not installed")
        console.print("[yellow]Install with:[/] pip install langchain-llm-toolkit")
    except Exception as e:
        console.print(f"[red]Error generating summary:[/] {str(e)}")


@rag.command()
def info():
    """Show RAG system information"""
    try:
        console.print("[bold blue]RAG System Information[/]")
        console.print("[dim]RAG system is ready to use[/]")
        console.print("[dim]Upload documents first using 'lobster rag upload'[/]")

    except Exception as e:
        console.print(f"[red]Error getting RAG info:[/] {str(e)}")

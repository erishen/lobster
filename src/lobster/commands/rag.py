"""RAG (Retrieval Augmented Generation) commands"""

import click
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


@click.group()
def rag():
    """RAG system commands"""
    pass


@rag.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--vector-store', type=click.Choice(['faiss', 'qdrant']), default='faiss', help='Vector store type')
@click.option('--embedding-type', type=click.Choice(['openai', 'ollama']), default='ollama', help='Embedding type')
@click.option('--embedding-model', default='nomic-embed-text', help='Embedding model (for Ollama)')
def upload(file_path, vector_store, embedding_type, embedding_model):
    """Upload and index a document for RAG"""
    try:
        from langchain_llm_toolkit import RAGSystem
        from langchain_llm_toolkit import DocumentLoader
        
        console.print(f"[bold blue]Uploading document to RAG system...[/]")
        console.print(f"[dim]File: {file_path}, Vector Store: {vector_store}, Embedding: {embedding_type}[/]")
        
        # 加载文档
        loader = DocumentLoader()
        documents = loader.load_document(file_path)
        
        # 创建 RAG 系统并初始化向量存储
        rag_system = RAGSystem(vector_store_type=vector_store, embedding_type=embedding_type, embedding_model=embedding_model)
        
        with console.status("[bold green]Processing and indexing..."):
            rag_system.create_vector_store(documents)
        
        console.print(f"[green]✓[/] Document successfully indexed")
        console.print(f"[dim]Vector store type: {vector_store}, Embedding: {embedding_type}[/]")
        
    except ImportError:
        console.print("[red]Error:[/] langchain-llm-toolkit not installed")
        console.print("[yellow]Install with:[/] pip install langchain-llm-toolkit")
    except Exception as e:
        console.print(f"[red]Error uploading document:[/] {str(e)}")


@rag.command()
@click.argument('query')
@click.option('--k', default=4, help='Number of documents to retrieve')
@click.option('--vector-store', type=click.Choice(['faiss', 'qdrant']), default='faiss', help='Vector store type')
@click.option('--model', default='ollama/gemma3', help='Model for answer generation')
def query(query, k, vector_store, model):
    """Query the RAG system"""
    try:
        from langchain_llm_toolkit import RAGSystem
        
        console.print(f"[bold blue]Querying RAG system...[/]")
        console.print(f"[dim]Query: {query}[/]")
        
        rag_system = RAGSystem(vector_store_type=vector_store)
        
        with console.status("[bold green]Searching and generating answer..."):
            result = rag_system.query(query, k=k)
        
        console.print(Panel(result['answer'], title="[bold green]Answer[/]", border_style="green"))
        
        if result.get('sources'):
            console.print("\n[bold yellow]Sources:[/]")
            
            table = Table()
            table.add_column("Index", style="cyan")
            table.add_column("Content Preview", style="green")
            table.add_column("Score", style="yellow")
            
            for i, source in enumerate(result['sources'][:3]):
                preview = source['content'][:100] + "..." if len(source['content']) > 100 else source['content']
                score = f"{source.get('score', 0):.3f}"
                table.add_row(str(i), preview, score)
            
            console.print(table)
        
    except ImportError:
        console.print("[red]Error:[/] langchain-llm-toolkit not installed")
        console.print("[yellow]Install with:[/] pip install langchain-llm-toolkit")
    except Exception as e:
        console.print(f"[red]Error querying RAG:[/] {str(e)}")


@rag.command()
@click.argument('query')
@click.option('--k', default=4, help='Number of documents to retrieve')
def search(query, k):
    """Search for similar documents without generating answer"""
    try:
        from langchain_llm_toolkit import RAGSystem
        
        console.print(f"[bold blue]Searching for similar documents...[/]")
        console.print(f"[dim]Query: {query}, k={k}[/]")
        
        rag_system = RAGSystem()
        
        with console.status("[bold green]Searching..."):
            results = rag_system.similarity_search(query, k=k)
        
        if not results:
            console.print("[yellow]No similar documents found[/]")
            return
        
        console.print(f"[green]✓[/] Found {len(results)} similar document(s)\n")
        
        table = Table(title="Similar Documents")
        table.add_column("Index", style="cyan")
        table.add_column("Content Preview", style="green")
        table.add_column("Metadata", style="yellow")
        
        for i, doc in enumerate(results):
            preview = doc.page_content[:100] + "..." if len(doc.page_content) > 100 else doc.page_content
            metadata = str(doc.metadata)[:50]
            table.add_row(str(i), preview, metadata)
        
        console.print(table)
        
    except ImportError:
        console.print("[red]Error:[/] langchain-llm-toolkit not installed")
        console.print("[yellow]Install with:[/] pip install langchain-llm-toolkit")
    except Exception as e:
        console.print(f"[red]Error searching documents:[/] {str(e)}")


@rag.command()
@click.argument('query')
def summarize(query):
    """Generate a summary from retrieved documents"""
    try:
        from langchain_llm_toolkit import RAGSystem
        
        console.print(f"[bold blue]Generating summary...[/]")
        console.print(f"[dim]Query: {query}[/]")
        
        rag_system = RAGSystem()
        
        with console.status("[bold green]Retrieving and summarizing..."):
            summary = rag_system.generate_summary(query)
        
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

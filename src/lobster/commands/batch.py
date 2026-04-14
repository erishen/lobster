"""Batch processing commands"""

import click
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from typing import List
import concurrent.futures
import time

console = Console()


@click.group()
def batch():
    """Batch processing commands"""
    pass


@batch.command()
@click.argument('directory', type=click.Path(exists=True))
@click.option('--output', '-o', default='./output', help='Output directory')
@click.option('--chunk-size', default=1000, help='Chunk size for splitting')
@click.option('--pattern', default='*.txt', help='File pattern to process')
def split(directory, output, chunk_size, pattern):
    """Batch split documents in a directory"""
    from langchain_llm_toolkit import DocumentLoader, TextSplitter
    from pathlib import Path
    
    dir_path = Path(directory)
    output_path = Path(output)
    output_path.mkdir(parents=True, exist_ok=True)
    
    files = list(dir_path.glob(pattern))
    
    if not files:
        console.print(f"[yellow]No files found matching pattern: {pattern}[/]")
        return
    
    console.print(f"[bold blue]Batch splitting {len(files)} files...[/]")
    
    loader = DocumentLoader()
    splitter = TextSplitter()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("[cyan]Processing files...", total=len(files))
        
        total_chunks = 0
        for file in files:
            try:
                documents = loader.load_document(str(file))
                split_docs = splitter.split_documents(documents, chunk_size=chunk_size)
                
                output_file = output_path / f"{file.stem}_chunks.txt"
                with open(output_file, 'w', encoding='utf-8') as f:
                    for i, doc in enumerate(split_docs):
                        f.write(f"--- Chunk {i+1} ---\n")
                        f.write(doc.page_content)
                        f.write("\n\n")
                
                total_chunks += len(split_docs)
                progress.advance(task)
                
            except Exception as e:
                console.print(f"[red]Error processing {file.name}:[/] {str(e)}")
    
    console.print(f"[green]✓[/] Processed {len(files)} files into {total_chunks} chunks")
    console.print(f"[dim]Output saved to: {output_path.absolute()}[/]")


@batch.command()
@click.argument('directory', type=click.Path(exists=True))
@click.option('--output', '-o', default='./processed', help='Output directory')
@click.option('--pattern', default='*.txt', help='File pattern to process')
def load(directory, output, pattern):
    """Batch load and analyze documents"""
    from langchain_llm_toolkit import DocumentLoader
    from pathlib import Path
    
    dir_path = Path(directory)
    output_path = Path(output)
    output_path.mkdir(parents=True, exist_ok=True)
    
    files = list(dir_path.glob(pattern))
    
    if not files:
        console.print(f"[yellow]No files found matching pattern: {pattern}[/]")
        return
    
    console.print(f"[bold blue]Batch loading {len(files)} files...[/]")
    
    loader = DocumentLoader()
    
    results = []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("[cyan]Loading files...", total=len(files))
        
        for file in files:
            try:
                documents = loader.load_document(str(file))
                
                result = {
                    "file": file.name,
                    "documents": len(documents),
                    "total_chars": sum(len(doc.page_content) for doc in documents),
                    "status": "success"
                }
                results.append(result)
                
                progress.advance(task)
                
            except Exception as e:
                results.append({
                    "file": file.name,
                    "documents": 0,
                    "total_chars": 0,
                    "status": f"error: {str(e)}"
                })
                progress.advance(task)
    
    table = Table(title="Batch Load Results")
    table.add_column("File", style="cyan")
    table.add_column("Documents", style="green")
    table.add_column("Characters", style="yellow")
    table.add_column("Status", style="magenta")
    
    for result in results:
        table.add_row(
            result["file"],
            str(result["documents"]),
            str(result["total_chars"]),
            result["status"]
        )
    
    console.print(table)
    
    total_docs = sum(r["documents"] for r in results)
    total_chars = sum(r["total_chars"] for r in results)
    success_count = sum(1 for r in results if r["status"] == "success")
    
    console.print(f"\n[green]✓[/] Successfully loaded {success_count}/{len(files)} files")
    console.print(f"[dim]Total: {total_docs} documents, {total_chars} characters[/]")


@batch.command()
@click.argument('directory', type=click.Path(exists=True))
@click.option('--vector-store', type=click.Choice(['faiss', 'qdrant']), default='faiss', help='Vector store type')
@click.option('--embedding-type', type=click.Choice(['openai', 'ollama']), default='ollama', help='Embedding type')
@click.option('--pattern', default='*.txt', help='File pattern to process')
def index(directory, vector_store, embedding_type, pattern):
    """Batch index documents to vector store"""
    from langchain_llm_toolkit import RAGSystem, DocumentLoader
    from pathlib import Path
    
    dir_path = Path(directory)
    files = list(dir_path.glob(pattern))
    
    if not files:
        console.print(f"[yellow]No files found matching pattern: {pattern}[/]")
        return
    
    console.print(f"[bold blue]Batch indexing {len(files)} files...[/]")
    console.print(f"[dim]Vector store: {vector_store}, Embedding: {embedding_type}[/]")
    
    loader = DocumentLoader()
    
    all_documents = []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("[cyan]Loading documents...", total=len(files))
        
        for file in files:
            try:
                documents = loader.load_document(str(file))
                all_documents.extend(documents)
                progress.advance(task)
            except Exception as e:
                console.print(f"[red]Error loading {file.name}:[/] {str(e)}")
                progress.advance(task)
    
    if not all_documents:
        console.print("[red]Error:[/] No documents loaded")
        return
    
    console.print(f"[dim]Total documents: {len(all_documents)}[/]")
    
    with console.status("[bold green]Creating vector store..."):
        rag_system = RAGSystem(vector_store_type=vector_store, embedding_type=embedding_type)
        rag_system.create_vector_store(all_documents)
    
    console.print(f"[green]✓[/] Successfully indexed {len(all_documents)} documents from {len(files)} files")


@batch.command()
@click.argument('prompts_file', type=click.Path(exists=True))
@click.option('--output', '-o', default='./responses.txt', help='Output file for responses')
@click.option('--model', '-m', default='ollama/gemma3', help='Model to use')
@click.option('--temperature', '-t', default=0.7, help='Temperature parameter')
def generate(prompts_file, output, model, temperature):
    """Batch generate responses from a file of prompts"""
    from langchain_llm_toolkit import LLMIntegration
    from pathlib import Path
    
    prompts_path = Path(prompts_file)
    output_path = Path(output)
    
    with open(prompts_path, 'r', encoding='utf-8') as f:
        prompts = [line.strip() for line in f if line.strip()]
    
    if not prompts:
        console.print("[yellow]No prompts found in file[/]")
        return
    
    console.print(f"[bold blue]Batch generating responses for {len(prompts)} prompts...[/]")
    console.print(f"[dim]Model: {model}, Temperature: {temperature}[/]")
    
    llm = LLMIntegration()
    llm.set_model(model)
    llm.set_temperature(temperature)
    
    responses = []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("[cyan]Generating responses...", total=len(prompts))
        
        for i, prompt in enumerate(prompts):
            try:
                response = llm.generate(prompt)
                responses.append({
                    "prompt": prompt,
                    "response": response,
                    "status": "success"
                })
            except Exception as e:
                responses.append({
                    "prompt": prompt,
                    "response": "",
                    "status": f"error: {str(e)}"
                })
            
            progress.advance(task)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        for i, resp in enumerate(responses):
            f.write(f"--- Prompt {i+1} ---\n")
            f.write(f"{resp['prompt']}\n\n")
            f.write(f"--- Response ---\n")
            f.write(f"{resp['response']}\n\n\n")
    
    success_count = sum(1 for r in responses if r["status"] == "success")
    
    console.print(f"[green]✓[/] Generated {success_count}/{len(prompts)} responses")
    console.print(f"[dim]Output saved to: {output_path.absolute()}[/]")

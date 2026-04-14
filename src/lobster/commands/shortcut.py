"""快捷命令模块 - 提供常用命令的快捷方式"""

import click
from rich.console import Console
from rich.panel import Panel

from langchain_llm_toolkit import LLMIntegration
from lobster.core.config import ConfigManager

console = Console()


@click.command()
@click.argument('question')
@click.option('--model', '-m', default=None, help='指定使用的模型')
@click.option('--stream', '-s', is_flag=True, help='流式输出')
def ask(question, model, stream):
    """快速提问 - lobster ask "你的问题"
    
    示例:
        lobster ask "什么是 AI?"
        lobster ask "解释下 Python 装饰器" -m ollama/llama3
        lobster ask "讲个故事" -s
    """
    config = ConfigManager()
    model = model or config.get('default_model', 'ollama/gemma3')
    
    console.print(Panel(f"🤔 [bold cyan]{question}[/bold cyan]", title="问题", border_style="blue"))
    
    llm = LLMIntegration()
    llm.set_model(model)
    
    if stream:
        console.print("\n💡 [bold green]回答:[/bold green]")
        for chunk in llm.generate_stream(question):
            console.print(chunk, end="")
        console.print("\n")
    else:
        with console.status("[bold green]思考中...[/bold green]"):
            response = llm.generate(question)
        console.print(f"\n💡 [bold green]回答:[/bold green]\n{response}\n")


@click.command()
@click.argument('query_text')
@click.option('--k', '-k', default=3, help='返回结果数量')
@click.option('--model', '-m', default=None, help='指定使用的模型')
def query(query_text, k, model):
    """快速查询 RAG - lobster query "你的问题"
    
    示例:
        lobster query "项目的主要功能是什么?"
        lobster query "如何使用?" -k 5
    """
    from langchain_llm_toolkit import RAGSystem
    
    config = ConfigManager()
    model = model or config.get('default_model', 'ollama/gemma3')
    
    console.print(Panel(f"🔍 [bold cyan]{query_text}[/bold cyan]", title="查询", border_style="blue"))
    
    with console.status("[bold green]搜索中...[/bold green]"):
        rag = RAGSystem()
        answer, docs = rag.query(query_text, k=k)
    
    console.print(f"\n💡 [bold green]回答:[/bold green]\n{answer}\n")
    
    if docs:
        console.print(f"\n📚 [bold yellow]相关文档 ({len(docs)} 条):[/bold yellow]")
        for i, doc in enumerate(docs, 1):
            content = doc.page_content[:100] + "..." if len(doc.page_content) > 100 else doc.page_content
            console.print(f"  {i}. {content}")


@click.command()
@click.argument('content')
@click.option('--tags', '-t', multiple=True, help='添加标签')
@click.option('--category', '-c', default='general', help='分类')
def remember(content, tags, category):
    """快速记忆 - lobster remember "内容"
    
    示例:
        lobster remember "OpenClaw 是一个 AI 助手项目"
        lobster remember "重要配置" -t config -t important
    """
    from langchain_llm_toolkit import RAGSystem
    from datetime import datetime
    import json
    from pathlib import Path
    
    console.print(Panel(f"📝 [bold cyan]{content}[/bold cyan]", title="记忆", border_style="blue"))
    
    memory_dir = Path(".lobster_memory")
    memory_dir.mkdir(exist_ok=True)
    
    memory_data = {
        "content": content,
        "tags": list(tags),
        "category": category,
        "timestamp": datetime.now().isoformat(),
    }
    
    index_file = memory_dir / "memory_index.json"
    if index_file.exists():
        with open(index_file, 'r') as f:
            memories = json.load(f)
    else:
        memories = []
    
    memory_id = len(memories) + 1
    memory_data["id"] = memory_id
    memories.append(memory_data)
    
    with open(index_file, 'w') as f:
        json.dump(memories, f, indent=2)
    
    rag = RAGSystem(vector_store_type="faiss", embedding_type="ollama")
    rag.add_documents_from_text(content, metadatas=[{"id": memory_id, "tags": ",".join(tags)}])
    
    console.print(f"✅ [bold green]已记住！[/bold green] ID: {memory_id}")
    if tags:
        console.print(f"🏷️  标签: {', '.join(tags)}")


@click.command()
@click.argument('search_text')
def recall(search_text):
    """快速回忆 - lobster recall "关键词"
    
    示例:
        lobster recall "OpenClaw"
        lobster recall "配置"
    """
    from langchain_llm_toolkit import RAGSystem
    
    console.print(Panel(f"🧠 [bold cyan]{search_text}[/bold cyan]", title="回忆", border_style="blue"))
    
    with console.status("[bold green]搜索记忆中...[/bold green]"):
        rag = RAGSystem(vector_store_type="faiss", embedding_type="ollama")
        results = rag.search(search_text, k=5)
    
    if results:
        console.print(f"\n💭 [bold green]找到 {len(results)} 条相关记忆:[/bold green]\n")
        for i, doc in enumerate(results, 1):
            console.print(f"  {i}. {doc.page_content}")
            if doc.metadata:
                tags = doc.metadata.get('tags', '')
                if tags:
                    console.print(f"     🏷️  {tags}")
    else:
        console.print("\n❌ [bold red]没有找到相关记忆[/bold red]")


@click.command()
def status():
    """快速状态检查 - lobster status
    
    显示系统状态、模型信息、记忆统计等
    """
    from pathlib import Path
    import json
    
    console.print(Panel("🦞 [bold cyan]Lobster 状态[/bold cyan]", border_style="blue"))
    
    config = ConfigManager()
    
    console.print("\n📊 [bold]系统信息[/bold]")
    console.print(f"  版本: 0.1.0")
    console.print(f"  配置文件: {config.config_file}")
    
    console.print("\n🤖 [bold]模型配置[/bold]")
    console.print(f"  默认模型: {config.get('default_model', '未设置')}")
    
    memory_dir = Path(".lobster_memory")
    if memory_dir.exists():
        index_file = memory_dir / "memory_index.json"
        if index_file.exists():
            with open(index_file, 'r') as f:
                memories = json.load(f)
            console.print(f"\n🧠 [bold]记忆统计[/bold]")
            console.print(f"  总记忆数: {len(memories)}")
            
            tags_count = {}
            for m in memories:
                for tag in m.get('tags', []):
                    tags_count[tag] = tags_count.get(tag, 0) + 1
            if tags_count:
                console.print(f"  标签分布: {dict(tags_count)}")
    
    console.print("\n✅ [bold green]系统正常[/bold green]\n")

"""快捷命令模块 - 提供常用命令的快捷方式"""

import click
from rich.console import Console
from rich.panel import Panel

from lobster.core.llm_client import get_llm_client
from lobster.core.memory_store import MemoryManager
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
    
    llm = get_llm_client(model)
    
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
    """快速查询 - lobster query "你的问题"
    
    示例:
        lobster query "项目的主要功能是什么?"
        lobster query "如何使用?" -k 5
    """
    config = ConfigManager()
    model = model or config.get('default_model', 'ollama/gemma3')
    
    console.print(Panel(f"🔍 [bold cyan]{query_text}[/bold cyan]", title="查询", border_style="blue"))
    
    # 使用简单的记忆搜索
    memory = MemoryManager()
    results = memory.search_memory(query_text, k=k)
    
    if results:
        console.print(f"\n� [bold green]找到 {len(results)} 条相关记忆:[/bold green]\n")
        for i, mem in enumerate(results, 1):
            console.print(f"  {i}. {mem['content']}")
            tags = mem.get('metadata', {}).get('tags', [])
            if tags:
                console.print(f"     🏷  {', '.join(tags)}")
    else:
        console.print("\n❌ [bold red]没有找到相关记忆[/bold red]")


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
    console.print(Panel(f"📝 [bold cyan]{content}[/bold cyan]", title="记忆", border_style="blue"))
    
    # 使用简单的记忆存储
    memory = MemoryManager()
    memory_id = memory.add_memory(
        content=content,
        tags=list(tags),
        category=category,
    )
    
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
    console.print(Panel(f"🧠 [bold cyan]{search_text}[/bold cyan]", title="回忆", border_style="blue"))
    
    # 使用简单的记忆搜索
    memory = MemoryManager()
    results = memory.search_memory(search_text, k=5)
    
    if results:
        console.print(f"\n💭 [bold green]找到 {len(results)} 条相关记忆:[/bold green]\n")
        for i, mem in enumerate(results, 1):
            console.print(f"  {i}. {mem['content']}")
            tags = mem.get('metadata', {}).get('tags', [])
            if tags:
                console.print(f"     🏷  {', '.join(tags)}")
    else:
        console.print("\n❌ [bold red]没有找到相关记忆[/bold red]")


@click.command()
def status():
    """快速状态检查 - lobster status
    
    显示系统状态、模型信息、记忆统计等
    """
    console.print(Panel("🦞 [bold cyan]Lobster 状态[/bold cyan]", border_style="blue"))
    
    config = ConfigManager()
    
    console.print("\n📊 [bold]系统信息[/bold]")
    console.print(f"  版本: 0.1.0")
    console.print(f"  配置文件: {config.config_file}")
    
    console.print("\n🤖 [bold]模型配置[/bold]")
    console.print(f"  默认模型: {config.get('default_model', '未设置')}")
    
    # 使用简单的记忆管理
    memory = MemoryManager()
    stats = memory.get_stats()
    
    console.print(f"\n🧠 [bold]记忆统计[/bold]")
    console.print(f"  总记忆数: {stats['total']}")
    
    if stats['categories']:
        console.print(f"  分类分布: {stats['categories']}")
    
    if stats['tags']:
        console.print(f"  标签分布: {stats['tags']}")
    
    console.print("\n✅ [bold green]系统正常[/bold green]\n")

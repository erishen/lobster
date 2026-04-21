"""Serena 代码分析命令模块"""

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax
import json

console = Console()


@click.group()
def serena():
    """Serena 代码分析工具 - IDE 级别的代码理解能力"""
    pass


@serena.command()
@click.argument("project_path", type=click.Path(exists=True), required=False)
def init(project_path):
    """初始化 Serena - lobster serena init [project_path]

    示例:
        lobster serena init
        lobster serena init /path/to/project
    """
    from lobster.core.serena_client import get_serena_client
    import os

    client = get_serena_client()

    if not client.is_available():
        console.print("[red]Error: Serena 未安装或未配置[/]")
        console.print("[yellow]请设置 SERENA_DIR 环境变量:[/]")
        console.print("  export SERENA_DIR=/path/to/serena")
        return

    if project_path is None:
        project_path = os.getcwd()

    console.print(
        Panel(f"🔧 [bold cyan]初始化 Serena: {project_path}[/bold cyan]", border_style="blue")
    )

    result = client.initialize(project_path)

    if result.get("success"):
        console.print("[green]✓ Serena 初始化成功[/]")
        console.print(f"  项目路径: {result.get('project')}")
        console.print(f"  语言后端: {result.get('language_backend')}")
        console.print(f"  可用工具: {len(result.get('available_tools', []))} 个")
    else:
        console.print(f"[red]✗ 初始化失败: {result.get('error')}[/]")


@serena.command()
def status():
    """检查 Serena 状态 - lobster serena status"""
    from lobster.core.serena_client import get_serena_client

    client = get_serena_client()

    console.print(Panel("📊 [bold cyan]Serena 状态[/bold cyan]", border_style="blue"))

    result = client.get_current_config()

    table = Table()
    table.add_column("项目", style="cyan")
    table.add_column("值", style="green")

    table.add_row("可用", "✓ 是" if result.get("available") else "✗ 否")
    table.add_row("已初始化", "✓ 是" if result.get("initialized") else "✗ 否")
    table.add_row("Serena 目录", result.get("serena_dir", "未设置"))

    if result.get("config"):
        table.add_row("项目路径", result["config"].get("project_path", "N/A"))
        table.add_row("语言后端", result["config"].get("language_backend", "N/A"))

    console.print(table)


@serena.command()
@click.argument("file_path")
@click.option("--depth", "-d", default=1, help="符号深度")
def symbols(file_path, depth):
    """获取文件符号概览 - lobster serena symbols <file>

    示例:
        lobster serena symbols src/main.py
        lobster serena symbols config.py -d 2
    """
    from lobster.core.serena_client import get_serena_client

    client = get_serena_client()

    if not client.is_initialized():
        console.print("[yellow]正在初始化...[/]")
        import os

        client.initialize(os.getcwd())

    console.print(Panel(f"📋 [bold cyan]符号概览: {file_path}[/bold cyan]", border_style="blue"))

    result = client.get_symbols_overview(file_path, depth=depth)

    if isinstance(result, dict):
        for kind, symbols in result.items():
            if symbols:
                console.print(f"\n[bold green]{kind}:[/]")
                for s in symbols[:10]:
                    name = s.get("name_path", s.get("name", "unknown"))
                    line = s.get("line", s.get("body_location", {}).get("start_line", ""))
                    console.print(f"  • {name}" + (f" (L{line})" if line else ""))
    else:
        console.print(f"[red]Error: {result}[/]")


@serena.command()
@click.argument("symbol_name")
@click.option("--file", "-f", "file_path", default=None, help="限制搜索文件")
@click.option("--body", "-b", is_flag=True, help="显示符号体")
def find(symbol_name, file_path, body):
    """查找符号 - lobster serena find <symbol>

    示例:
        lobster serena find MyClass
        lobster serena find main -f src/main.py
        lobster serena find calculate -b
    """
    from lobster.core.serena_client import get_serena_client

    client = get_serena_client()

    if not client.is_initialized():
        console.print("[yellow]正在初始化...[/]")
        import os

        client.initialize(os.getcwd())

    console.print(Panel(f"🔍 [bold cyan]查找符号: {symbol_name}[/bold cyan]", border_style="blue"))

    result = client.find_symbol(symbol_name, relative_path=file_path, include_body=body)

    if isinstance(result, list):
        for i, s in enumerate(result[:5], 1):
            name = s.get("name_path", "unknown")
            kind = s.get("kind", "unknown")
            path = s.get("relative_path", "")
            line = s.get("line", s.get("body_location", {}).get("start_line", ""))

            console.print(f"\n[bold green]{i}. {name}[/] ([dim]{kind}[/])")
            console.print(f"   文件: {path}" + (f" (L{line})" if line else ""))

            if body and s.get("body"):
                console.print("\n[dim]代码:[/]")
                syntax = Syntax(s["body"], "python", theme="monokai", line_numbers=True)
                console.print(syntax)
    else:
        console.print(f"[red]Error: {result}[/]")


@serena.command()
@click.argument("pattern")
@click.option("--glob", "-g", "glob_pattern", default=None, help="文件 glob 模式")
@click.option("--context", "-c", default=2, help="上下文行数")
def search(pattern, glob_pattern, context):
    """正则搜索代码 - lobster serena search <pattern>

    示例:
        lobster serena search "def.*init"
        lobster serena search "TODO" -g "*.py"
        lobster serena search "import" -c 3
    """
    from lobster.core.serena_client import get_serena_client

    client = get_serena_client()

    if not client.is_initialized():
        console.print("[yellow]正在初始化...[/]")
        import os

        client.initialize(os.getcwd())

    console.print(Panel(f"🔎 [bold cyan]搜索: {pattern}[/bold cyan]", border_style="blue"))

    result = client.search_for_pattern(
        pattern,
        paths_include_glob=glob_pattern,
        context_lines_before=context,
        context_lines_after=context,
    )

    if isinstance(result, dict):
        for file_path, matches in list(result.items())[:10]:
            console.print(f"\n[bold green]{file_path}:[/]")
            for m in matches[:5]:
                line = m.get("line", "")
                content = m.get("content", "")
                console.print(f"  L{line}: {content[:100]}")
    else:
        console.print(f"[red]Error: {result}[/]")


@serena.command()
@click.argument("file_mask")
@click.option("--path", "-p", "relative_path", default=".", help="搜索路径")
def find_file(file_mask, relative_path):
    """查找文件 - lobster serena find-file <pattern>

    示例:
        lobster serena find-file config.py
        lobster serena find-file "*.json" -p src
    """
    from lobster.core.serena_client import get_serena_client

    client = get_serena_client()

    if not client.is_initialized():
        console.print("[yellow]正在初始化...[/]")
        import os

        client.initialize(os.getcwd())

    console.print(Panel(f"📁 [bold cyan]查找文件: {file_mask}[/bold cyan]", border_style="blue"))

    result = client.find_file(file_mask, relative_path)

    if isinstance(result, dict):
        files = result.get("files", result)
        if isinstance(files, list):
            for f in files[:20]:
                if isinstance(f, dict):
                    console.print(f"  • {f.get('path', f.get('name', str(f)))}")
                else:
                    console.print(f"  • {f}")
        else:
            console.print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        console.print(f"[red]Error: {result}[/]")


@serena.command()
@click.argument("symbol_name")
@click.argument("file_path")
def refs(symbol_name, file_path):
    """查找符号引用 - lobster serena refs <symbol> <file>

    示例:
        lobster serena refs MyClass src/main.py
        lobster serena refs calculate utils/math.py
    """
    from lobster.core.serena_client import get_serena_client

    client = get_serena_client()

    if not client.is_initialized():
        console.print("[yellow]正在初始化...[/]")
        import os

        client.initialize(os.getcwd())

    console.print(Panel(f"🔗 [bold cyan]查找引用: {symbol_name}[/bold cyan]", border_style="blue"))

    result = client.find_referencing_symbols(symbol_name, file_path)

    if isinstance(result, list):
        for ref in result[:20]:
            name = ref.get("name", "unknown")
            path = ref.get("relative_path", "")
            line = ref.get("line", "")
            console.print(f"  • {name} in {path}" + (f" (L{line})" if line else ""))
    else:
        console.print(f"[red]Error: {result}[/]")


if __name__ == "__main__":
    serena()

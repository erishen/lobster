"""数据分析工具命令模块"""

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from pathlib import Path
import json

from lobster.core.llm_client import get_llm_client
from lobster.core.config import ConfigManager

console = Console()


@click.group()
def data():
    """数据分析工具"""
    pass


@data.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--model', '-m', default=None, help='指定模型')
def analyze(file_path, model):
    """分析数据文件 - lobster data analyze <file>
    
    示例:
        lobster data analyze data.csv
        lobster data analyze sales.json -m ollama/llama3
    """
    config = ConfigManager()
    model = model or config.get('default_model', 'ollama/gemma3')
    
    console.print(Panel(f"📊 [bold cyan]数据分析: {file_path}[/bold cyan]", border_style="blue"))
    
    # 读取文件
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 显示文件信息
    file_size = Path(file_path).stat().st_size
    console.print(f"\n📁 文件大小: {file_size / 1024:.2f} KB")
    
    llm = get_llm_client(model)
    
    prompt = f"""请分析以下数据文件：

```
{content[:3000]}
```

请提供：
1. **数据概览** - 数据的基本情况
2. **数据结构** - 字段和数据类型
3. **关键洞察** - 重要发现和模式
4. **建议** - 进一步分析建议

请用中文回答。"""
    
    with console.status("[bold green]分析中...[/bold green]"):
        result = llm.generate(prompt)
    
    console.print(f"\n💡 [bold green]分析结果:[/bold green]\n{result}\n")


@data.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--output', '-o', default=None, help='输出文件')
def stats(file_path, output):
    """统计信息 - lobster data stats <file>
    
    示例:
        lobster data stats data.csv
        lobster data stats data.json -o stats.txt
    """
    console.print(Panel(f"📈 [bold cyan]统计信息: {file_path}[/bold cyan]", border_style="blue"))
    
    # 读取文件
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 基本统计
    lines = content.split('\n')
    words = content.split()
    chars = len(content)
    
    table = Table(title="文件统计")
    table.add_column("指标", style="cyan")
    table.add_column("值", style="green")
    
    table.add_row("总行数", str(len(lines)))
    table.add_row("总词数", str(len(words)))
    table.add_row("总字符数", str(chars))
    table.add_row("平均行长", f"{chars / len(lines):.1f}" if lines else "0")
    
    console.print(f"\n{table}\n")
    
    if output:
        with open(output, 'w', encoding='utf-8') as f:
            f.write(f"总行数: {len(lines)}\n")
            f.write(f"总词数: {len(words)}\n")
            f.write(f"总字符数: {chars}\n")
        console.print(f"✅ [bold green]已保存到: {output}[/bold green]\n")


@data.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.argument('output_format', type=click.Choice(['json', 'csv', 'yaml']))
@click.option('--output', '-o', default=None, help='输出文件')
def convert(file_path, output_format, output):
    """格式转换 - lobster data convert <file> <format>
    
    示例:
        lobster data convert data.csv json
        lobster data convert data.json csv -o output.csv
    """
    console.print(Panel(f"🔄 [bold cyan]格式转换: {file_path} -> {output_format}[/bold cyan]", border_style="blue"))
    
    # 读取文件
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 简单的格式转换逻辑
    if output_format == 'json':
        # 尝试解析为 JSON
        try:
            data = json.loads(content)
            result = json.dumps(data, indent=2, ensure_ascii=False)
        except:
            # 如果不是 JSON，创建简单的结构
            lines = content.strip().split('\n')
            data = [{"line": i, "content": line} for i, line in enumerate(lines, 1)]
            result = json.dumps(data, indent=2, ensure_ascii=False)
    
    elif output_format == 'csv':
        # 简单的 CSV 转换
        lines = content.strip().split('\n')
        result = '\n'.join([f'"{line}"' for line in lines])
    
    elif output_format == 'yaml':
        # 简单的 YAML 转换
        lines = content.strip().split('\n')
        result = '\n'.join([f'- {line}' for line in lines])
    
    # 输出结果
    if output:
        with open(output, 'w', encoding='utf-8') as f:
            f.write(result)
        console.print(f"✅ [bold green]已保存到: {output}[/bold green]\n")
    else:
        console.print(f"\n💡 [bold green]转换结果:[/bold green]\n{result}\n")


@data.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--model', '-m', default=None, help='指定模型')
def clean(file_path, model):
    """数据清洗 - lobster data clean <file>
    
    示例:
        lobster data clean data.csv
    """
    config = ConfigManager()
    model = model or config.get('default_model', 'ollama/gemma3')
    
    console.print(Panel(f"🧹 [bold cyan]数据清洗: {file_path}[/bold cyan]", border_style="blue"))
    
    # 读取文件
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    llm = get_llm_client(model)
    
    prompt = f"""请清洗以下数据：

```
{content[:3000]}
```

请提供：
1. **清洗建议** - 需要清洗的问题
2. **清洗步骤** - 具体清洗方法
3. **清洗后数据** - 清洗后的数据示例

请用中文回答。"""
    
    with console.status("[bold green]清洗中...[/bold green]"):
        result = llm.generate(prompt)
    
    console.print(f"\n💡 [bold green]清洗结果:[/bold green]\n{result}\n")


@data.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--model', '-m', default=None, help='指定模型')
def summarize(file_path, model):
    """数据摘要 - lobster data summarize <file>
    
    示例:
        lobster data summarize report.csv
    """
    config = ConfigManager()
    model = model or config.get('default_model', 'ollama/gemma3')
    
    console.print(Panel(f"📝 [bold cyan]数据摘要: {file_path}[/bold cyan]", border_style="blue"))
    
    # 读取文件
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    llm = get_llm_client(model)
    
    prompt = f"""请为以下数据生成摘要：

```
{content[:3000]}
```

请提供：
1. **核心内容** - 数据的主要内容
2. **关键指标** - 重要的数字和指标
3. **趋势分析** - 数据趋势和模式
4. **结论** - 主要结论

请用中文回答，简洁明了。"""
    
    with console.status("[bold green]生成摘要中...[/bold green]"):
        result = llm.generate(prompt)
    
    console.print(f"\n💡 [bold green]数据摘要:[/bold green]\n{result}\n")

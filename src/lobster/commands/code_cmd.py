"""代码工具命令模块"""

import click
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from pathlib import Path

from lobster.core.llm_client import get_llm_client
from lobster.core.config import ConfigManager

console = Console()


@click.group()
def code():
    """代码分析工具"""
    pass


@code.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--model', '-m', default=None, help='指定模型')
def review(file_path, model):
    """代码审查 - lobster code review <file>
    
    示例:
        lobster code review mycode.py
        lobster code review src/main.py -m ollama/llama3
    """
    config = ConfigManager()
    model = model or config.get('default_model', 'ollama/gemma3')
    
    console.print(Panel(f"🔍 [bold cyan]代码审查: {file_path}[/bold cyan]", border_style="blue"))
    
    with open(file_path, 'r') as f:
        code_content = f.read()
    
    console.print("\n📄 [bold]代码内容:[/bold]")
    syntax = Syntax(code_content, "python", theme="monokai", line_numbers=True)
    console.print(syntax)
    
    llm = get_llm_client(model)
    llm.set_model(model)
    
    prompt = f"""请审查以下代码，指出潜在问题和改进建议：

```
{code_content}
```

请从以下方面分析：
1. **代码质量** - 代码风格、可读性
2. **潜在Bug** - 逻辑错误、边界情况
3. **性能问题** - 性能瓶颈、优化建议
4. **最佳实践** - 设计模式、最佳实践
5. **安全风险** - 安全漏洞、风险点

请用中文回答，并给出具体的改进建议。"""
    
    with console.status("[bold green]分析中...[/bold green]"):
        result = llm.generate(prompt)
    
    console.print(f"\n💡 [bold green]审查结果:[/bold green]\n{result}\n")


@code.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--model', '-m', default=None, help='指定模型')
def explain(file_path, model):
    """代码解释 - lobster code explain <file>
    
    示例:
        lobster code explain algorithm.py
        lobster code explain complex.js -m ollama/llama3
    """
    config = ConfigManager()
    model = model or config.get('default_model', 'ollama/gemma3')
    
    console.print(Panel(f"📖 [bold cyan]代码解释: {file_path}[/bold cyan]", border_style="blue"))
    
    with open(file_path, 'r') as f:
        code_content = f.read()
    
    console.print("\n📄 [bold]代码内容:[/bold]")
    syntax = Syntax(code_content, "python", theme="monokai", line_numbers=True)
    console.print(syntax)
    
    llm = get_llm_client(model)
    llm.set_model(model)
    
    prompt = f"""请解释以下代码的功能：

```
{code_content}
```

请用简单的语言解释：
1. **主要功能** - 这段代码做什么
2. **关键逻辑** - 核心算法和逻辑
3. **使用方法** - 如何使用这段代码
4. **注意事项** - 使用时需要注意什么

请用中文回答，并尽量用通俗易懂的语言。"""
    
    with console.status("[bold green]分析中...[/bold green]"):
        result = llm.generate(prompt)
    
    console.print(f"\n💡 [bold green]代码解释:[/bold green]\n{result}\n")


@code.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--model', '-m', default=None, help='指定模型')
@click.option('--focus', '-f', default='all', help='关注点 (all/performance/readability/security)')
def refactor(file_path, model, focus):
    """重构建议 - lobster code refactor <file>
    
    示例:
        lobster code refactor legacy.py
        lobster code refactor slow.py -f performance
    """
    config = ConfigManager()
    model = model or config.get('default_model', 'ollama/gemma3')
    
    console.print(Panel(f"🔧 [bold cyan]重构建议: {file_path}[/bold cyan]", border_style="blue"))
    
    with open(file_path, 'r') as f:
        code_content = f.read()
    
    llm = get_llm_client(model)
    llm.set_model(model)
    
    focus_prompts = {
        'all': '所有方面',
        'performance': '性能优化',
        'readability': '可读性',
        'security': '安全性',
    }
    
    prompt = f"""请为以下代码提供重构建议，重点关注{focus_prompts.get(focus, '所有方面')}：

```
{code_content}
```

请提供：
1. **问题分析** - 当前代码存在的问题
2. **重构建议** - 具体的重构方案
3. **重构后代码** - 给出重构后的代码示例
4. **改进效果** - 重构带来的改进

请用中文回答，并提供可执行的代码示例。"""
    
    with console.status("[bold green]分析中...[/bold green]"):
        result = llm.generate(prompt)
    
    console.print(f"\n💡 [bold green]重构建议:[/bold green]\n{result}\n")


@code.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--language', '-l', default='python', help='编程语言')
@click.option('--model', '-m', default=None, help='指定模型')
def test(file_path, language, model):
    """生成测试 - lobster code test <file>
    
    示例:
        lobster code test mymodule.py
        lobster code test utils.js -l javascript
    """
    config = ConfigManager()
    model = model or config.get('default_model', 'ollama/gemma3')
    
    console.print(Panel(f"🧪 [bold cyan]生成测试: {file_path}[/bold cyan]", border_style="blue"))
    
    with open(file_path, 'r') as f:
        code_content = f.read()
    
    llm = get_llm_client(model)
    llm.set_model(model)
    
    prompt = f"""请为以下 {language} 代码生成单元测试：

```
{code_content}
```

请生成：
1. **测试用例** - 覆盖主要功能和边界情况
2. **测试代码** - 完整可运行的测试代码
3. **测试说明** - 每个测试的目的

使用 {language} 的标准测试框架（如 Python 的 pytest）。
请用中文注释说明测试目的。"""
    
    with console.status("[bold green]生成测试中...[/bold green]"):
        result = llm.generate(prompt)
    
    console.print(f"\n💡 [bold green]测试代码:[/bold green]\n{result}\n")


@code.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.argument('target_language')
@click.option('--model', '-m', default=None, help='指定模型')
def translate(file_path, target_language, model):
    """代码翻译 - lobster code translate <file> <target_language>
    
    示例:
        lobster code translate script.py javascript
        lobster code translate utils.js python
    """
    config = ConfigManager()
    model = model or config.get('default_model', 'ollama/gemma3')
    
    console.print(Panel(f"🌐 [bold cyan]代码翻译: {file_path} -> {target_language}[/bold cyan]", border_style="blue"))
    
    with open(file_path, 'r') as f:
        code_content = f.read()
    
    llm = get_llm_client(model)
    llm.set_model(model)
    
    prompt = f"""请将以下代码翻译为 {target_language}：

```
{code_content}
```

要求：
1. 保持原有功能和逻辑
2. 遵循目标语言的最佳实践
3. 添加必要的注释
4. 确保代码可直接运行

请提供完整的翻译后代码。"""
    
    with console.status("[bold green]翻译中...[/bold green]"):
        result = llm.generate(prompt)
    
    console.print(f"\n💡 [bold green]翻译结果:[/bold green]\n{result}\n")


@code.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--model', '-m', default=None, help='指定模型')
def document(file_path, model):
    """生成文档 - lobster code document <file>
    
    示例:
        lobster code document mymodule.py
    """
    config = ConfigManager()
    model = model or config.get('default_model', 'ollama/gemma3')
    
    console.print(Panel(f"📝 [bold cyan]生成文档: {file_path}[/bold cyan]", border_style="blue"))
    
    with open(file_path, 'r') as f:
        code_content = f.read()
    
    llm = get_llm_client(model)
    llm.set_model(model)
    
    prompt = f"""请为以下代码生成文档：

```
{code_content}
```

请生成：
1. **模块说明** - 整体功能描述
2. **函数/类文档** - 每个函数和类的文档
3. **参数说明** - 参数类型和说明
4. **返回值** - 返回值类型和说明
5. **使用示例** - 具体的使用示例

使用 Markdown 格式，用中文编写。"""
    
    with console.status("[bold green]生成文档中...[/bold green]"):
        result = llm.generate(prompt)
    
    console.print(f"\n💡 [bold green]文档内容:[/bold green]\n{result}\n")

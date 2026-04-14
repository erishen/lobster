"""文档工具命令模块"""

import click
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from pathlib import Path

from lobster.core.llm_client import get_llm_client
from lobster.core.config import ConfigManager

console = Console()


@click.group()
def doc_tool():
    """文档处理工具"""
    pass


@doc_tool.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--model', '-m', default=None, help='指定模型')
@click.option('--length', '-l', default='medium', help='总结长度 (short/medium/long)')
def summarize(file_path, model, length):
    """文档总结 - lobster doc-tool summarize <file>
    
    示例:
        lobster doc-tool summarize report.md
        lobster doc-tool summarize paper.pdf -l long
    """
    config = ConfigManager()
    model = model or config.get('default_model', 'ollama/gemma3')
    
    console.print(Panel(f"📄 [bold cyan]文档总结: {file_path}[/bold cyan]", border_style="blue"))
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    llm = get_llm_client(model)
    llm.set_model(model)
    
    length_prompts = {
        'short': '用1-2句话总结',
        'medium': '用3-5句话总结',
        'long': '详细总结，包括主要观点和细节',
    }
    
    prompt = f"""请{length_prompts.get(length, '总结')}以下文档：

{content[:5000]}

请用中文总结，突出重点内容。"""
    
    with console.status("[bold green]总结中...[/bold green]"):
        result = llm.generate(prompt)
    
    console.print(f"\n💡 [bold green]文档总结:[/bold green]\n{result}\n")


@doc_tool.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.argument('target_language')
@click.option('--model', '-m', default=None, help='指定模型')
def translate(file_path, target_language, model):
    """文档翻译 - lobster doc-tool translate <file> <language>
    
    示例:
        lobster doc-tool translate README.md en
        lobster doc-tool translate article.txt zh
    """
    config = ConfigManager()
    model = model or config.get('default_model', 'ollama/gemma3')
    
    console.print(Panel(f"🌐 [bold cyan]文档翻译: {file_path} -> {target_language}[/bold cyan]", border_style="blue"))
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    llm = get_llm_client(model)
    llm.set_model(model)
    
    prompt = f"""请将以下文档翻译为{target_language}：

{content[:5000]}

要求：
1. 保持原有格式和结构
2. 准确翻译专业术语
3. 保持原文的语气和风格
4. 确保翻译流畅自然

请提供完整的翻译结果。"""
    
    with console.status("[bold green]翻译中...[/bold green]"):
        result = llm.generate(prompt)
    
    console.print(f"\n💡 [bold green]翻译结果:[/bold green]\n")
    console.print(Markdown(result))


@doc_tool.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--model', '-m', default=None, help='指定模型')
@click.option('--output', '-o', default=None, help='输出文件')
def rewrite(file_path, model, output):
    """文档改写 - lobster doc-tool rewrite <file>
    
    示例:
        lobster doc-tool rewrite draft.md
        lobster doc-tool rewrite article.txt -o polished.md
    """
    config = ConfigManager()
    model = model or config.get('default_model', 'ollama/gemma3')
    
    console.print(Panel(f"✏️  [bold cyan]文档改写: {file_path}[/bold cyan]", border_style="blue"))
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    llm = get_llm_client(model)
    llm.set_model(model)
    
    prompt = f"""请改写以下文档，使其更加清晰、流畅和专业：

{content[:5000]}

要求：
1. 改善语言表达
2. 优化文档结构
3. 增强可读性
4. 保持原意不变

请提供改写后的完整文档。"""
    
    with console.status("[bold green]改写中...[/bold green]"):
        result = llm.generate(prompt)
    
    if output:
        with open(output, 'w') as f:
            f.write(result)
        console.print(f"\n✅ [bold green]已保存到: {output}[/bold green]\n")
    else:
        console.print(f"\n💡 [bold green]改写结果:[/bold green]\n")
        console.print(Markdown(result))


@doc_tool.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--model', '-m', default=None, help='指定模型')
def outline(file_path, model):
    """生成大纲 - lobster doc-tool outline <file>
    
    示例:
        lobster doc-tool outline report.md
    """
    config = ConfigManager()
    model = model or config.get('default_model', 'ollama/gemma3')
    
    console.print(Panel(f"📋 [bold cyan]生成大纲: {file_path}[/bold cyan]", border_style="blue"))
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    llm = get_llm_client(model)
    llm.set_model(model)
    
    prompt = f"""请为以下文档生成大纲：

{content[:5000]}

要求：
1. 提取主要章节和要点
2. 使用层级结构
3. 简洁明了
4. 突出重点

请用 Markdown 格式输出大纲。"""
    
    with console.status("[bold green]生成大纲中...[/bold green]"):
        result = llm.generate(prompt)
    
    console.print(f"\n💡 [bold green]文档大纲:[/bold green]\n")
    console.print(Markdown(result))


@doc_tool.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--model', '-m', default=None, help='指定模型')
def keywords(file_path, model):
    """提取关键词 - lobster doc-tool keywords <file>
    
    示例:
        lobster doc-tool keywords article.md
    """
    config = ConfigManager()
    model = model or config.get('default_model', 'ollama/gemma3')
    
    console.print(Panel(f"🏷️  [bold cyan]提取关键词: {file_path}[/bold cyan]", border_style="blue"))
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    llm = get_llm_client(model)
    llm.set_model(model)
    
    prompt = f"""请从以下文档中提取关键词：

{content[:5000]}

要求：
1. 提取5-10个核心关键词
2. 按重要性排序
3. 简要说明每个关键词的上下文

请用列表格式输出。"""
    
    with console.status("[bold green]提取关键词中...[/bold green]"):
        result = llm.generate(prompt)
    
    console.print(f"\n💡 [bold green]关键词:[/bold green]\n{result}\n")


@doc_tool.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--model', '-m', default=None, help='指定模型')
def qa(file_path, model):
    """生成问答对 - lobster doc-tool qa <file>
    
    示例:
        lobster doc-tool qa tutorial.md
    """
    config = ConfigManager()
    model = model or config.get('default_model', 'ollama/gemma3')
    
    console.print(Panel(f"❓ [bold cyan]生成问答对: {file_path}[/bold cyan]", border_style="blue"))
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    llm = get_llm_client(model)
    llm.set_model(model)
    
    prompt = f"""请根据以下文档生成问答对：

{content[:5000]}

要求：
1. 生成5-10个问答对
2. 问题要具体且有针对性
3. 答案要准确且简洁
4. 覆盖文档的主要内容

格式：
Q: 问题
A: 答案

请用中文生成。"""
    
    with console.status("[bold green]生成问答对中...[/bold green]"):
        result = llm.generate(prompt)
    
    console.print(f"\n💡 [bold green]问答对:[/bold green]\n{result}\n")


@doc_tool.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--model', '-m', default=None, help='指定模型')
@click.option('--format', '-f', default='markdown', help='输出格式 (markdown/html/text)')
def slides(file_path, model, format):
    """生成幻灯片内容 - lobster doc-tool slides <file>
    
    示例:
        lobster doc-tool slides presentation.md
        lobster doc-tool slides report.txt -f html
    """
    config = ConfigManager()
    model = model or config.get('default_model', 'ollama/gemma3')
    
    console.print(Panel(f"🎨 [bold cyan]生成幻灯片: {file_path}[/bold cyan]", border_style="blue"))
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    llm = get_llm_client(model)
    llm.set_model(model)
    
    prompt = f"""请将以下文档转换为幻灯片内容：

{content[:5000]}

要求：
1. 分成5-10张幻灯片
2. 每张幻灯片有明确的主题
3. 内容简洁，要点突出
4. 使用 {format} 格式

请生成完整的幻灯片内容。"""
    
    with console.status("[bold green]生成幻灯片中...[/bold green]"):
        result = llm.generate(prompt)
    
    console.print(f"\n💡 [bold green]幻灯片内容:[/bold green]\n")
    if format == 'markdown':
        console.print(Markdown(result))
    else:
        console.print(result)

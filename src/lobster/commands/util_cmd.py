"""实用工具命令模块"""

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from pathlib import Path
from datetime import datetime
import shutil
import zipfile
import hashlib

console = Console()


@click.group()
def util():
    """实用工具"""
    pass


@util.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--output', '-o', default=None, help='输出文件')
def hash(file_path, output):
    """计算文件哈希 - lobster util hash <file>
    
    示例:
        lobster util hash data.txt
        lobster util hash data.txt -o hash.txt
    """
    console.print(Panel(f"🔐 [bold cyan]计算哈希: {file_path}[/bold cyan]", border_style="blue"))
    
    path = Path(file_path)
    
    # 计算各种哈希
    with open(path, 'rb') as f:
        content = f.read()
    
    md5 = hashlib.md5(content).hexdigest()
    sha1 = hashlib.sha1(content).hexdigest()
    sha256 = hashlib.sha256(content).hexdigest()
    
    # 显示结果
    table = Table(title="哈希值")
    table.add_column("算法", style="cyan")
    table.add_column("哈希值", style="green")
    
    table.add_row("MD5", md5)
    table.add_row("SHA1", sha1)
    table.add_row("SHA256", sha256)
    
    console.print(f"\n{table}\n")
    
    if output:
        with open(output, 'w') as f:
            f.write(f"MD5: {md5}\n")
            f.write(f"SHA1: {sha1}\n")
            f.write(f"SHA256: {sha256}\n")
        console.print(f"✅ [bold green]已保存到: {output}[/bold green]\n")


@util.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--output', '-o', default=None, help='输出文件')
def compress(file_path, output):
    """压缩文件 - lobster util compress <file>
    
    示例:
        lobster util compress data.txt
        lobster util compress data.txt -o data.zip
    """
    console.print(Panel(f"📦 [bold cyan]压缩文件: {file_path}[/bold cyan]", border_style="blue"))
    
    path = Path(file_path)
    output_path = Path(output) if output else path.with_suffix('.zip')
    
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        if path.is_file():
            zipf.write(path, path.name)
        elif path.is_dir():
            for file in path.rglob('*'):
                if file.is_file():
                    zipf.write(file, file.relative_to(path))
    
    original_size = path.stat().st_size if path.is_file() else sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
    compressed_size = output_path.stat().st_size
    ratio = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0
    
    console.print(f"\n✅ [bold green]压缩完成[/bold green]")
    console.print(f"📁 原始大小: {original_size / 1024:.2f} KB")
    console.print(f"📦 压缩后: {compressed_size / 1024:.2f} KB")
    console.print(f"📊 压缩率: {ratio:.1f}%\n")


@util.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.argument('destination', type=click.Path())
def backup(file_path, destination):
    """备份文件/目录 - lobster util backup <source> <dest>
    
    示例:
        lobster util backup data.txt backup/
        lobster util backup project/ backup/
    """
    console.print(Panel(f"💾 [bold cyan]备份: {file_path} -> {destination}[/bold cyan]", border_style="blue"))
    
    src = Path(file_path)
    dst = Path(destination)
    
    # 添加时间戳
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if src.is_file():
        backup_path = dst / f"{src.stem}_{timestamp}{src.suffix}"
        shutil.copy2(src, backup_path)
    else:
        backup_path = dst / f"{src.name}_{timestamp}"
        shutil.copytree(src, backup_path)
    
    console.print(f"\n✅ [bold green]备份完成[/bold green]")
    console.print(f"📁 备份位置: {backup_path}\n")


@util.command()
@click.argument('file_path', type=click.Path(exists=True))
def info(file_path):
    """文件信息 - lobster util info <file>
    
    示例:
        lobster util info data.txt
    """
    console.print(Panel(f"ℹ️  [bold cyan]文件信息: {file_path}[/bold cyan]", border_style="blue"))
    
    path = Path(file_path)
    stat = path.stat()
    
    table = Table(title="文件信息")
    table.add_column("属性", style="cyan")
    table.add_column("值", style="green")
    
    table.add_row("文件名", path.name)
    table.add_row("路径", str(path.absolute()))
    table.add_row("大小", f"{stat.st_size / 1024:.2f} KB")
    table.add_row("创建时间", datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S"))
    table.add_row("修改时间", datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"))
    table.add_row("访问时间", datetime.fromtimestamp(stat.st_atime).strftime("%Y-%m-%d %H:%M:%S"))
    table.add_row("权限", oct(stat.st_mode)[-3:])
    
    console.print(f"\n{table}\n")


@util.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--lines', '-n', default=10, help='显示行数')
def head(file_path, lines):
    """查看文件头部 - lobster util head <file>
    
    示例:
        lobster util head data.txt
        lobster util head data.txt -n 20
    """
    console.print(Panel(f"📄 [bold cyan]文件头部: {file_path}[/bold cyan]", border_style="blue"))
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            if i > lines:
                break
            console.print(f"[dim]{i:4d}[/] {line.rstrip()}")
    
    console.print()


@util.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--lines', '-n', default=10, help='显示行数')
def tail(file_path, lines):
    """查看文件尾部 - lobster util tail <file>
    
    示例:
        lobster util tail data.txt
        lobster util tail data.txt -n 20
    """
    console.print(Panel(f"📄 [bold cyan]文件尾部: {file_path}[/bold cyan]", border_style="blue"))
    
    with open(file_path, 'r', encoding='utf-8') as f:
        all_lines = f.readlines()
    
    for i, line in enumerate(all_lines[-lines:], len(all_lines) - lines + 1):
        console.print(f"[dim]{i:4d}[/] {line.rstrip()}")
    
    console.print()


@util.command()
@click.argument('directory', type=click.Path(exists=True))
@click.option('--pattern', '-p', default='*', help='文件模式')
def find(directory, pattern):
    """查找文件 - lobster util find <dir>
    
    示例:
        lobster util find .
        lobster util find . --pattern "*.py"
    """
    console.print(Panel(f"🔍 [bold cyan]查找文件: {directory}[/bold cyan]", border_style="blue"))
    
    dir_path = Path(directory)
    files = list(dir_path.rglob(pattern))
    
    if not files:
        console.print("\n❌ [bold red]没有找到文件[/bold red]\n")
        return
    
    # 显示结果
    table = Table(title=f"找到 {len(files)} 个文件")
    table.add_column("文件", style="cyan")
    table.add_column("大小", style="green")
    
    for file in files[:50]:  # 限制显示数量
        if file.is_file():
            size = file.stat().st_size
            table.add_row(str(file.relative_to(dir_path)), f"{size / 1024:.2f} KB")
    
    console.print(f"\n{table}\n")
    
    if len(files) > 50:
        console.print(f"[dim]显示前 50 个文件，共 {len(files)} 个文件[/]\n")


@util.command()
def clean_cache():
    """清理缓存 - lobster util clean-cache
    
    示例:
        lobster util clean-cache
    """
    console.print(Panel(f"🧹 [bold cyan]清理缓存[/bold cyan]", border_style="blue"))
    
    cache_dirs = [
        Path(".lobster_cache"),
        Path("__pycache__"),
        Path(".pytest_cache"),
        Path(".mypy_cache"),
        Path(".ruff_cache"),
    ]
    
    cleaned = 0
    for cache_dir in cache_dirs:
        if cache_dir.exists():
            shutil.rmtree(cache_dir)
            cleaned += 1
            console.print(f"✓ 已删除: {cache_dir}")
    
    if cleaned > 0:
        console.print(f"\n✅ [bold green]已清理 {cleaned} 个缓存目录[/bold green]\n")
    else:
        console.print("\n✅ [bold green]没有缓存需要清理[/bold green]\n")

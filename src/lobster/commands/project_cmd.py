"""项目管理工具命令模块"""

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from pathlib import Path
from datetime import datetime
import json

from lobster.core.llm_client import get_llm_client
from lobster.core.config import ConfigManager

console = Console()


@click.group()
def project():
    """项目管理工具"""
    pass


@project.command()
@click.option("--name", "-n", default="my-project", help="项目名称")
@click.option("--type", "-t", default="python", help="项目类型 (python/node/go/rust)")
def init(name, type):
    """初始化项目 - lobster project init

    示例:
        lobster project init --name myapp --type python
    """
    console.print(Panel(f"🚀 [bold cyan]初始化项目: {name}[/bold cyan]", border_style="blue"))

    project_dir = Path(name)
    project_dir.mkdir(exist_ok=True)

    # 创建基本目录结构
    (project_dir / "src").mkdir(exist_ok=True)
    (project_dir / "tests").mkdir(exist_ok=True)
    (project_dir / "docs").mkdir(exist_ok=True)

    # 创建 README
    readme_content = f"""# {name}

## 项目简介

{type} 项目

## 安装

```bash
# 安装依赖
```

## 使用

```bash
# 运行项目
```

## 测试

```bash
# 运行测试
```

## 许可证

MIT
"""
    (project_dir / "README.md").write_text(readme_content, encoding="utf-8")

    # 创建 .gitignore
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
ENV/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
"""
    (project_dir / ".gitignore").write_text(gitignore_content, encoding="utf-8")

    console.print(f"\n✅ [bold green]项目已创建: {name}[/bold green]")
    console.print("📁 目录结构:")
    console.print(f"  {name}/")
    console.print("  ├── src/")
    console.print("  ├── tests/")
    console.print("  ├── docs/")
    console.print("  ├── README.md")
    console.print("  └── .gitignore\n")


@project.command()
@click.option("--path", "-p", default=".", help="项目路径")
@click.option("--model", "-m", default=None, help="指定模型")
def analyze(path, model):
    """分析项目 - lobster project analyze

    示例:
        lobster project analyze
        lobster project analyze --path ./myproject
    """
    config = ConfigManager()
    model = model or config.get("default_model", "ollama/gemma3")

    console.print(Panel(f"🔍 [bold cyan]项目分析: {path}[/bold cyan]", border_style="blue"))

    project_path = Path(path)

    # 收集项目信息
    files = []
    for file_path in project_path.rglob("*"):
        if file_path.is_file() and not file_path.name.startswith("."):
            try:
                relative_path = file_path.relative_to(project_path)
                file_size = file_path.stat().st_size
                files.append(
                    {
                        "path": str(relative_path),
                        "size": file_size,
                        "ext": file_path.suffix,
                    }
                )
            except (OSError, ValueError):
                continue

    # 统计信息
    total_files = len(files)
    total_size = sum(f["size"] for f in files)
    extensions = {}
    for f in files:
        ext = f["ext"] or "no_ext"
        extensions[ext] = extensions.get(ext, 0) + 1

    # 显示统计
    table = Table(title="项目统计")
    table.add_column("指标", style="cyan")
    table.add_column("值", style="green")

    table.add_row("总文件数", str(total_files))
    table.add_row("总大小", f"{total_size / 1024:.2f} KB")
    table.add_row("文件类型", str(len(extensions)))

    console.print(f"\n{table}\n")

    # 文件类型分布
    if extensions:
        ext_table = Table(title="文件类型分布")
        ext_table.add_column("类型", style="cyan")
        ext_table.add_column("数量", style="green")

        for ext, count in sorted(extensions.items(), key=lambda x: x[1], reverse=True)[:10]:
            ext_table.add_row(ext, str(count))

        console.print(ext_table)

    # AI 分析
    if total_files > 0:
        llm = get_llm_client(model)

        file_list = "\n".join([f["path"] for f in files[:50]])

        prompt = f"""请分析以下项目结构：

```
{file_list}
```

请提供：
1. **项目类型** - 推测的项目类型
2. **架构分析** - 项目架构特点
3. **改进建议** - 项目结构优化建议

请用中文回答，简洁明了。"""

        with console.status("[bold green]分析中...[/bold green]"):
            result = llm.generate(prompt)

        console.print(f"\n💡 [bold green]项目分析:[/bold green]\n{result}\n")


@project.command()
@click.option("--path", "-p", default=".", help="项目路径")
@click.option("--model", "-m", default=None, help="指定模型")
def report(path, model):
    """生成项目报告 - lobster project report

    示例:
        lobster project report
        lobster project report --path ./myproject -o report.md
    """
    config = ConfigManager()
    model = model or config.get("default_model", "ollama/gemma3")

    console.print(Panel(f"📊 [bold cyan]生成项目报告: {path}[/bold cyan]", border_style="blue"))

    project_path = Path(path)

    # 收集项目信息
    readme_file = project_path / "README.md"
    readme_content = (
        readme_file.read_text(encoding="utf-8") if readme_file.exists() else "无 README"
    )

    code_lines = 0
    for file_path in project_path.rglob("*"):
        if file_path.is_file() and file_path.suffix in [".py", ".js", ".ts", ".go", ".rs", ".java"]:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    code_lines += len(f.readlines())
            except (OSError, UnicodeDecodeError):
                continue

    llm = get_llm_client(model)

    prompt = f"""请为以下项目生成报告：

README:
```
{readme_content[:2000]}
```

代码行数: {code_lines}

请生成：
1. **项目概述** - 项目简介
2. **技术栈** - 使用的技术
3. **项目状态** - 当前状态评估
4. **改进建议** - 下一步建议

请用 Markdown 格式，中文回答。"""

    with console.status("[bold green]生成报告中...[/bold green]"):
        result = llm.generate(prompt)

    console.print(f"\n💡 [bold green]项目报告:[/bold green]\n{result}\n")


@project.command()
@click.option("--path", "-p", default=".", help="项目路径")
def todo(path):
    """管理待办事项 - lobster project todo

    示例:
        lobster project todo
    """
    console.print(Panel("📋 [bold cyan]待办事项管理[/bold cyan]", border_style="blue"))

    project_path = Path(path)
    todo_file = project_path / ".lobster_todo.json"

    if todo_file.exists():
        with open(todo_file, "r", encoding="utf-8") as f:
            todos = json.load(f)
    else:
        todos = []

    if not todos:
        console.print("\n✅ [bold green]没有待办事项[/bold green]\n")
        return

    # 显示待办事项
    table = Table(title="待办事项")
    table.add_column("ID", style="cyan", width=5)
    table.add_column("状态", style="green", width=10)
    table.add_column("优先级", style="yellow", width=10)
    table.add_column("内容", style="white")

    for i, todo in enumerate(todos, 1):
        status = "✓" if todo.get("done") else "○"
        priority = todo.get("priority", "medium")
        content = todo.get("content", "")
        table.add_row(str(i), status, priority, content)

    console.print(f"\n{table}\n")


@project.command("add-todo")
@click.argument("content")
@click.option("--priority", "-r", default="medium", help="优先级 (high/medium/low)")
@click.option("--path", "-p", default=".", help="项目路径")
def add_todo(content, priority, path):
    """添加待办事项 - lobster project add-todo "内容"

    示例:
        lobster project add-todo "实现新功能" --priority high
    """
    console.print(Panel("➕ [bold cyan]添加待办事项[/bold cyan]", border_style="blue"))

    project_path = Path(path)
    todo_file = project_path / ".lobster_todo.json"

    if todo_file.exists():
        with open(todo_file, "r", encoding="utf-8") as f:
            todos = json.load(f)
    else:
        todos = []

    todos.append(
        {
            "content": content,
            "priority": priority,
            "done": False,
            "created_at": datetime.now().isoformat(),
        }
    )

    with open(todo_file, "w", encoding="utf-8") as f:
        json.dump(todos, f, indent=2, ensure_ascii=False)

    console.print("\n✅ [bold green]已添加待办事项[/bold green]")
    console.print(f"📝 内容: {content}")
    console.print(f"🎯 优先级: {priority}\n")


@project.command("done-todo")
@click.argument("todo_id", type=int)
@click.option("--path", "-p", default=".", help="项目路径")
def done_todo(todo_id, path):
    """完成待办事项 - lobster project done-todo <id>

    示例:
        lobster project done-todo 1
    """
    console.print(Panel("✅ [bold cyan]完成待办事项[/bold cyan]", border_style="blue"))

    project_path = Path(path)
    todo_file = project_path / ".lobster_todo.json"

    if not todo_file.exists():
        console.print("\n❌ [bold red]没有待办事项[/bold red]\n")
        return

    with open(todo_file, "r", encoding="utf-8") as f:
        todos = json.load(f)

    if 1 <= todo_id <= len(todos):
        todos[todo_id - 1]["done"] = True
        todos[todo_id - 1]["completed_at"] = datetime.now().isoformat()

        with open(todo_file, "w", encoding="utf-8") as f:
            json.dump(todos, f, indent=2, ensure_ascii=False)

        console.print(f"\n✅ [bold green]已完成待办事项 #{todo_id}[/bold green]\n")
    else:
        console.print("\n❌ [bold red]无效的待办事项 ID[/bold red]\n")

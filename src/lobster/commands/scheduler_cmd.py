"""定时任务命令模块"""

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from pathlib import Path
import json
from datetime import datetime

console = Console()

SCHEDULER_FILE = Path(".lobster_scheduler.json")


@click.group()
def scheduler():
    """定时任务管理"""
    pass


@scheduler.command()
@click.argument("name")
@click.argument("command")
@click.option("--interval", "-i", default=60, help="间隔时间(秒)")
@click.option("--cron", "-c", default=None, help="Cron 表达式")
@click.option("--enabled", "-e", is_flag=True, default=True, help="是否启用")
def add(name, command, interval, cron, enabled):
    """添加定时任务 - lobster scheduler add <name> <command>

    示例:
        lobster scheduler add backup "lobster datax backup" --interval 3600
        lobster scheduler add daily_report "lobster data analyze report.csv" --cron "0 9 * * *"
    """
    console.print(Panel(f"⏰ [bold cyan]添加定时任务: {name}[/bold cyan]", border_style="blue"))

    tasks = _load_tasks()

    task = {
        "name": name,
        "command": command,
        "interval": interval,
        "cron": cron,
        "enabled": enabled,
        "created_at": datetime.now().isoformat(),
        "last_run": None,
        "run_count": 0,
    }

    tasks[name] = task
    _save_tasks(tasks)

    console.print(f"✅ [green]任务已添加:[/] {name}")
    console.print(f"   命令: {command}")
    if cron:
        console.print(f"   Cron: {cron}")
    else:
        console.print(f"   间隔: {interval} 秒")


@scheduler.command()
def list():
    """列出所有定时任务"""
    console.print(Panel("📋 [bold cyan]定时任务列表[/bold cyan]", border_style="blue"))

    tasks = _load_tasks()

    if not tasks:
        console.print("[yellow]没有定时任务[/]")
        return

    table = Table()
    table.add_column("名称", style="cyan")
    table.add_column("命令", style="green")
    table.add_column("间隔/Cron", style="yellow")
    table.add_column("状态", style="magenta")
    table.add_column("运行次数", style="blue")

    for name, task in tasks.items():
        schedule = task.get("cron") or f"{task.get('interval')}s"
        status = "✅ 启用" if task.get("enabled") else "❌ 禁用"
        run_count = task.get("run_count", 0)

        table.add_row(name, task.get("command", "")[:30], schedule, status, str(run_count))

    console.print(f"\n{table}\n")


@scheduler.command()
@click.argument("name")
def enable(name):
    """启用定时任务"""
    tasks = _load_tasks()

    if name not in tasks:
        console.print(f"[red]任务不存在: {name}[/]")
        return

    tasks[name]["enabled"] = True
    _save_tasks(tasks)

    console.print(f"✅ [green]任务已启用: {name}[/]")


@scheduler.command()
@click.argument("name")
def disable(name):
    """禁用定时任务"""
    tasks = _load_tasks()

    if name not in tasks:
        console.print(f"[red]任务不存在: {name}[/]")
        return

    tasks[name]["enabled"] = False
    _save_tasks(tasks)

    console.print(f"✅ [green]任务已禁用: {name}[/]")


@scheduler.command()
@click.argument("name")
def remove(name):
    """删除定时任务"""
    tasks = _load_tasks()

    if name not in tasks:
        console.print(f"[red]任务不存在: {name}[/]")
        return

    del tasks[name]
    _save_tasks(tasks)

    console.print(f"✅ [green]任务已删除: {name}[/]")


@scheduler.command()
def run():
    """运行所有启用的定时任务"""
    console.print(Panel("🚀 [bold cyan]启动定时任务调度器[/bold cyan]", border_style="blue"))

    tasks = _load_tasks()
    enabled_tasks = [t for t in tasks.values() if t.get("enabled")]

    if not enabled_tasks:
        console.print("[yellow]没有启用的定时任务[/]")
        return

    console.print(f"将运行 {len(enabled_tasks)} 个任务 (按 Ctrl+C 停止)...")

    try:
        import time

        while True:
            for task in enabled_tasks:
                _run_task(task)

            time.sleep(5)

    except KeyboardInterrupt:
        console.print("\n[yellow]调度器已停止[/]")


def _load_tasks() -> dict:
    """加载任务列表"""
    if SCHEDULER_FILE.exists():
        with open(SCHEDULER_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _save_tasks(tasks: dict):
    """保存任务列表"""
    with open(SCHEDULER_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)


def _run_task(task: dict):
    """执行任务"""
    import subprocess

    console.print(f"\n▶️ 运行任务: {task['name']}")

    try:
        result = subprocess.run(
            task["command"],
            shell=True,
            capture_output=True,
            text=True,
            timeout=300,
        )

        task["last_run"] = datetime.now().isoformat()
        task["run_count"] = task.get("run_count", 0) + 1
        _save_tasks(_load_tasks())

        if result.returncode == 0:
            console.print(f"✅ 任务完成: {task['name']}")
        else:
            console.print(f"❌ 任务失败: {result.stderr}")

    except Exception as e:
        console.print(f"❌ 执行错误: {str(e)}")


if __name__ == "__main__":
    scheduler()

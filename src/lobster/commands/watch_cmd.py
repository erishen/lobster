"""文件监控命令模块"""

import json
import logging
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

logger = logging.getLogger(__name__)

console = Console()

WATCHER_FILE = Path(".lobster_watchers.json")


@click.group()
def watch():
    """文件监控命令"""
    pass


@watch.command()
@click.argument("path", type=click.Path(exists=True))
@click.argument("command")
@click.option("--pattern", "-p", default="*", help="文件匹配模式")
@click.option("--recursive", "-r", is_flag=True, help="递归监控子目录")
def add(path, command, pattern, recursive):
    """添加文件监控 - lobster watch add <path> <command>

    示例:
        lobster watch add . "linter check" --pattern "*.py"
        lobster watch add ./src "compile" --recursive
    """
    console.print(Panel(f"👁️ [bold cyan]添加文件监控: {path}[/bold cyan]", border_style="blue"))

    watchers = _load_watchers()

    watcher = {
        "path": str(Path(path).absolute()),
        "command": command,
        "pattern": pattern,
        "recursive": recursive,
        "enabled": True,
    }

    watcher_id = str(len(watchers))
    watchers[watcher_id] = watcher
    _save_watchers(watchers)

    logger.info(" 监控已添加:")
    logger.info(f" 路径: {path}")
    logger.info(f" 命令: {command}")
    logger.info(f" 模式: {pattern}")


@watch.command()
def list():
    """列出所有文件监控"""
    console.print(Panel("📋 [bold cyan]文件监控列表[/bold cyan]", border_style="blue"))

    watchers = _load_watchers()

    if not watchers:
        logger.info("没有文件监控")
        return

    table = Table()
    table.add_column("ID", style="cyan", width=5)
    table.add_column("路径", style="green")
    table.add_column("命令", style="yellow")
    table.add_column("模式", style="magenta")
    table.add_column("状态", style="blue")

    for wid, watcher in watchers.items():
        status = "✅ 启用" if watcher.get("enabled") else "❌ 禁用"
        table.add_row(
            wid,
            watcher.get("path", "")[:30],
            watcher.get("command", "")[:25],
            watcher.get("pattern", "*"),
            status,
        )

    console.print(f"\n{table}\n")


@watch.command()
@click.argument("watcher_id")
def start(watcher_id):
    """启动文件监控"""
    console.print(Panel("▶️ [bold cyan]启动文件监控[/bold cyan]", border_style="blue"))

    watchers = _load_watchers()

    if watcher_id not in watchers:
        logger.error(f"监控不存在: {watcher_id}")
        return

    watcher = watchers[watcher_id]

    logger.info(f"监控路径: {watcher['path']}")
    logger.info(f"执行命令: {watcher['command']}")
    logger.info(f"模式: {watcher['pattern']}")
    logger.info("\n按 Ctrl+C 停止监控...\n")

    try:
        import time

        from watchdog.events import FileSystemEventHandler
        from watchdog.observers import Observer

        class WatchHandler(FileSystemEventHandler):
            def __init__(self, cmd, pattern):
                self.cmd = cmd
                self.pattern = pattern
                self.last_run = 0

            def on_modified(self, event):
                if event.is_directory:
                    return

                import re

                if re.match(self.pattern.replace("*", ".*"), event.src_path):
                    now = time.time()
                    if now - self.last_run > 2:
                        self.last_run = now
                        self.run_command(event.src_path, event.event_type)

            def on_created(self, event):
                if event.is_directory:
                    return
                self.run_command(event.src_path, "created")

            def run_command(self, file_path, event_type):
                import subprocess

                logger.info(f"\n 文件 {event_type}: {file_path}")
                logger.info(f"▶️ 执行: {self.cmd}")

                try:
                    result = subprocess.run(
                        self.cmd,
                        shell=True,
                        capture_output=True,
                        text=True,
                        timeout=60,
                    )

                    if result.returncode == 0:
                        logger.info(" 完成")
                    else:
                        logger.error(f" 失败: {result.stderr[:100]}")

                except Exception as e:
                    logger.error(f" 错误: {e!s}")

        handler = WatchHandler(watcher["command"], watcher["pattern"])
        observer = Observer()

        observer.schedule(handler, watcher["path"], recursive=watcher.get("recursive", False))
        observer.start()

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        logger.info("\n监控已停止")
        observer.stop()
        observer.join()
    except ImportError:
        logger.error("Error: watchdog 库未安装")
        logger.info("Install with: pip install watchdog")


@watch.command()
@click.argument("watcher_id")
def remove(watcher_id):
    """删除文件监控"""
    watchers = _load_watchers()

    if watcher_id not in watchers:
        logger.error(f"监控不存在: {watcher_id}")
        return

    del watchers[watcher_id]
    _save_watchers(watchers)

    logger.info(" 监控已删除")


def _load_watchers() -> dict:
    """加载监控列表"""
    if WATCHER_FILE.exists():
        with open(WATCHER_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {}


def _save_watchers(watchers: dict):
    """保存监控列表"""
    with open(WATCHER_FILE, "w", encoding="utf-8") as f:
        json.dump(watchers, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    watch()

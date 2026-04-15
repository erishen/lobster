"""导出/导入命令模块"""

import click
import json
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from datetime import datetime

console = Console()


@click.group()
def datax():
    """数据导出/导入命令"""
    pass


@datax.command()
@click.option("--memories", "-m", is_flag=True, help="导出记忆")
@click.option("--history", "-h", is_flag=True, help="导出对话历史")
@click.option("--config", "-c", is_flag=True, help="导出配置")
@click.option("--all", "-a", is_flag=True, help="导出所有")
@click.option("--output", "-o", default=None, help="输出文件路径")
def export(memories, history, config, all, output):
    """导出数据 - lobster datax export

    示例:
        lobster datax export --all
        lobster datax export --memories -o backup.json
    """
    if not any([memories, history, config, all]):
        console.print("[yellow]请指定导出内容: --memories, --history, --config 或 --all[/]")
        return

    if output:
        output_path = Path(output)
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = Path(f"lobster_backup_{timestamp}.json")

    console.print(Panel(f"📤 [bold cyan]导出数据到: {output_path}[/bold cyan]", border_style="blue"))

    export_data = {
        "version": "1.0",
        "timestamp": datetime.now().isoformat(),
    }

    if all or memories:
        try:
            from lobster.core.memory_store import EnhancedMemoryManager

            memory = EnhancedMemoryManager()
            memories = memory.list_memories()
            export_data["memories"] = memories
            console.print(f"✅ 导出 {len(memories)} 条记忆")
        except Exception as e:
            console.print(f"[red]导出记忆失败: {str(e)}[/]")

    if all or history:
        try:
            from lobster.commands.history import load_conversations

            conversations = load_conversations()
            export_data["conversations"] = conversations
            console.print(f"✅ 导出 {len(conversations)} 条对话历史")
        except Exception as e:
            console.print(f"[red]导出历史失败: {str(e)}[/]")

    if all or config:
        try:
            from lobster.core.config import ConfigManager

            config_mgr = ConfigManager()
            export_data["config"] = config_mgr.config.model_dump()
            console.print("✅ 导出配置")
        except Exception as e:
            console.print(f"[red]导出配置失败: {str(e)}[/]")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)

    console.print(f"\n✅ [bold green]导出完成: {output_path}[/]")


@datax.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.option("--memories", "-m", is_flag=True, help="导入记忆")
@click.option("--history", "-h", is_flag=True, help="导入对话历史")
@click.option("--config", "-c", is_flag=True, help="导入配置")
@click.option("--all", "-a", is_flag=True, help="导入所有")
@click.option("--merge", is_flag=True, default=True, help="合并到现有数据")
@click.option("--replace", is_flag=True, help="替换现有数据")
def import_data(file_path, memories, history, config, all, merge, replace):
    """导入数据 - lobster datax import <file>

    示例:
        lobster datax import backup.json
        lobster datax import backup.json --memories
    """
    if not any([memories, history, config, all]):
        console.print("[yellow]请指定导入内容: --memories, --history, --config 或 --all[/]")
        return

    console.print(Panel(f"📥 [bold cyan]从 {file_path} 导入数据[/bold cyan]", border_style="blue"))

    with open(file_path, "r", encoding="utf-8") as f:
        import_data = json.load(f)

    if replace:
        console.print("[yellow]警告: 将替换现有数据![/]")

    if all or memories:
        if "memories" in import_data:
            try:
                from lobster.core.memory_store import EnhancedMemoryManager

                memory = EnhancedMemoryManager()

                if replace:
                    memory.clear_memories()

                count = 0
                for mem in import_data["memories"]:
                    memory.add_memory(
                        mem.get("content", ""),
                        tags=mem.get("metadata", {}).get("tags", []),
                        category=mem.get("metadata", {}).get("category", "general"),
                    )
                    count += 1

                console.print(f"✅ 导入 {count} 条记忆")
            except Exception as e:
                console.print(f"[red]导入记忆失败: {str(e)}[/]")
        else:
            console.print("[yellow]文件中没有记忆数据[/]")

    if all or config:
        if "config" in import_data:
            try:
                from lobster.core.config import ConfigManager

                config_mgr = ConfigManager()
                for key, value in import_data["config"].items():
                    config_mgr.set(key, value)

                console.print("✅ 导入配置")
            except Exception as e:
                console.print(f"[red]导入配置失败: {str(e)}[/]")
        else:
            console.print("[yellow]文件中没有配置数据[/]")

    console.print("\n✅ [bold green]导入完成[/]")


@datax.command()
def backup():
    """快速备份 - lobster datax backup

    创建带时间戳的完整备份
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = Path(f"lobster_backup_{timestamp}.json")

    console.print(Panel(f"💾 [bold cyan]创建备份: {output_path}[/bold cyan]", border_style="blue"))

    export_data = {
        "version": "1.0",
        "timestamp": datetime.now().isoformat(),
    }

    try:
        from lobster.core.memory_store import EnhancedMemoryManager

        memory = EnhancedMemoryManager()
        export_data["memories"] = memory.list_memories()
        console.print(f"✅ 记忆: {len(export_data['memories'])} 条")
    except Exception as e:
        console.print(f"[red]备份记忆失败: {str(e)}[/]")

    try:
        from lobster.commands.history import load_conversations

        export_data["conversations"] = load_conversations()
        console.print(f"✅ 对话: {len(export_data['conversations'])} 条")
    except Exception as e:
        console.print(f"[red]备份对话失败: {str(e)}[/]")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)

    console.print(f"\n✅ [bold green]备份完成: {output_path}[/]")


@datax.command()
@click.argument("backup_file", type=click.Path(exists=True))
def restore(backup_file):
    """恢复备份 - lobster datax restore <backup_file>

    从备份文件恢复所有数据
    """
    console.print(Panel(f"♻️ [bold cyan]从 {backup_file} 恢复数据[/bold cyan]", border_style="blue"))
    console.print("[yellow]注意: 此操作将替换所有现有数据![/]\n")

    with open(backup_file, "r", encoding="utf-8") as f:
        import_data = json.load(f)

    try:
        from lobster.core.memory_store import EnhancedMemoryManager

        memory = EnhancedMemoryManager()
        memory.clear_memories()

        for mem in import_data.get("memories", []):
            memory.add_memory(
                mem.get("content", ""),
                tags=mem.get("metadata", {}).get("tags", []),
                category=mem.get("metadata", {}).get("category", "general"),
            )

        console.print(f"✅ 恢复 {len(import_data.get('memories', []))} 条记忆")
    except Exception as e:
        console.print(f"[red]恢复记忆失败: {str(e)}[/]")

    console.print("\n✅ [bold green]恢复完成[/]")


if __name__ == "__main__":
    datax()

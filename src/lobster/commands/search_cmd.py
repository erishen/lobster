"""全局搜索命令模块"""

import logging

import click
import requests
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

logger = logging.getLogger(__name__)

console = Console()


@click.command()
@click.argument("query")
@click.option("--memory", "-m", is_flag=True, help="搜索记忆")
@click.option("--history", "-h", is_flag=True, help="搜索对话历史")
@click.option("--project", "-p", is_flag=True, help="搜索项目文件")
@click.option("--all", "-a", is_flag=True, help="搜索所有")
def search(query, memory, history, project, all):
    """全局搜索 - lobster search "关键词"

    示例:
        lobster search "机器学习"
        lobster search "问题" --memory
        lobster search "项目" --all
    """
    console.print(Panel(f"🔍 [bold cyan]全局搜索: {query}[/bold cyan]", border_style="blue"))

    results_found = False

    if all or memory:
        results_found = True
        _search_memories(query)

    if all or history:
        results_found = True
        _search_history(query)

    if all or project:
        results_found = True
        _search_project(query)

    if not results_found:
        logger.info("请指定搜索范围: --memory, --history, --project 或 --all")


def _search_memories(query: str):
    """搜索记忆"""
    logger.info("\n 记忆搜索结果:")

    try:
        from lobster.core.memory_store import EnhancedMemoryManager

        memory = EnhancedMemoryManager()
        results = memory.search_memory(query, method="hybrid", k=10)

        if results:
            table = Table()
            table.add_column("ID", style="cyan", width=10)
            table.add_column("内容", style="white")
            table.add_column("分类", style="green", width=12)

            for _i, mem in enumerate(results, 1):
                content = mem["content"][:60] + "..." if len(mem["content"]) > 60 else mem["content"]
                category = mem.get("metadata", {}).get("category", "general")
                table.add_row(mem["id"], content, category)

            console.print(table)
        else:
            logger.debug("没有找到相关记忆")

    except requests.RequestException as e:
        logger.error(f"搜索记忆失败: {e!s}")

    except KeyError as e:
        logger.error(f"搜索记忆失败: {e!s}")

    except Exception as e:
        logger.error(f"搜索记忆失败: {e!s}")


def _search_history(query: str):
    """搜索对话历史"""
    logger.info("\n 对话历史搜索结果:")

    try:
        from lobster.commands.history import load_conversations

        conversations = load_conversations()
        matches = []

        for conv in conversations:
            filename = conv.get("filename", "")
            if query.lower() in filename.lower():
                matches.append(conv)
                continue

            try:
                from lobster.commands.history import load_conversation

                data = load_conversation(filename)
                messages = data.get("data", {}).get("messages", [])
                for msg in messages:
                    if query.lower() in msg.get("content", "").lower():
                        matches.append(conv)
                        break
            except requests.RequestException:
                pass

            except Exception:
                pass

        if matches:
            table = Table()
            table.add_column("时间", style="cyan", width=19)
            table.add_column("消息数", style="green", width=10)
            table.add_column("预览", style="white")

            for conv in matches[:10]:
                table.add_row(
                    conv.get("timestamp", "")[:19],
                    str(conv.get("message_count", 0)),
                    conv.get("preview", "")[:40],
                )

            console.print(table)
        else:
            logger.debug("没有找到相关对话")

    except requests.RequestException as e:
        logger.error(f"搜索历史失败: {e!s}")

    except KeyError as e:
        logger.error(f"搜索历史失败: {e!s}")

    except Exception as e:
        logger.error(f"搜索历史失败: {e!s}")


def _search_project(query: str):
    """搜索项目文件"""
    logger.info("\n📁 项目文件搜索结果:")

    from pathlib import Path

    current_dir = Path(".")
    matches = []

    for pattern in ["*.py", "*.md", "*.txt", "*.json", "*.yaml", "*.yml"]:
        for file_path in current_dir.rglob(pattern):
            if file_path.name.startswith("."):
                continue
            try:
                content = file_path.read_text(errors="ignore")
                if query.lower() in content.lower():
                    matches.append(str(file_path))
            except (OSError, UnicodeDecodeError):
                pass

    if matches:
        logger.info(f"找到 {len(matches)} 个匹配文件:")
        for i, path in enumerate(matches[:20], 1):
            logger.info(f" {i}. {path}")
        if len(matches) > 20:
            logger.info(f" ... 还有 {len(matches) - 20} 个文件")
    else:
        logger.debug("没有找到相关文件")


if __name__ == "__main__":
    search()

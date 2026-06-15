"""RAG 知识库命令模块 - 调用 langchain-llm-toolkit API"""

import logging
import os

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

logger = logging.getLogger(__name__)

console = Console()

RAG_API_URL = os.environ.get("RAG_API_URL", "http://localhost:8000")


@click.group()
def rag():
    """RAG 知识库工具 - 文档问答系统"""
    pass


@rag.command()
def status():
    """检查知识库状态 - lobster rag status"""
    console.print(Panel("📊 [bold cyan]知识库状态[/bold cyan]", border_style="blue"))

    try:
        import requests

        response = requests.get(f"{RAG_API_URL}/health", timeout=5)

        if response.status_code == 200:
            logger.info(" 知识库服务运行中")
            logger.info(f" API 地址: {RAG_API_URL}")
            logger.info(f" API 文档: {RAG_API_URL}/docs")

            try:
                info_response = requests.get(f"{RAG_API_URL}/api/v1/rag/info", timeout=5)
                if info_response.status_code == 200:
                    info = info_response.json()
                    logger.info(f" 状态: {info.get('status', 'unknown')}")
                    logger.info(f" 向量存储: {info.get('vector_store_type', 'unknown')}")
            except requests.RequestException:
                pass

            except ValueError:
                pass

            except Exception:
                pass
        else:
            logger.error(f" 服务异常: {response.status_code}")

    except requests.exceptions.ConnectionError:
        logger.error(" 无法连接到知识库服务")
        logger.info("请确保 langchain-llm-toolkit API 正在运行:")
        logger.info(" cd langchain-llm-toolkit && make api")
    except ImportError:
        logger.error("Error: requests 库未安装")
        logger.info("Install with: pip install requests")


@rag.command()
@click.argument("query")
@click.option("--top-k", "-k", default=3, help="返回的相关文档数量")
@click.option("--model", "-m", default=None, help="使用的模型")
def ask(query, top_k, model):
    """查询知识库 - lobster rag ask <query>

    示例:
        lobster rag ask "项目的主要功能是什么？"
        lobster rag ask "如何配置 API？" -k 5
    """
    console.print(Panel("❓ [bold cyan]知识库查询[/bold cyan]", border_style="blue"))
    logger.info(f"问题: {query}\n")

    try:
        import requests

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("正在查询知识库...", total=None)

            response = requests.post(
                f"{RAG_API_URL}/api/v1/rag/query",
                json={"query": query, "k": top_k},
                timeout=60,
            )

            progress.remove_task(task)

        if response.status_code == 200:
            result = response.json()

            logger.info("\n回答:")
            logger.info(f"{result.get('answer', '无回答')}\n")

            sources = result.get("sources", [])
            if sources:
                logger.info(f"相关文档 ({len(sources)} 个):")
                for i, doc in enumerate(sources[:3], 1):
                    content = doc.get("content", "")[:200]
                    metadata = doc.get("metadata", {})
                    source = metadata.get("source", "unknown")
                    logger.debug(f" {i}. {source}")
                    logger.info(f" {content}...\n")
        elif response.status_code == 404:
            logger.info("知识库为空，请先上传文档")
            logger.info(" 使用: lobster rag upload <file>")
        else:
            logger.error(f"查询失败: {response.status_code}")
            logger.info(response.text[:500])

    except requests.exceptions.ConnectionError:
        logger.error(" 无法连接到知识库服务")
        logger.info("请确保 langchain-llm-toolkit API 正在运行:")
        logger.info(" cd langchain-llm-toolkit && make api")
    except ImportError:
        logger.error("Error: requests 库未安装")


@rag.command()
@click.argument("file_path", type=click.Path(exists=True))
def upload(file_path):
    """上传文档到知识库 - lobster rag upload <file>

    示例:
        lobster rag upload report.pdf
        lobster rag upload notes.txt
    """
    console.print(Panel("📤 [bold cyan]上传文档[/bold cyan]", border_style="blue"))
    logger.info(f"文件: {file_path}\n")

    try:
        import requests

        filename = os.path.basename(file_path)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(f"正在上传 {filename}...", total=None)

            with open(file_path, "rb") as f:
                response = requests.post(
                    f"{RAG_API_URL}/api/v1/rag/upload",
                    files={"file": (filename, f)},
                    timeout=120,
                )

            progress.remove_task(task)

        if response.status_code == 200:
            result = response.json()
            logger.info(" 上传成功")
            logger.info(f" 文件: {result.get('filename', filename)}")
            logger.info(f" 文档数: {result.get('documents_count', 'unknown')}")
        else:
            logger.error(f"上传失败: {response.status_code}")
            logger.info(response.text[:500])

    except requests.exceptions.ConnectionError:
        logger.error(" 无法连接到知识库服务")
        logger.info("请确保 langchain-llm-toolkit API 正在运行:")
        logger.info(" cd langchain-llm-toolkit && make api")
    except ImportError:
        logger.error("Error: requests 库未安装")


@rag.command()
def clear():
    """清空知识库 - lobster rag clear"""
    console.print(Panel("🗑️ [bold cyan]清空知识库[/bold cyan]", border_style="blue"))

    if not click.confirm("确定要清空知识库吗？此操作不可恢复。"):
        logger.info("已取消")
        return

    try:
        import requests

        response = requests.delete(f"{RAG_API_URL}/api/v1/rag/clear", timeout=30)

        if response.status_code == 200:
            logger.info(" 知识库已清空")
        else:
            logger.error(f"清空失败: {response.status_code}")

    except requests.exceptions.ConnectionError:
        logger.error(" 无法连接到知识库服务")
    except ImportError:
        logger.error("Error: requests 库未安装")


@rag.command()
def models():
    """列出可用模型 - lobster rag models"""
    console.print(Panel("🤖 [bold cyan]可用模型[/bold cyan]", border_style="blue"))

    try:
        import requests

        response = requests.get(f"{RAG_API_URL}/api/v1/models", timeout=10)

        if response.status_code == 200:
            result = response.json()
            models_list = result.get("models", [])

            table = Table()
            table.add_column("模型", style="cyan")
            table.add_column("类型", style="green")
            table.add_column("说明", style="yellow")

            for m in models_list:
                table.add_row(
                    m.get("name", "unknown"),
                    m.get("type", "unknown"),
                    m.get("description", "")[:50],
                )

            console.print(table)
        else:
            logger.error(f"获取模型列表失败: {response.status_code}")

    except requests.exceptions.ConnectionError:
        logger.error(" 无法连接到知识库服务")
    except ImportError:
        logger.error("Error: requests 库未安装")


@rag.command()
@click.argument("prompt")
@click.option("--model", "-m", default="ollama/gemma3", help="使用的模型")
def generate(prompt, model):
    """生成文本 - lobster rag generate <prompt>

    示例:
        lobster rag generate "介绍一下自己"
        lobster rag generate "Hello" -m gpt-4o
    """
    console.print(Panel("✨ [bold cyan]文本生成[/bold cyan]", border_style="blue"))

    try:
        import requests

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("正在生成...", total=None)

            response = requests.post(
                f"{RAG_API_URL}/api/v1/generate",
                json={"prompt": prompt, "model": model},
                timeout=60,
            )

            progress.remove_task(task)

        if response.status_code == 200:
            result = response.json()
            logger.info("\n回答:")
            logger.info(result.get("response", "无回答"))
            logger.debug(f"\n模型: {result.get('model', model)}")
            logger.debug(f"耗时: {result.get('elapsed_time', 0):.2f}s")
        else:
            logger.error(f"生成失败: {response.status_code}")

    except requests.exceptions.ConnectionError:
        logger.error(" 无法连接到知识库服务")
    except ImportError:
        logger.error("Error: requests 库未安装")


if __name__ == "__main__":
    rag()

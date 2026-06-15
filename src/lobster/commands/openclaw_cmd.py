"""OpenClaw 集成命令模块"""

import logging
import subprocess

import click
import requests
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

logger = logging.getLogger(__name__)

console = Console()


@click.group()
def openclaw():
    """OpenClaw 服务管理命令"""
    pass


@openclaw.command()
def status():
    """检查 OpenClaw 服务状态"""
    console.print(Panel("🔍 [bold cyan]OpenClaw 服务状态[/bold cyan]", border_style="blue"))

    try:
        response = requests.get("http://localhost:8000/health", timeout=2)
        if response.status_code == 200:
            data = response.json()
            logger.info("\n OpenClaw 正在运行")
            logger.info(" 服务地址: http://localhost:8000")
            if "version" in data:
                logger.info(f" 版本: {data['version']}")
            if "model" in data:
                logger.info(f" 当前模型: {data['model']}")
        else:
            logger.error("\n OpenClaw 服务异常")
            logger.info(f" 状态码: {response.status_code}")
    except requests.exceptions.ConnectionError:
        logger.error("\n OpenClaw 未运行")
        logger.info("\n 提示: 运行 'lobster openclaw start' 启动服务")
    except requests.RequestException as e:
        logger.error(f"\n 检查失败: {e!s}")

    except ValueError as e:
        logger.error(f"\n 检查失败: {e!s}")

    except KeyError as e:
        logger.error(f"\n 检查失败: {e!s}")

    except Exception as e:
        logger.error(f"\n 检查失败: {e!s}")


@openclaw.command()
@click.option("--port", "-p", default=8000, help="服务端口")
@click.option("--host", "-h", default="localhost", help="服务主机")
@click.option("--model", "-m", default="ollama/gemma3", help="默认模型")
@click.option("--daemon", "-d", is_flag=True, help="后台运行")
def start(port, host, model, daemon):
    """启动 OpenClaw 服务"""
    console.print(Panel("🚀 [bold cyan]启动 OpenClaw[/bold cyan]", border_style="blue"))

    try:
        cmd = ["openclaw", "start", "--port", str(port), "--host", host, "--model", model]

        if daemon:
            cmd.append("--daemon")
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            logger.info("\n OpenClaw 已在后台启动")
            logger.info(f" 服务地址: http://{host}:{port}")
            logger.info(f" 默认模型: {model}")
        else:
            logger.info("\n 启动中...")
            logger.info(f" 服务地址: http://{host}:{port}")
            logger.info(f" 默认模型: {model}")
            logger.info("\n 按 Ctrl+C 停止服务\n")
            subprocess.run(cmd)
    except FileNotFoundError:
        logger.error("\n 未找到 openclaw 命令")
        logger.info("\n 请先安装 OpenClaw:")
        logger.info(" pip install openclaw")
    except KeyboardInterrupt:
        logger.info("\n\n 服务已停止")
    except Exception as e:
        logger.error(f"\n 启动失败: {e!s}")


@openclaw.command()
def stop():
    """停止 OpenClaw 服务"""
    console.print(Panel("🛑 [bold cyan]停止 OpenClaw[/bold cyan]", border_style="blue"))

    try:
        result = subprocess.run(["openclaw", "stop"], capture_output=True, text=True)
        if result.returncode == 0:
            logger.info("\n OpenClaw 已停止")
        else:
            logger.error(f"\n 停止失败: {result.stderr}")
    except FileNotFoundError:
        logger.error("\n 未找到 openclaw 命令")
    except Exception as e:
        logger.error(f"\n 停止失败: {e!s}")


@openclaw.command()
@click.option("--follow", "-f", is_flag=True, help="实时查看日志")
def logs(follow):
    """查看 OpenClaw 日志"""
    console.print(Panel("📋 [bold cyan]OpenClaw 日志[/bold cyan]", border_style="blue"))

    try:
        cmd = ["openclaw", "logs"]
        if follow:
            cmd.append("--follow")
        subprocess.run(cmd)
    except FileNotFoundError:
        logger.error("\n 未找到 openclaw 命令")
    except KeyboardInterrupt:
        logger.info("\n\n 日志查看结束")
    except Exception as e:
        logger.error(f"\n 查看日志失败: {e!s}")


@openclaw.command()
def config():
    """查看 OpenClaw 配置"""
    console.print(Panel("⚙️  [bold cyan]OpenClaw 配置[/bold cyan]", border_style="blue"))

    try:
        result = subprocess.run(["openclaw", "config", "show"], capture_output=True, text=True)
        if result.returncode == 0:
            logger.info(f"\n{result.stdout}")
        else:
            logger.error(f"\n 获取配置失败: {result.stderr}")
    except FileNotFoundError:
        logger.error("\n 未找到 openclaw 命令")
    except Exception as e:
        logger.error(f"\n 获取配置失败: {e!s}")


@openclaw.command()
@click.option("--model", "-m", default=None, help="指定模型")
def chat(model):
    """与 OpenClaw 对话"""
    console.print(Panel("💬 [bold cyan]OpenClaw 对话[/bold cyan]", border_style="blue"))

    try:
        cmd = ["openclaw", "chat"]
        if model:
            cmd.extend(["--model", model])
        subprocess.run(cmd)
    except FileNotFoundError:
        logger.error("\n 未找到 openclaw 命令")
    except KeyboardInterrupt:
        logger.info("\n\n 对话结束")
    except Exception as e:
        logger.error(f"\n 对话失败: {e!s}")


@openclaw.command()
def models():
    """列出 OpenClaw 可用模型"""
    console.print(Panel("🤖 [bold cyan]OpenClaw 可用模型[/bold cyan]", border_style="blue"))

    try:
        result = subprocess.run(["openclaw", "models", "list"], capture_output=True, text=True)
        if result.returncode == 0:
            logger.info(f"\n{result.stdout}")
        else:
            logger.error(f"\n 获取模型列表失败: {result.stderr}")
    except FileNotFoundError:
        logger.error("\n 未找到 openclaw 命令")
    except Exception as e:
        logger.error(f"\n 获取模型列表失败: {e!s}")


@openclaw.command()
@click.argument("model_name")
def pull(model_name):
    """拉取 OpenClaw 模型"""
    console.print(Panel(f"📥 [bold cyan]拉取模型: {model_name}[/bold cyan]", border_style="blue"))

    try:
        subprocess.run(["openclaw", "models", "pull", model_name])
    except FileNotFoundError:
        logger.error("\n 未找到 openclaw 命令")
    except Exception as e:
        logger.error(f"\n 拉取模型失败: {e!s}")


@openclaw.command()
def info():
    """显示 OpenClaw 详细信息"""
    console.print(Panel("ℹ️  [bold cyan]OpenClaw 信息[/bold cyan]", border_style="blue"))

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("项目", style="cyan")
    table.add_column("值", style="green")

    try:
        result = subprocess.run(["openclaw", "--version"], capture_output=True, text=True)
        version = result.stdout.strip() if result.returncode == 0 else "未知"
        table.add_row("版本", version)
    except (subprocess.SubprocessError, FileNotFoundError):
        table.add_row("版本", "未安装")

    table.add_row("服务地址", "http://localhost:8000")
    table.add_row("配置文件", "~/.openclaw/config.yaml")
    table.add_row("数据目录", "~/.openclaw/data")
    table.add_row("日志目录", "~/.openclaw/logs")

    console.print(f"\n{table}\n")

    logger.info(" 常用命令:")
    logger.info(" lobster openclaw status - 查看状态")
    logger.info(" lobster openclaw start - 启动服务")
    logger.info(" lobster openclaw stop - 停止服务")
    logger.info(" lobster openclaw chat - 开始对话")
    logger.info(" lobster openclaw logs - 查看日志")
    console.print()

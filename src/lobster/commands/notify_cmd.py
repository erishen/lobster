"""系统通知命令模块"""

import logging

import click
from rich.console import Console
from rich.panel import Panel

logger = logging.getLogger(__name__)

console = Console()


@click.group()
def notify():
    """系统通知命令"""
    pass


@notify.command()
@click.argument("message")
@click.option("--title", "-t", default="Lobster", help="通知标题")
@click.option("--icon", "-i", default=None, help="通知图标")
def send(message, title, icon):
    """发送系统通知 - lobster notify send "消息内容"

    示例:
        lobster notify send "任务完成"
        lobster notify send "错误: 服务宕机" --title "警告"
    """
    logger.info(f" 发送通知: {title} - {message}")

    import sys

    if sys.platform == "darwin":
        _send_macos(message, title)
    elif sys.platform == "linux":
        _send_linux(message, title)
    elif sys.platform == "win32":
        _send_windows(message, title)
    else:
        logger.info("不支持的平台")


def _send_macos(message: str, title: str):
    """发送 macOS 通知"""
    import subprocess

    try:
        script = f'display notification "{message}" with title "{title}"'
        subprocess.run(["osascript", "-e", script], check=True)
        logger.info(" 通知已发送")
    except Exception as e:
        logger.error(f" 发送失败: {e!s}")


def _send_linux(message: str, title: str):
    """发送 Linux 通知"""
    import subprocess

    try:
        subprocess.run(
            ["notify-send", title, message],
            check=True,
        )
        logger.info(" 通知已发送")
    except FileNotFoundError:
        logger.error("Error: notify-send 未安装 (sudo apt install libnotify-bin)")
    except Exception as e:
        logger.error(f" 发送失败: {e!s}")


def _send_windows(message: str, title: str):
    """发送 Windows 通知"""
    try:
        from win10toast import ToastNotifier

        toaster = ToastNotifier()
        toaster.show_toast(title, message, duration=5)
        logger.info(" 通知已发送")
    except ImportError:
        logger.error("Error: win10toast 未安装 (pip install win10toast)")
    except Exception as e:
        logger.error(f" 发送失败: {e!s}")


@notify.command()
@click.argument("message")
@click.option("--title", "-t", default="Lobster", help="通知标题")
def alert(message, title):
    """发送重要警报 - lobster notify alert "警报内容"

    示例:
        lobster notify alert "服务器负载过高!"
    """
    logger.info(f" 发送警报: {title}")
    logger.info(f" {message}\n")

    send.callback(message, title, None)


@notify.command()
def list():
    """列出通知历史 (如果有)"""
    console.print(Panel("📋 [bold cyan]通知历史[/bold cyan]", border_style="blue"))
    logger.info("通知历史功能需要额外配置")
    logger.info("提示: 可以使用 lobster remember 记录重要通知")


@notify.command()
@click.option("--sound", "-s", is_flag=True, help="播放提示音")
def beep(sound):
    """播放提示音 - lobster notify beep

    示例:
        lobster notify beep
        lobster notify beep --sound
    """
    import sys

    if sys.platform == "darwin":
        try:
            import subprocess

            if sound:
                subprocess.run(["say", "beep"], capture_output=True)
            else:
                logger.info("\a")
            logger.info(" 提示音已播放")
        except Exception:
            logger.info("\a")
            logger.info(" 提示音已播放")

    elif sys.platform == "linux":
        logger.info("\a")
        logger.info(" 提示音已播放")

    elif sys.platform == "win32":
        import winsound

        winsound.Beep(1000, 500)
        logger.info(" 提示音已播放")

    else:
        logger.info("不支持的平台")


@notify.command()
def check():
    """检查通知功能 - lobster notify check

    示例:
        lobster notify check
    """
    console.print(Panel("🧪 [bold cyan]检查通知[/bold cyan]", border_style="blue"))

    import sys

    if sys.platform == "darwin":
        _send_macos("这是一条测试通知", "Lobster 检查")
    elif sys.platform == "linux":
        _send_linux("这是一条测试通知", "Lobster 检查")
    elif sys.platform == "win32":
        _send_windows("这是一条测试通知", "Lobster 检查")
    else:
        logger.info("不支持的平台")

    logger.info("\n如果收到通知，说明通知功能正常工作")


if __name__ == "__main__":
    notify()

"""OpenClaw 集成命令模块"""

import click
import subprocess
import requests
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

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
            console.print("\n✅ [bold green]OpenClaw 正在运行[/bold green]")
            console.print(f"  服务地址: http://localhost:8000")
            if 'version' in data:
                console.print(f"  版本: {data['version']}")
            if 'model' in data:
                console.print(f"  当前模型: {data['model']}")
        else:
            console.print("\n⚠️  [bold yellow]OpenClaw 服务异常[/bold yellow]")
            console.print(f"  状态码: {response.status_code}")
    except requests.exceptions.ConnectionError:
        console.print("\n❌ [bold red]OpenClaw 未运行[/bold red]")
        console.print("\n💡 提示: 运行 'lobster openclaw start' 启动服务")
    except Exception as e:
        console.print(f"\n❌ [bold red]检查失败: {str(e)}[/bold red]")


@openclaw.command()
@click.option('--port', '-p', default=8000, help='服务端口')
@click.option('--host', '-h', default='localhost', help='服务主机')
@click.option('--model', '-m', default='ollama/gemma3', help='默认模型')
@click.option('--daemon', '-d', is_flag=True, help='后台运行')
def start(port, host, model, daemon):
    """启动 OpenClaw 服务"""
    console.print(Panel("🚀 [bold cyan]启动 OpenClaw[/bold cyan]", border_style="blue"))
    
    try:
        cmd = ["openclaw", "start", "--port", str(port), "--host", host, "--model", model]
        
        if daemon:
            cmd.append("--daemon")
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            console.print(f"\n✅ [bold green]OpenClaw 已在后台启动[/bold green]")
            console.print(f"  服务地址: http://{host}:{port}")
            console.print(f"  默认模型: {model}")
        else:
            console.print(f"\n🚀 [bold green]启动中...[/bold green]")
            console.print(f"  服务地址: http://{host}:{port}")
            console.print(f"  默认模型: {model}")
            console.print("\n💡 按 Ctrl+C 停止服务\n")
            subprocess.run(cmd)
    except FileNotFoundError:
        console.print("\n❌ [bold red]未找到 openclaw 命令[/bold red]")
        console.print("\n💡 请先安装 OpenClaw:")
        console.print("  pip install openclaw")
    except KeyboardInterrupt:
        console.print("\n\n✅ [bold green]服务已停止[/bold green]")
    except Exception as e:
        console.print(f"\n❌ [bold red]启动失败: {str(e)}[/bold red]")


@openclaw.command()
def stop():
    """停止 OpenClaw 服务"""
    console.print(Panel("🛑 [bold cyan]停止 OpenClaw[/bold cyan]", border_style="blue"))
    
    try:
        result = subprocess.run(["openclaw", "stop"], capture_output=True, text=True)
        if result.returncode == 0:
            console.print("\n✅ [bold green]OpenClaw 已停止[/bold green]")
        else:
            console.print(f"\n⚠️  [bold yellow]停止失败: {result.stderr}[/bold yellow]")
    except FileNotFoundError:
        console.print("\n❌ [bold red]未找到 openclaw 命令[/bold red]")
    except Exception as e:
        console.print(f"\n❌ [bold red]停止失败: {str(e)}[/bold red]")


@openclaw.command()
@click.option('--follow', '-f', is_flag=True, help='实时查看日志')
def logs(follow):
    """查看 OpenClaw 日志"""
    console.print(Panel("📋 [bold cyan]OpenClaw 日志[/bold cyan]", border_style="blue"))
    
    try:
        cmd = ["openclaw", "logs"]
        if follow:
            cmd.append("--follow")
        subprocess.run(cmd)
    except FileNotFoundError:
        console.print("\n❌ [bold red]未找到 openclaw 命令[/bold red]")
    except KeyboardInterrupt:
        console.print("\n\n✅ [bold green]日志查看结束[/bold green]")
    except Exception as e:
        console.print(f"\n❌ [bold red]查看日志失败: {str(e)}[/bold red]")


@openclaw.command()
def config():
    """查看 OpenClaw 配置"""
    console.print(Panel("⚙️  [bold cyan]OpenClaw 配置[/bold cyan]", border_style="blue"))
    
    try:
        result = subprocess.run(["openclaw", "config", "show"], capture_output=True, text=True)
        if result.returncode == 0:
            console.print(f"\n{result.stdout}")
        else:
            console.print(f"\n⚠️  [bold yellow]获取配置失败: {result.stderr}[/bold yellow]")
    except FileNotFoundError:
        console.print("\n❌ [bold red]未找到 openclaw 命令[/bold red]")
    except Exception as e:
        console.print(f"\n❌ [bold red]获取配置失败: {str(e)}[/bold red]")


@openclaw.command()
@click.option('--model', '-m', default=None, help='指定模型')
def chat(model):
    """与 OpenClaw 对话"""
    console.print(Panel("💬 [bold cyan]OpenClaw 对话[/bold cyan]", border_style="blue"))
    
    try:
        cmd = ["openclaw", "chat"]
        if model:
            cmd.extend(["--model", model])
        subprocess.run(cmd)
    except FileNotFoundError:
        console.print("\n❌ [bold red]未找到 openclaw 命令[/bold red]")
    except KeyboardInterrupt:
        console.print("\n\n✅ [bold green]对话结束[/bold green]")
    except Exception as e:
        console.print(f"\n❌ [bold red]对话失败: {str(e)}[/bold red]")


@openclaw.command()
def models():
    """列出 OpenClaw 可用模型"""
    console.print(Panel("🤖 [bold cyan]OpenClaw 可用模型[/bold cyan]", border_style="blue"))
    
    try:
        result = subprocess.run(["openclaw", "models", "list"], capture_output=True, text=True)
        if result.returncode == 0:
            console.print(f"\n{result.stdout}")
        else:
            console.print(f"\n⚠️  [bold yellow]获取模型列表失败: {result.stderr}[/bold yellow]")
    except FileNotFoundError:
        console.print("\n❌ [bold red]未找到 openclaw 命令[/bold red]")
    except Exception as e:
        console.print(f"\n❌ [bold red]获取模型列表失败: {str(e)}[/bold red]")


@openclaw.command()
@click.argument('model_name')
def pull(model_name):
    """拉取 OpenClaw 模型"""
    console.print(Panel(f"📥 [bold cyan]拉取模型: {model_name}[/bold cyan]", border_style="blue"))
    
    try:
        subprocess.run(["openclaw", "models", "pull", model_name])
    except FileNotFoundError:
        console.print("\n❌ [bold red]未找到 openclaw 命令[/bold red]")
    except Exception as e:
        console.print(f"\n❌ [bold red]拉取模型失败: {str(e)}[/bold red]")


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
    except:
        table.add_row("版本", "未安装")
    
    table.add_row("服务地址", "http://localhost:8000")
    table.add_row("配置文件", "~/.openclaw/config.yaml")
    table.add_row("数据目录", "~/.openclaw/data")
    table.add_row("日志目录", "~/.openclaw/logs")
    
    console.print(f"\n{table}\n")
    
    console.print("📚 [bold]常用命令:[/bold]")
    console.print("  lobster openclaw status   - 查看状态")
    console.print("  lobster openclaw start     - 启动服务")
    console.print("  lobster openclaw stop      - 停止服务")
    console.print("  lobster openclaw chat      - 开始对话")
    console.print("  lobster openclaw logs      - 查看日志")
    console.print()

"""Webhook 命令模块"""

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from pathlib import Path
import json

console = Console()

WEBHOOK_FILE = Path(".lobster_webhooks.json")


@click.group()
def webhook():
    """Webhook 管理命令"""
    pass


@webhook.command()
@click.argument("name")
@click.argument("url")
@click.option("--method", "-m", default="POST", help="请求方法")
@click.option("--event", "-e", default="*", help="触发事件 (* 表示所有)")
@click.option("--header", "-H", multiple=True, help="自定义请求头")
def add(name, url, method, event, header):
    """添加 Webhook - lobster webhook add <name> <url>

    示例:
        lobster webhook add notify "https://hooks.slack.com/xxx" --event message
        lobster webhook add backup "https://example.com/backup" --method POST
    """
    console.print(Panel(f"🪝 [bold cyan]添加 Webhook: {name}[/bold cyan]", border_style="blue"))

    hooks = _load_webhooks()

    headers = {}
    for h in header:
        if ":" in h:
            key, value = h.split(":", 1)
            headers[key.strip()] = value.strip()

    hook = {
        "name": name,
        "url": url,
        "method": method,
        "event": event,
        "headers": headers,
        "enabled": True,
    }

    hooks[name] = hook
    _save_webhooks(hooks)

    console.print(f"✅ [green]Webhook 已添加:[/] {name}")
    console.print(f"   URL: {url}")
    console.print(f"   方法: {method}")
    console.print(f"   事件: {event}")


@webhook.command()
def list():
    """列出所有 Webhook"""
    console.print(Panel("📋 [bold cyan]Webhook 列表[/bold cyan]", border_style="blue"))

    hooks = _load_webhooks()

    if not hooks:
        console.print("[yellow]没有 Webhook[/]")
        return

    table = Table()
    table.add_column("名称", style="cyan")
    table.add_column("URL", style="green")
    table.add_column("方法", style="yellow")
    table.add_column("事件", style="magenta")
    table.add_column("状态", style="blue")

    for name, hook in hooks.items():
        status = "✅ 启用" if hook.get("enabled") else "❌ 禁用"
        table.add_row(
            name,
            hook.get("url", "")[:40],
            hook.get("method", "POST"),
            hook.get("event", "*"),
            status,
        )

    console.print(f"\n{table}\n")


@webhook.command()
@click.argument("name")
def test(name):
    """测试 Webhook"""
    hooks = _load_webhooks()

    if name not in hooks:
        console.print(f"[red]Webhook 不存在: {name}[/]")
        return

    hook = hooks[name]
    console.print(f"🧪 [bold]测试 Webhook: {name}[/]")

    try:
        import requests

        test_data = {
            "event": "test",
            "source": "lobster",
            "timestamp": "2024-01-01T00:00:00Z",
        }

        response = requests.request(
            method=hook.get("method", "POST"),
            url=hook["url"],
            json=test_data,
            headers=hook.get("headers", {}),
            timeout=10,
        )

        if response.status_code < 400:
            console.print(f"✅ [green]请求成功 (状态码: {response.status_code})[/]")
        else:
            console.print(f"❌ [red]请求失败 (状态码: {response.status_code})[/]")

    except ImportError:
        console.print("[red]Error: requests 库未安装[/]")
    except Exception as e:
        console.print(f"❌ [red]测试失败: {str(e)}[/]")


@webhook.command()
@click.argument("name")
def remove(name):
    """删除 Webhook"""
    hooks = _load_webhooks()

    if name not in hooks:
        console.print(f"[red]Webhook 不存在: {name}[/]")
        return

    del hooks[name]
    _save_webhooks(hooks)

    console.print(f"✅ [green]Webhook 已删除: {name}[/]")


@webhook.command()
@click.argument("event")
@click.option("--data", "-d", default="{}", help="事件数据 (JSON)")
def trigger(event, data):
    """触发 Webhook - lobster webhook trigger <event>

    示例:
        lobster webhook trigger message
        lobster webhook trigger backup --data '{"key": "value"}'
    """
    console.print(f"🔔 [bold]触发事件: {event}[/]")

    hooks = _load_webhooks()
    triggered = []

    for name, hook in hooks.items():
        if not hook.get("enabled"):
            continue

        if hook.get("event") != "*" and hook.get("event") != event:
            continue

        try:
            import requests

            import json

            event_data = json.loads(data) if data != "{}" else {}

            response = requests.request(
                method=hook.get("method", "POST"),
                url=hook["url"],
                json={
                    "event": event,
                    "data": event_data,
                    "source": "lobster",
                },
                headers=hook.get("headers", {}),
                timeout=10,
            )

            if response.status_code < 400:
                console.print(f"✅ {name}: 成功")
                triggered.append(name)
            else:
                console.print(f"❌ {name}: 失败 ({response.status_code})")

        except Exception as e:
            console.print(f"❌ {name}: 错误 - {str(e)}")

    console.print(f"\n触发 {len(triggered)}/{len(hooks)} Webhooks")


def _load_webhooks() -> dict:
    """加载 Webhook 列表"""
    if WEBHOOK_FILE.exists():
        with open(WEBHOOK_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _save_webhooks(hooks: dict):
    """保存 Webhook 列表"""
    with open(WEBHOOK_FILE, "w", encoding="utf-8") as f:
        json.dump(hooks, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    webhook()

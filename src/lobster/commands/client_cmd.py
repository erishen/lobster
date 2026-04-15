"""API 客户端命令模块"""

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


@click.group()
def client():
    """API 客户端命令"""
    pass


@client.command()
@click.argument("method", type=click.Choice(["GET", "POST", "PUT", "DELETE", "PATCH"]))
@click.argument("url")
@click.option("--data", "-d", default=None, help="请求数据 (JSON)")
@click.option("--header", "-H", multiple=True, help="自定义请求头")
@click.option("--auth", "-a", default=None, help="认证 Bearer Token")
@click.option("--form", "-f", default=None, help="表单数据 (key=value)")
@click.option("--output", "-o", default=None, help="输出文件")
def request(method, url, data, header, auth, form, output):
    """发送 API 请求 - lobster client request <method> <url>

    示例:
        lobster client request GET "https://api.example.com/users"
        lobster client request POST "https://api.example.com/users" --data '{"name": "test"}'
        lobster client request GET "https://api.example.com/data" -a "your-token"
    """
    console.print(Panel(f"🌐 [bold cyan]{method} {url}[/bold cyan]", border_style="blue"))

    try:
        import requests
    except ImportError:
        console.print("[red]Error: requests 库未安装[/]")
        console.print("[yellow]Install with:[/] pip install requests")
        return

    headers = {}
    for h in header:
        if ":" in h:
            key, value = h.split(":", 1)
            headers[key.strip()] = value.strip()

    if auth:
        headers["Authorization"] = f"Bearer {auth}"

    try:
        if data:
            try:
                import json

                body = json.loads(data)
            except (json.JSONDecodeError, ValueError):
                body = data

            response = requests.request(method, url, json=body, headers=headers, timeout=30)

        elif form:
            form_data = {}
            for item in form.split(","):
                if "=" in item:
                    key, value = item.split("=", 1)
                    form_data[key.strip()] = value.strip()

            response = requests.request(method, url, data=form_data, headers=headers, timeout=30)

        else:
            response = requests.request(method, url, headers=headers, timeout=30)

        console.print("\n📊 [bold]响应:[/]")
        console.print(f"   状态码: {response.status_code}")
        console.print(f"   耗时: {response.elapsed.total_seconds():.2f}s")

        if response.headers.get("Content-Type", "").startswith("application/json"):
            try:
                import json

                console.print("\n📄 [bold]响应内容 (JSON):[/]")
                console.print(json.dumps(response.json(), indent=2, ensure_ascii=False)[:2000])
            except Exception:
                console.print("\n📄 [bold]响应内容:[/]")
                console.print(response.text[:2000])
        else:
            console.print("\n📄 [bold]响应内容:[/]")
            console.print(response.text[:2000])

        if output:
            with open(output, "w", encoding="utf-8") as f:
                f.write(response.text)
            console.print(f"\n✅ [green]响应已保存到: {output}[/]")

    except Exception as e:
        console.print(f"\n❌ [red]请求失败: {str(e)}[/]")


@client.command()
@click.argument("url")
@click.option("--interval", "-i", default=60, help="检查间隔(秒)")
@click.option("--timeout", "-t", default=30, help="超时时间(秒)")
def ping(url, interval, timeout):
    """持续 Ping API - lobster client ping <url>

    示例:
        lobster client ping "https://api.example.com/health"
        lobster client ping "https://api.example.com/health" --interval 30
    """
    console.print(Panel(f"🏓 [bold cyan]持续 Ping: {url}[/bold cyan]", border_style="blue"))
    console.print(f"间隔: {interval} 秒, 超时: {timeout} 秒")
    console.print("按 Ctrl+C 停止...\n")

    try:
        import requests
        import time
        from datetime import datetime

        stats = {"success": 0, "failed": 0, "total": 0}

        while True:
            stats["total"] += 1
            start_time = time.time()

            try:
                response = requests.get(url, timeout=timeout)
                elapsed = time.time() - start_time

                if response.status_code < 400:
                    stats["success"] += 1
                    status = "✅"
                else:
                    stats["failed"] += 1
                    status = "❌"

                success_rate = (stats["success"] / stats["total"]) * 100
                console.print(
                    f"{status} [{datetime.now().strftime('%H:%M:%S')}] "
                    f"{response.status_code} - {elapsed:.2f}s "
                    f"(成功率: {success_rate:.1f}%)"
                )

            except Exception as e:
                stats["failed"] += 1
                elapsed = time.time() - start_time
                success_rate = (stats["success"] / stats["total"]) * 100
                console.print(
                    f"❌ [{datetime.now().strftime('%H:%M:%S')}] "
                    f"Error - {elapsed:.2f}s "
                    f"(成功率: {success_rate:.1f}%): {str(e)[:50]}"
                )

            time.sleep(interval)

    except KeyboardInterrupt:
        console.print("\n[yellow]停止 Ping[/]")
        console.print("\n📊 [bold]统计:[/]")
        console.print(f"   总请求: {stats['total']}")
        console.print(f"   成功: {stats['success']}")
        console.print(f"   失败: {stats['failed']}")

    except ImportError:
        console.print("[red]Error: requests 库未安装[/]")


@client.command()
@click.argument("url")
def docs(url):
    """获取 API 文档 - lobster client docs <url>

    示例:
        lobster client docs "https://api.example.com/openapi.json"
    """
    console.print(f"📚 [bold]获取 API 文档: {url}[/]")

    try:
        import requests
    except ImportError:
        console.print("[red]Error: requests 库未安装[/]")
        return

    try:
        response = requests.get(url, timeout=30)

        if response.status_code == 200:
            try:
                spec = response.json()

                if "openapi" in spec:
                    console.print("\n✅ [green]OpenAPI 文档获取成功[/]")
                    console.print(f"   版本: {spec.get('openapi')}")
                    console.print(f"   标题: {spec.get('info', {}).get('title', 'N/A')}")

                    paths = spec.get("paths", {})
                    console.print(f"\n📋 [bold]可用端点 ({len(paths)}):[/]")

                    table = Table()
                    table.add_column("方法", style="cyan", width=8)
                    table.add_column("路径", style="green")
                    table.add_column("说明", style="yellow")

                    for path, methods in list(paths.items())[:20]:
                        for method, details in methods.items():
                            if method.upper() in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                                summary = details.get("summary", details.get("operationId", ""))
                                table.add_row(method.upper(), path, summary[:40])

                    console.print(table)

                else:
                    console.print("\n📄 [bold]响应内容:[/]")
                    console.print(response.text[:2000])

            except Exception:
                console.print("\n📄 [bold]响应内容:[/]")
                console.print(response.text[:2000])

        else:
            console.print(f"❌ [red]请求失败: {response.status_code}[/]")

    except Exception as e:
        console.print(f"❌ [red]错误: {str(e)}[/]")


if __name__ == "__main__":
    client()

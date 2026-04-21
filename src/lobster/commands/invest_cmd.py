"""
Investment Commands for Lobster CLI.
投资相关命令 - 股票信号、投资组合分析
"""

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


@click.group()
def invest():
    """💰 Investment commands - 投资相关命令"""
    pass


@invest.command()
@click.option("--top", "-n", default=10, help="显示前 N 个信号")
@click.option("--min-confidence", "-c", default=0.6, help="最小置信度阈值")
def signals(top: int, min_confidence: float):
    """获取 ML 预测信号"""
    try:
        import requests

        response = requests.get("http://localhost:8000/api/ml/signals", timeout=10)
        if response.status_code != 200:
            console.print("[red]Error:[/] 无法连接到 Asset Lens API")
            console.print("[yellow]请确保 Asset Lens 服务正在运行:[/] asset-lens serve")
            return

        data = response.json()
        signals_list = data.get("signals", [])

        if not signals_list:
            console.print("[yellow]暂无预测信号[/]")
            if data.get("model_status") != "loaded":
                console.print("[dim]提示: 模型未加载，请先训练模型[/]")
            return

        filtered = [s for s in signals_list if s.get("confidence", 0) >= min_confidence]
        filtered = sorted(filtered, key=lambda x: x.get("confidence", 0), reverse=True)[:top]

        table = Table(title=f"ML 预测信号 (置信度 >= {min_confidence:.0%})")
        table.add_column("代码", style="cyan")
        table.add_column("名称")
        table.add_column("预测", justify="center")
        table.add_column("置信度", justify="right")
        table.add_column("上涨概率", justify="right")
        table.add_column("信号强度", justify="center")

        for s in filtered:
            prediction = s.get("prediction", "")
            pred_style = "green" if prediction == "up" else "red"
            pred_text = "📈 看涨" if prediction == "up" else "📉 看跌"

            strength = s.get("signal_strength", "weak")
            strength_style = (
                "green" if strength == "strong" else "yellow" if strength == "medium" else "dim"
            )

            table.add_row(
                s.get("code", ""),
                s.get("name", ""),
                f"[{pred_style}]{pred_text}[/{pred_style}]",
                f"{s.get('confidence', 0):.1%}",
                f"{s.get('up_prob', 0):.1%}",
                f"[{strength_style}]{strength}[/{strength_style}]",
            )

        console.print(table)
        console.print(
            f"\n[dim]共 {len(filtered)} 个信号 | 模型状态: {data.get('model_status', 'unknown')}[/]"
        )

    except ImportError:
        console.print("[red]Error:[/] requests 未安装")
        console.print("[yellow]安装:[/] pip install requests")
    except Exception as e:
        console.print(f"[red]Error:[/] {e}")


@invest.command()
@click.option("--detailed", "-d", is_flag=True, help="显示详细信息")
def portfolio(detailed: bool):
    """查看投资组合概览"""
    try:
        import requests

        response = requests.get("http://localhost:8000/api/portfolio/summary", timeout=10)
        if response.status_code != 200:
            console.print("[red]Error:[/] 无法连接到 Asset Lens API")
            console.print("[yellow]请确保 Asset Lens 服务正在运行:[/] asset-lens serve")
            return

        data = response.json()

        total_assets = data.get("total_assets", 0)
        total_profit = data.get("total_profit", 0)
        total_return = data.get("total_return", 0)
        position_count = data.get("position_count", 0)

        console.print(
            Panel(
                f"[bold cyan]总资产:[/] ¥{total_assets:,.2f}\n"
                f"[bold cyan]总收益:[/] {'[green]' if total_profit >= 0 else '[red]'}¥{total_profit:,.2f}[/{'green' if total_profit >= 0 else 'red'}]\n"
                f"[bold cyan]收益率:[/] {'[green]' if total_return >= 0 else '[red]'}{total_return:.2f}%[/{'green' if total_return >= 0 else 'red'}]\n"
                f"[bold cyan]持仓数量:[/] {position_count}",
                title="投资组合概览",
                border_style="cyan",
            )
        )

        if detailed:
            response = requests.get("http://localhost:8000/api/portfolio/items", timeout=10)
            if response.status_code == 200:
                items_data = response.json()
                items = items_data.get("items", [])

                if items:
                    table = Table(title="持仓详情")
                    table.add_column("名称", style="cyan")
                    table.add_column("类型")
                    table.add_column("当前金额", justify="right")
                    table.add_column("收益", justify="right")
                    table.add_column("收益率", justify="right")

                    for item in items[:20]:
                        profit = item.get("profit_amount", item.get("profit", 0))
                        rate = item.get("return_rate", item.get("profit_rate", 0))

                        table.add_row(
                            item.get("name", ""),
                            item.get("investment_type", item.get("type", "")),
                            f"¥{item.get('current_amount', 0):,.2f}",
                            f"{'[green]' if profit >= 0 else '[red]'}¥{profit:,.2f}[/{'green' if profit >= 0 else 'red'}]",
                            f"{'[green]' if rate >= 0 else '[red]'}{rate:.2f}%[/{'green' if rate >= 0 else 'red'}]",
                        )

                    console.print(table)

    except ImportError:
        console.print("[red]Error:[/] requests 未安装")
        console.print("[yellow]安装:[/] pip install requests")
    except Exception as e:
        console.print(f"[red]Error:[/] {e}")


@invest.command()
def risk():
    """查看风险预警"""
    try:
        import requests

        response = requests.get("http://localhost:8000/api/risk/alerts", timeout=10)
        if response.status_code != 200:
            console.print("[red]Error:[/] 无法连接到 Asset Lens API")
            console.print("[yellow]请确保 Asset Lens 服务正在运行:[/] asset-lens serve")
            return

        data = response.json()
        alerts = data.get("alerts", [])

        if not alerts:
            console.print("[green]✅ 暂无风险预警[/]")
            return

        table = Table(title="风险预警")
        table.add_column("级别", justify="center")
        table.add_column("类型")
        table.add_column("消息")
        table.add_column("建议")

        for alert in alerts:
            level = alert.get("level", "info")
            level_style = "red" if level == "danger" else "yellow" if level == "warning" else "blue"
            level_icon = "🔴" if level == "danger" else "🟡" if level == "warning" else "🔵"

            table.add_row(
                f"[{level_style}]{level_icon} {level}[/{level_style}]",
                alert.get("type", ""),
                alert.get("message", ""),
                alert.get("suggestion", ""),
            )

        console.print(table)

    except ImportError:
        console.print("[red]Error:[/] requests 未安装")
        console.print("[yellow]安装:[/] pip install requests")
    except Exception as e:
        console.print(f"[red]Error:[/] {e}")


@invest.command()
@click.argument("code")
def signal(code: str):
    """查看单只股票的预测信号"""
    try:
        import requests

        response = requests.get(f"http://localhost:8000/api/ml/signal/{code}", timeout=10)
        if response.status_code != 200:
            console.print("[red]Error:[/] 无法连接到 Asset Lens API")
            return

        data = response.json()
        signal_data = data.get("signal")

        if not signal_data:
            console.print(f"[yellow]无法获取 {code} 的预测信号[/]")
            if data.get("message"):
                console.print(f"[dim]{data.get('message')}[/]")
            return

        prediction = signal_data.get("prediction", "")
        confidence = signal_data.get("confidence", 0)
        up_prob = signal_data.get("up_prob", 0)
        down_prob = signal_data.get("down_prob", 0)

        pred_style = "green" if prediction == "up" else "red"
        pred_text = "📈 看涨" if prediction == "up" else "📉 看跌"

        console.print(
            Panel(
                f"[bold cyan]股票代码:[/] {code}\n"
                f"[bold cyan]预测方向:[/] [{pred_style}]{pred_text}[/{pred_style}]\n"
                f"[bold cyan]置信度:[/] {confidence:.1%}\n"
                f"[bold cyan]上涨概率:[/] [green]{up_prob:.1%}[/green]\n"
                f"[bold cyan]下跌概率:[/] [red]{down_prob:.1%}[/red]",
                title="股票预测信号",
                border_style="cyan",
            )
        )

    except ImportError:
        console.print("[red]Error:[/] requests 未安装")
        console.print("[yellow]安装:[/] pip install requests")
    except Exception as e:
        console.print(f"[red]Error:[/] {e}")


@invest.command()
def market():
    """查看市场行情"""
    try:
        import requests

        response = requests.get("http://localhost:8000/api/market/indexes", timeout=10)
        if response.status_code != 200:
            console.print("[red]Error:[/] 无法连接到 Asset Lens API")
            return

        data = response.json()
        indexes = data.get("indexes", [])

        if not indexes:
            console.print("[yellow]暂无市场数据[/]")
            return

        table = Table(title="市场行情")
        table.add_column("指数", style="cyan")
        table.add_column("价格", justify="right")
        table.add_column("涨跌", justify="right")
        table.add_column("涨跌幅", justify="right")

        for idx in indexes:
            change_pct = idx.get("change_percent", idx.get("changePercent", 0))
            style = "green" if change_pct >= 0 else "red"

            table.add_row(
                idx.get("name", ""),
                f"{idx.get('price', 0):.2f}",
                f"[{style}]{idx.get('change', 0):+.2f}[/{style}]",
                f"[{style}]{change_pct:+.2f}%[/{style}]",
            )

        console.print(table)

    except ImportError:
        console.print("[red]Error:[/] requests 未安装")
        console.print("[yellow]安装:[/] pip install requests")
    except Exception as e:
        console.print(f"[red]Error:[/] {e}")

"""投资工具模块 - 股票、基金、行情数据"""

from __future__ import annotations

import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from lobster.core.tools import ToolRegistry

from lobster.core.config import get_config


@dataclass
class StockQuote:
    """股票行情"""

    code: str
    name: str
    price: float
    change: float
    change_percent: float
    open: float
    high: float
    low: float
    volume: int
    amount: float
    timestamp: str


@dataclass
class FundQuote:
    """基金净值"""

    code: str
    name: str
    net_value: float
    acc_value: float
    date: str
    day_growth: float


class InvestmentTools:
    """投资工具类"""

    def __init__(self):
        self._cache: Dict[str, Any] = {}
        self._cache_time: Dict[str, float] = {}
        self._cache_ttl = 60

    def _get_cached(self, key: str) -> Optional[Any]:
        """获取缓存数据"""
        if key in self._cache and time.time() - self._cache_time.get(key, 0) < self._cache_ttl:
            return self._cache[key]
        return None

    def _set_cache(self, key: str, value: Any):
        """设置缓存"""
        self._cache[key] = value
        self._cache_time[key] = time.time()

    def get_stock_quote(self, code: str) -> Dict[str, Any]:
        """获取股票行情

        Args:
            code: 股票代码 (如 600519, sh600519, sz000001, hk00700)
        """
        cached = self._get_cached(f"stock_{code}")
        if cached:
            return cached

        try:
            import urllib.request
            import re

            # 处理代码格式
            if code.startswith("sh") or code.startswith("sz"):
                full_code = code
            elif code.startswith("hk"):
                full_code = code
            elif code.startswith("6"):
                full_code = f"sh{code}"
            elif code.startswith("0") or code.startswith("3"):
                full_code = f"sz{code}"
            else:
                full_code = code

            url = f"https://hq.sinajs.cn/list={full_code}"
            req = urllib.request.Request(
                url, headers={"Referer": "https://finance.sina.com.cn", "User-Agent": "Mozilla/5.0"}
            )

            with urllib.request.urlopen(req, timeout=10) as response:
                data = response.read().decode("gbk")

            match = re.search(r'="([^"]*)"', data)
            if not match:
                return {"error": f"未找到股票: {code}"}

            parts = match.group(1).split(",")
            if len(parts) < 32:
                return {"error": f"数据格式错误: {code}"}

            name = parts[0]
            open_price = float(parts[1]) if parts[1] else 0
            last_close = float(parts[2]) if parts[2] else 0
            price = float(parts[3]) if parts[3] else 0
            high = float(parts[4]) if parts[4] else 0
            low = float(parts[5]) if parts[5] else 0
            volume = int(float(parts[8])) if parts[8] else 0
            amount = float(parts[9]) if parts[9] else 0

            change = price - last_close if last_close > 0 else 0
            change_percent = (change / last_close * 100) if last_close > 0 else 0

            result = {
                "code": code,
                "name": name,
                "price": round(price, 2),
                "change": round(change, 2),
                "change_percent": round(change_percent, 2),
                "open": round(open_price, 2),
                "high": round(high, 2),
                "low": round(low, 2),
                "last_close": round(last_close, 2),
                "volume": volume,
                "amount": round(amount, 2),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

            self._set_cache(f"stock_{code}", result)
            return result

        except Exception as e:
            return {"error": f"获取股票行情失败: {str(e)}"}

    def get_fund_quote(self, code: str) -> Dict[str, Any]:
        """获取基金净值

        Args:
            code: 基金代码 (如 000001, 110022)
        """
        cached = self._get_cached(f"fund_{code}")
        if cached:
            return cached

        try:
            import urllib.request

            url = f"http://fundgz.1234567.com.cn/js/{code}.js"
            req = urllib.request.Request(
                url, headers={"Referer": "http://fund.eastmoney.com/", "User-Agent": "Mozilla/5.0"}
            )

            with urllib.request.urlopen(req, timeout=10) as response:
                data = response.read().decode("utf-8")

            import re

            match = re.search(r"jsonpgz\((.*)\)", data)
            if not match:
                return {"error": f"未找到基金: {code}"}

            fund_data = json.loads(match.group(1))

            result = {
                "code": fund_data.get("fundcode", code),
                "name": fund_data.get("name", ""),
                "net_value": float(fund_data.get("gsz", 0)),
                "acc_value": float(fund_data.get("gszzl", 0)),
                "date": fund_data.get("gztime", ""),
                "day_growth": float(fund_data.get("gszzl", 0)),
                "estimated": fund_data.get("gsz", ""),
            }

            self._set_cache(f"fund_{code}", result)
            return result

        except Exception as e:
            return {"error": f"获取基金净值失败: {str(e)}"}

    def get_index_quote(self, code: str) -> Dict[str, Any]:
        """获取指数行情

        Args:
            code: 指数代码 (如 sh000001 上证指数, sz399001 深证成指)
        """
        return self.get_stock_quote(code)

    def get_stock_list(self, codes: List[str]) -> Dict[str, Any]:
        """批量获取股票行情

        Args:
            codes: 股票代码列表
        """
        results = []
        for code in codes:
            quote = self.get_stock_quote(code)
            if "error" not in quote:
                results.append(quote)

        return {
            "count": len(results),
            "stocks": results,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

    def get_market_summary(self) -> Dict[str, Any]:
        """获取市场概况"""
        indices = [
            ("sh000001", "上证指数"),
            ("sz399001", "深证成指"),
            ("sz399006", "创业板指"),
            ("sh000300", "沪深300"),
            ("sh000016", "上证50"),
            ("sh000905", "中证500"),
        ]

        results = []
        for code, name in indices:
            quote = self.get_stock_quote(code)
            if "error" not in quote:
                quote["display_name"] = name
                results.append(quote)

        up_count = sum(1 for q in results if q.get("change", 0) > 0)
        down_count = sum(1 for q in results if q.get("change", 0) < 0)

        return {
            "indices": results,
            "summary": {
                "up_count": up_count,
                "down_count": down_count,
                "flat_count": len(results) - up_count - down_count,
            },
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

    def search_stock(self, keyword: str) -> Dict[str, Any]:
        """搜索股票

        Args:
            keyword: 股票名称或代码关键词
        """
        try:
            import urllib.request
            import urllib.parse

            encoded_keyword = urllib.parse.quote(keyword)
            url = f"https://suggest3.sinajs.cn/suggest/type=11,12,13,14,15&key={encoded_keyword}"
            req = urllib.request.Request(
                url, headers={"Referer": "https://finance.sina.com.cn", "User-Agent": "Mozilla/5.0"}
            )

            with urllib.request.urlopen(req, timeout=10) as response:
                data = response.read().decode("gbk")

            results = []
            lines = data.strip().split(";")

            for line in lines:
                if not line.strip():
                    continue
                parts = line.split(",")
                if len(parts) >= 4:
                    code = parts[3].strip('"')
                    name = parts[4].strip('"') if len(parts) > 4 else parts[1].strip('"')
                    market = parts[0].split("=")[1] if "=" in parts[0] else ""

                    results.append(
                        {
                            "code": code,
                            "name": name,
                            "market": market,
                        }
                    )

            return {
                "keyword": keyword,
                "count": len(results),
                "results": results[:20],
            }

        except Exception as e:
            return {"error": f"搜索股票失败: {str(e)}"}

    def get_stock_kline(self, code: str, period: str = "daily") -> Dict[str, Any]:
        """获取股票K线数据

        Args:
            code: 股票代码
            period: 周期 (daily, weekly, monthly)
        """
        try:
            import urllib.request

            market = "sh" if code.startswith("6") else "sz"
            full_code = f"{market}{code}"

            period_map = {
                "daily": "101",
                "weekly": "102",
                "monthly": "103",
            }

            url = f"https://quotes.sina.cn/cn/api/json_v2.php/CN_MarketDataService.getKLineData?symbol={full_code}&scale={period_map.get(period, '101')}&datalen=100"

            req = urllib.request.Request(
                url, headers={"Referer": "https://finance.sina.com.cn", "User-Agent": "Mozilla/5.0"}
            )

            with urllib.request.urlopen(req, timeout=10) as response:
                data = response.read().decode("utf-8")

            kline_data = json.loads(data)

            if not kline_data:
                return {"error": f"未获取到K线数据: {code}"}

            result = {
                "code": code,
                "period": period,
                "count": len(kline_data),
                "data": kline_data[-30:],
            }

            return result

        except Exception as e:
            return {"error": f"获取K线数据失败: {str(e)}"}


investment_tools = InvestmentTools()


def register_investment_tools(registry: "ToolRegistry"):
    """注册投资工具到注册表"""
    from lobster.core.tools import Tool

    registry.register(
        Tool(
            name="stock_quote",
            description="获取股票实时行情",
            parameters={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "股票代码 (如 sh600519, sz000001, hk00700)",
                    },
                },
                "required": ["code"],
            },
            handler=lambda code: investment_tools.get_stock_quote(code),
            category="investment",
        )
    )

    registry.register(
        Tool(
            name="fund_quote",
            description="获取基金净值",
            parameters={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "基金代码 (如 000001, 110022)",
                    },
                },
                "required": ["code"],
            },
            handler=lambda code: investment_tools.get_fund_quote(code),
            category="investment",
        )
    )

    registry.register(
        Tool(
            name="index_quote",
            description="获取指数行情",
            parameters={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "指数代码 (如 sh000001 上证指数)",
                    },
                },
                "required": ["code"],
            },
            handler=lambda code: investment_tools.get_index_quote(code),
            category="investment",
        )
    )

    registry.register(
        Tool(
            name="stock_list",
            description="批量获取股票行情",
            parameters={
                "type": "object",
                "properties": {
                    "codes": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "股票代码列表",
                    },
                },
                "required": ["codes"],
            },
            handler=lambda codes: investment_tools.get_stock_list(codes),
            category="investment",
        )
    )

    registry.register(
        Tool(
            name="market_summary",
            description="获取市场概况 (主要指数)",
            parameters={
                "type": "object",
                "properties": {},
                "required": [],
            },
            handler=lambda: investment_tools.get_market_summary(),
            category="investment",
        )
    )

    registry.register(
        Tool(
            name="search_stock",
            description="搜索股票",
            parameters={
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "股票名称或代码关键词",
                    },
                },
                "required": ["keyword"],
            },
            handler=lambda keyword: investment_tools.search_stock(keyword),
            category="investment",
        )
    )

    registry.register(
        Tool(
            name="stock_kline",
            description="获取股票K线数据",
            parameters={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "股票代码",
                    },
                    "period": {
                        "type": "string",
                        "enum": ["daily", "weekly", "monthly"],
                        "default": "daily",
                        "description": "K线周期",
                    },
                },
                "required": ["code"],
            },
            handler=lambda code, period="daily": investment_tools.get_stock_kline(code, period),
            category="investment",
        )
    )

    # Tushare 数据源 (需要 API Token)
    config = get_config()
    if config.has_tushare:

        def get_tushare_daily(
            code: str, start_date: str = "", end_date: str = ""
        ) -> Dict[str, Any]:
            """获取 Tushare 日线数据"""
            try:
                import tushare as ts

                ts.set_token(config.tushare_token)
                pro = ts.pro_api()

                df = pro.daily(ts_code=code, start_date=start_date, end_date=end_date)

                if df.empty:
                    return {"error": f"未获取到数据: {code}"}

                return {
                    "code": code,
                    "count": len(df),
                    "data": df.to_dict("records")[:30],
                }

            except ImportError:
                return {"error": "tushare 库未安装，请运行: pip install tushare"}
            except Exception as e:
                return {"error": f"Tushare 查询失败: {str(e)}"}

        def get_tushare_basic() -> Dict[str, Any]:
            """获取股票列表"""
            try:
                import tushare as ts

                ts.set_token(config.tushare_token)
                pro = ts.pro_api()

                df = pro.stock_basic(exchange="", list_status="L")

                return {
                    "count": len(df),
                    "stocks": df[["ts_code", "name", "industry", "market"]].to_dict("records")[:50],
                }

            except ImportError:
                return {"error": "tushare 库未安装，请运行: pip install tushare"}
            except Exception as e:
                return {"error": f"Tushare 查询失败: {str(e)}"}

        registry.register(
            Tool(
                name="tushare_daily",
                description="获取A股日线数据 (需要 Tushare Token)",
                parameters={
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "股票代码 (如 600519.SH)",
                        },
                        "start_date": {
                            "type": "string",
                            "description": "开始日期 (如 20240101)",
                        },
                        "end_date": {
                            "type": "string",
                            "description": "结束日期 (如 20241231)",
                        },
                    },
                    "required": ["code"],
                },
                handler=get_tushare_daily,
                category="investment",
            )
        )

        registry.register(
            Tool(
                name="tushare_stocks",
                description="获取A股股票列表 (需要 Tushare Token)",
                parameters={
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
                handler=get_tushare_basic,
                category="investment",
            )
        )

    # Alpha Vantage 数据源 (需要 API Key)
    if config.has_alphavantage:

        def get_alpha_quote(symbol: str) -> Dict[str, Any]:
            """获取 Alpha Vantage 股票行情"""
            try:
                import urllib.request

                url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={config.alphavantage_api_key}"

                with urllib.request.urlopen(url, timeout=10) as response:
                    data = json.loads(response.read().decode("utf-8"))

                if "Global Quote" not in data:
                    return {"error": f"未获取到数据: {symbol}"}

                quote = data["Global Quote"]
                return {
                    "symbol": symbol,
                    "price": float(quote.get("05. price", 0)),
                    "change": float(quote.get("09. change", 0)),
                    "change_percent": quote.get("10. change percent", "0%"),
                    "volume": int(quote.get("06. volume", 0)),
                    "latest_trading_day": quote.get("07. latest trading day", ""),
                }

            except Exception as e:
                return {"error": f"Alpha Vantage 查询失败: {str(e)}"}

        def get_alpha_forex(from_currency: str, to_currency: str = "CNY") -> Dict[str, Any]:
            """获取汇率"""
            try:
                import urllib.request

                url = f"https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency={from_currency}&to_currency={to_currency}&apikey={config.alphavantage_api_key}"

                with urllib.request.urlopen(url, timeout=10) as response:
                    data = json.loads(response.read().decode("utf-8"))

                if "Realtime Currency Exchange Rate" not in data:
                    return {"error": f"未获取到汇率: {from_currency}/{to_currency}"}

                rate = data["Realtime Currency Exchange Rate"]
                return {
                    "from": from_currency,
                    "to": to_currency,
                    "rate": float(rate.get("5. Exchange Rate", 0)),
                    "time": rate.get("6. Last Refreshed", ""),
                }

            except Exception as e:
                return {"error": f"Alpha Vantage 查询失败: {str(e)}"}

        registry.register(
            Tool(
                name="alpha_quote",
                description="获取美股行情 (需要 Alpha Vantage Key)",
                parameters={
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "股票代码 (如 AAPL, MSFT)",
                        },
                    },
                    "required": ["symbol"],
                },
                handler=get_alpha_quote,
                category="investment",
            )
        )

        registry.register(
            Tool(
                name="alpha_forex",
                description="获取汇率 (需要 Alpha Vantage Key)",
                parameters={
                    "type": "object",
                    "properties": {
                        "from_currency": {
                            "type": "string",
                            "description": "源货币 (如 USD)",
                        },
                        "to_currency": {
                            "type": "string",
                            "description": "目标货币 (如 CNY)",
                        },
                    },
                    "required": ["from_currency"],
                },
                handler=get_alpha_forex,
                category="investment",
            )
        )

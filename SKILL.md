# Lobster Tools Skill

为 OpenClaw 龙虾助理提供工具调用能力。

## 描述

Lobster 是一个工具集服务，为 AI 助理提供文件操作、网络请求、代码执行、系统交互、数据处理和投资分析等能力。

## 能力

### 文件操作
- `file_read` - 读取文件内容
- `file_write` - 写入文件内容
- `file_list` - 列出目录内容
- `file_delete` - 删除文件

### 网络请求
- `http_get` - 发送 HTTP GET 请求
- `http_post` - 发送 HTTP POST 请求
- `web_search` - 网络搜索

### 代码执行
- `run_python` - 执行 Python 代码
- `run_shell` - 执行 Shell 命令

### 系统交互
- `notify` - 发送系统通知
- `clipboard` - 操作剪贴板

### 数据处理
- `json_parse` - 解析 JSON 数据
- `text_process` - 文本处理
- `calculate` - 数学计算

### 投资工具 (免费)
- `stock_quote` - 获取股票实时行情 (新浪财经)
- `fund_quote` - 获取基金净值 (天天基金)
- `index_quote` - 获取指数行情
- `stock_list` - 批量获取股票行情
- `market_summary` - 获取市场概况
- `search_stock` - 搜索股票
- `stock_kline` - 获取K线数据

### 投资工具 (需要配置 API Key)
- `tushare_daily` - 获取A股日线数据 (Tushare)
- `tushare_stocks` - 获取A股股票列表 (Tushare)
- `alpha_quote` - 获取美股行情 (Alpha Vantage)
- `alpha_forex` - 获取汇率 (Alpha Vantage)

## 使用方式

### 启动服务

```bash
lobster api serve
```

服务默认运行在 `http://localhost:8000`

### API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/tools` | GET | 列出所有可用工具 |
| `/tools/openai` | GET | 获取 OpenAI Function Calling 格式 |
| `/tools/{name}` | GET | 获取工具详情 |
| `/tools/{name}/execute` | POST | 执行工具 |
| `/stats` | GET | 工具使用统计 |
| `/cache/stats` | GET | 缓存统计 |

### 调用示例

```python
import requests

# 获取工具列表
response = requests.get("http://localhost:8000/tools")
tools = response.json()["tools"]

# 执行工具
result = requests.post(
    "http://localhost:8000/tools/file_read/execute",
    json={"path": "/path/to/file.txt"}
)
print(result.json())
```

### OpenAI Function Calling 集成

```python
# 获取工具定义
tools = requests.get("http://localhost:8000/tools/openai").json()["tools"]

# 在 OpenAI API 中使用
response = openai.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "读取 /tmp/test.txt 文件"}],
    tools=tools
)

# 执行工具调用
if response.choices[0].message.tool_calls:
    tool_call = response.choices[0].message.tool_calls[0]
    result = requests.post(
        f"http://localhost:8000/tools/{tool_call.function.name}/execute",
        json=json.loads(tool_call.function.arguments)
    )
```

## 工具详情

### file_read
读取文件内容。

参数:
- `path` (string, required): 文件路径
- `encoding` (string, default: "utf-8"): 文件编码

返回:
```json
{
  "content": "文件内容",
  "size": 100,
  "lines": 10
}
```

### file_write
写入文件内容。

参数:
- `path` (string, required): 文件路径
- `content` (string, required): 文件内容
- `mode` (string, default: "write"): 写入模式 (write/append)

返回:
```json
{
  "path": "/absolute/path/to/file",
  "size": 100
}
```

### file_list
列出目录内容。

参数:
- `path` (string, default: "."): 目录路径
- `pattern` (string, default: "*"): 文件匹配模式

返回:
```json
{
  "files": [
    {"name": "file.txt", "path": "./file.txt", "type": "file", "size": 100}
  ],
  "count": 1
}
```

### http_get
发送 HTTP GET 请求。

参数:
- `url` (string, required): 请求 URL
- `headers` (object, optional): 请求头
- `timeout` (integer, default: 30): 超时时间

返回:
```json
{
  "status_code": 200,
  "content": "响应内容",
  "headers": {}
}
```

### run_python
执行 Python 代码。

参数:
- `code` (string, required): Python 代码
- `timeout` (integer, default: 30): 超时时间

返回:
```json
{
  "stdout": "标准输出",
  "stderr": "标准错误",
  "returncode": 0
}
```

### run_shell
执行 Shell 命令。

参数:
- `command` (string, required): Shell 命令
- `timeout` (integer, default: 30): 超时时间

返回:
```json
{
  "stdout": "标准输出",
  "stderr": "标准错误",
  "returncode": 0
}
```

### notify
发送系统通知。

参数:
- `message` (string, required): 通知内容
- `title` (string, default: "OpenClaw"): 通知标题

返回:
```json
{
  "sent": true,
  "message": "通知内容"
}
```

### json_parse
解析 JSON 数据。

参数:
- `data` (string, required): JSON 字符串
- `path` (string, optional): 提取路径 (如: data.items.0.name)

返回:
```json
{
  "data": "解析后的数据"
}
```

### text_process
文本处理。

参数:
- `text` (string, required): 输入文本
- `operation` (string, required): 操作类型 (uppercase/lowercase/trim/lines/words/count)

返回:
```json
{
  "result": "处理结果"
}
```

### calculate
数学计算。

参数:
- `expression` (string, required): 数学表达式

返回:
```json
{
  "expression": "2 + 2",
  "result": 4
}
```

### stock_quote
获取股票实时行情。

参数:
- `code` (string, required): 股票代码 (如 600519, sh600519)

返回:
```json
{
  "code": "600519",
  "name": "贵州茅台",
  "price": 1407.24,
  "change": -55.6,
  "change_percent": -3.8,
  "open": 1460.0,
  "high": 1465.0,
  "low": 1400.0,
  "volume": 12345678,
  "timestamp": "2024-04-18 15:00:00"
}
```

### fund_quote
获取基金净值。

参数:
- `code` (string, required): 基金代码 (如 110022)

返回:
```json
{
  "code": "110022",
  "name": "易方达消费行业股票",
  "net_value": 3.1517,
  "day_growth": -0.92,
  "date": "2024-04-17"
}
```

### market_summary
获取市场概况。

参数: 无

返回:
```json
{
  "indices": [
    {"code": "sh000001", "name": "上证指数", "price": 4051.43, "change_percent": -0.10}
  ],
  "summary": {
    "up_count": 3,
    "down_count": 3
  }
}
```

### search_stock
搜索股票。

参数:
- `keyword` (string, required): 股票名称或代码关键词

返回:
```json
{
  "keyword": "茅台",
  "count": 1,
  "results": [
    {"code": "sh600519", "name": "贵州茅台", "market": "sh"}
  ]
}
```

### stock_kline
获取K线数据。

参数:
- `code` (string, required): 股票代码
- `period` (string, default: "daily"): 周期 (daily/weekly/monthly)

返回:
```json
{
  "code": "600519",
  "period": "daily",
  "count": 100,
  "data": [...]
}
```

### alpha_quote
获取美股行情 (需要 Alpha Vantage API Key)。

参数:
- `symbol` (string, required): 股票代码 (如 AAPL, MSFT)

返回:
```json
{
  "symbol": "AAPL",
  "price": 270.23,
  "change": 6.83,
  "change_percent": "2.5930%",
  "volume": 59615468
}
```

### alpha_forex
获取汇率 (需要 Alpha Vantage API Key)。

参数:
- `from_currency` (string, required): 源货币 (如 USD)
- `to_currency` (string, default: "CNY"): 目标货币

返回:
```json
{
  "from": "USD",
  "to": "CNY",
  "rate": 6.8164,
  "time": "2024-04-18 00:50:57"
}
```

### tushare_daily
获取A股日线数据 (需要 Tushare Token)。

参数:
- `code` (string, required): 股票代码 (如 600519.SH)
- `start_date` (string, optional): 开始日期 (如 20240101)
- `end_date` (string, optional): 结束日期

返回:
```json
{
  "code": "600519.SH",
  "count": 100,
  "data": [...]
}
```

## 配置

创建 `.env` 文件配置 API Keys:

```env
# Alpha Vantage API (美股、汇率)
ALPHAVANTAGE_API_KEY=your_key_here

# Tushare API (A股数据)
TUSHARE_TOKEN=your_token_here

# Finnhub API (美股实时)
FINNHUB_API_KEY=your_key_here

# DeepSeek API (AI 分析)
DEEPSEEK_API_KEY=your_key_here
```

## 安装

```bash
pip install lobster

# 或安装所有功能
pip install "lobster[all]"
```

## 依赖

核心依赖:
- click >= 8.1.0
- pydantic >= 2.0.0
- rich >= 13.0.0
- litellm >= 1.0.0

可选依赖:
- fastapi, uvicorn (API 服务)
- requests (HTTP 请求)
- tushare (A股数据)
- streamlit (Web UI)

## 安全注意事项

- `run_shell` 和 `run_python` 具有较高权限，请谨慎使用
- 建议在生产环境中添加认证和授权机制
- 文件操作受系统权限限制
- API Keys 请妥善保管，不要提交到代码仓库

## 版本

当前版本: 0.1.0

## 许可证

MIT License

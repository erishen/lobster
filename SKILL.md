# Lobster Tools Skill

为 OpenClaw 龙虾助理提供工具调用能力。

## 描述

Lobster 是一个工具集服务，为 AI 助理提供文件操作、网络请求、代码执行、系统交互和数据处理等能力。

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
- streamlit (Web UI)

## 安全注意事项

- `run_shell` 和 `run_python` 具有较高权限，请谨慎使用
- 建议在生产环境中添加认证和授权机制
- 文件操作受系统权限限制

## 版本

当前版本: 0.1.0

## 许可证

MIT License

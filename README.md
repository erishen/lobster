# 🦞 Lobster - OpenClaw 龙虾助理工具集

为 OpenClaw 龙虾助理提供可调用的工具集 CLI。

## ✨ 特性

- 🔧 **工具注册表** - 提供标准化工具接口
- 🚀 **API 服务器** - REST API 供 OpenClaw 调用
- 📋 **OpenAI Function Calling** - 兼容 OpenAI 函数调用格式
- 🎯 **简单命令** - 易用的命令行结构
- 📦 **现代技术栈** - 基于 Click, Pydantic, Rich, LiteLLM

## 🚀 快速开始

### 安装

```bash
# 克隆仓库
git clone <repository-url>
cd lobster

# 安装基础依赖
make install
# 或
uv pip install -e ".[dev]"

# 安装可选功能
pip install -e ".[api]"      # API 服务器
pip install -e ".[serena]"   # Serena 代码分析
pip install -e ".[investment]"  # 投资工具
pip install -e ".[all]"      # 安装所有功能
```

### 基本使用

```bash
# 显示帮助
lobster --help

# 快捷命令
lobster ask "你的问题"
lobster remember "要记住的内容"
lobster recall "关键词"

# 交互式对话
lobster chat -i

# 启动 Web UI
lobster web
```

## 🔗 OpenClaw 集成

### 启动 API 服务器

```bash
# 启动 API 服务器
lobster api serve

# 指定端口
lobster api serve -p 8080
```

### API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/tools` | GET | 列出所有可用工具 |
| `/tools/openai` | GET | OpenAI Function Calling 格式 |
| `/tools/{name}` | GET | 获取工具详情 |
| `/tools/{name}/execute` | POST | 执行工具 |

### OpenClaw 调用示例

```python
import requests

# 获取工具列表
response = requests.get("http://localhost:8000/tools")
tools = response.json()["tools"]

# 执行工具
result = requests.post(
    "http://localhost:8000/tools/ask/execute",
    json={"question": "什么是 Python?"}
)
print(result.json())
```

### 可用工具

| 工具 | 分类 | 说明 |
|------|------|------|
| `ask` | ai | 向 AI 提问并获取回答 |
| `remember` | memory | 记住信息，存储到记忆库 |
| `recall` | memory | 从记忆库中搜索回忆 |
| `search` | search | 全局搜索（记忆、历史、项目） |
| `code_analyze` | code | 分析代码文件 |
| `data_analyze` | data | 分析数据文件 |
| `notify` | system | 发送系统通知 |
| `execute_command` | system | 执行系统命令 |

### OpenAI Function Calling 格式

```bash
# 获取 OpenAI 格式的工具定义
curl http://localhost:8000/tools/openai
```

返回格式：
```json
{
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "ask",
        "description": "向 AI 提问并获取回答",
        "parameters": {
          "type": "object",
          "properties": {
            "question": {"type": "string", "description": "要提问的问题"},
            "model": {"type": "string", "default": "ollama/gemma3"}
          },
          "required": ["question"]
        }
      }
    }
  ]
}
```

## 📖 命令列表

### 快捷命令

| 命令 | 说明 |
|------|------|
| `lobster ask "问题"` | 快速提问 |
| `lobster remember "内容"` | 快速记忆 |
| `lobster recall "关键词"` | 快速回忆 |
| `lobster status` | 快速状态检查 |

### 核心命令

| 命令 | 说明 |
|------|------|
| `lobster chat` | 对话模式 |
| `lobster api` | API 服务器 |
| `lobster config` | 配置管理 |
| `lobster memory` | 记忆管理 |
| `lobster search` | 全局搜索 |

### 工具命令

| 命令 | 说明 |
|------|------|
| `lobster code` | 代码分析工具 |
| `lobster data` | 数据分析工具 |
| `lobster project` | 项目管理工具 |
| `lobster notify` | 系统通知 |

### 高级命令

| 命令 | 说明 |
|------|------|
| `lobster datax` | 数据导出/导入 |
| `lobster scheduler` | 定时任务 |
| `lobster webhook` | Webhook 管理 |
| `lobster watch` | 文件监控 |
| `lobster client` | API 客户端 |

## 🛠️ 开发

### 项目结构

```
lobster/
├── src/lobster/
│   ├── commands/     # 命令模块
│   ├── core/         # 核心功能
│   │   ├── tools.py  # 工具注册表
│   │   ├── llm_client.py
│   │   └── memory_store.py
│   └── web/          # Web UI
├── tests/            # 测试文件
└── pyproject.toml    # 项目配置
```

### 开发命令

```bash
make install    # 安装依赖
make test       # 运行测试
make lint       # 代码检查
```

### 添加新工具

在 `src/lobster/core/tools.py` 中注册新工具：

```python
self.register(Tool(
    name="my_tool",
    description="工具描述",
    parameters={
        "type": "object",
        "properties": {
            "input": {"type": "string", "description": "输入参数"}
        },
        "required": ["input"]
    },
    handler=self._handle_my_tool,
    category="custom"
))
```

## 🔧 配置

### 环境变量

```bash
export OPENCLAW_URL="http://localhost:8000"
export OPENCLAW_API_KEY="your-api-key"
```

### 配置文件 (`~/.lobster/config.json`)

```json
{
  "service_url": "http://localhost:8000",
  "api_key": "your-api-key"
}
```

## 📦 依赖

### 核心依赖
- `click` - CLI 框架
- `pydantic` - 数据验证
- `rich` - 终端格式化
- `litellm` - LLM 集成

### 可选依赖
- `fastapi`, `uvicorn` - API 服务器
- `streamlit` - Web UI
- `watchdog` - 文件监控
- `requests` - HTTP 客户端

## 📝 License

MIT License

---

**Lobster** - 为 OpenClaw 龙虾助理提供强大工具支持！🦞

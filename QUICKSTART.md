# Lobster 快速入门指南

## 🚀 5分钟快速开始

### 1. 安装

```bash
cd /Users/erishen/Workspace/TraeSolo/lobster
make install
```

### 2. 基础使用

#### 快速提问
```bash
# 最简单的使用方式
lobster ask "什么是 AI?"

# 指定模型
lobster ask "解释下 Python 装饰器" -m ollama/llama3

# 流式输出
lobster ask "讲个故事" -s
```

#### OpenClaw 管理
```bash
# 检查状态
lobster openclaw status

# 启动服务
lobster openclaw start

# 查看日志
lobster openclaw logs
```

#### 代码审查
```bash
# 审查代码
lobster code review mycode.py

# 解释代码
lobster code explain algorithm.py
```

#### 文档处理
```bash
# 总结文档
lobster doc-tool summarize report.md

# 翻译文档
lobster doc-tool translate README.md en
```

---

## 📚 常用命令速查

### 快捷命令
| 命令 | 说明 | 示例 |
|------|------|------|
| `ask` | 快速提问 | `lobster ask "问题"` |
| `query` | 快速查询 RAG | `lobster query "问题"` |
| `remember` | 快速记忆 | `lobster remember "内容"` |
| `recall` | 快速回忆 | `lobster recall "关键词"` |

### OpenClaw 管理
| 命令 | 说明 | 示例 |
|------|------|------|
| `status` | 检查状态 | `lobster openclaw status` |
| `start` | 启动服务 | `lobster openclaw start` |
| `stop` | 停止服务 | `lobster openclaw stop` |
| `logs` | 查看日志 | `lobster openclaw logs` |

### 代码工具
| 命令 | 说明 | 示例 |
|------|------|------|
| `review` | 代码审查 | `lobster code review file.py` |
| `explain` | 代码解释 | `lobster code explain file.py` |
| `refactor` | 重构建议 | `lobster code refactor file.py` |
| `test` | 生成测试 | `lobster code test file.py` |

### 文档工具
| 命令 | 说明 | 示例 |
|------|------|------|
| `summarize` | 文档总结 | `lobster doc-tool summarize file.md` |
| `translate` | 文档翻译 | `lobster doc-tool translate file.md en` |
| `rewrite` | 文档改写 | `lobster doc-tool rewrite file.md` |
| `outline` | 生成大纲 | `lobster doc-tool outline file.md` |

---

## 💡 使用技巧

### 1. 配置默认模型
```bash
# 设置默认模型
lobster config set default_model ollama/llama3

# 查看配置
lobster config show
```

### 2. 使用记忆功能
```bash
# 添加记忆
lobster remember "OpenClaw 是一个 AI 助手项目" -t project

# 搜索记忆
lobster recall "OpenClaw"

# 查看所有记忆
lobster memory list
```

### 3. 交互式对话
```bash
# 启动交互式对话
lobster chat -i

# 启用记忆增强
lobster chat -i --with-memory
```

### 4. Web UI
```bash
# 启动 Web UI
lobster web

# 指定端口
lobster web --port 8502
```

---

## 🎯 典型工作流

### 工作流 1：代码审查
```bash
# 1. 审查代码
lobster code review mycode.py

# 2. 解释复杂部分
lobster code explain complex.py

# 3. 生成测试
lobster code test mycode.py

# 4. 生成文档
lobster code document mycode.py
```

### 工作流 2：文档处理
```bash
# 1. 总结文档
lobster doc-tool summarize report.md

# 2. 提取关键词
lobster doc-tool keywords report.md

# 3. 生成大纲
lobster doc-tool outline report.md

# 4. 翻译文档
lobster doc-tool translate report.md en
```

### 工作流 3：项目管理
```bash
# 1. 检查 OpenClaw 状态
lobster openclaw status

# 2. 启动服务
lobster openclaw start

# 3. 查看日志
lobster openclaw logs --follow

# 4. 与 OpenClaw 对话
lobster openclaw chat
```

---

## 🔧 高级功能

### 1. 批量处理
```bash
# 批量分割文档
lobster batch split /path/to/directory --pattern "*.txt"

# 批量索引文档
lobster batch index /path/to/directory
```

### 2. RAG 系统
```bash
# 上传文档到向量存储
lobster rag upload document.pdf

# 查询 RAG 系统
lobster rag query "问题"

# 搜索相似文档
lobster rag search "关键词"
```

### 3. 模板管理
```bash
# 查看内置模板
lobster template builtin

# 创建模板
lobster template create my_template

# 应用模板
lobster template apply my_template
```

---

## 📖 获取帮助

### 查看命令帮助
```bash
# 查看所有命令
lobster --help

# 查看特定命令帮助
lobster ask --help
lobster openclaw --help
lobster code --help
lobster doc-tool --help
```

### 系统诊断
```bash
# 检查系统状态
lobster doctor check

# 查看系统信息
lobster doctor info
```

---

## 🎉 开始使用

现在你已经了解了 Lobster 的基本用法，开始使用吧！

```bash
# 快速体验
lobster ask "你好，介绍一下你自己"

# 启动 OpenClaw
lobster openclaw start

# 开始对话
lobster chat -i
```

**祝你使用愉快！** 🦞

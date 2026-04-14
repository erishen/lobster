# Lobster CLI 工具使用指南

## 工具简介

Lobster CLI 是一个功能强大的命令行工具，集成了 LangChain 和 LiteLLM，提供文档处理、LLM 功能、RAG 系统、模型管理等全面功能。

## 安装位置

- 项目路径：`/Users/erishen/Workspace/TraeSolo/lobster`
- 虚拟环境：`/Users/erishen/Workspace/TraeSolo/lobster/.venv`

## 使用方法

### 激活环境

```bash
cd /Users/erishen/Workspace/TraeSolo/lobster
source .venv/bin/activate
```

### 基本命令格式

```bash
PYTHONPATH=src python -m lobster <command> [options]
```

## 核心功能

### 1. LLM 功能

**生成文本**
```bash
PYTHONPATH=src python -m lobster llm generate "你的问题" --model ollama/gemma3
```

**交互式聊天**
```bash
PYTHONPATH=src python -m lobster llm chat --model ollama/gemma3
```

**查看可用模型**
```bash
PYTHONPATH=src python -m lobster llm models
```

**流式生成**
```bash
PYTHONPATH=src python -m lobster llm stream "讲个故事" --model ollama/gemma3
```

### 2. 文档处理

**加载文档**
```bash
PYTHONPATH=src python -m lobster doc load /path/to/document.pdf
```

**分割文档**
```bash
PYTHONPATH=src python -m lobster doc split /path/to/document.txt --chunk-size 1000
```

**列出目录文档**
```bash
PYTHONPATH=src python -m lobster doc list /path/to/directory
```

### 3. RAG 系统

**上传文档到向量存储**
```bash
PYTHONPATH=src python -m lobster rag upload /path/to/document.txt --vector-store faiss --embedding-type ollama
```

**查询 RAG 系统**
```bash
PYTHONPATH=src python -m lobster rag query "你的问题" --model ollama/gemma3
```

**搜索相似文档**
```bash
PYTHONPATH=src python -m lobster rag search "搜索内容"
```

### 4. 模型管理

**列出已安装的 Ollama 模型**
```bash
PYTHONPATH=src python -m lobster model list
```

**拉取新模型**
```bash
PYTHONPATH=src python -m lobster model pull llama3.1:8b
```

**查看模型信息**
```bash
PYTHONPATH=src python -m lobster model info gemma3:latest
```

**查看流行模型**
```bash
PYTHONPATH=src python -m lobster model popular
```

### 5. 配置管理

**查看当前配置**
```bash
PYTHONPATH=src python -m lobster config show
```

**设置配置**
```bash
PYTHONPATH=src python -m lobster config set default_model ollama/gemma3
```

**获取配置值**
```bash
PYTHONPATH=src python -m lobster config get default_model
```

### 6. 记忆管理 (OpenClaw Memory)

**添加记忆**
```bash
PYTHONPATH=src python -m lobster memory add "OpenClaw 是一个 AI 助手项目" -t project -t openclaw
```

**列出所有记忆**
```bash
PYTHONPATH=src python -m lobster memory list
```

**搜索记忆**
```bash
PYTHONPATH=src python -m lobster memory search "OpenClaw"
```

**查看记忆统计**
```bash
PYTHONPATH=src python -m lobster memory stats
```

**删除记忆**
```bash
PYTHONPATH=src python -m lobster memory delete <memory_id>
```

**清空所有记忆**
```bash
PYTHONPATH=src python -m lobster memory clear
```

### 7. 批量处理

**批量分割文档**
```bash
PYTHONPATH=src python -m lobster batch split /path/to/directory --pattern "*.txt"
```

**批量索引文档**
```bash
PYTHONPATH=src python -m lobster batch index /path/to/directory --vector-store faiss
```

### 7. 工具命令

**文本统计**
```bash
PYTHONPATH=src python -m lobster util textstat /path/to/file.txt
```

**代码分析**
```bash
PYTHONPATH=src python -m lobster util codeinfo /path/to/code.py
```

**JSON 格式化**
```bash
PYTHONPATH=src python -m lobster util jsonfmt /path/to/file.json
```

**环境检查**
```bash
PYTHONPATH=src python -m lobster util envcheck
```

### 8. 系统诊断

**系统检查**
```bash
PYTHONPATH=src python -m lobster doctor check
```

**系统信息**
```bash
PYTHONPATH=src python -m lobster doctor info
```

**修复常见问题**
```bash
PYTHONPATH=src python -m lobster doctor fix
```

### 9. 模板管理

**查看内置模板**
```bash
PYTHONPATH=src python -m lobster template builtin
```

**创建模板**
```bash
PYTHONPATH=src python -m lobster template create my_template
```

**应用模板**
```bash
PYTHONPATH=src python -m lobster template apply my_template --model ollama/gemma3
```

### 10. 插件系统

**列出插件**
```bash
PYTHONPATH=src python -m lobster plugin list
```

**创建插件**
```bash
PYTHONPATH=src python -m lobster plugin create my_plugin
```

## 常用场景

### 场景 1：快速问答

```bash
cd /Users/erishen/Workspace/TraeSolo/lobster
source .venv/bin/activate
PYTHONPATH=src python -m lobster llm generate "什么是 LangChain?"
```

### 场景 2：文档问答

```bash
# 1. 上传文档
PYTHONPATH=src python -m lobster rag upload /path/to/document.pdf

# 2. 查询文档
PYTHONPATH=src python -m lobster rag query "文档的主要内容是什么?"
```

### 场景 3：批量处理文档

```bash
# 批量索引目录中的所有文档
PYTHONPATH=src python -m lobster batch index /path/to/documents --vector-store faiss
```

### 场景 4：代码分析

```bash
# 分析代码文件
PYTHONPATH=src python -m lobster util codeinfo /path/to/code.py
```

## 注意事项

1. **环境激活**：使用前必须激活虚拟环境
   ```bash
   cd /Users/erishen/Workspace/TraeSolo/lobster
   source .venv/bin/activate
   ```

2. **PYTHONPATH 设置**：所有命令都需要设置 PYTHONPATH=src

3. **Ollama 运行**：使用本地模型前，确保 Ollama 服务正在运行
   ```bash
   ollama serve
   ```

4. **模型选择**：
   - 本地模型：`ollama/gemma3`, `ollama/llama3.1:8b`, `ollama/deepseek-r1:7b`
   - 云端模型：`gpt-4o`, `claude-3-opus` (需要 API key)

5. **配置文件**：配置保存在 `~/.lobster/config.json`

6. **向量存储**：默认使用 FAISS，支持 Qdrant

## 依赖项目

- langchain-llm-toolkit：`/Users/erishen/Workspace/TraeSolo/langchain-llm-toolkit`
- Ollama：本地 LLM 服务

## 快速帮助

查看任何命令的帮助：
```bash
PYTHONPATH=src python -m lobster <command> --help
```

示例：
```bash
PYTHONPATH=src python -m lobster llm --help
PYTHONPATH=src python -m lobster rag --help
PYTHONPATH=src python -m lobster doc --help
```

## 完整命令列表

运行以下命令查看所有可用命令：
```bash
PYTHONPATH=src python -m lobster --help
```

## 测试

运行测试套件：
```bash
cd /Users/erishen/Workspace/TraeSolo/lobster
source .venv/bin/activate
python -m pytest tests/ -v
```

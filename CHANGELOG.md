# Changelog

All notable changes to this project will be documented in this file.

## [0.1.0] - 2024-01-01

### Added
- 初始版本发布
- 14 个工具供 OpenClaw 调用
  - 文件操作: file_read, file_write, file_list, file_delete
  - 网络请求: http_get, http_post, web_search
  - 代码执行: run_python, run_shell
  - 系统交互: notify, clipboard
  - 数据处理: json_parse, text_process, calculate
- API 服务器支持 OpenAI Function Calling 格式
- API Key 认证机制
- 安全验证
  - 路径安全验证
  - 命令执行白名单/黑名单
  - URL 安全验证
  - Python 代码危险操作检测
- 32 个 CLI 命令
- Web UI (Streamlit)
- 完整测试覆盖 (120 tests)

### Security
- API Key 认证保护 API 端点
- 文件操作路径验证防止目录遍历
- 命令执行黑名单防止危险操作
- URL 验证防止 SSRF 攻击
- Python 代码执行限制危险操作

### Changed
- 移除 langchain-llm-toolkit 依赖
- 改用 LiteLLM 直接调用 LLM
- 重新设计工具集专注于 AI 助理扩展能力

### Removed
- 旧命令: batch, document, llm, plugin, rag, util
- 旧模块: chat_session

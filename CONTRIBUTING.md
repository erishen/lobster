# Contributing to Lobster

感谢你对 Lobster 项目感兴趣！

## 开发环境设置

```bash
# 克隆仓库
git clone <repository-url>
cd lobster

# 安装开发依赖
make install

# 运行测试
make test

# 运行 lint
make lint
```

## 代码风格

- 使用 [Black](https://black.readthedocs.io/) 格式化代码
- 使用 [Ruff](https://docs.astral.sh/ruff/) 进行 lint 检查
- 遵循 PEP 8 规范
- 最大行长度: 100 字符

## 提交代码

1. Fork 仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 添加新工具

在 `src/lobster/core/tools.py` 中注册新工具：

```python
self.register(
    Tool(
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
    )
)
```

## 添加新命令

1. 在 `src/lobster/commands/` 创建命令文件
2. 在 `src/lobster/__main__.py` 导入并注册命令
3. 添加测试文件

## 测试

- 所有新功能必须有测试
- 测试覆盖率应保持在高水平
- 运行 `make test` 确保所有测试通过

## 安全注意事项

- 不要提交敏感信息（API keys, passwords）
- 文件操作需要路径验证
- 命令执行需要安全检查
- HTTP 请求需要 URL 验证

## 许可证

通过贡献代码，你同意你的代码将在 MIT 许可证下发布。

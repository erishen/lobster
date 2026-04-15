"""API Server 命令模块 - 供 OpenClaw 调用"""

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


@click.group()
def api():
    """API 服务命令"""
    pass


@api.command()
@click.option("--host", "-h", default="0.0.0.0", help="服务地址")
@click.option("--port", "-p", default=8000, help="服务端口")
@click.option("--reload", "-r", is_flag=True, help="启用热重载")
def serve(host, port, reload):
    """启动 API 服务器 - lobster api serve

    示例:
        lobster api serve
        lobster api serve -h 0.0.0.0 -p 8080
    """
    console.print(Panel("🚀 [bold cyan]启动 API 服务器[/bold cyan]", border_style="blue"))

    try:
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware
        import uvicorn

        app = FastAPI(
            title="Lobster API",
            version="0.1.0",
            description="Lobster CLI API - 供 OpenClaw 龙虾助理调用",
        )

        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        @app.get("/")
        def root():
            return {
                "name": "Lobster API",
                "version": "0.1.0",
                "description": "Lobster CLI API - 供 OpenClaw 龙虾助理调用",
            }

        @app.get("/health")
        def health():
            return {"status": "healthy"}

        @app.get("/tools")
        def list_tools():
            """列出所有可用工具 - OpenClaw 可调用"""
            from lobster.core.tools import registry

            return {"tools": registry.list_all(), "count": len(registry.list_all())}

        @app.get("/tools/openai")
        def get_openai_tools():
            """获取 OpenAI Function Calling 格式的工具列表"""
            from lobster.core.tools import registry

            return {"tools": registry.get_openai_tools()}

        @app.get("/tools/{tool_name}")
        def get_tool(tool_name: str):
            """获取单个工具详情"""
            from lobster.core.tools import registry

            tool = registry.get(tool_name)
            if not tool:
                return {"error": f"Tool not found: {tool_name}"}

            return {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters,
                "category": tool.category,
            }

        @app.post("/tools/{tool_name}/execute")
        def execute_tool(tool_name: str, parameters: dict):
            """执行工具 - OpenClaw 调用入口"""
            from lobster.core.tools import registry

            result = registry.execute(tool_name, **parameters)
            return result

        @app.post("/chat")
        def chat_endpoint(message: str, model: str = "ollama/gemma3"):
            from lobster.core.llm_client import get_llm_client

            llm = get_llm_client(model)
            response = llm.generate(message)
            return {"response": response, "model": model}

        @app.get("/memory")
        def list_memories():
            from lobster.core.memory_store import EnhancedMemoryManager

            memory = EnhancedMemoryManager()
            memories = memory.list_memories()
            return {"memories": memories, "count": len(memories)}

        @app.post("/memory")
        def add_memory(content: str, tags: str = "", category: str = "general"):
            from lobster.core.memory_store import EnhancedMemoryManager

            memory = EnhancedMemoryManager()
            tag_list = [t.strip() for t in tags.split(",")] if tags else []
            memory_id = memory.add_memory(content, tags=tag_list, category=category)
            return {"id": memory_id, "status": "added"}

        @app.get("/search")
        def search_memories(q: str):
            from lobster.core.memory_store import EnhancedMemoryManager

            memory = EnhancedMemoryManager()
            results = memory.search_memory(q, method="hybrid")
            return {"results": results, "count": len(results)}

        console.print("\n🌐 [bold green]API 服务器启动成功[/bold green]")
        console.print(f"   地址: http://{host}:{port}")
        console.print(f"   文档: http://{host}:{port}/docs")
        console.print("\n📋 [bold]OpenClaw 集成端点:[/]")
        console.print("  GET  /tools              - 列出所有工具")
        console.print("  GET  /tools/openai       - OpenAI Function Calling 格式")
        console.print("  GET  /tools/{name}       - 获取工具详情")
        console.print("  POST /tools/{name}/execute - 执行工具")
        console.print("\n📦 [bold]其他端点:[/]")
        console.print("  GET  /health    - 健康检查")
        console.print("  POST /chat      - 对话")
        console.print("  GET  /memory    - 列出记忆")
        console.print("  POST /memory    - 添加记忆")
        console.print("  GET  /search    - 搜索记忆\n")

        uvicorn.run(app, host=host, port=port, reload=reload)

    except ImportError:
        console.print("[red]Error:[/] FastAPI or uvicorn not installed")
        console.print("[yellow]Install with:[/] pip install fastapi uvicorn")


@api.command()
def tools():
    """列出所有可用工具"""
    console.print(Panel("🔧 [bold cyan]可用工具列表[/bold cyan]", border_style="blue"))

    from lobster.core.tools import registry

    tools_list = registry.list_all()

    table = Table()
    table.add_column("名称", style="cyan")
    table.add_column("分类", style="green")
    table.add_column("描述", style="yellow")

    for tool in tools_list:
        table.add_row(tool["name"], tool["category"], tool["description"])

    console.print(f"\n{table}\n")


@api.command()
def docs():
    """打开 API 文档"""
    console.print(Panel("📚 [bold cyan]API 文档[/bold cyan]", border_style="blue"))

    table = Table(title="OpenClaw 集成端点")
    table.add_column("方法", style="cyan", width=10)
    table.add_column("路径", style="green")
    table.add_column("说明", style="yellow")

    table.add_row("GET", "/tools", "列出所有可用工具")
    table.add_row("GET", "/tools/openai", "OpenAI Function Calling 格式")
    table.add_row("GET", "/tools/{name}", "获取工具详情")
    table.add_row("POST", "/tools/{name}/execute", "执行工具")

    console.print(f"\n{table}\n")

    table2 = Table(title="其他端点")
    table2.add_column("方法", style="cyan", width=10)
    table2.add_column("路径", style="green")
    table2.add_column("说明", style="yellow")

    table2.add_row("GET", "/", "根路径")
    table2.add_row("GET", "/health", "健康检查")
    table2.add_row("POST", "/chat", "发送消息进行对话")
    table2.add_row("GET", "/memory", "列出所有记忆")
    table2.add_row("POST", "/memory", "添加新记忆")
    table2.add_row("GET", "/search", "搜索记忆")

    console.print(f"{table2}\n")
    console.print("使用 lobster api serve 启动服务器后访问完整文档")


if __name__ == "__main__":
    api()

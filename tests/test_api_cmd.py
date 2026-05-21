"""测试 API 命令"""

import pytest
from click.testing import CliRunner
from lobster.commands.api_cmd import api


class TestApiDocs:
    """测试 API 文档命令"""

    def test_docs(self):
        """测试显示 API 文档"""
        runner = CliRunner()
        result = runner.invoke(api, ["docs"])

        assert result.exit_code == 0
        assert "API 文档" in result.output or "端点" in result.output


class TestApiServe:
    """测试 API 服务命令"""

    def test_serve_missing_fastapi(self):
        """测试缺少 FastAPI 时的提示"""
        runner = CliRunner()

        import sys

        fastapi_module = sys.modules.get("fastapi")
        uvicorn_module = sys.modules.get("uvicorn")

        sys.modules["fastapi"] = None
        sys.modules["uvicorn"] = None

        try:
            result = runner.invoke(api, ["serve"])
            assert "FastAPI" in result.output or "not installed" in result.output
        finally:
            if fastapi_module:
                sys.modules["fastapi"] = fastapi_module
            else:
                sys.modules.pop("fastapi", None)
            if uvicorn_module:
                sys.modules["uvicorn"] = uvicorn_module
            else:
                sys.modules.pop("uvicorn", None)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

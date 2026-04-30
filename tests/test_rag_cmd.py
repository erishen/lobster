"""
Tests for Lobster RAG Commands.
RAG 命令测试
"""

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import click
from click.testing import CliRunner

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from lobster.commands.rag_cmd import rag, status, ask


class TestRAGGroup:
    """测试 RAG 命令组"""

    def test_rag_group_exists(self):
        """测试 RAG 命令组存在"""
        assert isinstance(rag, click.Group)

    def test_rag_has_commands(self):
        """测试 RAG 命令组包含命令"""
        assert "status" in rag.commands
        assert "ask" in rag.commands


class TestStatusCommand:
    """测试状态命令"""

    def test_status_service_running(self):
        """测试服务运行中"""
        runner = CliRunner()

        with patch("requests.get") as mock_get:
            mock_health = MagicMock()
            mock_health.status_code = 200

            mock_info = MagicMock()
            mock_info.status_code = 200
            mock_info.json.return_value = {
                "status": "ready",
                "vector_store_type": "qdrant",
            }

            mock_get.side_effect = [mock_health, mock_info]

            result = runner.invoke(status)

            assert result.exit_code == 0

    def test_status_service_error(self):
        """测试服务异常"""
        runner = CliRunner()

        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_get.return_value = mock_response

            result = runner.invoke(status)

            assert result.exit_code == 0

    def test_status_connection_error(self):
        """测试连接错误"""
        runner = CliRunner()

        import requests

        with patch("requests.get") as mock_get:
            mock_get.side_effect = requests.exceptions.ConnectionError()

            result = runner.invoke(status)

            assert result.exit_code == 0


class TestAskCommand:
    """测试查询命令"""

    def test_ask_success(self):
        """测试查询成功"""
        runner = CliRunner()

        with patch("requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "answer": "这是一个测试回答",
                "sources": [{"content": "相关文档内容", "metadata": {"source": "test.md"}}],
            }
            mock_post.return_value = mock_response

            result = runner.invoke(ask, ["测试问题"])

            assert result.exit_code == 0

    def test_ask_with_top_k(self):
        """测试指定 top_k"""
        runner = CliRunner()

        with patch("requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "answer": "测试回答",
                "sources": [],
            }
            mock_post.return_value = mock_response

            result = runner.invoke(ask, ["测试问题", "-k", "5"])

            assert result.exit_code == 0

    def test_ask_api_error(self):
        """测试 API 错误"""
        runner = CliRunner()

        with patch("requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_post.return_value = mock_response

            result = runner.invoke(ask, ["测试问题"])

            assert result.exit_code == 0


class TestRAGAPIURL:
    """测试 RAG API URL"""

    def test_default_api_url(self):
        """测试默认 API URL"""
        from lobster.commands.rag_cmd import RAG_API_URL

        assert RAG_API_URL == os.environ.get("RAG_API_URL", "http://localhost:8000")

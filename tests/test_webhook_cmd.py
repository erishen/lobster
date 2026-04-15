"""测试 Webhook 命令"""

import pytest
from pathlib import Path
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from lobster.commands.webhook_cmd import webhook


class TestWebhookAdd:
    """测试添加 Webhook"""

    def test_add_webhook(self, tmp_path):
        """测试添加 Webhook"""
        runner = CliRunner()

        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(
                webhook,
                ["add", "test_hook", "https://example.com/webhook"],
            )

            assert result.exit_code == 0
            assert "Webhook 已添加" in result.output

    def test_add_webhook_with_event(self, tmp_path):
        """测试添加带事件的 Webhook"""
        runner = CliRunner()

        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(
                webhook,
                ["add", "event_hook", "https://example.com/webhook", "--event", "message"],
            )

            assert result.exit_code == 0


class TestWebhookList:
    """测试列出 Webhook"""

    def test_list_empty(self, tmp_path):
        """测试空列表"""
        runner = CliRunner()

        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(webhook, ["list"])

            assert result.exit_code == 0
            assert "没有 Webhook" in result.output

    def test_list_with_hooks(self, tmp_path):
        """测试有 Webhook 的列表"""
        runner = CliRunner()

        with runner.isolated_filesystem(temp_dir=tmp_path):
            runner.invoke(webhook, ["add", "hook1", "https://example.com/1"])
            result = runner.invoke(webhook, ["list"])

            assert result.exit_code == 0


class TestWebhookRemove:
    """测试删除 Webhook"""

    def test_remove_nonexistent(self, tmp_path):
        """测试删除不存在的 Webhook"""
        runner = CliRunner()

        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(webhook, ["remove", "nonexistent"])

            assert result.exit_code == 0
            assert "不存在" in result.output

    def test_remove_existing(self, tmp_path):
        """测试删除存在的 Webhook"""
        runner = CliRunner()

        with runner.isolated_filesystem(temp_dir=tmp_path):
            runner.invoke(webhook, ["add", "hook1", "https://example.com/1"])
            result = runner.invoke(webhook, ["remove", "hook1"])

            assert result.exit_code == 0
            assert "已删除" in result.output


class TestWebhookTest:
    """测试 Webhook 测试"""

    def test_test_nonexistent(self, tmp_path):
        """测试不存在的 Webhook"""
        runner = CliRunner()

        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(webhook, ["test", "nonexistent"])

            assert result.exit_code == 0
            assert "不存在" in result.output


class TestWebhookTrigger:
    """测试触发 Webhook"""

    def test_trigger_no_hooks(self, tmp_path):
        """测试没有 Webhook 时触发"""
        runner = CliRunner()

        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(webhook, ["trigger", "test_event"])

            assert result.exit_code == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

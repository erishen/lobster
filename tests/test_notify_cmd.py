"""测试通知命令"""

import pytest
from click.testing import CliRunner
from unittest.mock import patch
from lobster.commands.notify_cmd import notify


class TestNotifySend:
    """测试发送通知"""

    def test_send_macos(self):
        """测试 macOS 通知"""
        runner = CliRunner()

        with patch("lobster.commands.notify_cmd._send_macos"):
            result = runner.invoke(notify, ["send", "测试消息"])

            assert result.exit_code == 0

    def test_send_with_title(self):
        """测试带标题的通知"""
        runner = CliRunner()

        with patch("lobster.commands.notify_cmd._send_macos"):
            result = runner.invoke(notify, ["send", "测试消息", "--title", "测试标题"])

            assert result.exit_code == 0


class TestNotifyAlert:
    """测试警报通知"""

    def test_alert(self):
        """测试发送警报"""
        runner = CliRunner()

        with patch("lobster.commands.notify_cmd._send_macos"):
            result = runner.invoke(notify, ["alert", "警报消息"])

            assert result.exit_code == 0


class TestNotifyBeep:
    """测试提示音"""

    def test_beep(self):
        """测试播放提示音"""
        runner = CliRunner()
        result = runner.invoke(notify, ["beep"])

        assert result.exit_code == 0


class TestNotifyCheck:
    """测试通知功能检查"""

    def test_notify_check(self):
        """测试通知检查功能"""
        runner = CliRunner()

        with patch("lobster.commands.notify_cmd._send_macos"):
            result = runner.invoke(notify, ["check"])

            assert result.exit_code == 0


class TestNotifyList:
    """测试通知历史"""

    def test_list(self):
        """测试列出通知历史"""
        runner = CliRunner()
        result = runner.invoke(notify, ["list"])

        assert result.exit_code == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

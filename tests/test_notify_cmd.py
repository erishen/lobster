"""测试通知命令"""

import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from lobster.commands.notify_cmd import notify


class TestNotifySend:
    """测试发送通知"""

    def test_send_macos(self):
        """测试 macOS 通知"""
        runner = CliRunner()

        with patch("lobster.commands.notify_cmd._send_macos") as mock_send:
            result = runner.invoke(notify, ["send", "测试消息"])

            assert result.exit_code == 0

    def test_send_with_title(self):
        """测试带标题的通知"""
        runner = CliRunner()

        with patch("lobster.commands.notify_cmd._send_macos") as mock_send:
            result = runner.invoke(notify, ["send", "测试消息", "--title", "测试标题"])

            assert result.exit_code == 0


class TestNotifyAlert:
    """测试警报通知"""

    def test_alert(self):
        """测试发送警报"""
        runner = CliRunner()

        with patch("lobster.commands.notify_cmd._send_macos") as mock_send:
            result = runner.invoke(notify, ["alert", "警报消息"])

            assert result.exit_code == 0


class TestNotifyBeep:
    """测试提示音"""

    def test_beep(self):
        """测试播放提示音"""
        runner = CliRunner()
        result = runner.invoke(notify, ["beep"])

        assert result.exit_code == 0


class TestNotifyTest:
    """测试通知功能测试"""

    @pytest.mark.skip(reason="test 命令名称与 pytest 冲突")
    def test_notify_test(self):
        """测试通知功能"""
        import lobster.commands.notify_cmd as notify_module

        test_cmd = getattr(notify_module, "test")
        runner = CliRunner()

        with patch("lobster.commands.notify_cmd._send_macos"):
            result = runner.invoke(test_cmd, [])

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

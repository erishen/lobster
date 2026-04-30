"""
Tests for Lobster Scheduler Commands.
定时任务命令测试
"""

import json
import sys
from pathlib import Path
from unittest.mock import patch

import click
from click.testing import CliRunner

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from lobster.commands.scheduler_cmd import (
    scheduler,
    add,
    list,
    enable,
    disable,
    remove,
    _load_tasks,
    _save_tasks,
)


class TestSchedulerGroup:
    """测试定时任务命令组"""

    def test_scheduler_group_exists(self):
        """测试定时任务命令组存在"""
        assert isinstance(scheduler, click.Group)

    def test_scheduler_has_commands(self):
        """测试定时任务命令组包含命令"""
        assert "add" in scheduler.commands
        assert "list" in scheduler.commands
        assert "enable" in scheduler.commands
        assert "disable" in scheduler.commands
        assert "remove" in scheduler.commands
        assert "run" in scheduler.commands


class TestAddCommand:
    """测试添加任务命令"""

    def test_add_task_interval(self, tmp_path):
        """测试添加间隔任务"""
        runner = CliRunner()

        with patch("lobster.commands.scheduler_cmd.SCHEDULER_FILE", tmp_path / "scheduler.json"):
            from lobster.commands import scheduler_cmd

            scheduler_cmd.SCHEDULER_FILE = tmp_path / "scheduler.json"

            result = runner.invoke(
                add,
                ["backup", "lobster datax backup", "--interval", "3600"],
            )

            assert result.exit_code == 0
            assert "任务已添加" in result.output

    def test_add_task_cron(self, tmp_path):
        """测试添加 Cron 任务"""
        runner = CliRunner()

        with patch("lobster.commands.scheduler_cmd.SCHEDULER_FILE", tmp_path / "scheduler.json"):
            from lobster.commands import scheduler_cmd

            scheduler_cmd.SCHEDULER_FILE = tmp_path / "scheduler.json"

            result = runner.invoke(
                add,
                ["daily_report", "lobster data analyze", "--cron", "0 9 * * *"],
            )

            assert result.exit_code == 0


class TestListCommand:
    """测试列出任务命令"""

    def test_list_empty(self, tmp_path):
        """测试空任务列表"""
        runner = CliRunner()

        with patch("lobster.commands.scheduler_cmd.SCHEDULER_FILE", tmp_path / "scheduler.json"):
            from lobster.commands import scheduler_cmd

            scheduler_cmd.SCHEDULER_FILE = tmp_path / "scheduler.json"

            result = runner.invoke(list)

            assert result.exit_code == 0
            assert "没有定时任务" in result.output

    def test_list_with_tasks(self, tmp_path):
        """测试有任务列表"""
        runner = CliRunner()

        scheduler_file = tmp_path / "scheduler.json"
        tasks = {
            "backup": {
                "name": "backup",
                "command": "lobster datax backup",
                "interval": 3600,
                "cron": None,
                "enabled": True,
                "run_count": 5,
            },
            "report": {
                "name": "report",
                "command": "lobster data analyze",
                "interval": 86400,
                "cron": "0 9 * * *",
                "enabled": False,
                "run_count": 0,
            },
        }

        with open(scheduler_file, "w") as f:
            json.dump(tasks, f)

        with patch("lobster.commands.scheduler_cmd.SCHEDULER_FILE", scheduler_file):
            from lobster.commands import scheduler_cmd

            scheduler_cmd.SCHEDULER_FILE = scheduler_file

            result = runner.invoke(list)

            assert result.exit_code == 0


class TestEnableCommand:
    """测试启用任务命令"""

    def test_enable_existing(self, tmp_path):
        """测试启用已存在任务"""
        runner = CliRunner()

        scheduler_file = tmp_path / "scheduler.json"
        tasks = {
            "backup": {
                "name": "backup",
                "command": "lobster datax backup",
                "enabled": False,
            }
        }

        with open(scheduler_file, "w") as f:
            json.dump(tasks, f)

        with patch("lobster.commands.scheduler_cmd.SCHEDULER_FILE", scheduler_file):
            from lobster.commands import scheduler_cmd

            scheduler_cmd.SCHEDULER_FILE = scheduler_file

            result = runner.invoke(enable, ["backup"])

            assert result.exit_code == 0
            assert "已启用" in result.output

    def test_enable_not_existing(self, tmp_path):
        """测试启用不存在任务"""
        runner = CliRunner()

        with patch("lobster.commands.scheduler_cmd.SCHEDULER_FILE", tmp_path / "scheduler.json"):
            from lobster.commands import scheduler_cmd

            scheduler_cmd.SCHEDULER_FILE = tmp_path / "scheduler.json"

            result = runner.invoke(enable, ["nonexistent"])

            assert result.exit_code == 0
            assert "不存在" in result.output


class TestDisableCommand:
    """测试禁用任务命令"""

    def test_disable_existing(self, tmp_path):
        """测试禁用已存在任务"""
        runner = CliRunner()

        scheduler_file = tmp_path / "scheduler.json"
        tasks = {
            "backup": {
                "name": "backup",
                "command": "lobster datax backup",
                "enabled": True,
            }
        }

        with open(scheduler_file, "w") as f:
            json.dump(tasks, f)

        with patch("lobster.commands.scheduler_cmd.SCHEDULER_FILE", scheduler_file):
            from lobster.commands import scheduler_cmd

            scheduler_cmd.SCHEDULER_FILE = scheduler_file

            result = runner.invoke(disable, ["backup"])

            assert result.exit_code == 0
            assert "已禁用" in result.output


class TestRemoveCommand:
    """测试删除任务命令"""

    def test_remove_existing(self, tmp_path):
        """测试删除已存在任务"""
        runner = CliRunner()

        scheduler_file = tmp_path / "scheduler.json"
        tasks = {
            "backup": {
                "name": "backup",
                "command": "lobster datax backup",
                "enabled": True,
            }
        }

        with open(scheduler_file, "w") as f:
            json.dump(tasks, f)

        with patch("lobster.commands.scheduler_cmd.SCHEDULER_FILE", scheduler_file):
            from lobster.commands import scheduler_cmd

            scheduler_cmd.SCHEDULER_FILE = scheduler_file

            result = runner.invoke(remove, ["backup"])

            assert result.exit_code == 0
            assert "已删除" in result.output

    def test_remove_not_existing(self, tmp_path):
        """测试删除不存在任务"""
        runner = CliRunner()

        with patch("lobster.commands.scheduler_cmd.SCHEDULER_FILE", tmp_path / "scheduler.json"):
            from lobster.commands import scheduler_cmd

            scheduler_cmd.SCHEDULER_FILE = tmp_path / "scheduler.json"

            result = runner.invoke(remove, ["nonexistent"])

            assert result.exit_code == 0
            assert "不存在" in result.output


class TestLoadSaveTasks:
    """测试加载和保存任务"""

    def test_load_empty(self, tmp_path):
        """测试加载空文件"""
        scheduler_file = tmp_path / "scheduler.json"

        with patch("lobster.commands.scheduler_cmd.SCHEDULER_FILE", scheduler_file):
            from lobster.commands import scheduler_cmd

            scheduler_cmd.SCHEDULER_FILE = scheduler_file

            tasks = _load_tasks()
            assert tasks == {}

    def test_save_and_load(self, tmp_path):
        """测试保存和加载"""
        scheduler_file = tmp_path / "scheduler.json"

        with patch("lobster.commands.scheduler_cmd.SCHEDULER_FILE", scheduler_file):
            from lobster.commands import scheduler_cmd

            scheduler_cmd.SCHEDULER_FILE = scheduler_file

            tasks = {
                "test": {
                    "name": "test",
                    "command": "echo test",
                    "enabled": True,
                }
            }

            _save_tasks(tasks)
            loaded = _load_tasks()

            assert loaded == tasks

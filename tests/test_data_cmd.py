"""
Tests for Lobster Data Commands.
数据命令测试
"""

import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import click
from click.testing import CliRunner

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from lobster.commands.data_cmd import data, analyze, stats


class TestDataGroup:
    """测试数据命令组"""

    def test_data_group_exists(self):
        """测试数据命令组存在"""
        assert isinstance(data, click.Group)

    def test_data_has_commands(self):
        """测试数据命令组包含命令"""
        assert "analyze" in data.commands
        assert "stats" in data.commands


class TestAnalyzeCommand:
    """测试分析命令"""

    def test_analyze_csv_file(self):
        """测试分析 CSV 文件"""
        runner = CliRunner()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("name,value\n")
            f.write("A,100\n")
            f.write("B,200\n")
            csv_path = Path(f.name)

        try:
            with patch("lobster.commands.data_cmd.get_llm_client") as mock_llm:
                mock_client = MagicMock()
                mock_client.generate.return_value = "这是一个测试分析结果"
                mock_llm.return_value = mock_client

                result = runner.invoke(analyze, [str(csv_path)])

                assert result.exit_code == 0
        finally:
            csv_path.unlink(missing_ok=True)

    def test_analyze_json_file(self):
        """测试分析 JSON 文件"""
        runner = CliRunner()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"name": "test", "values": [1, 2, 3]}, f)
            json_path = Path(f.name)

        try:
            with patch("lobster.commands.data_cmd.get_llm_client") as mock_llm:
                mock_client = MagicMock()
                mock_client.generate.return_value = "JSON 分析结果"
                mock_llm.return_value = mock_client

                result = runner.invoke(analyze, [str(json_path)])

                assert result.exit_code == 0
        finally:
            json_path.unlink(missing_ok=True)

    def test_analyze_with_model(self):
        """测试指定模型分析"""
        runner = CliRunner()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("test data")
            file_path = Path(f.name)

        try:
            with patch("lobster.commands.data_cmd.get_llm_client") as mock_llm:
                mock_client = MagicMock()
                mock_client.generate.return_value = "分析结果"
                mock_llm.return_value = mock_client

                result = runner.invoke(analyze, [str(file_path), "-m", "gpt-4"])

                assert result.exit_code == 0
        finally:
            file_path.unlink(missing_ok=True)

    def test_analyze_file_not_found(self):
        """测试文件不存在"""
        runner = CliRunner()

        result = runner.invoke(analyze, ["/nonexistent/file.csv"])

        assert result.exit_code != 0


class TestStatsCommand:
    """测试统计命令"""

    def test_stats_csv_file(self):
        """测试 CSV 文件统计"""
        runner = CliRunner()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("name,value\n")
            f.write("A,100\n")
            f.write("B,200\n")
            f.write("C,300\n")
            csv_path = Path(f.name)

        try:
            result = runner.invoke(stats, [str(csv_path)])

            assert result.exit_code == 0
        finally:
            csv_path.unlink(missing_ok=True)

    def test_stats_json_file(self):
        """测试 JSON 文件统计"""
        runner = CliRunner()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"items": [1, 2, 3, 4, 5]}, f)
            json_path = Path(f.name)

        try:
            result = runner.invoke(stats, [str(json_path)])

            assert result.exit_code == 0
        finally:
            json_path.unlink(missing_ok=True)

    def test_stats_with_output(self):
        """测试输出到文件"""
        runner = CliRunner()

        with tempfile.TemporaryDirectory() as temp_dir:
            input_file = Path(temp_dir) / "data.csv"
            output_file = Path(temp_dir) / "stats.txt"

            with open(input_file, "w") as f:
                f.write("name,value\nA,100\n")

            result = runner.invoke(stats, [str(input_file), "-o", str(output_file)])

            assert result.exit_code == 0

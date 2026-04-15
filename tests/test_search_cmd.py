"""测试搜索命令"""

import pytest
from pathlib import Path
from click.testing import CliRunner
from lobster.commands.search_cmd import search


class TestSearch:
    """测试全局搜索命令"""

    def test_search_no_scope(self):
        """测试未指定搜索范围"""
        runner = CliRunner()
        result = runner.invoke(search, ["test"])

        assert result.exit_code == 0
        assert "指定搜索范围" in result.output

    def test_search_memory(self, tmp_path):
        """测试搜索记忆"""
        runner = CliRunner()

        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(search, ["test", "--memory"])

            assert result.exit_code == 0

    def test_search_history(self, tmp_path):
        """测试搜索历史"""
        runner = CliRunner()

        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(search, ["test", "--history"])

            assert result.exit_code == 0

    def test_search_project(self, tmp_path):
        """测试搜索项目"""
        runner = CliRunner()

        with runner.isolated_filesystem(temp_dir=tmp_path):
            test_file = Path("test.py")
            test_file.write_text("test content")

            result = runner.invoke(search, ["test", "--project"])

            assert result.exit_code == 0

    def test_search_all(self, tmp_path):
        """测试搜索所有"""
        runner = CliRunner()

        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(search, ["test", "--all"])

            assert result.exit_code == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

"""测试数据导出/导入命令"""

import pytest
import json
from pathlib import Path
from click.testing import CliRunner
from lobster.commands.datax_cmd import datax


class TestDataxExport:
    """测试导出命令"""

    def test_export_no_content(self):
        """测试未指定导出内容"""
        runner = CliRunner()
        result = runner.invoke(datax, ["export"])

        assert result.exit_code == 0
        assert "指定导出内容" in result.output

    def test_export_memories(self, tmp_path):
        """测试导出记忆"""
        runner = CliRunner()

        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(datax, ["export", "--memories"])

            assert result.exit_code == 0

    def test_export_to_file(self, tmp_path):
        """测试导出到指定文件"""
        runner = CliRunner()

        with runner.isolated_filesystem(temp_dir=tmp_path):
            output_file = "test_backup.json"
            result = runner.invoke(datax, ["export", "--memories", "-o", output_file])

            assert result.exit_code == 0


class TestDataxImport:
    """测试导入命令"""

    def test_import_no_content(self, tmp_path):
        """测试未指定导入内容"""
        runner = CliRunner()

        with runner.isolated_filesystem(temp_dir=tmp_path):
            backup_file = Path("backup.json")
            backup_file.write_text('{"version": "1.0"}')

            result = runner.invoke(datax, ["import-data", "backup.json"])

            assert result.exit_code == 0
            assert "指定导入内容" in result.output

    def test_import_memories(self, tmp_path):
        """测试导入记忆"""
        runner = CliRunner()

        with runner.isolated_filesystem(temp_dir=tmp_path):
            backup_file = Path("backup.json")
            backup_data = {
                "version": "1.0",
                "memories": [{"content": "test memory", "metadata": {"tags": [], "category": "general"}}],
            }
            backup_file.write_text(json.dumps(backup_data))

            result = runner.invoke(datax, ["import-data", "backup.json", "--memories"])

            assert result.exit_code == 0


class TestDataxBackup:
    """测试备份命令"""

    def test_backup(self, tmp_path):
        """测试快速备份"""
        runner = CliRunner()

        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(datax, ["backup"])

            assert result.exit_code == 0


class TestDataxRestore:
    """测试恢复命令"""

    def test_restore(self, tmp_path):
        """测试恢复备份"""
        runner = CliRunner()

        with runner.isolated_filesystem(temp_dir=tmp_path):
            backup_file = Path("backup.json")
            backup_data = {
                "version": "1.0",
                "memories": [{"content": "test memory", "metadata": {"tags": [], "category": "general"}}],
            }
            backup_file.write_text(json.dumps(backup_data))

            result = runner.invoke(datax, ["restore", "backup.json"])

            assert result.exit_code == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

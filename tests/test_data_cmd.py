"""测试数据分析命令"""

import pytest
import json
from pathlib import Path
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from lobster.commands.data_cmd import data


class TestDataAnalyze:
    """测试数据分析命令"""

    def test_analyze_csv_file(self, tmp_path):
        """测试分析 CSV 文件"""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("name,age,city\nAlice,25,Beijing\nBob,30,Shanghai")
        
        runner = CliRunner()
        
        with patch('lobster.commands.data_cmd.get_llm_client') as mock_llm:
            mock_client = MagicMock()
            mock_client.generate.return_value = "这是一个测试分析结果"
            mock_llm.return_value = mock_client
            
            result = runner.invoke(data, ['analyze', str(csv_file)])
            
            assert result.exit_code == 0

    def test_analyze_json_file(self, tmp_path):
        """测试分析 JSON 文件"""
        json_file = tmp_path / "test.json"
        json_file.write_text('{"name": "test", "value": 123}')
        
        runner = CliRunner()
        
        with patch('lobster.commands.data_cmd.get_llm_client') as mock_llm:
            mock_client = MagicMock()
            mock_client.generate.return_value = "JSON 分析结果"
            mock_llm.return_value = mock_client
            
            result = runner.invoke(data, ['analyze', str(json_file)])
            
            assert result.exit_code == 0

    def test_analyze_with_custom_model(self, tmp_path):
        """测试使用自定义模型分析"""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("a,b,c\n1,2,3")
        
        runner = CliRunner()
        
        with patch('lobster.commands.data_cmd.get_llm_client') as mock_llm:
            mock_client = MagicMock()
            mock_client.generate.return_value = "分析结果"
            mock_llm.return_value = mock_client
            
            result = runner.invoke(data, ['analyze', str(csv_file), '-m', 'ollama/llama3'])
            
            assert result.exit_code == 0
            mock_llm.assert_called_with('ollama/llama3')


class TestDataStats:
    """测试统计信息命令"""

    def test_stats_basic(self, tmp_path):
        """测试基本统计"""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello World\nThis is a test\nPython is great")
        
        runner = CliRunner()
        result = runner.invoke(data, ['stats', str(test_file)])
        
        assert result.exit_code == 0

    def test_stats_with_output(self, tmp_path):
        """测试统计并输出到文件"""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Test content\nMultiple lines")
        
        output_file = tmp_path / "stats_output.txt"
        
        runner = CliRunner()
        result = runner.invoke(data, ['stats', str(test_file), '-o', str(output_file)])
        
        assert result.exit_code == 0
        assert output_file.exists()

    def test_stats_empty_file(self, tmp_path):
        """测试空文件统计"""
        test_file = tmp_path / "empty.txt"
        test_file.write_text("")
        
        runner = CliRunner()
        result = runner.invoke(data, ['stats', str(test_file)])
        
        assert result.exit_code == 0


class TestDataConvert:
    """测试格式转换命令"""

    def test_convert_to_json(self, tmp_path):
        """测试转换为 JSON"""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Line 1\nLine 2\nLine 3")
        
        runner = CliRunner()
        result = runner.invoke(data, ['convert', str(test_file), 'json'])
        
        assert result.exit_code == 0

    def test_convert_to_csv(self, tmp_path):
        """测试转换为 CSV"""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Line 1\nLine 2")
        
        runner = CliRunner()
        result = runner.invoke(data, ['convert', str(test_file), 'csv'])
        
        assert result.exit_code == 0

    def test_convert_to_yaml(self, tmp_path):
        """测试转换为 YAML"""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Item 1\nItem 2")
        
        runner = CliRunner()
        result = runner.invoke(data, ['convert', str(test_file), 'yaml'])
        
        assert result.exit_code == 0

    def test_convert_with_output(self, tmp_path):
        """测试转换并输出到文件"""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Content")
        
        output_file = tmp_path / "output.json"
        
        runner = CliRunner()
        result = runner.invoke(data, ['convert', str(test_file), 'json', '-o', str(output_file)])
        
        assert result.exit_code == 0
        assert output_file.exists()


class TestDataClean:
    """测试数据清洗命令"""

    def test_clean_data(self, tmp_path):
        """测试数据清洗"""
        test_file = tmp_path / "dirty.csv"
        test_file.write_text("name,value\ntest,123\n,456")
        
        runner = CliRunner()
        
        with patch('lobster.commands.data_cmd.get_llm_client') as mock_llm:
            mock_client = MagicMock()
            mock_client.generate.return_value = "清洗建议：去除空值"
            mock_llm.return_value = mock_client
            
            result = runner.invoke(data, ['clean', str(test_file)])
            
            assert result.exit_code == 0


class TestDataSummarize:
    """测试数据摘要命令"""

    def test_summarize_data(self, tmp_path):
        """测试数据摘要"""
        test_file = tmp_path / "report.csv"
        test_file.write_text("product,sales\nA,100\nB,200\nC,150")
        
        runner = CliRunner()
        
        with patch('lobster.commands.data_cmd.get_llm_client') as mock_llm:
            mock_client = MagicMock()
            mock_client.generate.return_value = "数据摘要：总销售额 450"
            mock_llm.return_value = mock_client
            
            result = runner.invoke(data, ['summarize', str(test_file)])
            
            assert result.exit_code == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

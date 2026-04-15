"""测试项目管理命令"""

import pytest
import json
from pathlib import Path
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from lobster.commands.project_cmd import project


class TestProjectInit:
    """测试项目初始化命令"""

    def test_init_default_project(self, tmp_path):
        """测试默认初始化项目"""
        runner = CliRunner()
        
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(project, ['init'])
            
            assert result.exit_code == 0
            assert Path("my-project").exists()
            assert Path("my-project/src").exists()
            assert Path("my-project/tests").exists()
            assert Path("my-project/docs").exists()
            assert Path("my-project/README.md").exists()
            assert Path("my-project/.gitignore").exists()

    def test_init_custom_project(self, tmp_path):
        """测试自定义项目初始化"""
        runner = CliRunner()
        
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(project, ['init', '-n', 'myapp', '-t', 'python'])
            
            assert result.exit_code == 0
            assert Path("myapp").exists()
            assert Path("myapp/README.md").exists()

    def test_init_creates_readme(self, tmp_path):
        """测试创建 README"""
        runner = CliRunner()
        
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(project, ['init', '-n', 'testproj'])
            
            readme = Path("testproj/README.md")
            assert readme.exists()
            content = readme.read_text()
            assert "testproj" in content


class TestProjectAnalyze:
    """测试项目分析命令"""

    def test_analyze_project(self, tmp_path):
        """测试项目分析"""
        runner = CliRunner()
        
        with runner.isolated_filesystem(temp_dir=tmp_path):
            Path("src").mkdir()
            Path("src/main.py").write_text("print('hello')")
            Path("src/utils.py").write_text("def helper(): pass")
            
            with patch('lobster.commands.project_cmd.get_llm_client') as mock_llm:
                mock_client = MagicMock()
                mock_client.generate.return_value = "项目分析结果"
                mock_llm.return_value = mock_client
                
                result = runner.invoke(project, ['analyze'])
                
                assert result.exit_code == 0

    def test_analyze_with_path(self, tmp_path):
        """测试指定路径分析"""
        runner = CliRunner()
        
        with runner.isolated_filesystem(temp_dir=tmp_path):
            test_proj = Path("testproj")
            test_proj.mkdir()
            (test_proj / "app.py").write_text("# app")
            
            with patch('lobster.commands.project_cmd.get_llm_client') as mock_llm:
                mock_client = MagicMock()
                mock_client.generate.return_value = "分析结果"
                mock_llm.return_value = mock_client
                
                result = runner.invoke(project, ['analyze', '-p', 'testproj'])
                
                assert result.exit_code == 0


class TestProjectReport:
    """测试项目报告命令"""

    def test_generate_report(self, tmp_path):
        """测试生成项目报告"""
        runner = CliRunner()
        
        with runner.isolated_filesystem(temp_dir=tmp_path):
            Path("README.md").write_text("# My Project\n\nDescription")
            Path("main.py").write_text("# main code")
            
            with patch('lobster.commands.project_cmd.get_llm_client') as mock_llm:
                mock_client = MagicMock()
                mock_client.generate.return_value = "# 项目报告\n\n## 概述\n\n测试报告"
                mock_llm.return_value = mock_client
                
                result = runner.invoke(project, ['report'])
                
                assert result.exit_code == 0


class TestProjectTodo:
    """测试待办事项命令"""

    def test_list_empty_todos(self, tmp_path):
        """测试空待办列表"""
        runner = CliRunner()
        
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(project, ['todo'])
            
            assert result.exit_code == 0

    def test_add_todo(self, tmp_path):
        """测试添加待办事项"""
        runner = CliRunner()
        
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(project, ['add-todo', '实现新功能', '-r', 'high'])
            
            assert result.exit_code == 0
            
            todo_file = Path(".lobster_todo.json")
            assert todo_file.exists()
            
            todos = json.loads(todo_file.read_text())
            assert len(todos) == 1
            assert todos[0]["content"] == "实现新功能"
            assert todos[0]["priority"] == "high"
            assert todos[0]["done"] is False

    def test_list_todos(self, tmp_path):
        """测试列出待办事项"""
        runner = CliRunner()
        
        with runner.isolated_filesystem(temp_dir=tmp_path):
            runner.invoke(project, ['add-todo', '任务1'])
            runner.invoke(project, ['add-todo', '任务2'])
            
            result = runner.invoke(project, ['todo'])
            
            assert result.exit_code == 0

    def test_complete_todo(self, tmp_path):
        """测试完成待办事项"""
        runner = CliRunner()
        
        with runner.isolated_filesystem(temp_dir=tmp_path):
            runner.invoke(project, ['add-todo', '要完成的任务'])
            
            result = runner.invoke(project, ['done-todo', '1'])
            
            assert result.exit_code == 0
            
            todo_file = Path(".lobster_todo.json")
            todos = json.loads(todo_file.read_text())
            assert todos[0]["done"] is True

    def test_complete_nonexistent_todo(self, tmp_path):
        """测试完成不存在的待办事项"""
        runner = CliRunner()
        
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(project, ['done-todo', '999'])
            
            assert result.exit_code == 0

    def test_todo_with_different_priorities(self, tmp_path):
        """测试不同优先级的待办事项"""
        runner = CliRunner()
        
        with runner.isolated_filesystem(temp_dir=tmp_path):
            runner.invoke(project, ['add-todo', '高优先级', '-r', 'high'])
            runner.invoke(project, ['add-todo', '中优先级', '-r', 'medium'])
            runner.invoke(project, ['add-todo', '低优先级', '-r', 'low'])
            
            todo_file = Path(".lobster_todo.json")
            todos = json.loads(todo_file.read_text())
            
            assert len(todos) == 3
            assert todos[0]["priority"] == "high"
            assert todos[1]["priority"] == "medium"
            assert todos[2]["priority"] == "low"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

"""Tests for system diagnostics"""

import pytest
from unittest.mock import patch, Mock
import sys
import tempfile


def test_doctor_check():
    """Test system check"""
    from lobster.commands.doctor import check
    from click.testing import CliRunner
    
    # Mock successful Ollama response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"models": []}
    
    with patch('requests.get', return_value=mock_response):
        runner = CliRunner()
        result = runner.invoke(check)
        
        assert result.exit_code == 0
        assert "System Check Results" in result.output
        assert "Python" in result.output


def test_doctor_info():
    """Test system information"""
    from lobster.commands.doctor import info
    from click.testing import CliRunner
    
    runner = CliRunner()
    result = runner.invoke(info)
    
    assert result.exit_code == 0
    assert "System Information" in result.output
    assert "OS" in result.output
    assert "Python Version" in result.output


def test_doctor_fix():
    """Test fixing common issues"""
    from lobster.commands.doctor import fix
    from click.testing import CliRunner
    
    with tempfile.TemporaryDirectory() as tmpdir:
        from pathlib import Path
        import lobster.commands.doctor as doctor_module
        
        # Mock home directory
        with patch('pathlib.Path.home', return_value=Path(tmpdir)):
            runner = CliRunner()
            result = runner.invoke(fix)
            
            assert result.exit_code == 0
            assert "Fixed issues" in result.output or "No issues found" in result.output


def test_doctor_deps():
    """Test showing dependencies"""
    from lobster.commands.doctor import deps
    from click.testing import CliRunner
    
    runner = CliRunner()
    result = runner.invoke(deps)
    
    assert result.exit_code == 0
    assert "Installed Packages" in result.output or "Error" in result.output


def test_check_python():
    """Test Python version check"""
    from lobster.commands.doctor import check_python
    
    result = check_python()
    
    assert result['component'] == 'Python'
    assert result['status'] in ['✓', '✗']
    assert 'details' in result


def test_check_dependencies():
    """Test dependencies check"""
    from lobster.commands.doctor import check_dependencies
    
    results = check_dependencies()
    
    assert len(results) > 0
    for result in results:
        assert 'component' in result
        assert 'status' in result
        assert 'details' in result


def test_check_ollama_running():
    """Test Ollama check when running"""
    from lobster.commands.doctor import check_ollama
    
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"models": [{"name": "test"}]}
    
    with patch('requests.get', return_value=mock_response):
        result = check_ollama()
        
        assert result['component'] == 'Ollama'
        assert result['status'] == '✓'


def test_check_ollama_not_running():
    """Test Ollama check when not running"""
    from lobster.commands.doctor import check_ollama
    
    with patch('requests.get', side_effect=Exception("Connection error")):
        result = check_ollama()
        
        assert result['component'] == 'Ollama'
        assert result['status'] == '✗'


def test_check_environment():
    """Test environment variables check"""
    from lobster.commands.doctor import check_environment
    
    result = check_environment()
    
    assert result['component'] == 'API Keys'
    assert result['status'] in ['✓', '⚠']

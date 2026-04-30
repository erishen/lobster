"""Tests for model management commands"""

from unittest.mock import patch, Mock
import requests


def test_model_list_success():
    """Test listing models successfully"""
    from lobster.commands.model import list
    from click.testing import CliRunner

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "models": [
            {
                "name": "gemma3:latest",
                "size": 5000000000,
                "modified_at": "2024-01-01T00:00:00Z",
                "digest": "abc123def456",
            }
        ]
    }

    with patch("requests.get", return_value=mock_response):
        runner = CliRunner()
        result = runner.invoke(list)

        assert result.exit_code == 0
        assert "Installed Ollama Models" in result.output


def test_model_list_no_models():
    """Test listing models when none installed"""
    from lobster.commands.model import list
    from click.testing import CliRunner

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"models": []}

    with patch("requests.get", return_value=mock_response):
        runner = CliRunner()
        result = runner.invoke(list)

        assert result.exit_code == 0
        assert "No models installed" in result.output


def test_model_list_connection_error():
    """Test listing models with connection error"""
    from lobster.commands.model import list
    from click.testing import CliRunner

    with patch("requests.get", side_effect=requests.exceptions.ConnectionError()):
        runner = CliRunner()
        result = runner.invoke(list)

        assert result.exit_code == 0
        assert "Cannot connect to Ollama" in result.output


def test_model_popular():
    """Test showing popular models"""
    from lobster.commands.model import popular
    from click.testing import CliRunner

    runner = CliRunner()
    result = runner.invoke(popular)

    assert result.exit_code == 0
    assert "Popular Ollama Models" in result.output
    assert "gemma3:latest" in result.output
    assert "llama3.1:8b" in result.output


def test_model_info_success():
    """Test getting model info successfully"""
    from lobster.commands.model import info
    from click.testing import CliRunner

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "license": "MIT",
        "modelfile": "FROM gemma3",
        "parameters": "temperature 0.7",
    }

    with patch("requests.post", return_value=mock_response):
        runner = CliRunner()
        result = runner.invoke(info, ["gemma3:latest"])

        assert result.exit_code == 0
        assert "Model Information" in result.output


def test_model_info_not_found():
    """Test getting info for non-existent model"""
    from lobster.commands.model import info
    from click.testing import CliRunner

    mock_response = Mock()
    mock_response.status_code = 404

    with patch("requests.post", return_value=mock_response):
        runner = CliRunner()
        result = runner.invoke(info, ["nonexistent"])

        assert result.exit_code == 0
        assert "Model not found" in result.output or "Error" in result.output


def test_model_ps_no_models():
    """Test showing running models when none running"""
    from lobster.commands.model import ps
    from click.testing import CliRunner

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"models": []}

    with patch("requests.get", return_value=mock_response):
        runner = CliRunner()
        result = runner.invoke(ps)

        assert result.exit_code == 0
        assert "No models currently running" in result.output

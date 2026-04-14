"""Tests for utility commands"""

import pytest
from pathlib import Path
import tempfile
import json


def test_textstat():
    """Test text statistics"""
    from lobster.commands.util import textstat
    from click.testing import CliRunner
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Hello world\nThis is a test\n")
        f.flush()
        
        runner = CliRunner()
        result = runner.invoke(textstat, [f.name])
        
        assert result.exit_code == 0
        assert "Text Statistics" in result.output
        assert "Lines" in result.output
        assert "Words" in result.output


def test_wordcount():
    """Test word count"""
    from lobster.commands.util import wordcount
    from click.testing import CliRunner
    
    runner = CliRunner()
    result = runner.invoke(wordcount, ["Hello world this is a test"])
    
    assert result.exit_code == 0
    assert "Words" in result.output
    assert "Characters" in result.output


def test_jsonfmt_valid():
    """Test JSON formatting with valid JSON"""
    from lobster.commands.util import jsonfmt
    from click.testing import CliRunner
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({"test": "value", "number": 123}, f)
        f.flush()
        
        runner = CliRunner()
        result = runner.invoke(jsonfmt, [f.name])
        
        assert result.exit_code == 0
        assert "Valid JSON" in result.output


def test_jsonfmt_invalid():
    """Test JSON formatting with invalid JSON"""
    from lobster.commands.util import jsonfmt
    from click.testing import CliRunner
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write("{invalid json}")
        f.flush()
        
        runner = CliRunner()
        result = runner.invoke(jsonfmt, [f.name])
        
        assert result.exit_code == 0
        assert "Invalid JSON" in result.output or "Error" in result.output


def test_checksum():
    """Test checksum calculation"""
    from lobster.commands.util import checksum
    from click.testing import CliRunner
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write("test content")
        f.flush()
        
        runner = CliRunner()
        result = runner.invoke(checksum, [f.name])
        
        assert result.exit_code == 0
        assert "MD5" in result.output
        assert "SHA1" in result.output
        assert "SHA256" in result.output


def test_codeinfo():
    """Test code information analysis"""
    from lobster.commands.util import codeinfo
    from click.testing import CliRunner
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("# Comment\nprint('hello')\n\n# Another comment\nx = 1\n")
        f.flush()
        
        runner = CliRunner()
        result = runner.invoke(codeinfo, [f.name])
        
        assert result.exit_code == 0
        assert "Code Analysis" in result.output
        assert "Python" in result.output


def test_findlarge():
    """Test finding large files"""
    from lobster.commands.util import findlarge
    from click.testing import CliRunner
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a test file
        test_file = Path(tmpdir) / "test.txt"
        test_file.write_text("test content")
        
        runner = CliRunner()
        result = runner.invoke(findlarge, [tmpdir])
        
        assert result.exit_code == 0
        assert "Large Files" in result.output or "No files found" in result.output

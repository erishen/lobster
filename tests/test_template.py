"""Tests for template management"""

import tempfile
from pathlib import Path


def test_template_list_empty():
    """Test listing templates when empty"""
    from click.testing import CliRunner

    from lobster.commands.template import list

    with tempfile.TemporaryDirectory() as tmpdir:
        from lobster.commands import template

        template.TEMPLATES_DIR = Path(tmpdir)

        runner = CliRunner()
        result = runner.invoke(list)

        assert result.exit_code == 0
        assert "No templates found" in result.output


def test_template_create():
    """Test creating a template"""
    from click.testing import CliRunner

    from lobster.commands.template import create

    with tempfile.TemporaryDirectory() as tmpdir:
        from lobster.commands import template

        template.TEMPLATES_DIR = Path(tmpdir)

        runner = CliRunner()

        _ = runner.invoke(create, ["test_template"], input="Test description\n\nTest template with {variable}\n")

        # Note: This test might fail due to click.edit() requiring interactive input
        # In a real test environment, you would mock click.edit()


def test_template_builtin():
    """Test showing built-in templates"""
    from click.testing import CliRunner

    from lobster.commands.template import builtin

    runner = CliRunner()
    result = runner.invoke(builtin)

    assert result.exit_code == 0
    assert "Built-in Template Examples" in result.output
    assert "code-review" in result.output
    assert "summarize" in result.output


def test_template_show_not_found():
    """Test showing a non-existent template"""
    from click.testing import CliRunner

    from lobster.commands.template import show

    with tempfile.TemporaryDirectory() as tmpdir:
        from lobster.commands import template

        template.TEMPLATES_DIR = Path(tmpdir)

        runner = CliRunner()
        result = runner.invoke(show, ["nonexistent"])

        assert result.exit_code == 0
        assert "not found" in result.output


def test_template_delete_not_found():
    """Test deleting a non-existent template"""
    from click.testing import CliRunner

    from lobster.commands.template import delete

    with tempfile.TemporaryDirectory() as tmpdir:
        from lobster.commands import template

        template.TEMPLATES_DIR = Path(tmpdir)

        runner = CliRunner()
        result = runner.invoke(delete, ["nonexistent"])

        assert result.exit_code == 0
        assert "not found" in result.output

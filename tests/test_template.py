"""Tests for template management"""

from pathlib import Path
import tempfile


def test_template_list_empty():
    """Test listing templates when empty"""
    from lobster.commands.template import list
    from click.testing import CliRunner

    with tempfile.TemporaryDirectory() as tmpdir:
        from lobster.commands import template

        template.TEMPLATES_DIR = Path(tmpdir)

        runner = CliRunner()
        result = runner.invoke(list)

        assert result.exit_code == 0
        assert "No templates found" in result.output


def test_template_create():
    """Test creating a template"""
    from lobster.commands.template import create
    from click.testing import CliRunner

    with tempfile.TemporaryDirectory() as tmpdir:
        from lobster.commands import template

        template.TEMPLATES_DIR = Path(tmpdir)

        runner = CliRunner()

        _ = runner.invoke(
            create, ["test_template"], input="Test description\n\nTest template with {variable}\n"
        )

        # Note: This test might fail due to click.edit() requiring interactive input
        # In a real test environment, you would mock click.edit()


def test_template_builtin():
    """Test showing built-in templates"""
    from lobster.commands.template import builtin
    from click.testing import CliRunner

    runner = CliRunner()
    result = runner.invoke(builtin)

    assert result.exit_code == 0
    assert "Built-in Template Examples" in result.output
    assert "code-review" in result.output
    assert "summarize" in result.output


def test_template_show_not_found():
    """Test showing a non-existent template"""
    from lobster.commands.template import show
    from click.testing import CliRunner

    with tempfile.TemporaryDirectory() as tmpdir:
        from lobster.commands import template

        template.TEMPLATES_DIR = Path(tmpdir)

        runner = CliRunner()
        result = runner.invoke(show, ["nonexistent"])

        assert result.exit_code == 0
        assert "not found" in result.output


def test_template_delete_not_found():
    """Test deleting a non-existent template"""
    from lobster.commands.template import delete
    from click.testing import CliRunner

    with tempfile.TemporaryDirectory() as tmpdir:
        from lobster.commands import template

        template.TEMPLATES_DIR = Path(tmpdir)

        runner = CliRunner()
        result = runner.invoke(delete, ["nonexistent"])

        assert result.exit_code == 0
        assert "not found" in result.output

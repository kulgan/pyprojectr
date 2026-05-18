import json
import pathlib

from click.testing import CliRunner

from pyprojectr.cli import main


def test_cli_convert_uv_to_pylock(tmp_path: pathlib.Path):
    # Create a uv.lock file
    uv_content = """
version = 1
revision = 1
[[package]]
name = "pkg"
version = "1.0.0"
"""
    input_file = tmp_path / "uv.lock"
    input_file.write_text(uv_content)
    output_file = tmp_path / "pylock.toml"

    runner = CliRunner()
    result = runner.invoke(main, ["convert", str(input_file), str(output_file)])

    assert result.exit_code == 0
    assert "Successfully converted" in result.output
    assert output_file.exists()
    content = output_file.read_text()
    assert 'name = "pkg"' in content
    assert 'version = "1.0.0"' in content


def test_cli_convert_pylock_to_pipfile(tmp_path: pathlib.Path):
    # Create a pylock.toml file
    pylock_content = """
lock-version = "1.0"
created-by = "test"
[[packages]]
name = "pkg"
version = "2.0.0"
"""
    input_file = tmp_path / "pylock.toml"
    input_file.write_text(pylock_content)
    output_file = tmp_path / "pipfile.lock"

    runner = CliRunner()
    result = runner.invoke(main, ["convert", str(input_file), str(output_file)])

    assert result.exit_code == 0
    assert "Successfully converted" in result.output
    assert output_file.exists()
    with output_file.open() as f:
        data = json.load(f)
    assert "_meta" in data
    assert "pkg" in data["default"]
    assert data["default"]["pkg"]["version"] == "==2.0.0"


def test_cli_invalid_input(tmp_path: pathlib.Path):
    runner = CliRunner()
    result = runner.invoke(main, ["convert", "nonexistent.lock", "output.toml"])
    assert result.exit_code != 0
    assert "does not exist" in result.output

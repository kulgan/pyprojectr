import json
import pathlib
from typing import Any

import click

from pyprojectr import PipfileLock, PylockFile, UvLockFile, convert, pipfile_lock, pylock, uv_lock


@click.group()
def main():
    """pyprojectr CLI tool"""
    pass


@main.command("convert")
@click.argument("input", type=click.Path(exists=True, path_type=pathlib.Path))
@click.argument("output", type=click.Path(path_type=pathlib.Path))
@click.option("--from", "from_format", type=click.Choice(["uv", "pipfile", "pylock"]), help="Input format")
@click.option("--to", "to_format", type=click.Choice(["uv", "pipfile", "pylock"]), help="Output format")
def convert_cmd(input: pathlib.Path, output: pathlib.Path, from_format: str | None, to_format: str | None):
    """Convert between lock file formats"""
    # Detect input format
    from_fmt = from_format or detect_format(input)
    if not from_fmt:
        raise click.UsageError(f"Could not detect input format for {input}. Use --from.")

    # Detect output format
    to_fmt = to_format or detect_format(output)
    if not to_fmt:
        raise click.UsageError(f"Could not detect output format for {output}. Use --to.")

    # Load source
    try:
        if from_fmt == "uv":
            source = uv_lock.from_file(input)
        elif from_fmt == "pipfile":
            source = pipfile_lock.from_file(input)
        else:
            source = pylock.from_file(input)
    except Exception as e:
        raise click.ClickException(f"Error loading input file: {e}")

    # Target type
    target_type = {
        "uv": UvLockFile,
        "pipfile": PipfileLock,
        "pylock": PylockFile,
    }[to_fmt]

    # Convert
    try:
        result = convert(source, target_type)
    except Exception as e:
        raise click.ClickException(f"Error during conversion: {e}")

    # Write output
    try:
        data = result.to_data()
        if to_fmt == "pipfile":
            # Pipfile.lock uses _meta
            if "meta" in data:
                data["_meta"] = data.pop("meta")
            with output.open("w") as f:
                json.dump(data, f, indent=4)
        else:
            # TOML doesn't support None values, so we filter them out
            data = filter_none(data)
            write_toml(data, output)
        click.echo(f"Successfully converted {input} to {output}")
    except Exception as e:
        raise click.ClickException(f"Error writing output file: {e}")


def detect_format(path: pathlib.Path) -> str | None:
    name = path.name.lower()
    if name == "uv.lock":
        return "uv"
    if name == "pipfile.lock":
        return "pipfile"
    if name == "pylock.toml" or name.startswith("pylock."):
        return "pylock"
    if path.suffix == ".toml":
        return "pylock"
    if path.suffix == ".lock":
        return "uv"  # Default to uv for .lock
    return None


def filter_none(d: Any) -> Any:
    if isinstance(d, dict):
        return {k: filter_none(v) for k, v in d.items() if v is not None}
    if isinstance(d, list):
        return [filter_none(i) for i in d if i is not None]
    return d


def write_toml(data: dict[str, Any], path: pathlib.Path):
    """Basic TOML writer for the models."""
    try:
        import tomli_w

        with path.open("wb") as f:
            tomli_w.dump(data, f)
    except ImportError:
        click.secho("Warning: 'tomli-w' not found. Using a basic TOML dumper.", fg="yellow", err=True)
        with path.open("w") as f:
            f.write(simple_toml_dumps(data))


def simple_toml_dumps(data: dict[str, Any], indent="") -> str:
    lines = []
    for k, v in data.items():
        if isinstance(v, dict):
            lines.append(f"\n{indent}[{k}]")
            lines.append(simple_toml_dumps(v, indent + "  "))
        elif isinstance(v, list):
            if v and isinstance(v[0], dict):
                for item in v:
                    lines.append(f"\n{indent}[[{k}]]")
                    lines.append(simple_toml_dumps(item, indent + "  "))
            else:
                lines.append(f"{k} = {json.dumps(v)}")
        else:
            lines.append(f"{k} = {json.dumps(v)}")
    return "\n".join(lines)


if __name__ == "__main__":
    main()

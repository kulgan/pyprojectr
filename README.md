# pyprojectr

`pyprojectr` is a Python library and CLI designed to parse, model, and convert Python project metadata and lock files. It provides a type-safe way to interact with `pyproject.toml`, PEP 751 (`pylock.toml`), `uv.lock`, and `Pipfile.lock` files.

## Features

- **Type-Safe Modeling**: Full support for `pyproject.toml`, PEP 751, `uv.lock`, and `Pipfile.lock`.
- **Lock File Conversion**: Convert between different lock file formats using PEP 751 as a standardized pivot.
- **Dependency Scope Preservation**: Maintains the distinction between production and development dependencies during conversion.
- **Flexible Parsing**: Handles both simple and complex field formats automatically.
- **Naming Conventions**: Automatically maps TOML/JSON hyphenated keys (e.g., `requires-python`) to Pythonic underscored attributes (e.g., `requires_python`).
- **CLI Tool**: A powerful command-line interface for easy file conversion.

## Installation

You can install `pyprojectr` using `pip`:

```bash
pip install pyprojectr
```

Or using `uv`:

```bash
uv add pyprojectr
```

## Usage

### CLI: Converting Lock Files

`pyprojectr` provides a CLI to convert between lock file formats. It automatically detects the format based on the file name.

```bash
# Convert uv.lock to PEP 751 format
pyprojectr convert uv.lock pylock.toml

# Convert PEP 751 to Pipfile.lock (Pipenv format)
pyprojectr convert pylock.toml Pipfile.lock

# Explicitly specify formats
pyprojectr convert input.lock output.toml --from uv --to pylock
```

### Library: Loading and Converting

```python
from pathlib import Path
from pyprojectr import uv_lock, PylockFile, PipfileLock, convert

# Load a uv.lock file
uv = uv_lock.from_file(Path("uv.lock"))

# Convert to PEP 751 (Pylock)
pylock = convert(uv, PylockFile)

# Convert to Pipfile.lock
pipfile = convert(uv, PipfileLock)
```

## Pre-commit Hook

You can use `pyprojectr` as a pre-commit hook to ensure your exported lock files (like `pylock.toml`) are always in sync with your primary lock file (like `uv.lock`).

Add this to your `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/kulgan/pyprojectr
    rev: v0.1.3
    hooks:
      - id: uv-to-pipfile
        name: sync uv to pipfile
        entry: pyprojectr convert uv.lock pylock.toml
        files: ^uv\.lock$
        pass_filenames: false
```

## Supported Formats

| Format        | File Name        | Standard                      |
|:--------------|:-----------------|:------------------------------|
| **PEP 751**   | `pylock.toml`    | Standardized Python Lock File |
| **uv**        | `uv.lock`        | uv Package Manager            |
| **Pipenv**    | `Pipfile.lock`   | Pipenv / Pipfile standard     |
| **pyproject** | `pyproject.toml` | PEP 517 / PEP 621             |

## License

This project is licensed under the Apache-2.0 License.

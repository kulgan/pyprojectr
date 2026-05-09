# pyprojectr

`pyprojectr` is a Python library designed to parse and model `pyproject.toml` files. It provides a type-safe way to interact with the metadata of your Python projects.

## Features

- **Type-Safe Modeling**: Full support for the standard `[project]` and `[build-system]` tables.
- **Flexible Parsing**: Handles both simple and complex field formats (e.g., `readme` as a string or a table).
- **Naming Conventions**: Automatically maps TOML hyphenated keys (e.g., `requires-python`) to Pythonic underscored attributes (e.g., `requires_python`).
- **Extensible**: Easily extendable to support additional `[tool]` sections.

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

### Loading a `pyproject.toml` file

```python
from pathlib import Path
from pyprojectr.pyproject import from_file

# Load pyproject.toml from the current directory
pyproj = from_file(Path("pyproject.toml"))

print(f"Project Name: {pyproj.project.name}")
print(f"Version: {pyproj.project.version}")
print(f"Dependencies: {pyproj.project.dependencies}")

# Access tool-specific configuration
if pyproj.tool and pyproj.tool.pytest:
    print(f"Pytest Options: {pyproj.tool.pytest.addopts}")
```

### Creating Models Programmatically

```python
from pyprojectr import PyProject, Author

project = PyProject(
    name="my-awesome-project",
    version="0.1.0",
    authors=[Author(name="Jane Doe", email="jane@example.com")]
)

print(project.name)
```

### Extending with Custom Tools

You can easily define your own data classes for custom tool configurations by inheriting from `BaseModel`. `pyprojectr` will automatically handle the conversion between TOML's hyphenated keys and your Python attributes.

```python
import attrs
from pyprojectr.core import BaseModel

@attrs.define(frozen=True)
class MyCustomTool(BaseModel):
    api_key: str
    max_retries: int = 3
    enable_logging: bool = True

# Example data that might come from a [tool.my-custom-tool] section in pyproject.toml
tool_data = {
    "api-key": "secret-token",
    "max-retries": 5,
    "enable-logging": False
}

# Use from_data to create an instance with automatic key mapping
my_tool = MyCustomTool.from_data(tool_data)

print(my_tool.api_key)        # Output: secret-token

# Use to_data to unstructure the instance back to a dictionary with hyphenated keys
unstructured = my_tool.to_data()
print(unstructured["api-key"]) # Output: secret-token
```

#### Controlling Attribute Renaming

By default, `pyprojectr` converts all underscored attributes to hyphenated keys. You can disable this behavior for specific fields or entire classes:

**Disable for a specific field:**

```python
import attrs
from pyprojectr import BaseModel

@attrs.define(frozen=True)
class MyTool(BaseModel):
    # This will look for 'api_key' instead of 'api-key' in TOML
    api_key: str = attrs.field(metadata={"pyprojectr_no_rename": True})
```

**Disable for an entire class:**

```python
import attrs
from pyprojectr import BaseModel

@attrs.define(frozen=True)
class MyTool(BaseModel):
    __pyprojectr_no_rename__ = True

    # Both will look for underscored names in TOML
    api_key: str
    max_retries: int
```

## Development

`pyprojectr` uses `uv` for dependency management and `tox` for testing across multiple Python versions.

### Setting up for development

1. Clone the repository.
2. Install dependencies:
   ```bash
   uv sync
   ```
3. Run tests:
   ```bash
   tox
   ```

### Quality Assurance

- **Linting**: `ruff` is used for linting and formatting.
- **Testing**: `pytest` is used for unit testing with coverage reporting.

## License

This project is licensed under the Apache-2.0 License.

import pathlib

import pytest


@pytest.fixture
def minimal_pyproject_toml(tmp_path: pathlib.Path) -> pathlib.Path:
    """
    Test from_file with a pyproject.toml that only has [project.name].
    This should fail because build-system is mandatory.
    """
    toml_content = """
[project]
name = "minimal-project"
    """
    pyproject_path = tmp_path / "pyproject.toml"
    pyproject_path.write_text(toml_content)
    return pyproject_path


@pytest.fixture
def complete_pyproject_toml(tmp_path: pathlib.Path) -> pathlib.Path:
    """
    Test from_file with a more complete pyproject.toml file.
    """
    toml_content = """
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"
backend-path = ["."]

[project]
name = "complete-project"
version = "0.1.0"
description = "A complete example project"
readme = "README.md"
requires-python = ">=3.8"
keywords = ["example", "complete"]
classifiers = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
]
authors = [
    {name = "Test Author", email = "test@example.com"},
]
urls = {Homepage = "https://example.com", Repository = "https://github.com/example/complete-project"}
license = {file = "LICENSE"}
dependencies = [
    "requests>=2.28.1",
    "attrs>=21.3.0",
]

[project.optional-dependencies]
dev = ["pytest>=7.0"]
doc = ["sphinx>=4.0"]

[tool.pytest]
minversion = "6.0"
addopts = "--strict-markers"

[dependency-groups]
dev = ["uv>=0.1.0"]
prod = ["fastapi>=0.1.0"]
"""
    pyproject_path = tmp_path / "pyproject.toml"
    pyproject_path.write_text(toml_content)
    return pyproject_path

import attrs
import pytest

from pyprojectr import pyproject


def test_readme_initialization_all_fields():
    """Test Readme initialization with all fields."""
    readme = pyproject.Readme(file="README.md", text="My project readme", content_type="text/markdown")
    assert readme.file == "README.md"
    assert readme.text == "My project readme"
    assert readme.content_type == "text/markdown"


def test_readme_initialization_optional_fields():
    """Test Readme initialization with only optional fields."""
    readme_file = pyproject.Readme(file="README.rst")
    assert readme_file.file == "README.rst"
    assert readme_file.text is None
    assert readme_file.content_type is None

    readme_text = pyproject.Readme(text="Just some text")
    assert readme_text.file is None
    assert readme_text.text == "Just some text"
    assert readme_text.content_type is None

    readme_empty = pyproject.Readme()
    assert readme_empty.file is None
    assert readme_empty.text is None
    assert readme_empty.content_type is None


def test_readme_structure_from_dict():
    """Test that Readme can be structured from a dictionary."""
    data = {"file": "docs/README.md", "content-type": "text/markdown"}
    readme = pyproject.Readme.from_data(data)
    assert readme.file == "docs/README.md"
    assert readme.text is None
    assert readme.content_type == "text/markdown"


def test_readme_frozen():
    """Test that Readme is frozen and attributes cannot be modified."""
    readme = pyproject.Readme(file="README.md")
    with pytest.raises(attrs.exceptions.FrozenInstanceError):
        readme.file = "NEW_README.md"


def test_readme_equality__raw_file() -> None:
    readme = pyproject.Readme(file="README.md")
    assert readme == "README.md"

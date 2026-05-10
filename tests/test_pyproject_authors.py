import pytest

from pyprojectr import pyproject


def test_author_initialization():
    """Test that Author can be initialized with name and email."""
    author = pyproject.Author(name="John Doe", email="john@example.com")
    assert author.name == "John Doe"
    assert author.email == "john@example.com"


def test_author_optional_fields():
    """Test that Author fields are optional."""
    author_name = pyproject.Author(name="Jane Doe")
    assert author_name.name == "Jane Doe"
    assert author_name.email is None


def test_author_structure():
    """Test that Author can be structured from a dictionary."""
    data = {"name": "Alice", "email": "alice@example.com"}
    author = pyproject.Author.converter().structure(data, pyproject.Author)
    assert author.name == "Alice"
    assert author.email == "alice@example.com"


def test_author_empty_parameters() -> None:
    with pytest.raises(ValueError):
        pyproject.Author()


def test_maintainer_structure() -> None:
    """Test that Author can be structured from a dictionary."""
    data = {"name": "Alice", "email": "alice@example.com"}
    maintainer = pyproject.Maintainer.converter().structure(data, pyproject.Author)
    assert maintainer.name == "Alice"
    assert maintainer.email == "alice@example.com"

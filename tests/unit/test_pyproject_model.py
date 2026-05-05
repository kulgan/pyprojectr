from pyprojectr import Author, License, PyProject, Readme


def test_pyproject_initialization():
    """Test PyProject initialization with mandatory and optional fields."""
    project = PyProject(name="my-project", version="1.0.0", description="A test project")
    assert project.name == "my-project"
    assert project.version == "1.0.0"
    assert project.description == "A test project"
    assert project.authors == []
    assert project.dependencies == []


def test_pyproject_complex_fields():
    """Test PyProject with complex fields like authors, readme, and license."""
    authors = [Author(name="John", email="john@example.com")]
    readme = Readme(file="README.md", content_type="text/markdown")
    license_obj = License(text="MIT")

    project = PyProject(
        name="complex", authors=authors, readme=readme, license=license_obj, urls={"homepage": "https://example.com"}
    )

    assert project.authors[0].name == "John"
    assert isinstance(project.readme, Readme)
    assert project.readme.file == "README.md"
    assert project.license.text == "MIT"
    assert project.urls["homepage"] == "https://example.com"


def test_pyproject_structure_minimal():
    """Test structuring PyProject from a minimal dictionary."""
    data = {"name": "minimal"}
    project = PyProject.from_data(data)
    assert project.name == "minimal"


def test_pyproject_structure_full():
    """Test structuring PyProject from a full dictionary (hyphenated keys)."""
    data = {
        "name": "full-project",
        "requires-python": ">=3.10",
        "optional-dependencies": {"test": ["pytest"]},
        "urls": {"repo": "https://github.com/user/repo"},
    }
    project = PyProject.from_data(data)
    assert project.requires_python == ">=3.10"
    assert project.optional_dependencies["test"] == ["pytest"]
    # Check if 'project-urls' in TOML mapped to 'urls' in model
    assert project.urls["repo"] == "https://github.com/user/repo"


def test_pyproject_readme_string():
    """Test that readme can be a simple string (path)."""
    data = {"name": "test", "readme": "README.md"}
    project = PyProject.from_data(data)
    assert project.readme == "README.md"

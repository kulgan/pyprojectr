from pyprojectr import Author, License, PyProject, Readme
from pyprojectr.tools import PyProjectScmTool


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


def test_pyproject_to_data_roundtrip():
    """Test that PyProject can be unstructured back to data with hyphenated keys."""
    data = {
        "name": "full-project",
        "requires-python": ">=3.10",
        "dependencies": ["attrs", "cattrs"],
        "authors": [{"name": "Rowland", "email": "r@example.com"}],
    }
    project = PyProject.from_data(data)
    unstructured_data = project.to_data()

    assert unstructured_data["name"] == "full-project"
    assert unstructured_data["requires-python"] == ">=3.10"
    assert unstructured_data["dependencies"] == ["attrs", "cattrs"]
    assert unstructured_data["authors"][0]["name"] == "Rowland"
    # Ensure no 'requires_python' (underscored) key exists in the output
    assert "requires_python" not in unstructured_data


def test_pyproject_tool_underscore_naming():
    """Test that tool names with underscores are correctly handled."""
    from pyprojectr.pyproject import PyProjectFile

    data = {
        "build-system": {"requires": ["setuptools"], "build-backend": "setuptools.build_meta"},
        "project": {"name": "test-project"},
        "tool": {"setuptools_scm": {"write_to": "version.py"}},
    }

    # This might fail if it expects 'setuptools-scm'
    project_file = PyProjectFile.from_data(data)
    scm_tool = project_file.get_tool_options("setuptools_scm", PyProjectScmTool)
    assert scm_tool is not None
    assert scm_tool.write_to == "version.py"

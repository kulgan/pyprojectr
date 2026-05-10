import pathlib

from pyprojectr import pyproject


def test_from_file_minimal_project_name_only(minimal_pyproject_toml: pathlib.Path) -> None:
    """Test from_file with a pyproject.toml that only has [project.name].

    build-system should default to setuptools
    """

    pyproj = pyproject.from_file(minimal_pyproject_toml)
    assert pyproj.project.name == "minimal-project"
    assert pyproj.build_system.requires == ["setuptools>=80"]
    assert pyproj.build_system.build_backend is None


def test_from_file_complete_pyproject_toml(complete_pyproject_toml: pathlib.Path) -> None:
    """
    Test from_file with a more complete pyproject.toml file.
    """

    pyproject_file = pyproject.from_file(complete_pyproject_toml)

    assert isinstance(pyproject_file, pyproject.PyProjectFile)
    assert pyproject_file.build_system.requires == ["setuptools>=61.0"]
    assert pyproject_file.build_system.build_backend == "setuptools.build_meta"
    assert pyproject_file.build_system.backend_path == ["."]

    assert isinstance(pyproject_file.project, pyproject.PyProject)
    assert pyproject_file.project.name == "complete-project"
    assert pyproject_file.project.version == "0.1.0"
    assert pyproject_file.project.description == "A complete example project"
    assert pyproject_file.project.readme == "README.md"
    assert pyproject_file.project.requires_python == ">=3.8"
    assert pyproject_file.project.keywords == ["example", "complete"]
    assert "Programming Language :: Python :: 3" in pyproject_file.project.classifiers

    assert len(pyproject_file.project.authors) == 1
    assert isinstance(pyproject_file.project.authors[0], pyproject.Author)
    assert pyproject_file.project.authors[0].name == "Test Author"
    assert pyproject_file.project.authors[0].email == "test@example.com"

    assert pyproject_file.project.urls["Homepage"] == "https://example.com"

    assert isinstance(pyproject_file.project.license, pyproject.License)
    assert pyproject_file.project.license.file == "LICENSE"

    assert "requests>=2.28.1" in pyproject_file.project.dependencies
    assert "attrs>=21.3.0" in pyproject_file.project.dependencies
    assert pyproject_file.project.optional_dependencies["dev"] == ["pytest>=7.0"]
    assert pyproject_file.project.optional_dependencies["doc"] == ["sphinx>=4.0"]

    assert pyproject_file.dependency_groups["dev"] == ["uv>=0.1.0"]
    assert pyproject_file.dependency_groups["prod"] == ["fastapi>=0.1.0"]

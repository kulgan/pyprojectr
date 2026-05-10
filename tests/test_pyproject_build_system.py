import attrs
import pytest

from pyprojectr import pyproject


def test_build_system_initialization() -> None:
    """Test that BuildSystem can be initialized with correct attributes."""
    build_system = pyproject.BuildSystem(
        build_backend="setuptools.build_meta", requires=["setuptools>=80", "setuptools-scm[toml]"], backend_path=["."]
    )
    assert build_system.build_backend == "setuptools.build_meta"
    assert build_system.requires == ["setuptools>=80", "setuptools-scm[toml]"]
    assert build_system.backend_path == ["."]


@pytest.mark.parametrize(
    "payload, requires, build_backend, backend_path",
    [
        (
            {"requires": ["setuptools>=80"], "build-backend": "setuptools.build_meta"},
            ["setuptools>=80"],
            "setuptools.build_meta",
            None,
        ),
        ({"requires": ["setuptools"]}, ["setuptools"], None, None),
        (
            {
                "requires": ["flit_core >=3.2,<4"],
                "build-backend": "flit_core.buildapi",
                "backend-path": ["build-backend"],
            },
            ["flit_core >=3.2,<4"],
            "flit_core.buildapi",
            ["build-backend"],
        ),
    ],
)
def test_build_system_structure(
    payload: dict, requires: list[str], build_backend: str | None, backend_path: list[str] | None
) -> None:
    """Test that BuildSystem can be structured from a dictionary using its converter."""
    # Using the converter from the model class
    build_system = pyproject.BuildSystem.converter().structure(payload, pyproject.BuildSystem)

    assert build_system.build_backend == build_backend
    assert build_system.requires == requires
    assert build_system.backend_path == backend_path


def test_build_system_frozen():
    """Test that BuildSystem is frozen and attributes cannot be modified."""
    build_system = pyproject.BuildSystem(build_backend="setuptools.build_meta", requires=["setuptools"])
    with pytest.raises(attrs.exceptions.FrozenInstanceError):
        build_system.build_backend = "something.else"


def test_build_system_missing_required_fields():
    """Test that initialization fails if required fields are missing."""
    with pytest.raises(TypeError):
        # Missing requires
        pyproject.BuildSystem(build_backend="setuptools.build_meta")  # type: ignore

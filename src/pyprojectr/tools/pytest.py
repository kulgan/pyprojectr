import attrs

from pyprojectr.core import PyProjectTool


@attrs.define(frozen=True)
class PytestTool(PyProjectTool):
    """Model for [tool.pytest.ini_options] in pyproject.toml."""

    minversion: str | None = None
    addopts: str | None = None
    testpaths: list[str] = attrs.Factory(list)
    python_files: list[str] = attrs.Factory(list)
    python_classes: list[str] = attrs.Factory(list)
    python_functions: list[str] = attrs.Factory(list)
    markers: list[str] = attrs.Factory(list)
    norecursedirs: list[str] = attrs.Factory(list)

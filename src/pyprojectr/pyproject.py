import pathlib
from collections.abc import Mapping
from typing import Any, TypeVar

import attrs
import tomli

from pyprojectr import core
from pyprojectr.core import PyProjectTool

Tool = TypeVar("Tool", bound=PyProjectTool)


@attrs.define(frozen=True)
class BuildSystem(core.BaseModel):
    requires: list[str]
    build_backend: str | None = None
    backend_path: list[str] | None = None


@attrs.define(frozen=True)
class Author(core.BaseModel):
    name: str | None = None
    email: str | None = None

    def __attrs_post_init__(self) -> None:
        if not self.name and not self.email:
            raise ValueError("Author must have a name or email")


@attrs.define(frozen=True)
class Maintainer(Author): ...


@attrs.define(frozen=True, eq=False)
class Readme(core.BaseModel):
    file: str | None = None
    text: str | None = None
    content_type: str | None = None

    def __eq__(self, other) -> bool:
        if isinstance(other, str):
            return self.file == other
        if isinstance(other, Readme):
            return self.file == other.file
        return False


@attrs.define(frozen=True)
class License(core.BaseModel):
    file: str | None = None
    text: str | None = None


@attrs.define(frozen=True)
class PyProject(core.BaseModel):
    name: str
    version: str | None = None
    description: str | None = None
    readme: Readme | None = None
    requires_python: str | None = None
    license: License | None = None
    authors: list[Author] = attrs.Factory(list)
    maintainers: list[Maintainer] = attrs.Factory(list)
    keywords: list[str] = attrs.Factory(list)
    classifiers: list[str] = attrs.Factory(list)
    urls: dict[str, str] = attrs.Factory(dict)
    dependencies: list[str] = attrs.Factory(list)
    optional_dependencies: dict[str, list[str]] = attrs.Factory(dict)
    dynamic: list[str] = attrs.Factory(list)


class PyProjectToolMapping(Mapping[str, Any]):
    def __init__(self, tools_data: dict[str, Any]) -> None:
        self.tools_data = tools_data

    def __iter__(self): ...
    def __len__(self): ...
    def __setitem__(self, key, value, /): ...

    def __getitem__(self, name: str) -> Any:
        return self.tools_data[name]

    def __getattr__(self, name: str) -> Any:
        return self.tools_data[name]


@attrs.define(frozen=True)
class PyProjectFile(core.BaseModel):
    build_system: BuildSystem
    project: PyProject
    tool: dict[str, Any] | None = None
    dependency_groups: dict[str, Any] = attrs.Factory(dict)

    @property
    def tools(self) -> PyProjectToolMapping | None:
        if self.tool:
            return PyProjectToolMapping(self.tool)
        return None

    def get_tool_options(self, name: str, tool_class: type[Tool]) -> Tool | None:
        if self.tool and name in self.tool:
            return tool_class.from_data(self.tool[name])
        return None


@core.STRUCT_CONVERTER.register_structure_hook
def register_readme_hook(value: dict[str, Any] | str, _) -> Readme:
    if isinstance(value, str):
        value = dict(file=value)
    return core.convert_underscores(Readme)(value, Readme)


def from_file(path: pathlib.Path) -> PyProjectFile:
    with path.open("rb") as f:
        toml = tomli.load(f)
        return PyProjectFile.from_data(toml)

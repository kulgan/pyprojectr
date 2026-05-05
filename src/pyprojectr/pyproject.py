import pathlib
from typing import Any

import attrs
import tomli

from pyprojectr import core
from pyprojectr.tools import PytestTool


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
        print(other, type(other), self)
        if isinstance(other, str):
            return self.file == other
        return self.file == other.file


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


@attrs.define(frozen=True)
class PyProjectScmTool(core.BaseModel):
    version_scheme: str | None = None
    local_scheme: str | None = None
    write_to: str | None = None
    write_to_template: str | None = None
    relative_to: str | None = None
    tag_regex: str | None = None
    parentdir_prefix: str | None = None
    fallback_version: str | None = None
    parse: Any | None = None
    git_describe_command: str | None = None


@attrs.define(frozen=True)
class PyProjectScmxTool(core.BaseModel):
    ci_version_variable: str
    ci_main_branch_name: str


@attrs.define(frozen=True)
class PyProjectTool(core.BaseModel):
    setuptools_scm: PyProjectScmTool | None = None
    setuptools_scmx: PyProjectScmxTool | None = None
    pytest: PytestTool | None = None


@attrs.define(frozen=True)
class PyProjectFile(core.BaseModel):
    build_system: BuildSystem
    project: PyProject
    tool: PyProjectTool | None = None
    dependency_groups: dict[str, list[str | dict[str, Any]]] = attrs.Factory(dict)

    @property
    def tools(self) -> PyProjectTool | None:
        return self.tool

    def get_tool_options(self, name: str) -> Any:
        if self.tool and hasattr(self.tool, name):
            return getattr(self.tool, name)
        return None


@core.STRUCT_CONVERTER.register_structure_hook
def register_readme_hook(value: dict[str, Any] | str, _) -> Readme:
    if isinstance(value, str):
        value = dict(file=value)
    return core.convert_underscores(Readme)(value, Readme)


def from_file(path: pathlib.Path) -> PyProjectFile:
    with path.open() as f:
        toml = tomli.loads(f.read())
        return core.BaseModel.converter().structure(toml, PyProjectFile)

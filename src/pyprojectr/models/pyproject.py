import pathlib
from typing import Any

import attrs
import tomli

from pyprojectr.models.core import BaseModel


@attrs.define(frozen=True)
class BuildSystem(BaseModel):
    requires: list[str]
    build_backend: str | None = None
    backend_path: list[str] | None = None


@attrs.define(frozen=True)
class Author(BaseModel):
    name: str | None = None
    email: str | None = None

    def __attrs_post_init__(self) -> None:
        if not self.name and not self.email:
            raise ValueError("Author must have a name or email")


@attrs.define(frozen=True)
class Maintainer(Author): ...


@attrs.define
class PyProject(BaseModel):
    name: str
    version: str | None = None
    description: str | None = None
    authors: list[Author] = attrs.Factory(list)
    maintainers: list[Maintainer] = attrs.Factory(list)
    readme: Any = None
    requires_python: str | None = None
    dependencies: list[str] = attrs.Factory(list)
    optional_dependencies: dict[str, list[str]] = attrs.Factory(dict)
    dynamic: list[str] = attrs.Factory(list)
    classifiers: list[str] = attrs.Factory(list)
    license: Any | None = None


@attrs.define(frozen=True)
class PyProjectScmTool(BaseModel):
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
class PyProjectScmxTool(BaseModel):
    ci_version_variable: str
    ci_main_branch_name: str


@attrs.define(frozen=True)
class PyProjectTool(BaseModel):
    setuptools_scm: PyProjectScmTool | None = None
    setuptools_scmx: PyProjectScmxTool | None = None


@attrs.define(frozen=True)
class PyProjectFile(BaseModel):
    build_system: BuildSystem
    project: PyProject
    tool: PyProjectTool | None

    @property
    def tools(self):
        return self.tool

    def get_tool_options(self, name: str) -> Any:
        if hasattr(self.tool, name):
            return getattr(self.tool, name)
        return None

    @classmethod
    def from_file(cls, path: pathlib.Path) -> "PyProjectFile":
        with path.open() as f:
            toml = tomli.loads(f.read())
            return cls.converter().structure(toml, PyProjectFile)

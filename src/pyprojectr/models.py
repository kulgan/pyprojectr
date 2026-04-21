import pathlib
from typing import Any

import attrs
import cattrs
import tomli
from cattrs.gen import make_dict_structure_fn

STRUCT_CONVERTER = cattrs.Converter()


def convert_underscores(cls):
    return make_dict_structure_fn(
        cls,
        STRUCT_CONVERTER,
        **{a.name: cattrs.override(rename=_underscores_to_hyphen(a.name)) for a in attrs.fields(cls)
           })


def _underscores_to_hyphen(text: str, reverse: bool = False) -> str:
    if not reverse:
        return text.replace("_", "-")
    return text.replace("-", "_")

STRUCT_CONVERTER.register_structure_hook_factory(attrs.has, convert_underscores)

@attrs.define
class BaseModel:

    @classmethod
    def converter(cls) -> cattrs.Converter:
        return STRUCT_CONVERTER

@attrs.define
class Author(BaseModel):
    name: str | None = None
    email: str | None = None


@attrs.define
class BuildSystem(BaseModel):
    build_backend: str
    requires: list[str]


@attrs.define
class PyProject(BaseModel):
    name: str
    version: str | None = None
    description: str | None = None
    authors: list[Author] = attrs.Factory(list)
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

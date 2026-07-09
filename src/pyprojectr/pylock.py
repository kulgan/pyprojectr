import pathlib
import tomllib
from typing import Any

import attrs

from pyprojectr import core


@attrs.define(frozen=True)
class VCSSource(core.BaseModel):
    type: str
    url: str | None = None
    path: str | None = None
    commit_id: str | None = None
    subdirectory: str | None = None


@attrs.define(frozen=True)
class DirectorySource(core.BaseModel):
    path: str
    editable: bool = False
    subdirectory: str | None = None


@attrs.define(frozen=True)
class ArchiveSource(core.BaseModel):
    url: str | None = None
    path: str | None = None
    hashes: dict[str, str] = attrs.Factory(dict)
    size: int | None = None


@attrs.define(frozen=True)
class SdistSource(core.BaseModel):
    name: str | None = None
    url: str | None = None
    path: str | None = None
    hashes: dict[str, str] = attrs.Factory(dict)


@attrs.define(frozen=True)
class WheelSource(core.BaseModel):
    name: str | None = None
    url: str | None = None
    path: str | None = None
    hashes: dict[str, str] = attrs.Factory(dict)


@attrs.define(frozen=True)
class PackageDependency(core.BaseModel):
    name: str
    version: str | None = None


@attrs.define(frozen=True)
class Package(core.BaseModel):
    name: str
    version: str | None = None
    marker: str | None = None
    requires_python: str | None = None
    dependencies: list[PackageDependency] = attrs.Factory(list)
    vcs: VCSSource | None = None
    directory: DirectorySource | None = None
    archive: ArchiveSource | None = None
    sdist: SdistSource | None = None
    wheels: list[WheelSource] = attrs.Factory(list)
    tool: dict[str, Any] | None = None


@attrs.define(frozen=True)
class PylockFile(core.BaseModel):
    lock_version: str
    created_by: str
    requires_python: str | None = None
    environments: list[str] = attrs.Factory(list)
    extras: list[str] = attrs.Factory(list)
    dependency_groups: list[str] = attrs.Factory(list)
    default_groups: list[str] = attrs.Factory(list)
    packages: list[Package] = attrs.Factory(list)
    tool: dict[str, Any] | None = None


def from_file(path: pathlib.Path) -> PylockFile:
    with path.open("rb") as f:
        toml = tomllib.load(f)
        return PylockFile.from_data(toml)

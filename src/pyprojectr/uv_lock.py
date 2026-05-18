import pathlib
import tomllib
from typing import Any

import attrs

from pyprojectr import core


@attrs.define(frozen=True)
class UvLockSource(core.BaseModel):
    registry: str | None = None
    git: str | None = None
    rev: str | None = None
    path: str | None = None
    editable: bool | None = None


@attrs.define(frozen=True)
class UvLockSdist(core.BaseModel):
    url: str
    hash: str
    size: int | None = None
    upload_time: str | None = None


@attrs.define(frozen=True)
class UvLockWheel(core.BaseModel):
    url: str
    hash: str
    size: int | None = None
    upload_time: str | None = None


@attrs.define(frozen=True)
class UvLockPackageDependency(core.BaseModel):
    name: str
    extra: str | None = None


@attrs.define(frozen=True)
class UvLockPackage(core.BaseModel):
    name: str
    version: str | None = None
    source: UvLockSource | None = None
    dependencies: list[UvLockPackageDependency] = attrs.Factory(list)
    optional_dependencies: dict[str, list[UvLockPackageDependency]] = attrs.Factory(dict)
    dev_dependencies: dict[str, list[UvLockPackageDependency]] = attrs.Factory(dict)
    sdist: UvLockSdist | None = None
    wheels: list[UvLockWheel] = attrs.Factory(list)


@attrs.define(frozen=True)
class UvLockFile(core.BaseModel):
    version: int
    revision: int
    requires_python: str | None = None
    package: list[UvLockPackage] = attrs.Factory(list)
    resolver_options: dict[str, Any] = attrs.Factory(dict)
    manifest: dict[str, Any] = attrs.Factory(dict)


def from_file(path: pathlib.Path) -> UvLockFile:
    with path.open("rb") as f:
        toml = tomllib.load(f)
        return UvLockFile.from_data(toml)

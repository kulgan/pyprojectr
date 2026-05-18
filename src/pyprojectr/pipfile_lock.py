import json
import pathlib
from typing import Any

import attrs

from pyprojectr import core


@attrs.define(frozen=True)
class PipfileSource(core.BaseModel):
    name: str
    url: str
    verify_ssl: bool = attrs.field(metadata={"pyprojectr_no_rename": True})


@attrs.define(frozen=True)
class PipfileMeta(core.BaseModel):
    hash: dict[str, str]
    pipfile_spec: int
    requires: dict[str, str] = attrs.Factory(dict)
    sources: list[PipfileSource] = attrs.Factory(list)


@attrs.define(frozen=True)
class PipfilePackage(core.BaseModel):
    version: str
    hashes: list[str] = attrs.Factory(list)
    index: str | None = None
    markers: str | None = None
    editable: bool | None = None
    path: str | None = None
    git: str | None = None
    ref: str | None = None


@attrs.define(frozen=True)
class PipfileLock(core.BaseModel):
    meta: PipfileMeta = attrs.field(metadata={"pyprojectr_no_rename": True})
    default: dict[str, PipfilePackage] = attrs.Factory(dict)
    develop: dict[str, PipfilePackage] = attrs.Factory(dict)

    @classmethod
    def from_data(cls, data: dict[str, Any]) -> "PipfileLock":
        # Pipfile.lock uses "_meta" but we want to map it to "meta"
        # and it contains "pipfile-spec" which core.convert_underscores handles.
        if "_meta" in data:
            data["meta"] = data.pop("_meta")
        return super().from_data(data)


def from_file(path: pathlib.Path) -> PipfileLock:
    with path.open("r") as f:
        data = json.load(f)
        return PipfileLock.from_data(data)

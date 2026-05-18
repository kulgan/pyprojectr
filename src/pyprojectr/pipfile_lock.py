import json
import pathlib
from typing import Any

import attrs

from pyprojectr import core, pylock


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

    def to_pylock(self) -> pylock.PylockFile:
        packages = []

        def process_packages(pkg_dict: dict[str, PipfilePackage]):
            for name, pkg in pkg_dict.items():
                vcs = None
                directory = None
                wheels = []

                if pkg.git:
                    vcs = pylock.VCSSource(type="git", url=pkg.git, commit_id=pkg.ref)
                elif pkg.path:
                    directory = pylock.DirectorySource(path=pkg.path, editable=pkg.editable or False)
                else:
                    # Assume it's from a registry if no git/path
                    # Pipfile.lock often just has version and hashes
                    # We'll treat it as a wheel source if there are hashes
                    for h in pkg.hashes:
                        algo, val = h.split(":", 1)
                        wheels.append(pylock.WheelSource(hashes={algo: val}))

                packages.append(
                    pylock.Package(
                        name=name,
                        version=pkg.version.lstrip("="),
                        marker=pkg.markers,
                        vcs=vcs,
                        directory=directory,
                        wheels=wheels,
                    )
                )

        process_packages(self.default)
        process_packages(self.develop)

        return pylock.PylockFile(
            lock_version="1.0",
            created_by="pyprojectr (from Pipfile.lock)",
            requires_python=self.meta.requires.get("python_version"),
            packages=packages,
        )


def from_file(path: pathlib.Path) -> PipfileLock:
    with path.open("r") as f:
        data = json.load(f)
        return PipfileLock.from_data(data)

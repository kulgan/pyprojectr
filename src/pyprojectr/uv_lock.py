import pathlib
import tomllib
from typing import Any

import attrs

from pyprojectr import core, pylock


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

    def to_pylock(self) -> pylock.PylockFile:
        # 1. Identify production and dev dependencies
        production_names = set()
        dev_names = set()

        # Map name to package for easy lookup
        pkg_map = {p.name: p for p in self.package}

        def trace(name: str, visited: set[str]):
            if name in visited or name not in pkg_map:
                return
            visited.add(name)
            p = pkg_map[name]
            for dep in p.dependencies:
                trace(dep.name, visited)

        # Root packages are those with editable source or no source (workspace members)
        roots = [p for p in self.package if p.source and (p.source.editable or p.source.path == ".")]
        if not roots:
            # Fallback: everything is production if no roots found
            production_names = set(pkg_map.keys())
        else:
            for root in roots:
                # Production trace
                for dep in root.dependencies:
                    trace(dep.name, production_names)
                # Dev trace
                for group, deps in root.dev_dependencies.items():
                    for dep in deps:
                        trace(dep.name, dev_names)

        # Packages that are ONLY in dev_names (and not in production_names) are marked as dev
        dev_only = dev_names - production_names

        packages = []
        for pkg in self.package:
            # Skip roots themselves in the final package list if they are just the project
            if pkg in roots:
                continue

            # Map source
            vcs = None
            directory = None
            archive = None
            sdist = None
            wheels = []

            if pkg.source:
                if pkg.source.git:
                    vcs = pylock.VCSSource(type="git", url=pkg.source.git, commit_id=pkg.source.rev)
                elif pkg.source.path:
                    directory = pylock.DirectorySource(path=pkg.source.path, editable=pkg.source.editable or False)

            if pkg.sdist:
                sdist = pylock.SdistSource(
                    url=pkg.sdist.url, hashes={"sha256": pkg.sdist.hash.split(":")[-1]} if pkg.sdist.hash else {}
                )

            for whl in pkg.wheels:
                wheels.append(
                    pylock.WheelSource(url=whl.url, hashes={"sha256": whl.hash.split(":")[-1]} if whl.hash else {})
                )

            marker = None
            if pkg.name in dev_only:
                marker = "'dev' in dependency_groups"

            packages.append(
                pylock.Package(
                    name=pkg.name,
                    version=pkg.version,
                    dependencies=[pylock.PackageDependency(name=d.name) for d in pkg.dependencies],
                    vcs=vcs,
                    directory=directory,
                    archive=archive,
                    sdist=sdist,
                    wheels=wheels,
                    marker=marker,
                )
            )

        return pylock.PylockFile(
            lock_version="1.0",
            created_by="pyprojectr (from uv.lock)",
            requires_python=self.requires_python,
            packages=packages,
            dependency_groups=["dev"] if dev_names else [],
        )


def from_file(path: pathlib.Path) -> UvLockFile:
    with path.open("rb") as f:
        toml = tomllib.load(f)
        return UvLockFile.from_data(toml)

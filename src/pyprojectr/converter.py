from typing import Any, TypeVar

from pyprojectr import pipfile_lock, pylock, uv_lock

T = TypeVar("T")


def convert(source: Any, target_type: type[T]) -> T:
    """
    Convert a lock file from one format to another.
    Uses PylockFile (PEP 751) as the pivot format.
    """
    if isinstance(source, target_type):
        return source

    # Phase 1: Convert source to PylockFile
    if isinstance(source, pylock.PylockFile):
        pivot = source
    elif hasattr(source, "to_pylock"):
        pivot = source.to_pylock()
    else:
        raise TypeError(f"Cannot convert from {type(source)}")

    # Phase 2: Convert pivot (PylockFile) to target_type
    if target_type is pylock.PylockFile:
        return pivot  # type: ignore

    if target_type is uv_lock.UvLockFile:
        return _pylock_to_uv(pivot)  # type: ignore

    if target_type is pipfile_lock.PipfileLock:
        return _pylock_to_pipfile(pivot)  # type: ignore

    raise TypeError(f"Cannot convert to {target_type}")


def _pylock_to_uv(pivot: pylock.PylockFile) -> uv_lock.UvLockFile:
    packages = []
    for pkg in pivot.packages:
        source = None
        if pkg.vcs and pkg.vcs.type == "git":
            source = uv_lock.UvLockSource(git=pkg.vcs.url, rev=pkg.vcs.commit_id)
        elif pkg.directory:
            source = uv_lock.UvLockSource(path=pkg.directory.path, editable=pkg.directory.editable)
        else:
            source = uv_lock.UvLockSource(registry="https://pypi.org/simple")

        sdist = None
        if pkg.sdist:
            # UvLockSdist requires url and hash
            hash_val = ""
            if pkg.sdist.hashes:
                algo = next(iter(pkg.sdist.hashes.keys()))
                hash_val = f"{algo}:{pkg.sdist.hashes[algo]}"
            sdist = uv_lock.UvLockSdist(url=pkg.sdist.url or "", hash=hash_val)

        wheels = []
        for whl in pkg.wheels:
            hash_val = ""
            if whl.hashes:
                algo = next(iter(whl.hashes.keys()))
                hash_val = f"{algo}:{whl.hashes[algo]}"
            wheels.append(uv_lock.UvLockWheel(url=whl.url or "", hash=hash_val))

        packages.append(
            uv_lock.UvLockPackage(
                name=pkg.name,
                version=pkg.version,
                source=source,
                dependencies=[uv_lock.UvLockPackageDependency(name=d.name) for d in pkg.dependencies],
                sdist=sdist,
                wheels=wheels,
            )
        )

    return uv_lock.UvLockFile(
        version=1,
        revision=1,
        requires_python=pivot.requires_python,
        package=packages,
    )


def _pylock_to_pipfile(pivot: pylock.PylockFile) -> pipfile_lock.PipfileLock:
    default_pkgs = {}
    for pkg in pivot.packages:
        hashes = []
        # Combine sdist and wheel hashes
        if pkg.sdist and pkg.sdist.hashes:
            for algo, val in pkg.sdist.hashes.items():
                hashes.append(f"{algo}:{val}")
        for whl in pkg.wheels:
            if whl.hashes:
                for algo, val in whl.hashes.items():
                    hashes.append(f"{algo}:{val}")

        pip_pkg = pipfile_lock.PipfilePackage(
            version=f"=={pkg.version}" if pkg.version else "",
            hashes=hashes,
            markers=pkg.marker,
            git=pkg.vcs.url if pkg.vcs and pkg.vcs.type == "git" else None,
            ref=pkg.vcs.commit_id if pkg.vcs and pkg.vcs.type == "git" else None,
            path=pkg.directory.path if pkg.directory else None,
            editable=pkg.directory.editable if pkg.directory else None,
        )
        default_pkgs[pkg.name] = pip_pkg

    meta = pipfile_lock.PipfileMeta(
        hash={"sha256": ""},
        pipfile_spec=6,
        requires={"python_version": pivot.requires_python} if pivot.requires_python else {},
        sources=[pipfile_lock.PipfileSource(name="pypi", url="https://pypi.org/simple", verify_ssl=True)],
    )

    return pipfile_lock.PipfileLock(meta=meta, default=default_pkgs)

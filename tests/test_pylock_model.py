from pyprojectr.pylock import PylockFile


def test_pylock_basic_parsing():
    data = {
        "lock-version": "1.0",
        "created-by": "uv v0.1.0",
        "requires-python": ">=3.11",
        "packages": [
            {
                "name": "requests",
                "version": "2.31.0",
                "marker": "python_version >= '3.7'",
                "dependencies": [{"name": "urllib3", "version": ">=1.21.1"}],
                "wheels": [
                    {
                        "url": "https://example.com/requests-2.31.0-py3-none-any.whl",
                        "hashes": {"sha256": "62803525e169fd4ebef7de172747f9735bc83f89d352c9f455635f3f78b8ed07"},
                        "size": 62224,
                    }
                ],
            }
        ],
    }

    pylock = PylockFile.from_data(data)
    assert pylock.lock_version == "1.0"
    assert pylock.created_by == "uv v0.1.0"
    assert len(pylock.packages) == 1
    pkg = pylock.packages[0]
    assert pkg.name == "requests"
    assert pkg.version == "2.31.0"
    assert len(pkg.wheels) == 1
    assert pkg.wheels[0].hashes["sha256"] == "62803525e169fd4ebef7de172747f9735bc83f89d352c9f455635f3f78b8ed07"


def test_pylock_vcs_source():
    data = {
        "lock-version": "1.0",
        "created-by": "test-tool",
        "packages": [
            {
                "name": "my-pkg",
                "vcs": {"type": "git", "url": "https://github.com/user/repo", "commit-id": "abcdef123456"},
            }
        ],
    }
    pylock = PylockFile.from_data(data)
    pkg = pylock.packages[0]
    assert pkg.vcs and pkg.vcs.type == "git"
    assert pkg.vcs.commit_id == "abcdef123456"


def test_pylock_directory_source():
    data = {
        "lock-version": "1.0",
        "created-by": "test-tool",
        "packages": [{"name": "local-pkg", "directory": {"path": "./local-pkg", "editable": True}}],
    }
    pylock = PylockFile.from_data(data)
    pkg = pylock.packages[0]
    assert pkg.directory and pkg.directory.path == "./local-pkg"
    assert pkg.directory.editable is True


def test_pylock_archive_source():
    data = {
        "lock-version": "1.0",
        "created-by": "test-tool",
        "packages": [
            {
                "name": "archive-pkg",
                "archive": {"url": "https://example.com/pkg.zip", "hashes": {"sha256": "hash-value"}, "size": 1024},
            }
        ],
    }
    pylock = PylockFile.from_data(data)
    pkg = pylock.packages[0]
    assert pkg.archive and pkg.archive.url == "https://example.com/pkg.zip"
    assert pkg.archive.size == 1024


def test_pylock_roundtrip():
    data = {
        "lock-version": "1.0",
        "created-by": "test-tool",
        "environments": ["python_version >= '3.10'"],
        "packages": [
            {
                "name": "pkg",
                "version": "1.0.0",
                "sdist": {"url": "https://example.com/pkg-1.0.0.tar.gz", "hashes": {"sha256": "sdist-hash"}},
            }
        ],
    }
    pylock = PylockFile.from_data(data)
    unstructured = pylock.to_data()
    assert unstructured["lock-version"] == "1.0"
    assert unstructured["created-by"] == "test-tool"
    assert unstructured["packages"][0]["sdist"]["url"] == "https://example.com/pkg-1.0.0.tar.gz"

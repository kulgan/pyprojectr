from pyprojectr import PipfileLock, PylockFile, UvLockFile, convert


def test_convert_uv_to_pylock():
    data = {
        "version": 1,
        "revision": 3,
        "requires-python": ">=3.11",
        "package": [
            {
                "name": "attrs",
                "version": "26.1.0",
                "source": {"registry": "https://pypi.org/simple"},
                "sdist": {"url": "https://example.com/attrs.tar.gz", "hash": "sha256:hash1"},
            }
        ],
    }
    uv = UvLockFile.from_data(data)
    py_lock = convert(uv, PylockFile)

    assert isinstance(py_lock, PylockFile)
    assert py_lock.requires_python == ">=3.11"
    assert len(py_lock.packages) == 1
    assert py_lock.packages[0].name == "attrs"
    assert py_lock.packages[0].sdist.hashes["sha256"] == "hash1"


def test_convert_pipfile_to_pylock():
    data = {
        "_meta": {"hash": {"sha256": "h"}, "pipfile-spec": 6, "requires": {"python_version": "3.11"}, "sources": []},
        "default": {"requests": {"version": "==2.31.0", "hashes": ["sha256:hash1"]}},
        "develop": {},
    }
    pip = PipfileLock.from_data(data)
    py_lock = convert(pip, PylockFile)

    assert isinstance(py_lock, PylockFile)
    assert len(py_lock.packages) == 1
    assert py_lock.packages[0].name == "requests"
    assert py_lock.packages[0].version == "2.31.0"
    assert py_lock.packages[0].wheels[0].hashes["sha256"] == "hash1"


def test_convert_uv_to_pipfile_via_pivot():
    data = {
        "version": 1,
        "revision": 1,
        "package": [{"name": "pkg", "version": "1.0.0", "sdist": {"url": "url", "hash": "sha256:hash1"}}],
    }
    uv = UvLockFile.from_data(data)
    pip = convert(uv, PipfileLock)

    assert isinstance(pip, PipfileLock)
    assert "pkg" in pip.default
    assert pip.default["pkg"].version == "==1.0.0"
    assert "sha256:hash1" in pip.default["pkg"].hashes


def test_convert_pylock_to_uv():
    data = {
        "lock-version": "1.0",
        "created-by": "test",
        "requires-python": ">=3.11",
        "packages": [{"name": "pkg", "version": "1.2.3", "sdist": {"url": "url", "hashes": {"sha256": "hash1"}}}],
    }
    py_lock = PylockFile.from_data(data)
    uv = convert(py_lock, UvLockFile)

    assert isinstance(uv, UvLockFile)
    assert uv.requires_python == ">=3.11"
    assert len(uv.package) == 1
    assert uv.package[0].name == "pkg"
    assert uv.package[0].sdist.hash == "sha256:hash1"

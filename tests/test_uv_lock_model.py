from pyprojectr.uv_lock import UvLockFile


def test_uv_lock_basic_parsing():
    data = {
        "version": 1,
        "revision": 3,
        "requires-python": ">=3.11",
        "package": [
            {
                "name": "attrs",
                "version": "26.1.0",
                "source": {"registry": "https://pypi.org/simple"},
                "sdist": {"url": "https://example.com/attrs.tar.gz", "hash": "sha256:hash1", "size": 100},
                "wheels": [{"url": "https://example.com/attrs.whl", "hash": "sha256:hash2"}],
            }
        ],
    }
    uv_lock = UvLockFile.from_data(data)
    assert uv_lock.version == 1
    assert uv_lock.revision == 3
    assert uv_lock.requires_python == ">=3.11"
    assert len(uv_lock.package) == 1
    pkg = uv_lock.package[0]
    assert pkg.name == "attrs"
    assert pkg.version == "26.1.0"
    assert pkg.source.registry == "https://pypi.org/simple"
    assert pkg.sdist.url == "https://example.com/attrs.tar.gz"
    assert len(pkg.wheels) == 1


def test_uv_lock_dependencies():
    data = {
        "version": 1,
        "revision": 1,
        "package": [{"name": "pkg", "dependencies": [{"name": "dep1"}, {"name": "dep2", "extra": "foo"}]}],
    }
    uv_lock = UvLockFile.from_data(data)
    pkg = uv_lock.package[0]
    assert len(pkg.dependencies) == 2
    assert pkg.dependencies[0].name == "dep1"
    assert pkg.dependencies[1].extra == "foo"


def test_uv_lock_roundtrip():
    data = {
        "version": 1,
        "revision": 1,
        "requires-python": ">=3.11",
        "package": [{"name": "pkg", "sdist": {"url": "url", "hash": "hash", "upload-time": "2024-01-01T00:00:00Z"}}],
    }
    uv_lock = UvLockFile.from_data(data)
    unstructured = uv_lock.to_data()
    assert unstructured["requires-python"] == ">=3.11"
    assert unstructured["package"][0]["sdist"]["upload-time"] == "2024-01-01T00:00:00Z"

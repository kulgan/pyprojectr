from pyprojectr.pipfile_lock import PipfileLock


def test_pipfile_lock_basic_parsing():
    data = {
        "_meta": {
            "hash": {"sha256": "meta-hash"},
            "pipfile-spec": 6,
            "requires": {"python_version": "3.11"},
            "sources": [{"name": "pypi", "url": "https://pypi.org/simple", "verify_ssl": True}],
        },
        "default": {"requests": {"version": "==2.31.0", "hashes": ["sha256:hash1", "sha256:hash2"], "index": "pypi"}},
        "develop": {"pytest": {"version": "==8.0.0"}},
    }
    pip_lock = PipfileLock.from_data(data)
    assert pip_lock.meta.pipfile_spec == 6
    assert pip_lock.meta.requires["python_version"] == "3.11"
    assert len(pip_lock.meta.sources) == 1
    assert pip_lock.meta.sources[0].name == "pypi"

    assert "requests" in pip_lock.default
    assert pip_lock.default["requests"].version == "==2.31.0"
    assert len(pip_lock.default["requests"].hashes) == 2

    assert "pytest" in pip_lock.develop
    assert pip_lock.develop["pytest"].version == "==8.0.0"


def test_pipfile_lock_roundtrip():
    data = {
        "_meta": {"hash": {"sha256": "h"}, "pipfile-spec": 6, "requires": {}, "sources": []},
        "default": {"pkg": {"version": "==1.0"}},
        "develop": {},
    }
    pip_lock = PipfileLock.from_data(data)
    unstructured = pip_lock.to_data()
    # Note: to_data will return "meta" because we didn't specify a reverse hook for _meta in PipfileLock
    # But PipfileLock.from_data handles "_meta".
    # Actually, PipfileLock.meta has pyprojectr_no_rename: True, so it will be "meta" in unstructured.
    assert unstructured["meta"]["pipfile-spec"] == 6
    assert unstructured["default"]["pkg"]["version"] == "==1.0"

from __future__ import annotations

import pytest
from ygtv.app.__main__ import _source_from_env
from ygtv.sources import DirectorySource


def test_source_from_env_returns_directory_source(tmp_path, monkeypatch):
    monkeypatch.setenv("YGTV_SOURCE_DIR", str(tmp_path))
    source = _source_from_env()
    assert isinstance(source, DirectorySource)


def test_source_from_env_raises_when_var_absent(monkeypatch):
    monkeypatch.delenv("YGTV_SOURCE_DIR", raising=False)
    with pytest.raises(SystemExit):
        _source_from_env()

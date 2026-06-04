from __future__ import annotations

import pytest
from ygtv.app.__main__ import _live_refresh_ms_from_env, _source_from_env
from ygtv.app.pages.live import DEFAULT_REFRESH_MS
from ygtv.sources import DirectorySource


def test_source_from_env_returns_directory_source(tmp_path, monkeypatch):
    monkeypatch.setenv("YGTV_SOURCE_DIR", str(tmp_path))
    source = _source_from_env()
    assert isinstance(source, DirectorySource)


def test_source_from_env_raises_when_var_absent(monkeypatch):
    monkeypatch.delenv("YGTV_SOURCE_DIR", raising=False)
    with pytest.raises(SystemExit):
        _source_from_env()


def test_live_refresh_ms_defaults_when_unset(monkeypatch):
    monkeypatch.delenv("YGTV_LIVE_REFRESH_MS", raising=False)
    assert _live_refresh_ms_from_env() == DEFAULT_REFRESH_MS


def test_live_refresh_ms_parses_valid_int(monkeypatch):
    monkeypatch.setenv("YGTV_LIVE_REFRESH_MS", "2500")
    assert _live_refresh_ms_from_env() == 2500


def test_live_refresh_ms_rejects_non_integer(monkeypatch):
    monkeypatch.setenv("YGTV_LIVE_REFRESH_MS", "fast")
    with pytest.raises(SystemExit):
        _live_refresh_ms_from_env()


def test_live_refresh_ms_rejects_non_positive(monkeypatch):
    monkeypatch.setenv("YGTV_LIVE_REFRESH_MS", "0")
    with pytest.raises(SystemExit):
        _live_refresh_ms_from_env()

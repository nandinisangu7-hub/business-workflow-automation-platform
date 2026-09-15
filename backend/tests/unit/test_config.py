"""
Regression test for a real bug found while running Docker Compose:
pydantic-settings tries to JSON-decode any env var mapped to a `list[str]`
field before our own CSV-splitting validator runs, so a plain
comma-separated value (exactly what Docker Compose passes) raised a
SettingsError instead of being parsed. Fixed with `Annotated[list[str],
NoDecode]`. This test exists so that fix can never silently regress.
"""
import importlib

import app.core.config as config_module


def _reload_settings_with_env(monkeypatch, value):
    if value is None:
        monkeypatch.delenv("BACKEND_CORS_ORIGINS", raising=False)
    else:
        monkeypatch.setenv("BACKEND_CORS_ORIGINS", value)
    config_module.get_settings.cache_clear()
    importlib.reload(config_module)
    return config_module.get_settings()


def test_cors_origins_parses_comma_separated_env_var(monkeypatch):
    settings = _reload_settings_with_env(monkeypatch, "http://localhost:80,http://localhost:5173")
    assert settings.BACKEND_CORS_ORIGINS == ["http://localhost:80", "http://localhost:5173"]


def test_cors_origins_falls_back_to_default_when_unset(monkeypatch):
    settings = _reload_settings_with_env(monkeypatch, None)
    assert settings.BACKEND_CORS_ORIGINS == ["http://localhost:5173"]


def test_cors_origins_handles_single_origin_without_comma(monkeypatch):
    settings = _reload_settings_with_env(monkeypatch, "http://localhost:5173")
    assert settings.BACKEND_CORS_ORIGINS == ["http://localhost:5173"]

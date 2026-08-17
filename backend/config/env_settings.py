"""Resolve which settings module to use from the DJANGO_ENV env var.

DJANGO_ENV accepts "development"/"dev" or "production"/"prod" (case-insensitive).
Defaults to development so a bare `manage.py runserver` never accidentally
boots with production hardening (ALLOWED_HOSTS enforcement, HSTS, etc).
"""
import os

_ALIASES = {"development": "dev", "dev": "dev", "production": "prod", "prod": "prod"}


def resolve_settings_module():
    raw = os.environ.get("DJANGO_ENV", "development").strip().lower()
    suffix = _ALIASES.get(raw)
    if suffix is None:
        raise ValueError(f"Unknown DJANGO_ENV={raw!r}; expected one of {sorted(set(_ALIASES))}")
    return f"config.settings.{suffix}"

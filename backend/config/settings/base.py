"""
Shared Django settings. Environment-specific overrides live in dev.py / prod.py.

Everything that differs between environments (or between backend providers, e.g.
which LLM to call) is read from the process environment via django-environ, so
behaviour is controlled entirely by .env files / real env vars — never by editing
this file.
"""
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Exposed for dev.py/prod.py (`from .base import *` re-exports it too, but being
# explicit here avoids relying on star-import semantics for a non-constant name).
env = environ.Env(
    DEBUG=(bool, False),
)

# .env file resolution order: explicit ENV_FILE, then .env.<DJANGO_ENV>, then .env
_env_file = env.str("ENV_FILE", default="")
if _env_file:
    environ.Env.read_env(BASE_DIR / _env_file)
else:
    django_env = env.str("DJANGO_ENV", default="development")
    candidate = BASE_DIR / f".env.{django_env}"
    environ.Env.read_env(candidate if candidate.exists() else BASE_DIR / ".env")

SECRET_KEY = env.str("DJANGO_SECRET_KEY", default="django-insecure-change-me-in-production")
DEBUG = env.bool("DJANGO_DEBUG", default=False)
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.staticfiles",
    "django.contrib.admin",
    "django.contrib.sessions",
    "django.contrib.messages",
    "rest_framework",
    "corsheaders",
    "atlas_api",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

# The frontend calls endpoints without a trailing slash (e.g. /api/dashboard/v2);
# disable Django's redirect-to-slash behaviour so POSTs aren't silently dropped
# on a 301/308 redirect.
APPEND_SLASH = False

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# ---------- Database ----------
# Configurable via DATABASE_URL, e.g.:
#   sqlite:///db.sqlite3
#   postgres://user:pass@host:5432/dbname
DATABASES = {
    "default": env.db_url("DATABASE_URL", default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}"),
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = env.str("DJANGO_TIME_ZONE", default="UTC")
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------- CORS ----------
# Configurable so a separate frontend origin can be allowed per environment.
_cors_origins = env.str("CORS_ORIGINS", default="*")
if _cors_origins.strip() == "*":
    CORS_ALLOW_ALL_ORIGINS = True
else:
    CORS_ALLOWED_ORIGINS = [o.strip() for o in _cors_origins.split(",") if o.strip()]
CORS_ALLOW_CREDENTIALS = env.bool("CORS_ALLOW_CREDENTIALS", default=False)

# ---------- REST framework ----------
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser"],
    "EXCEPTION_HANDLER": "atlas_api.exceptions.api_exception_handler",
}

# ---------- Atlas app config ----------
# Every backend integration (LLM provider, model, keys) is env-driven so it can
# be swapped per-environment without code changes. See atlas_api/llm/factory.py.
ATLAS_LLM_PROVIDER = env.str("LLM_PROVIDER", default="gemini")
ATLAS_LLM_MODEL = env.str("LLM_MODEL", default="")  # provider supplies its own default if blank
ATLAS_LLM_TEMPERATURE = env.float("LLM_TEMPERATURE", default=0.4)
ATLAS_LLM_TIMEOUT = env.int("LLM_TIMEOUT_SECONDS", default=60)

GEMINI_API_KEY = env.str("GEMINI_API_KEY", default="")
GEMINI_API_BASE_URL = env.str(
    "GEMINI_API_BASE_URL", default="https://generativelanguage.googleapis.com/v1beta"
)
GEMINI_MODEL = env.str("GEMINI_MODEL", default="gemini-2.0-flash")

OPENAI_COMPATIBLE_API_KEY = env.str("OPENAI_COMPATIBLE_API_KEY", default=env.str("EMERGENT_LLM_KEY", default=""))
OPENAI_COMPATIBLE_BASE_URL = env.str(
    "OPENAI_COMPATIBLE_BASE_URL", default=env.str("EMERGENT_LLM_BASE_URL", default="https://api.openai.com/v1")
)
OPENAI_COMPATIBLE_MODEL = env.str("OPENAI_COMPATIBLE_MODEL", default="gpt-4.1")

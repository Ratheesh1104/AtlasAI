from .base import *  # noqa: F401,F403

DEBUG = False

if not ALLOWED_HOSTS or ALLOWED_HOSTS == ["*"]:
    raise ValueError("DJANGO_ALLOWED_HOSTS must be set explicitly in production")

SECURE_SSL_REDIRECT = env.bool("DJANGO_SECURE_SSL_REDIRECT", default=True)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = env.int("DJANGO_HSTS_SECONDS", default=31536000)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True

MIDDLEWARE = MIDDLEWARE[:1] + ["whitenoise.middleware.WhiteNoiseMiddleware"] + MIDDLEWARE[1:]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

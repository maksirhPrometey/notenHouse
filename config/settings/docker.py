"""Docker / DigitalOcean: TLS terminates in nginx, Gunicorn is HTTP-only."""

from decouple import config

from .production import *  # noqa: F403

USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# Critical: False — иначе healthcheck /healthz/ отримує 301 і web = unhealthy
SECURE_SSL_REDIRECT = False

_use_https = config('USE_HTTPS', default=False, cast=bool)
SESSION_COOKIE_SECURE = _use_https
CSRF_COOKIE_SECURE = _use_https

STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
    },
}

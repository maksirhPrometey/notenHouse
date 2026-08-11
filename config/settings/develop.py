"""Local development settings."""

from decouple import config

from .base import *  # noqa: F403

DEBUG = True

SECRET_KEY = config(
    'SECRET_KEY',
    default='dev-only-insecure-key-do-not-use-in-prod',
)

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]', 'testserver']

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    *MIDDLEWARE[1:],  # noqa: F405
]

STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedStaticFilesStorage',
    },
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

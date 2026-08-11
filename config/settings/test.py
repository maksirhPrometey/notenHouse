"""Test settings."""

from .develop import *  # noqa: F403

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]', 'testserver']

EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

from django.apps import AppConfig


class ContentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'src.content'

    def ready(self):
        # Proxy CMS models must be imported for admin/migrations discovery.
        from . import cms_proxy_models  # noqa: F401

"""Register Unfold ModelAdmin for each CMS proxy section."""

from __future__ import annotations

from django.contrib import admin
from unfold.admin import ModelAdmin

from .admin_site_content import SiteContentSectionAdminMixin
from .cms_proxy_models import SECTION_PROXY_MODELS
from .site_content_registry import validate_registry


def register_site_content_section_admins() -> None:
    validate_registry()
    for proxy, page_slug, section_slug in SECTION_PROXY_MODELS:
        admin_class = type(
            f'{proxy.__name__}Admin',
            (SiteContentSectionAdminMixin, ModelAdmin),
            {
                'page_slug': page_slug,
                'section_slug': section_slug,
            },
        )
        try:
            admin.site.register(proxy, admin_class)
        except admin.sites.AlreadyRegistered:
            continue

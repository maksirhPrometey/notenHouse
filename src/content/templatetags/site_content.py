"""Template tags for SiteBlock CMS."""

from __future__ import annotations

from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe

from src.content.site_blocks import (
    get_block_image_url,
    get_block_text,
    get_block_url,
    get_block_url_label,
    is_section_visible,
)

register = template.Library()


def _locale(context) -> str:
    request = context.get('request')
    if request is not None:
        return getattr(request, 'LANGUAGE_CODE', 'uk') or 'uk'
    return context.get('current_locale') or 'uk'


def _blocks(context):
    return context.get('site_blocks')


@register.simple_tag(takes_context=True)
def block_plain(context, page: str, key: str) -> str:
    return get_block_text(
        page,
        key,
        locale=_locale(context),
        site_blocks=_blocks(context),
    )


@register.simple_tag(takes_context=True)
def section_visible(context, page: str, visibility_key: str) -> bool:
    return is_section_visible(
        page,
        visibility_key,
        site_blocks=_blocks(context),
    )


@register.simple_tag(takes_context=True)
def block_url(context, page: str, key: str) -> str:
    return get_block_url(page, key, site_blocks=_blocks(context))


@register.simple_tag(takes_context=True)
def block_url_label(context, page: str, key: str) -> str:
    return get_block_url_label(
        page,
        key,
        locale=_locale(context),
        site_blocks=_blocks(context),
    )


@register.simple_tag(takes_context=True)
def block_image(context, page: str, key: str, css_class: str = '', alt: str = '') -> str:
    url = get_block_image_url(page, key, site_blocks=_blocks(context))
    if not url:
        return ''
    cls = f' class="{escape(css_class)}"' if css_class else ''
    return mark_safe(
        f'<img src="{escape(url)}" alt="{escape(alt)}"{cls} loading="lazy" decoding="async">'
    )


@register.simple_tag(takes_context=True)
def block_image_url(context, page: str, key: str) -> str:
    return get_block_image_url(page, key, site_blocks=_blocks(context))

"""Load / cache SiteBlock values for templates and CMS."""

from __future__ import annotations

from typing import Any

from django.core.cache import cache

from .block_defaults import (
    BLOCK_CONTENT_TYPES,
    BLOCK_DEFAULTS,
    default_text,
    get_block_default,
)
from .site_block_models import SiteBlock

SITE_BLOCKS_CACHE_KEY = 'notenhaus_site_blocks_v1'
SITE_BLOCKS_CACHE_TTL = 60


def invalidate_site_blocks_cache() -> None:
    cache.delete(SITE_BLOCKS_CACHE_KEY)
    # Hero text color lives in /theme.css — drop its cache too.
    from .views_theme import THEME_CSS_CACHE_KEY

    cache.delete(THEME_CSS_CACHE_KEY)


def ensure_site_blocks() -> int:
    """Idempotent seed from BLOCK_DEFAULTS. Returns created count."""
    created = 0
    for (page, key), data in BLOCK_DEFAULTS.items():
        content_type = BLOCK_CONTENT_TYPES.get(
            (page, key),
            SiteBlock.ContentType.TEXT,
        )
        defaults = {
            'label': data.get('label', key),
            'content_type': content_type,
            'text_uk': data.get('text_uk', ''),
            'text_en': data.get('text_en', ''),
            'link_url': data.get('link_url', ''),
            'link_label_uk': data.get('link_label_uk', ''),
            'link_label_en': data.get('link_label_en', ''),
            'is_active': True,
        }
        _, was_created = SiteBlock.objects.get_or_create(
            page=page,
            key=key,
            defaults=defaults,
        )
        if was_created:
            created += 1
    if created:
        invalidate_site_blocks_cache()
    return created


def _serialize_block(block: SiteBlock) -> dict[str, Any]:
    return {
        'page': block.page,
        'key': block.key,
        'label': block.label,
        'content_type': block.content_type,
        'text_uk': block.text_uk,
        'text_en': block.text_en,
        'image': block.image.url if block.image else '',
        'link_url': block.link_url,
        'link_label_uk': block.link_label_uk,
        'link_label_en': block.link_label_en,
        'video_embed_url': block.video_embed_url,
        'video_file': block.video_file.url if block.video_file else '',
        'is_active': block.is_active,
    }


def load_site_blocks(*, force: bool = False) -> dict[str, dict[str, Any]]:
    if not force:
        cached = cache.get(SITE_BLOCKS_CACHE_KEY)
        if cached is not None:
            return cached
    ensure_site_blocks()
    data = {
        block.cache_key: _serialize_block(block)
        for block in SiteBlock.objects.filter(is_active=True)
    }
    cache.set(SITE_BLOCKS_CACHE_KEY, data, SITE_BLOCKS_CACHE_TTL)
    return data


def get_block(
    page: str,
    key: str,
    *,
    site_blocks: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any] | None:
    blocks = site_blocks if site_blocks is not None else load_site_blocks()
    return blocks.get(f'{page}.{key}')


def get_block_text(
    page: str,
    key: str,
    *,
    locale: str = 'uk',
    site_blocks: dict[str, dict[str, Any]] | None = None,
    fallback: str | None = None,
) -> str:
    block = get_block(page, key, site_blocks=site_blocks)
    if block:
        if locale == 'en' and block.get('text_en'):
            return str(block['text_en'])
        if block.get('text_uk'):
            return str(block['text_uk'])
    if fallback is not None:
        return fallback
    return default_text(page, key, locale)


def is_section_visible(
    page: str,
    visibility_key: str,
    *,
    site_blocks: dict[str, dict[str, Any]] | None = None,
) -> bool:
    value = get_block_text(
        page,
        visibility_key,
        site_blocks=site_blocks,
        fallback='1',
    )
    return value not in {'0', 'false', 'False', ''}


def get_block_url(
    page: str,
    key: str,
    *,
    site_blocks: dict[str, dict[str, Any]] | None = None,
) -> str:
    block = get_block(page, key, site_blocks=site_blocks)
    if block and block.get('link_url'):
        return str(block['link_url'])
    return str(get_block_default(page, key).get('link_url') or '')


def get_block_url_label(
    page: str,
    key: str,
    *,
    locale: str = 'uk',
    site_blocks: dict[str, dict[str, Any]] | None = None,
) -> str:
    block = get_block(page, key, site_blocks=site_blocks)
    if block:
        if locale == 'en' and block.get('link_label_en'):
            return str(block['link_label_en'])
        if block.get('link_label_uk'):
            return str(block['link_label_uk'])
    data = get_block_default(page, key)
    if locale == 'en':
        return str(data.get('link_label_en') or data.get('link_label_uk') or '')
    return str(data.get('link_label_uk') or '')


def get_block_image_url(
    page: str,
    key: str,
    *,
    site_blocks: dict[str, dict[str, Any]] | None = None,
) -> str:
    block = get_block(page, key, site_blocks=site_blocks)
    if block and block.get('image'):
        return str(block['image'])
    return ''


def load_section_blocks(page: str, keys: list[str]) -> dict[str, SiteBlock]:
    """Lazy get_or_create for CMS form."""
    result: dict[str, SiteBlock] = {}
    for key in keys:
        data = get_block_default(page, key)
        content_type = BLOCK_CONTENT_TYPES.get(
            (page, key),
            SiteBlock.ContentType.TEXT,
        )
        block, _ = SiteBlock.objects.get_or_create(
            page=page,
            key=key,
            defaults={
                'label': data.get('label', key),
                'content_type': content_type,
                'text_uk': data.get('text_uk', ''),
                'text_en': data.get('text_en', ''),
                'link_url': data.get('link_url', ''),
                'link_label_uk': data.get('link_label_uk', ''),
                'link_label_en': data.get('link_label_en', ''),
            },
        )
        result[key] = block
    return result

"""Dynamic /theme.css — CSP-safe overrides from ActiveTheme + CMS tokens."""

from __future__ import annotations

import re

from django.core.cache import cache
from django.http import HttpResponse
from django.views.decorators.http import require_GET

from .site_blocks import get_block_text
from .theme import ActiveTheme

THEME_CSS_CACHE_KEY = 'theme_css_v1'
_HEX_RE = re.compile(r'^#[0-9A-Fa-f]{6}$')


def _hero_text_color() -> str:
    raw = (get_block_text('home', 'hero_text_color') or '').strip()
    if _HEX_RE.match(raw):
        return raw
    return '#ffffff'


def build_theme_css() -> str:
    theme = ActiveTheme.get_solo()
    parts = [theme.build_css().rstrip(), '']
    color = _hero_text_color()
    parts.append(f':root {{ --hero-text-color: {color}; }}')
    parts.append('')
    return '\n'.join(parts)


@require_GET
def theme_css(request):
    css = cache.get(THEME_CSS_CACHE_KEY)
    if css is None:
        css = build_theme_css()
        cache.set(THEME_CSS_CACHE_KEY, css, 3600)
    response = HttpResponse(css, content_type='text/css; charset=utf-8')
    response['Cache-Control'] = 'public, max-age=300'
    return response

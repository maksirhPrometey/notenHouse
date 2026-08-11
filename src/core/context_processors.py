"""Global template context."""

from decimal import Decimal
from pathlib import Path

from django.conf import settings

from src.catalog import selectors as catalog_selectors
from src.commerce.services import (
    cart_count,
    cart_product_ids,
    cart_total,
    get_or_create_cart,
)
from src.content.contacts_defaults import merge_contacts
from src.content.models import SiteSettings
from src.content.site_blocks import get_block_text, load_site_blocks
from src.content.theme import ActiveTheme


def _static_asset_version() -> int:
    """Newest mtime across ALL project CSS/JS (dev cache-bust).

    ERR-76/MA-11: a hand-picked file list silently misses new files and
    serves stale cached CSS after edits ("still broken" even though the
    fix is on disk). Scanning every *.css/*.js under static/ removes that
    whole class of bug — any styling/script change always changes ?v=.
    """
    static_root = Path(settings.BASE_DIR) / 'static'
    mtimes: list[int] = []
    for pattern in ('css/**/*.css', 'js/**/*.js'):
        for path in static_root.glob(pattern):
            try:
                mtimes.append(int(path.stat().st_mtime))
            except OSError:
                continue
    return max(mtimes) if mtimes else 0


def _theme_asset_version(theme: ActiveTheme) -> str:
    """Cache-bust /theme.css when ActiveTheme or hero text color changes."""
    theme_ts = int(theme.updated_at.timestamp()) if theme.updated_at else 0
    hero_color = (get_block_text('home', 'hero_text_color') or '#ffffff').strip().lstrip('#')
    return f'{theme_ts}-{hero_color}'


def site_context(request):
    site = SiteSettings.load()
    theme = ActiveTheme.get_solo()
    count = 0
    total = Decimal('0.00')
    product_ids: set[int] = set()
    wishlist_count = 0
    try:
        if request.session.session_key:
            cart = get_or_create_cart(request)
            count = cart_count(cart)
            total = cart_total(cart)
            product_ids = cart_product_ids(cart)
    except Exception:  # noqa: BLE001 — не ламати рендер
        count = 0
        total = Decimal('0.00')
        product_ids = set()
    try:
        user = getattr(request, 'user', None)
        if user is not None and user.is_authenticated:
            wishlist_count = user.wishlist_items.count()
    except Exception:  # noqa: BLE001 — не ламати рендер
        wishlist_count = 0
    return {
        'site_name': site.site_name,
        'site_contacts': merge_contacts(site.contacts_json),
        'site_logo': site.logo,
        'site_blocks': load_site_blocks(),
        'cart_count': count,
        'cart_total': total,
        'cart_product_ids': product_ids,
        'wishlist_count': wishlist_count,
        'current_locale': getattr(request, 'LANGUAGE_CODE', 'uk'),
        'theme_version': _theme_asset_version(theme),
        'static_version': _static_asset_version(),
        'theme_google_fonts_href': theme.google_fonts_href(),
        'nav_instruments': catalog_selectors.active_instruments(),
        'nav_genres': catalog_selectors.active_genres(),
        'nav_composers': catalog_selectors.active_composers(),
        'nav_levels': catalog_selectors.active_levels(),
    }

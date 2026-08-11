"""Locale field helpers (UK primary, EN optional fallback to UK)."""

from __future__ import annotations

from typing import Any


def pick_locale_field(obj: Any, field: str, locale: str = 'uk') -> str:
    """Return ``{field}_en`` when locale is en and value is non-empty, else ``{field}_uk``."""
    uk = getattr(obj, f'{field}_uk', None)
    uk_val = '' if uk is None else str(uk)
    if locale == 'en':
        en = getattr(obj, f'{field}_en', None)
        en_val = '' if en is None else str(en).strip()
        if en_val:
            return en_val
    return uk_val

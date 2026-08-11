"""Hero slides service + static fallback."""

from __future__ import annotations

from typing import Any

from .site_block_models import HeroSlide


def ensure_default_hero_slides() -> int:
    """No-op if any slides exist. Returns created count."""
    if HeroSlide.objects.exists():
        return 0
    # Без дефолтного фото — адмін додає сам; placeholder не створюємо.
    return 0


def get_hero_slides(*, locale: str = 'uk') -> list[dict[str, Any]]:
    ensure_default_hero_slides()
    slides = list(
        HeroSlide.objects.filter(is_active=True)
        .exclude(image='')
        .order_by('sort_order', 'pk')
    )
    result: list[dict[str, Any]] = []
    for slide in slides:
        if not slide.image:
            continue
        alt = slide.alt_for(locale)
        result.append({
            'image_url': slide.image.url,
            'alt': alt,
            'sort_order': slide.sort_order,
        })
    return result

"""Recommended image sizes for admin help text + upload processing."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class FitMode(str, Enum):
    COVER = 'cover'  # center-crop to exact box
    CONTAIN = 'contain'  # shrink to fit inside box, no crop


@dataclass(frozen=True)
class ImageSpec:
    width: int
    height: int
    mode: FitMode = FitMode.COVER
    to_webp: bool = True
    # Process resize/crop only when a side exceeds max × this ratio
    oversize_ratio: float = 1.25

    @property
    def help_text(self) -> str:
        if self.mode is FitMode.COVER:
            action = 'обрізаються та стискаються'
        else:
            action = 'масштабуються (без обрізки)'
        return (
            f'Рекомендований розмір: {self.width}×{self.height} px. '
            f'Значно більші фото автоматично {action}. '
            f'JPG/PNG → WebP.'
        )


PRODUCT_COVER = ImageSpec(800, 1200, FitMode.COVER)
HERO = ImageSpec(1920, 1080, FitMode.COVER)
LOGO = ImageSpec(480, 160, FitMode.CONTAIN)
TRUST_BADGE = ImageSpec(128, 128, FitMode.CONTAIN)

# SiteBlock (page, key) → spec
SITE_BLOCK_SPECS: dict[tuple[str, str], ImageSpec] = {
    ('home', 'hero_bg_image'): HERO,
    ('site', 'header_logo_fallback'): LOGO,
}

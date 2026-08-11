"""Нормалізований рядок імпорту (спільний для CSV і YML)."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal


@dataclass(slots=True)
class ImportRow:
    line_no: int
    sku: str = ''
    barcode: str = ''
    name_uk: str = ''
    name_en: str = ''
    composer: str = ''
    category: str = ''
    instruments: list[str] = field(default_factory=list)
    genres: list[str] = field(default_factory=list)
    level: str = ''
    format_name: str = ''
    description_uk: str = ''
    description_en: str = ''
    price_uah: Decimal | None = None
    stock_qty: int | None = None

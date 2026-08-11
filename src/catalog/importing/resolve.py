"""Пошук існуючого товару: sku → barcode → назва+композитор."""

from __future__ import annotations

from src.catalog.models import Product

from .row import ImportRow
from .taxonomy import find_composer_for_match


def find_existing_product(row: ImportRow) -> Product | None:
    sku = (row.sku or '').strip()
    if sku:
        found = Product.objects.filter(sku__iexact=sku).first()
        if found is not None:
            return found

    barcode = (row.barcode or '').strip()
    if barcode:
        found = Product.objects.filter(barcode=barcode).exclude(barcode='').first()
        if found is not None:
            return found

    name = ' '.join((row.name_uk or '').split()).strip()
    if not name:
        return None

    composer = find_composer_for_match(row.composer)
    qs = Product.objects.filter(name_uk__iexact=name)
    if composer is not None:
        return qs.filter(composer=composer).first()
    if not (row.composer or '').strip():
        return qs.filter(composer__isnull=True).first()
    return None

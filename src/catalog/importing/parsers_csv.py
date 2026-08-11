"""Парсер CSV → ImportRow."""

from __future__ import annotations

import csv
import io
from decimal import Decimal, InvalidOperation
from typing import BinaryIO, Iterator

from .row import ImportRow

REQUIRED_ALIASES = {
    'name_uk': ('name_uk', 'name', 'title', 'назва'),
    'price_uah': ('price_uah', 'price', 'ціна'),
}

OPTIONAL_ALIASES = {
    'sku': ('sku', 'article', 'артикул'),
    'barcode': ('barcode', 'ean', 'isbn', 'штрихкод'),
    'name_en': ('name_en', 'name_eng', 'title_en'),
    'composer': ('composer', 'author', 'композитор'),
    'category': ('category', 'category_name', 'категорія', 'категория'),
    'instruments': ('instruments', 'instrument', 'інструменти'),
    'genres': ('genres', 'genre', 'жанри'),
    'level': ('level', 'рівень'),
    'format_name': ('format', 'format_name', 'формат'),
    'description_uk': ('description_uk', 'description', 'опис'),
    'description_en': ('description_en', 'description_eng'),
    'stock_qty': ('stock_qty', 'stock', 'qty', 'кількість', 'залишок'),
}


def _split_multi(value: str) -> list[str]:
    if not value:
        return []
    parts = []
    for chunk in value.replace('|', ';').split(';'):
        item = chunk.strip()
        if item:
            parts.append(item)
    return parts


def _map_header(raw: str) -> str | None:
    key = (raw or '').strip().lstrip('\ufeff').casefold()
    for field, aliases in {**REQUIRED_ALIASES, **OPTIONAL_ALIASES}.items():
        if key in {a.casefold() for a in aliases}:
            return field
    return None


def _parse_price(raw: str) -> Decimal | None:
    text = (raw or '').strip().replace(' ', '').replace(',', '.')
    if not text:
        return None
    try:
        return Decimal(text)
    except InvalidOperation:
        raise ValueError(f'Некоректна ціна: {raw!r}') from None


def _parse_stock(raw: str) -> int | None:
    text = (raw or '').strip()
    if not text:
        return None
    return int(Decimal(text.replace(',', '.')))


def iter_csv_rows(stream: BinaryIO) -> Iterator[ImportRow]:
    raw = stream.read()
    if isinstance(raw, bytes):
        text = raw.decode('utf-8-sig')
    else:
        text = raw
    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames:
        raise ValueError('CSV без заголовків')

    colmap: dict[str, str] = {}
    for header in reader.fieldnames:
        field = _map_header(header or '')
        if field and field not in colmap:
            colmap[field] = header

    missing = [f for f in REQUIRED_ALIASES if f not in colmap]
    if missing:
        raise ValueError(f'CSV: відсутні обовʼязкові колонки: {", ".join(missing)}')

    for line_no, src in enumerate(reader, start=2):
        def get(field: str) -> str:
            header = colmap.get(field)
            if not header:
                return ''
            return (src.get(header) or '').strip()

        yield ImportRow(
            line_no=line_no,
            sku=get('sku'),
            barcode=get('barcode'),
            name_uk=get('name_uk'),
            name_en=get('name_en'),
            composer=get('composer'),
            category=get('category'),
            instruments=_split_multi(get('instruments')),
            genres=_split_multi(get('genres')),
            level=get('level'),
            format_name=get('format_name'),
            description_uk=get('description_uk'),
            description_en=get('description_en'),
            price_uah=_parse_price(get('price_uah')),
            stock_qty=_parse_stock(get('stock_qty')),
        )

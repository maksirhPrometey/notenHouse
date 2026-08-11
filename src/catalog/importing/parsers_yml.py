"""Парсер YML (Prom/Rozetka-подібний) → ImportRow."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from decimal import Decimal, InvalidOperation
from typing import BinaryIO, Iterator

from .row import ImportRow


def _text(el: ET.Element | None) -> str:
    if el is None or el.text is None:
        return ''
    return el.text.strip()


def _child(parent: ET.Element, *names: str) -> ET.Element | None:
    for name in names:
        found = parent.find(name)
        if found is not None:
            return found
    return None


def _parse_price(raw: str) -> Decimal | None:
    text = (raw or '').strip().replace(' ', '').replace(',', '.')
    if not text:
        return None
    try:
        return Decimal(text)
    except InvalidOperation:
        raise ValueError(f'Некоректна ціна: {raw!r}') from None


def iter_yml_rows(stream: BinaryIO) -> Iterator[ImportRow]:
    raw = stream.read()
    if isinstance(raw, str):
        raw = raw.encode('utf-8')
    try:
        root = ET.fromstring(raw)
    except ET.ParseError as exc:
        raise ValueError(f'Невалідний XML/YML: {exc}') from exc

    shop = root if root.tag.endswith('shop') else root.find('.//shop')
    if shop is None:
        shop = root

    categories: dict[str, str] = {}
    cats_el = shop.find('categories')
    if cats_el is not None:
        for cat in cats_el.findall('category'):
            cid = (cat.get('id') or '').strip()
            name = (cat.text or '').strip()
            if cid and name:
                categories[cid] = name

    offers_el = shop.find('offers')
    offer_nodes = offers_el.findall('offer') if offers_el is not None else shop.findall('.//offer')
    if not offer_nodes:
        raise ValueError('YML: не знайдено жодного <offer>')

    for idx, offer in enumerate(offer_nodes, start=1):
        name = _text(_child(offer, 'name', 'title'))
        price_raw = _text(_child(offer, 'price'))
        vendor_code = _text(_child(offer, 'vendorCode', 'vendor_code', 'article'))
        barcode = _text(_child(offer, 'barcode', 'ean', 'isbn'))
        vendor = _text(_child(offer, 'vendor', 'composer', 'author'))
        description = _text(_child(offer, 'description'))
        stock_raw = _text(_child(offer, 'stock_quantity', 'stock', 'quantity'))

        cat_id = _text(_child(offer, 'categoryId', 'category_id'))
        if not cat_id:
            cat_id = (offer.get('categoryId') or '').strip()
        category = categories.get(cat_id, '')

        sku = vendor_code or (offer.get('id') or '').strip()
        stock_qty = None
        if stock_raw:
            stock_qty = int(Decimal(stock_raw.replace(',', '.')))
        elif (offer.get('available') or '').lower() in {'true', '1', 'yes'}:
            stock_qty = 1
        elif (offer.get('available') or '').lower() in {'false', '0', 'no'}:
            stock_qty = 0

        yield ImportRow(
            line_no=idx,
            sku=sku,
            barcode=barcode,
            name_uk=name,
            name_en='',
            composer=vendor,
            category=category,
            instruments=[],
            genres=[],
            level='',
            format_name='',
            description_uk=description,
            description_en='',
            price_uah=_parse_price(price_raw),
            stock_qty=stock_qty,
        )

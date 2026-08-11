"""Унікальні slug для довідників і товарів."""

from __future__ import annotations

import re
import unicodedata

from django.db.models import Model


_SLUG_SAFE = re.compile(r'[^a-z0-9\-]+')
_MULTI_DASH = re.compile(r'-{2,}')


def slugify_uk(value: str, *, max_length: int = 160) -> str:
    text = (value or '').strip().lower()
    text = unicodedata.normalize('NFKD', text)
    text = ''.join(ch for ch in text if not unicodedata.combining(ch))
    trans = str.maketrans({
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'h', 'ґ': 'g', 'д': 'd', 'е': 'e',
        'є': 'ie', 'ж': 'zh', 'з': 'z', 'и': 'y', 'і': 'i', 'ї': 'i', 'й': 'i',
        'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r',
        'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch',
        'ш': 'sh', 'щ': 'shch', 'ь': '', 'ю': 'iu', 'я': 'ia',
        'ъ': '', 'ы': 'y', 'э': 'e',
    })
    text = text.translate(trans)
    text = _SLUG_SAFE.sub('-', text.replace(' ', '-'))
    text = _MULTI_DASH.sub('-', text).strip('-')
    if not text:
        text = 'item'
    return text[:max_length].rstrip('-')


def unique_slug(model: type[Model], base: str, *, exclude_pk: int | None = None) -> str:
    slug = slugify_uk(base)[:160]
    candidate = slug
    n = 2
    qs = model.objects.all()
    if exclude_pk is not None:
        qs = qs.exclude(pk=exclude_pk)
    while qs.filter(slug=candidate).exists():
        suffix = f'-{n}'
        candidate = f'{slug[: 160 - len(suffix)]}{suffix}'
        n += 1
    return candidate

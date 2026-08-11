"""Створення / резолв довідників каталогу під час імпорту."""

from __future__ import annotations

from django.db.models import Q

from src.catalog.models import Composer, Format, Genre, Instrument, Level
from src.catalog.taxonomy_i18n import lookup_english, norm_name

from .slug_utils import unique_slug


def _norm(name: str) -> str:
    return norm_name(name)


def get_or_create_by_name(model, name: str, *, cache: dict):
    key = _norm(name).casefold()
    if not key:
        return None
    if key in cache:
        return cache[key]

    name_uk = _norm(name)
    obj = model.objects.filter(
        Q(name_uk__iexact=name_uk) | Q(name_en__iexact=name_uk),
    ).first()

    if obj is None:
        en = lookup_english(model, name_uk)
        obj = model.objects.create(
            name_uk=name_uk,
            name_en=en,
            slug=unique_slug(model, name_uk),
            is_active=True,
        )
    else:
        # Імпорт раніше міг створити рядок без EN — доповнюємо зі словника.
        if not (obj.name_en or '').strip():
            en = lookup_english(model, obj.name_uk or name_uk)
            if en:
                obj.name_en = en
                obj.save(update_fields=['name_en', 'updated_at'])

    cache[key] = obj
    return obj


def resolve_category(
    category: str,
    *,
    instrument_cache: dict,
    genre_cache: dict,
) -> tuple[list, list]:
    """
    category → Instrument і/або Genre.
    - якщо є Instrument з такою назвою — лінкуємо;
    - якщо є Genre — лінкуємо;
    - якщо немає жодного — створюємо Instrument.
    """
    name = _norm(category)
    if not name:
        return [], []

    key = name.casefold()
    instruments: list = []
    genres: list = []

    inst = instrument_cache.get(key) or Instrument.objects.filter(
        Q(name_uk__iexact=name) | Q(name_en__iexact=name),
    ).first()
    gen = genre_cache.get(key) or Genre.objects.filter(
        Q(name_uk__iexact=name) | Q(name_en__iexact=name),
    ).first()

    if inst is not None:
        if not (inst.name_en or '').strip():
            en = lookup_english(Instrument, inst.name_uk or name)
            if en:
                inst.name_en = en
                inst.save(update_fields=['name_en', 'updated_at'])
        instrument_cache[key] = inst
        instruments.append(inst)
    if gen is not None:
        if not (gen.name_en or '').strip():
            en = lookup_english(Genre, gen.name_uk or name)
            if en:
                gen.name_en = en
                gen.save(update_fields=['name_en', 'updated_at'])
        genre_cache[key] = gen
        genres.append(gen)

    if not instruments and not genres:
        instruments.append(
            get_or_create_by_name(Instrument, name, cache=instrument_cache),
        )

    return instruments, genres


def resolve_composer(name: str, *, cache: dict) -> Composer | None:
    return get_or_create_by_name(Composer, name, cache=cache)


def resolve_level(name: str, *, cache: dict) -> Level | None:
    return get_or_create_by_name(Level, name, cache=cache)


def resolve_format(name: str, *, cache: dict) -> Format | None:
    return get_or_create_by_name(Format, name, cache=cache)


def find_composer_for_match(name: str) -> Composer | None:
    """Пошук композитора без створення (для дедупа назва+композитор)."""
    name = _norm(name)
    if not name:
        return None
    return Composer.objects.filter(
        Q(name_uk__iexact=name) | Q(name_en__iexact=name),
    ).first()

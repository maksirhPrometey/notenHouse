"""Catalog template helpers — product grid columns (product_grid_skill)."""

from django import template

from src.core.i18n_fields import pick_locale_field

register = template.Library()


def _locale(context) -> str:
    request = context.get('request')
    if request is not None:
        return getattr(request, 'LANGUAGE_CODE', 'uk') or 'uk'
    return context.get('current_locale') or 'uk'


@register.simple_tag(takes_context=True)
def loc(context, obj, field: str = 'name') -> str:
    """Localized model field: ``{% loc product %}`` / ``{% loc img 'alt' %}``."""
    if obj is None:
        return ''
    method = getattr(obj, f'{field}_for', None)
    if callable(method):
        return method(_locale(context))
    return pick_locale_field(obj, field, _locale(context))


def pick_grid_columns(count: int) -> int:
    """Desktop: лише 5, 4 або 3 колонки."""
    if count <= 0:
        return 2
    if count <= 2:
        return 3

    for cols in (5, 4, 3):
        if count % cols == 0:
            return cols

    for cols in (4, 5, 3):
        if count % cols >= 3:
            return cols

    for cols in (3, 5, 4):
        if count % cols == 2:
            return cols

    return 3


@register.simple_tag
def product_grid_cols(products) -> int:
    try:
        count = len(products)
    except TypeError:
        count = products.count() if hasattr(products, 'count') else 0
    return pick_grid_columns(count)

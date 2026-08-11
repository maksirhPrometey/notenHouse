"""Catalog read layer — tables.md filters + sitemap /katalog/ /nota/ /poshuk/."""

from django.db.models import Prefetch, Q, QuerySet

from .models import Genre, Instrument, Product, ProductFile, ProductFileKind, ProductImage


def published_products() -> QuerySet[Product]:
    return (
        Product.objects.filter(is_published=True)
        .select_related('composer', 'level', 'format')
        .prefetch_related(
            Prefetch(
                'images',
                queryset=ProductImage.objects.filter(is_main=True),
                to_attr='main_images',
            ),
            Prefetch(
                'files',
                queryset=ProductFile.objects.filter(kind=ProductFileKind.PREVIEW),
                to_attr='preview_files',
            ),
            'instruments',
            'genres',
        )
    )


def get_product_by_slug(slug: str) -> Product | None:
    return (
        published_products()
        .prefetch_related('images', 'files')
        .filter(slug=slug)
        .first()
    )


def filter_catalog(
    *,
    composer: str = '',
    instrument: str = '',
    genre: str = '',
    level: str = '',
    q: str = '',
    sort: str = 'new',
) -> QuerySet[Product]:
    qs = published_products()
    if composer:
        qs = qs.filter(composer__slug=composer)
    if instrument:
        qs = qs.filter(instruments__slug=instrument)
    if genre:
        qs = qs.filter(genres__slug=genre)
    if level:
        qs = qs.filter(level__slug=level)
    if q:
        qs = qs.filter(
            Q(name_uk__icontains=q)
            | Q(name_en__icontains=q)
            | Q(sku__icontains=q)
        )
    qs = qs.distinct()
    return apply_sort(qs, sort)


def apply_sort(qs: QuerySet[Product], sort: str) -> QuerySet[Product]:
    mapping = {
        'new': ('-published_at', '-id'),
        'popular': ('-is_popular', '-published_at'),
        'price_asc': ('price_uah', 'name_uk'),
        'price_desc': ('-price_uah', 'name_uk'),
        'name': ('name_uk',),
    }
    return qs.order_by(*mapping.get(sort, mapping['new']))


def search_products(q: str) -> QuerySet[Product]:
    q = (q or '').strip()
    if not q:
        return published_products().none()
    return filter_catalog(q=q)


def popular_products(limit: int = 8) -> QuerySet[Product]:
    return published_products().filter(is_popular=True).order_by('-published_at')[:limit]


def new_products(limit: int = 8) -> QuerySet[Product]:
    return published_products().filter(is_new=True).order_by('-published_at')[:limit]


def resolve_katalog_slug(slug: str) -> tuple[str, Instrument | Genre | None]:
    """Return ('instrument'|'genre'|'', obj)."""
    instrument = Instrument.objects.filter(slug=slug, is_active=True).first()
    if instrument:
        return 'instrument', instrument
    genre = Genre.objects.filter(slug=slug, is_active=True).first()
    if genre:
        return 'genre', genre
    return '', None


def active_instruments():
    return Instrument.objects.filter(is_active=True).order_by('sort_order', 'name_uk')


def active_genres():
    return Genre.objects.filter(is_active=True).order_by('sort_order', 'name_uk')


def active_composers():
    from .models import Composer

    return Composer.objects.filter(is_active=True).order_by('sort_order', 'name_uk')


def active_levels():
    from .models import Level

    return Level.objects.filter(is_active=True).order_by('sort_order', 'name_uk')

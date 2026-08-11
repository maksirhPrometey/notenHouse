"""Catalog public views."""

from django.core.paginator import Paginator
from django.http import Http404
from django.urls import reverse
from django.views.generic import DetailView, ListView, TemplateView

from src.content.site_blocks import get_block_text

from . import selectors


def _locale(request) -> str:
    return getattr(request, 'LANGUAGE_CODE', 'uk') or 'uk'


def _home_label(locale: str) -> str:
    return 'Home' if locale == 'en' else 'Головна'


class CatalogListView(ListView):
    template_name = 'catalog/list.html'
    context_object_name = 'products'
    paginate_by = 24

    def get_template_names(self):
        if getattr(self.request, 'htmx', False):
            return ['catalog/partials/catalog_results.html']
        return [self.template_name]

    def get_queryset(self):
        p = self.request.GET
        return selectors.filter_catalog(
            composer=p.get('composer', ''),
            instrument=p.get('instrument', ''),
            genre=p.get('genre', ''),
            level=p.get('level', ''),
            q=p.get('q', ''),
            sort=p.get('sort', 'new'),
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        p = self.request.GET
        locale = _locale(self.request)
        catalog_label = get_block_text('catalog', 'title', locale=locale)
        ctx.update(
            {
                'page_title': catalog_label,
                'meta_description': get_block_text('catalog', 'lead', locale=locale),
                'filters': {
                    'composer': p.get('composer', ''),
                    'instrument': p.get('instrument', ''),
                    'genre': p.get('genre', ''),
                    'level': p.get('level', ''),
                    'q': p.get('q', ''),
                    'sort': p.get('sort', 'new'),
                    'view': p.get('view') if p.get('view') in ('grid', 'list') else 'grid',
                },
                'composers': selectors.active_composers(),
                'instruments': selectors.active_instruments(),
                'genres': selectors.active_genres(),
                'levels': selectors.active_levels(),
                'breadcrumbs': [
                    (_home_label(locale), reverse('core:home')),
                    (catalog_label, None),
                ],
            }
        )
        return ctx


class CatalogFacetView(CatalogListView):
    """ /katalog/{slug}/ — instrument або genre. """

    def dispatch(self, request, *args, **kwargs):
        kind, obj = selectors.resolve_katalog_slug(kwargs['slug'])
        if not obj:
            raise Http404
        self.facet_kind = kind
        self.facet = obj
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        p = self.request.GET
        kwargs = {
            'composer': p.get('composer', ''),
            'level': p.get('level', ''),
            'q': p.get('q', ''),
            'sort': p.get('sort', 'new'),
        }
        if self.facet_kind == 'instrument':
            kwargs['instrument'] = self.facet.slug
            kwargs['genre'] = p.get('genre', '')
        else:
            kwargs['genre'] = self.facet.slug
            kwargs['instrument'] = p.get('instrument', '')
        return selectors.filter_catalog(**kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        locale = _locale(self.request)
        name = self.facet.name_for(locale)
        catalog_label = get_block_text('catalog', 'title', locale=locale)
        suffix = 'catalog' if locale == 'en' else 'каталог'
        ctx['page_title'] = f'{name} — {suffix}'
        ctx['breadcrumbs'] = [
            (_home_label(locale), reverse('core:home')),
            (catalog_label, reverse('catalog:katalog')),
            (name, None),
        ]
        ctx['filters'][self.facet_kind] = self.facet.slug
        ctx['facet'] = self.facet
        ctx['facet_kind'] = self.facet_kind
        return ctx


class ProductDetailView(DetailView):
    template_name = 'catalog/detail.html'
    context_object_name = 'product'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return selectors.published_products().prefetch_related('images', 'files')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        product = self.object
        locale = _locale(self.request)
        name = product.name_for(locale)
        description = product.description_for(locale)
        catalog_label = get_block_text('catalog', 'title', locale=locale)
        ctx['page_title'] = name
        ctx['meta_description'] = (product.seo_description or description)[:160]
        ctx['breadcrumbs'] = [
            (_home_label(locale), reverse('core:home')),
            (catalog_label, reverse('catalog:katalog')),
            (name, None),
        ]
        user = self.request.user
        ctx['is_wishlisted'] = (
            user.is_authenticated and user.wishlist_items.filter(product=product).exists()
        )
        return ctx


class SearchView(TemplateView):
    template_name = 'catalog/search.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        locale = _locale(self.request)
        q = (self.request.GET.get('q') or '').strip()
        products = selectors.search_products(q)
        paginator = Paginator(products, 24)
        page = paginator.get_page(self.request.GET.get('page'))
        search_label = get_block_text('search', 'title', locale=locale)
        crumbs = [
            (_home_label(locale), reverse('core:home')),
            (search_label, None),
        ]
        if q:
            crumbs = [
                (_home_label(locale), reverse('core:home')),
                (search_label, reverse('catalog:search')),
                (q, None),
            ]
        ctx.update(
            {
                'page_title': search_label,
                'q': q,
                'products': page,
                'page_obj': page,
                'empty': bool(q) and not page.object_list,
                'breadcrumbs': crumbs,
            }
        )
        return ctx

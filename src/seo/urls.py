from django.contrib.sitemaps import Sitemap
from django.contrib.sitemaps.views import sitemap
from django.http import HttpResponse
from django.urls import path, reverse
from django.views import View

from src.catalog.models import Genre, Instrument, Product
from src.content.models import Page, SiteSettings


class ProductSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return Product.objects.filter(is_published=True)

    def location(self, obj):
        return reverse('catalog:nota_detail', kwargs={'slug': obj.slug})


class InstrumentSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.6

    def items(self):
        return Instrument.objects.filter(is_active=True)

    def location(self, obj):
        return reverse('catalog:katalog_slug', kwargs={'slug': obj.slug})


class GenreSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.6

    def items(self):
        return Genre.objects.filter(is_active=True)

    def location(self, obj):
        return reverse('catalog:katalog_slug', kwargs={'slug': obj.slug})


class StaticSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.5

    def items(self):
        return [
            'core:home',
            'catalog:katalog',
            'catalog:search',
            'content:about',
            'content:shipping_payment',
            'content:contacts',
        ]

    def location(self, item):
        return reverse(item)


class PageSitemap(Sitemap):
    def items(self):
        # Fixed routes (/pro-nas/, /dostavka-i-oplata/) are in StaticViewSitemap.
        return Page.objects.filter(is_published=True).exclude(
            slug__in=('pro-nas', 'dostavka-i-oplata'),
        )

    def location(self, obj):
        return f'/{obj.slug}/'


class RobotsView(View):
    def get(self, request):
        site = SiteSettings.load()
        body = (site.robots_txt or '').strip()
        if not body:
            body = (
                'User-agent: *\n'
                'Disallow: /admin/\n'
                'Disallow: /payments/\n'
                f'Sitemap: {request.build_absolute_uri("/sitemap.xml")}\n'
            )
        return HttpResponse(body, content_type='text/plain')


sitemaps = {
    'products': ProductSitemap,
    'instruments': InstrumentSitemap,
    'genres': GenreSitemap,
    'static': StaticSitemap,
    'pages': PageSitemap,
}

app_name = 'seo'

urlpatterns = [
    path(
        'sitemap.xml',
        sitemap,
        {'sitemaps': sitemaps},
        name='django.contrib.sitemaps.views.sitemap',
    ),
    path('robots.txt', RobotsView.as_view(), name='robots'),
]

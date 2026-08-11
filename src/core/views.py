from django.views.generic import TemplateView

from src.catalog import selectors
from src.content.hero_slides import get_hero_slides
from src.content.site_blocks import get_block_text


class HomeView(TemplateView):
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        locale = getattr(self.request, 'LANGUAGE_CODE', 'uk') or 'uk'
        context['page_title'] = 'NotenHaus'
        context['meta_description'] = get_block_text(
            'home', 'meta_description', locale=locale,
        )
        context['popular_products'] = selectors.popular_products()
        context['new_products'] = selectors.new_products()
        context['hero_slides'] = get_hero_slides(locale=locale)
        return context

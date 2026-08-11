from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

from src.content.views_theme import theme_css
from src.core.views_i18n import set_language

urlpatterns = [
    path(
        'favicon.ico',
        RedirectView.as_view(
            url=settings.STATIC_URL + 'images/favicon.ico',
            permanent=True,
        ),
        name='favicon',
    ),
    path('admin/', admin.site.urls),
    path('theme.css', theme_css, name='theme_css'),
    path('healthz/', include('src.core.urls_health')),
    path('i18n/setlang/', set_language, name='set_language'),
    path('', include('src.payments.urls')),
    path('', include('src.shipping.urls')),
    path('', include('src.seo.urls')),
]

urlpatterns += i18n_patterns(
    path('', include('src.core.urls')),
    path('', include('src.catalog.urls')),
    path('', include('src.commerce.urls')),
    path('', include('src.content.urls')),
    path('', include('src.cabinet.urls')),
    prefix_default_language=False,
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

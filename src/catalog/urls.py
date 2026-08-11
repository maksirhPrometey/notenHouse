from django.urls import path

from .views import CatalogFacetView, CatalogListView, ProductDetailView, SearchView

app_name = 'catalog'

urlpatterns = [
    path('katalog/', CatalogListView.as_view(), name='katalog'),
    path('katalog/<slug:slug>/', CatalogFacetView.as_view(), name='katalog_slug'),
    path('nota/<slug:slug>/', ProductDetailView.as_view(), name='nota_detail'),
    path('poshuk/', SearchView.as_view(), name='search'),
]

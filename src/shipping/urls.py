from django.urls import path

from .views import CitiesView, WarehousesView

app_name = 'shipping'

urlpatterns = [
    path('api/np/cities/', CitiesView.as_view(), name='np_cities'),
    path('api/np/warehouses/', WarehousesView.as_view(), name='np_warehouses'),
]

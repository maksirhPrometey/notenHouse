from django.http import JsonResponse
from django.views import View

from .services import NovaPoshtaError, get_warehouses, search_cities


class CitiesView(View):
    def get(self, request):
        q = request.GET.get('q', '')
        try:
            cities = search_cities(q)
        except NovaPoshtaError as exc:
            return JsonResponse({'ok': False, 'error': str(exc)}, status=502)
        return JsonResponse({'ok': True, 'results': cities})


class WarehousesView(View):
    def get(self, request):
        city_ref = request.GET.get('city_ref', '')
        q = request.GET.get('q', '')
        try:
            rows = get_warehouses(city_ref, q)
        except NovaPoshtaError as exc:
            return JsonResponse({'ok': False, 'error': str(exc)}, status=502)
        return JsonResponse({'ok': True, 'results': rows})

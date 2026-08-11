from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from .views import LiqPayCallbackView

app_name = 'payments'

urlpatterns = [
    path(
        'payments/callback/',
        csrf_exempt(LiqPayCallbackView.as_view()),
        name='callback',
    ),
]

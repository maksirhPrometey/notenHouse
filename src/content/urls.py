from django.urls import path

from .views import (
    AboutView,
    ContactLeadCreateView,
    ContactsView,
    ShippingPaymentView,
)

app_name = 'content'

urlpatterns = [
    path('pro-nas/', AboutView.as_view(), name='about'),
    path(
        'dostavka-i-oplata/',
        ShippingPaymentView.as_view(),
        name='shipping_payment',
    ),
    path('kontakty/', ContactsView.as_view(), name='contacts'),
    path('kontakty/lead/', ContactLeadCreateView.as_view(), name='contact_lead'),
]

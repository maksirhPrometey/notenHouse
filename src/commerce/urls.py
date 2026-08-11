from django.urls import path

from .views import (
    CartAddView,
    CartDetailView,
    CartRemoveView,
    CartUpdateView,
    CheckoutView,
    PaymentRetryView,
    ThankYouView,
)

app_name = 'commerce'

urlpatterns = [
    path('koshyk/', CartDetailView.as_view(), name='cart'),
    path('koshyk/add/<int:product_id>/', CartAddView.as_view(), name='cart_add'),
    path('koshyk/update/<int:item_id>/', CartUpdateView.as_view(), name='cart_update'),
    path('koshyk/remove/<int:item_id>/', CartRemoveView.as_view(), name='cart_remove'),
    path('oformlennya/', CheckoutView.as_view(), name='checkout'),
    path('dyakuyemo/', ThankYouView.as_view(), name='thank_you'),
    path('oformlennya/oplata/', PaymentRetryView.as_view(), name='payment_retry'),
]

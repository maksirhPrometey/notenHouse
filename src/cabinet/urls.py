from django.urls import path

from .views import (
    CabinetLoginView,
    CabinetLogoutView,
    DashboardView,
    OrderDetailView,
    OrderListView,
    OrderReorderView,
    ProfileView,
    RegisterView,
    WishlistToggleView,
    WishlistView,
)

app_name = 'cabinet'

urlpatterns = [
    path('kabinet/', DashboardView.as_view(), name='dashboard'),
    path('kabinet/vkhid/', CabinetLoginView.as_view(), name='login'),
    path('kabinet/reyestratsiya/', RegisterView.as_view(), name='register'),
    path('kabinet/vykhid/', CabinetLogoutView.as_view(), name='logout'),
    path('kabinet/profil/', ProfileView.as_view(), name='profile'),
    path('kabinet/zamovlennya/', OrderListView.as_view(), name='orders'),
    path(
        'kabinet/zamovlennya/<str:number>/',
        OrderDetailView.as_view(),
        name='order_detail',
    ),
    path(
        'kabinet/zamovlennya/<str:number>/povtoryty/',
        OrderReorderView.as_view(),
        name='order_reorder',
    ),
    path('obrane/', WishlistView.as_view(), name='wishlist'),
    path('obrane/toggle/<int:product_id>/', WishlistToggleView.as_view(), name='wishlist_toggle'),
]

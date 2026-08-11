from unfold.admin import ModelAdmin, TabularInline
from django.contrib import admin

from .models import Cart, CartItem, Order, OrderItem, OrderStatusLog


class CartItemInline(TabularInline):
    model = CartItem
    extra = 0
    raw_id_fields = ('product',)
    tab = True


@admin.register(Cart)
class CartAdmin(ModelAdmin):
    list_display = ('id', 'session_key', 'status', 'created_at', 'updated_at')
    list_filter = ('status',)
    search_fields = ('session_key',)
    inlines = [CartItemInline]


class OrderItemInline(TabularInline):
    model = OrderItem
    extra = 0
    raw_id_fields = ('product',)
    can_delete = False
    tab = True


class OrderStatusLogInline(TabularInline):
    model = OrderStatusLog
    extra = 0
    readonly_fields = ('created_at',)
    tab = True


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = (
        'number',
        'status',
        'payment_status',
        'customer_name',
        'customer_email',
        'total_uah',
        'created_at',
    )
    list_filter = ('status', 'payment_status', 'shipping_method', 'payment_provider')
    list_filter_submit = True
    search_fields = ('number', 'customer_email', 'customer_phone', 'customer_name')
    inlines = [OrderItemInline, OrderStatusLogInline]
    readonly_fields = ('created_at', 'updated_at', 'paid_at')

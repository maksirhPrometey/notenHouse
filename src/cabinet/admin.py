from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import CustomerProfile, WishlistItem


@admin.register(CustomerProfile)
class CustomerProfileAdmin(ModelAdmin):
    list_display = ('user', 'display_name', 'phone', 'created_at')
    search_fields = ('user__email', 'display_name', 'phone')
    raw_id_fields = ('user',)


@admin.register(WishlistItem)
class WishlistItemAdmin(ModelAdmin):
    list_display = ('user', 'product', 'created_at')
    search_fields = ('user__email', 'product__name_uk', 'product__sku')
    raw_id_fields = ('user', 'product')

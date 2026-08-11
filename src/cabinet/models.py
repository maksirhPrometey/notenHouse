"""Cabinet — customer profile + wishlist (tables.md §10, M5 unlock)."""

from django.conf import settings
from django.db import models

from src.core.models import CreatedAtModel, TimeStampedModel


class CustomerProfile(TimeStampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='cabinet_profile',
        verbose_name='Користувач',
    )
    display_name = models.CharField('Імʼя', max_length=255, blank=True, default='')
    phone = models.CharField('Телефон', max_length=32, blank=True, default='')

    class Meta:
        verbose_name = 'Профіль клієнта'
        verbose_name_plural = 'Профілі клієнтів'
        db_table = 'cabinet_customer_profile'

    def __str__(self) -> str:
        return self.display_name or self.user.email


class WishlistItem(CreatedAtModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wishlist_items',
        verbose_name='Користувач',
    )
    product = models.ForeignKey(
        'catalog.Product',
        on_delete=models.CASCADE,
        related_name='wishlisted_by',
        verbose_name='Нота',
    )

    class Meta:
        verbose_name = 'Позиція обраного'
        verbose_name_plural = 'Обране'
        db_table = 'cabinet_wishlist_item'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'product'],
                name='cabinet_wishlist_item_uniq',
            ),
        ]

    def __str__(self) -> str:
        return f'{self.user_id} ♥ {self.product_id}'

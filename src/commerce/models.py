"""Commerce models — tables.md §3.5–3.9."""

from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q

from src.core.models import CreatedAtModel, TimeStampedModel


class CartStatus(models.TextChoices):
    ACTIVE = 'active', 'Активний'
    CONVERTED = 'converted', 'Оформлений'
    ABANDONED = 'abandoned', 'Покинутий'


class OrderStatus(models.TextChoices):
    NEW = 'new', 'Нове'
    PROCESSING = 'processing', 'В обробці'
    SHIPPED = 'shipped', 'Відправлено'
    COMPLETED = 'completed', 'Виконано'
    CANCELLED = 'cancelled', 'Скасовано'


class PaymentStatus(models.TextChoices):
    AWAITING = 'awaiting', 'Очікує оплати'
    PAID = 'paid', 'Оплачено'
    FAILED = 'failed', 'Помилка оплати'


class ShippingMethod(models.TextChoices):
    NP_WAREHOUSE = 'np_warehouse', 'Нова Пошта — відділення'
    NP_POSHTOMAT = 'np_poshtomat', 'Нова Пошта — поштомат'
    PICKUP = 'pickup', 'Самовивіз'


class PaymentProvider(models.TextChoices):
    LIQPAY = 'liqpay', 'LiqPay'
    COD = 'cod', 'Накладений платіж'
    IBAN = 'iban', 'IBAN / ФОП'


class Cart(TimeStampedModel):
    session_key = models.CharField('Session key', max_length=40, db_index=True)
    status = models.CharField(
        'Статус',
        max_length=20,
        choices=CartStatus.choices,
        default=CartStatus.ACTIVE,
    )

    class Meta:
        verbose_name = 'Кошик'
        verbose_name_plural = 'Кошики'
        db_table = 'commerce_cart'
        indexes = [
            models.Index(
                fields=['session_key'],
                name='commerce_cart_active_sess',
                condition=Q(status=CartStatus.ACTIVE),
            ),
        ]

    def __str__(self) -> str:
        return f'Cart {self.pk} ({self.status})'


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Кошик',
    )
    product = models.ForeignKey(
        'catalog.Product',
        on_delete=models.RESTRICT,
        related_name='cart_items',
        verbose_name='Нота',
    )
    qty = models.PositiveIntegerField(
        'Кількість',
        default=1,
        validators=[MinValueValidator(1)],
    )
    unit_price_uah = models.DecimalField(
        'Ціна за од.',
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))],
    )

    class Meta:
        verbose_name = 'Позиція кошика'
        verbose_name_plural = 'Позиції кошика'
        db_table = 'commerce_cart_item'
        constraints = [
            models.UniqueConstraint(
                fields=['cart', 'product'],
                name='commerce_cart_item_uniq',
            ),
        ]

    def __str__(self) -> str:
        return f'{self.product_id} x{self.qty}'


class Order(TimeStampedModel):
    number = models.CharField('Номер', max_length=32, unique=True)
    status = models.CharField(
        'Статус',
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.NEW,
        db_index=True,
    )
    payment_status = models.CharField(
        'Статус оплати',
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.AWAITING,
        db_index=True,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
        verbose_name='Клієнт',
        help_text='Заповнюється, якщо замовлення оформлене залогіненим клієнтом (tables.md §10)',
    )
    customer_name = models.CharField('Імʼя', max_length=255)
    customer_email = models.EmailField('Email', max_length=254, db_index=True)
    customer_phone = models.CharField('Телефон', max_length=32)
    customer_comment = models.TextField('Коментар', blank=True, default='')
    shipping_method = models.CharField(
        'Доставка',
        max_length=20,
        choices=ShippingMethod.choices,
    )
    np_city_ref = models.CharField('НП city ref', max_length=64, blank=True, default='')
    np_city_name = models.CharField('НП місто', max_length=255, blank=True, default='')
    np_warehouse_ref = models.CharField(
        'НП warehouse ref',
        max_length=64,
        blank=True,
        default='',
    )
    np_warehouse_name = models.CharField(
        'НП відділення',
        max_length=255,
        blank=True,
        default='',
    )
    np_area_ref = models.CharField('НП area ref', max_length=64, blank=True, default='')
    subtotal_uah = models.DecimalField('Підсумок', max_digits=12, decimal_places=2)
    shipping_uah = models.DecimalField(
        'Доставка (UAH)',
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
    )
    total_uah = models.DecimalField('Разом', max_digits=12, decimal_places=2)
    payment_provider = models.CharField(
        'Провайдер',
        max_length=20,
        choices=PaymentProvider.choices,
        default=PaymentProvider.LIQPAY,
    )
    payment_external_id = models.CharField(
        'External payment id',
        max_length=128,
        blank=True,
        default='',
        db_index=True,
    )
    paid_at = models.DateTimeField('Оплачено о', null=True, blank=True)
    locale = models.CharField('Мова', max_length=5, default='uk')
    cart = models.ForeignKey(
        Cart,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
        verbose_name='Кошик',
    )

    class Meta:
        verbose_name = 'Замовлення'
        verbose_name_plural = 'Замовлення'
        db_table = 'commerce_order'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
        ]

    def __str__(self) -> str:
        return self.number


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Замовлення',
    )
    product = models.ForeignKey(
        'catalog.Product',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='order_items',
        verbose_name='Нота',
    )
    product_sku = models.CharField('Артикул (snapshot)', max_length=64)
    product_name = models.CharField('Назва (snapshot)', max_length=255)
    qty = models.PositiveIntegerField(
        'Кількість',
        validators=[MinValueValidator(1)],
    )
    unit_price_uah = models.DecimalField(
        'Ціна за од.',
        max_digits=12,
        decimal_places=2,
    )
    line_total_uah = models.DecimalField(
        'Сума рядка',
        max_digits=12,
        decimal_places=2,
    )

    class Meta:
        verbose_name = 'Позиція замовлення'
        verbose_name_plural = 'Позиції замовлення'
        db_table = 'commerce_order_item'

    def __str__(self) -> str:
        return f'{self.product_sku} x{self.qty}'


class OrderStatusLog(CreatedAtModel):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='status_logs',
        verbose_name='Замовлення',
    )
    from_status = models.CharField('Зі статусу', max_length=20, blank=True, default='')
    to_status = models.CharField('У статус', max_length=20)
    note = models.TextField('Примітка', blank=True, default='')
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='order_status_logs',
        verbose_name='Хто змінив',
    )

    class Meta:
        verbose_name = 'Лог статусу замовлення'
        verbose_name_plural = 'Логи статусів замовлень'
        db_table = 'commerce_order_status_log'
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f'{self.order_id}: {self.from_status} → {self.to_status}'

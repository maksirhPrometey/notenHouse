"""Payments — tables.md §3.10 (LiqPay events)."""

from django.db import models

from src.core.models import CreatedAtModel


class PaymentEventType(models.TextChoices):
    CALLBACK = 'callback', 'Callback'
    REDIRECT_RETURN = 'redirect_return', 'Redirect return'


class PaymentProvider(models.TextChoices):
    LIQPAY = 'liqpay', 'LiqPay'
    COD = 'cod', 'Накладений платіж'
    IBAN = 'iban', 'IBAN / ФОП'


class PaymentEvent(CreatedAtModel):
    order = models.ForeignKey(
        'commerce.Order',
        on_delete=models.CASCADE,
        related_name='payment_events',
        verbose_name='Замовлення',
    )
    provider = models.CharField(
        'Провайдер',
        max_length=20,
        choices=PaymentProvider.choices,
        default=PaymentProvider.LIQPAY,
    )
    event_type = models.CharField(
        'Тип події',
        max_length=40,
        choices=PaymentEventType.choices,
    )
    external_id = models.CharField('External id', max_length=128, blank=True, default='')
    idempotency_key = models.CharField('Idempotency key', max_length=128, unique=True)
    payload = models.JSONField('Payload', default=dict)
    processed_ok = models.BooleanField('Оброблено успішно', default=False)

    class Meta:
        verbose_name = 'Подія оплати'
        verbose_name_plural = 'Події оплати'
        db_table = 'payments_event'
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f'{self.provider}:{self.event_type}:{self.idempotency_key}'

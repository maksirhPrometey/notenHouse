"""Notifications — Resend email log (tables.md §3.14)."""

from django.db import models

from src.core.models import CreatedAtModel


class EmailTemplateKey(models.TextChoices):
    ORDER_CREATED_ADMIN = 'order_created_admin', 'Нове замовлення (адмін)'
    LEAD_CREATED_ADMIN = 'lead_created_admin', 'Звернення (адмін)'
    ORDER_STATUS_CUSTOMER = 'order_status_customer', 'Статус замовлення (клієнт)'


class EmailLogStatus(models.TextChoices):
    QUEUED = 'queued', 'В черзі'
    SENT = 'sent', 'Надіслано'
    FAILED = 'failed', 'Помилка'


class EmailLog(CreatedAtModel):
    to_email = models.EmailField('Кому', max_length=254)
    template_key = models.CharField(
        'Шаблон',
        max_length=64,
        choices=EmailTemplateKey.choices,
    )
    related_object_type = models.CharField(
        'Тип обʼєкта',
        max_length=40,
        blank=True,
        default='',
    )
    related_object_id = models.BigIntegerField('ID обʼєкта', null=True, blank=True)
    resend_id = models.CharField('Resend id', max_length=128, blank=True, default='')
    status = models.CharField(
        'Статус',
        max_length=20,
        choices=EmailLogStatus.choices,
        default=EmailLogStatus.QUEUED,
    )
    error_message = models.TextField('Помилка', blank=True, default='')

    class Meta:
        verbose_name = 'Лог email'
        verbose_name_plural = 'Логи email'
        db_table = 'notifications_email_log'
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f'{self.template_key} → {self.to_email} ({self.status})'

import json

from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin

from .models import PaymentEvent


@admin.register(PaymentEvent)
class PaymentEventAdmin(ModelAdmin):
    list_display = (
        'id',
        'order',
        'provider',
        'event_type',
        'processed_ok',
        'created_at',
    )
    list_filter = ('provider', 'event_type', 'processed_ok')
    search_fields = ('idempotency_key', 'external_id', 'order__number')
    readonly_fields = ('created_at', 'payload_pretty')
    fields = (
        'order',
        'provider',
        'event_type',
        'idempotency_key',
        'external_id',
        'processed_ok',
        'created_at',
        'payload_pretty',
    )

    @admin.display(description='Payload')
    def payload_pretty(self, obj):
        if not obj or not obj.payload:
            return '—'
        text = json.dumps(obj.payload, ensure_ascii=False, indent=2)
        return format_html(
            '<pre style="white-space:pre-wrap;max-width:48rem;margin:0;">{}</pre>',
            text,
        )

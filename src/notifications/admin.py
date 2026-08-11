from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import EmailLog


@admin.register(EmailLog)
class EmailLogAdmin(ModelAdmin):
    list_display = (
        'id',
        'template_key',
        'to_email',
        'status',
        'resend_id',
        'created_at',
    )
    list_filter = ('template_key', 'status')
    search_fields = ('to_email', 'resend_id')
    readonly_fields = ('created_at',)

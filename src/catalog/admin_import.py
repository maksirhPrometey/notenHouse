"""Адмінка імпорту товарів (Unfold)."""

from __future__ import annotations

from pathlib import Path

from django.contrib import admin, messages
from django.http import FileResponse, HttpRequest, HttpResponse
from django.urls import path, reverse
from django.utils.html import format_html, format_html_join
from unfold.admin import ModelAdmin

from src.catalog.importing import run_product_import
from src.catalog.models import ProductImportJob

SAMPLES_DIR = Path(__file__).resolve().parent / 'samples'


@admin.register(ProductImportJob)
class ProductImportJobAdmin(ModelAdmin):
    list_display = (
        'id',
        'file',
        'format',
        'status',
        'created_count',
        'updated_count',
        'error_count',
        'created_at',
        'finished_at',
    )
    list_filter = ('status', 'format')
    list_filter_submit = True
    readonly_fields = (
        'status',
        'created_count',
        'updated_count',
        'skipped_count',
        'error_count',
        'report_preview',
        'error_message',
        'started_at',
        'finished_at',
        'created_at',
    )
    fields = (
        'file',
        'format',
        'status',
        'created_count',
        'updated_count',
        'skipped_count',
        'error_count',
        'report_preview',
        'error_message',
        'started_at',
        'finished_at',
        'created_at',
    )

    def has_change_permission(self, request, obj=None):
        return request.user.is_staff

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def report_preview(self, obj: ProductImportJob):
        report = obj.report_json or {}
        samples = report.get('error_samples') or []
        if not report and not obj.error_message:
            return '—'
        parts = [
            format_html(
                'створено: {} · оновлено: {} · пропущено: {} · помилок: {}',
                report.get('created', obj.created_count),
                report.get('updated', obj.updated_count),
                report.get('skipped', obj.skipped_count),
                report.get('errors', obj.error_count),
            ),
        ]
        if samples:
            items = format_html_join(
                '',
                '<li>рядок {}: {} — {}</li>',
                (
                    (s.get('line'), s.get('name') or '', s.get('error') or '')
                    for s in samples[:20]
                ),
            )
            parts.append(format_html('<ul style="margin-top:0.5rem">{}</ul>', items))
        return format_html('{}', format_html_join('', '{}', ((p,) for p in parts)))

    report_preview.short_description = 'Звіт'

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                'sample/<str:kind>/',
                self.admin_site.admin_view(self.download_sample),
                name='catalog_productimportjob_sample',
            ),
        ]
        return custom + urls

    def download_sample(self, request: HttpRequest, kind: str) -> HttpResponse:
        mapping = {
            'csv': ('products_sample.csv', 'text/csv'),
            'yml': ('products_sample.yml', 'application/xml'),
        }
        if kind not in mapping:
            messages.error(request, 'Невідомий зразок')
            return HttpResponse(status=404)
        filename, content_type = mapping[kind]
        path = SAMPLES_DIR / filename
        return FileResponse(path.open('rb'), as_attachment=True, filename=filename, content_type=content_type)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['sample_csv_url'] = reverse('admin:catalog_productimportjob_sample', args=['csv'])
        extra_context['sample_yml_url'] = reverse('admin:catalog_productimportjob_sample', args=['yml'])
        return super().changelist_view(request, extra_context=extra_context)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if change:
            return
        run_product_import(obj)
        obj.refresh_from_db()
        if obj.status == ProductImportJob.Status.DONE:
            messages.success(
                request,
                (
                    f'Імпорт завершено: створено {obj.created_count}, '
                    f'оновлено {obj.updated_count}, помилок {obj.error_count}.'
                ),
            )
        else:
            messages.error(request, f'Імпорт не вдався: {obj.error_message or obj.status}')

    change_list_template = 'admin/catalog/productimportjob/change_list.html'

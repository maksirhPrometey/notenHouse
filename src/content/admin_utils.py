"""Shared Unfold admin mixins."""

from __future__ import annotations

from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.html import format_html

from .admin_site_content_widgets import apply_readable_widget


class SingletonModelAdminMixin:
    singleton_get_or_create = True

    def has_add_permission(self, request):
        model = self.model
        return not model.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        model = self.model
        if self.singleton_get_or_create:
            obj, _ = model.objects.get_or_create(pk=1)
        else:
            obj = model.objects.first()
            if obj is None:
                return super().changelist_view(request, extra_context=extra_context)
        return HttpResponseRedirect(
            reverse(
                f'admin:{model._meta.app_label}_{model._meta.model_name}_change',
                args=[obj.pk],
            )
        )


class ReadableUnfoldFieldsMixin:
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        if formfield is not None and hasattr(formfield, 'widget'):
            apply_readable_widget(formfield.widget)
        return formfield


class ImagePreviewMixin:
    preview_max_height = 80

    def get_image_preview(self, obj, field_name: str = 'image'):
        image = getattr(obj, field_name, None)
        if not image:
            return '—'
        try:
            url = image.url
        except ValueError:
            return '—'
        return format_html(
            '<img src="{}" alt="" style="max-height:{}px;width:auto;border-radius:4px;">',
            url,
            self.preview_max_height,
        )

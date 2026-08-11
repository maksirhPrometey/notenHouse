import json

from django import forms
from django.contrib import admin
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.utils.html import format_html
from unfold.admin import ModelAdmin, TabularInline

from .admin_site_content_proxies import register_site_content_section_admins
from .admin_site_settings_form import SiteSettingsAdminForm
from .admin_utils import (
    ImagePreviewMixin,
    ReadableUnfoldFieldsMixin,
    SingletonModelAdminMixin,
)
from .models import (
    AboutMilestone,
    AboutPageSettings,
    AboutTimelineItem,
    AboutValueCard,
    CartCrossSellItem,
    CartPageSettings,
    CartRecommendedItem,
    CartTrustBadge,
    ContactLead,
    Page,
    SiteSettings,
)
from .theme import ActiveTheme
from .views_theme import THEME_CSS_CACHE_KEY

register_site_content_section_admins()


@admin.register(Page)
class PageAdmin(ReadableUnfoldFieldsMixin, ModelAdmin):
    list_display = ('slug', 'title_uk', 'is_published', 'updated_at')
    list_filter = ('is_published',)
    search_fields = ('slug', 'title_uk', 'title_en')
    prepopulated_fields = {'slug': ('title_uk',)}


@admin.register(ContactLead)
class ContactLeadAdmin(ModelAdmin):
    list_display = ('phone', 'name', 'topic', 'email', 'is_processed', 'created_at')
    list_filter = ('is_processed', 'topic')
    search_fields = ('phone', 'name', 'email', 'message')
    readonly_fields = ('created_at',)


@admin.register(SiteSettings)
class SiteSettingsAdmin(
    ReadableUnfoldFieldsMixin,
    SingletonModelAdminMixin,
    ModelAdmin,
):
    form = SiteSettingsAdminForm
    fieldsets = (
        (None, {
            'fields': ('site_name', 'logo', 'admin_notify_email', 'default_locale'),
        }),
        ('Контакти вітрини', {
            'fields': (
                'phones',
                'phone_display',
                'email',
                'email_response',
                'hours',
                'address',
                'maps_url',
                'viber',
                'telegram',
            ),
        }),
        ('Графік роботи', {
            'fields': (
                'schedule_timezone',
                'schedule_days',
                'schedule_open',
                'schedule_close',
            ),
            'description': 'Робочі дні та години для статусу «відкрито / закрито» на вітрині.',
        }),
        ('Доставка та оплата (вітрина + checkout)', {
            'fields': (
                'shipping_show_pickup',
                'shipping_show_payment_cod',
                'shipping_show_payment_iban',
            ),
            'description': (
                'Увімкнені способи оплати з’являться на /dostavka-i-oplata/ '
                'та в оформленні замовлення.'
            ),
        }),
        ('Реквізити IBAN', {
            'fields': (
                'payment_iban_recipient',
                'payment_iban',
                'payment_iban_edrpou',
                'payment_iban_bank',
                'payment_iban_purpose',
            ),
            'description': 'Показуються клієнту після замовлення з оплатою IBAN.',
        }),
        ('Сповіщення', {
            'fields': ('notify_customer_on_status', 'robots_txt'),
        }),
    )

    def changelist_view(self, request, extra_context=None):
        SiteSettings.load()
        return super().changelist_view(request, extra_context=extra_context)


class CartRecommendedItemInline(TabularInline):
    model = CartRecommendedItem
    extra = 1
    autocomplete_fields = ('product',)
    ordering = ('sort_order', 'id')
    tab = True


class CartCrossSellItemInline(TabularInline):
    model = CartCrossSellItem
    extra = 1
    autocomplete_fields = ('product',)
    ordering = ('sort_order', 'id')
    tab = True


class CartTrustBadgeInline(ImagePreviewMixin, TabularInline):
    model = CartTrustBadge
    extra = 0
    fields = (
        'badge_type',
        'label_uk',
        'label_en',
        'image',
        'image_preview',
        'sort_order',
        'is_active',
    )
    readonly_fields = ('image_preview',)
    ordering = ('sort_order', 'id')
    tab = True

    def image_preview(self, obj):
        return self.get_image_preview(obj)


class AboutMilestoneInline(TabularInline):
    model = AboutMilestone
    extra = 0
    fields = (
        'value_uk',
        'value_en',
        'count_target',
        'count_suffix',
        'label_uk',
        'label_en',
        'sort_order',
        'is_active',
    )
    ordering = ('sort_order', 'id')
    tab = True


class AboutTimelineItemInline(TabularInline):
    model = AboutTimelineItem
    extra = 0
    fields = (
        'year_uk',
        'year_en',
        'title_uk',
        'title_en',
        'text_uk',
        'text_en',
        'sort_order',
        'is_active',
    )
    ordering = ('sort_order', 'id')
    tab = True


class AboutValueCardInline(TabularInline):
    model = AboutValueCard
    extra = 0
    fields = (
        'icon_key',
        'title_uk',
        'title_en',
        'text_uk',
        'text_en',
        'sort_order',
        'is_active',
    )
    ordering = ('sort_order', 'id')
    tab = True


@admin.register(AboutPageSettings)
class AboutPageSettingsAdmin(
    ReadableUnfoldFieldsMixin,
    SingletonModelAdminMixin,
    ModelAdmin,
):
    fieldsets = (
        ('Hero', {
            'fields': (
                'hero_title_uk',
                'hero_title_en',
                'hero_subtitle_uk',
                'hero_subtitle_en',
            ),
        }),
        ('Секції', {
            'fields': (
                'timeline_title_uk',
                'timeline_title_en',
                'timeline_lead_uk',
                'timeline_lead_en',
                'values_title_uk',
                'values_title_en',
            ),
        }),
        ('CTA', {
            'fields': (
                'cta_title_uk',
                'cta_title_en',
                'cta_button_uk',
                'cta_button_en',
            ),
        }),
        ('SEO', {
            'fields': ('meta_description_uk', 'meta_description_en'),
        }),
    )
    inlines = (
        AboutMilestoneInline,
        AboutTimelineItemInline,
        AboutValueCardInline,
    )

    def changelist_view(self, request, extra_context=None):
        AboutPageSettings.load()
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(CartPageSettings)
class CartPageSettingsAdmin(
    ReadableUnfoldFieldsMixin,
    SingletonModelAdminMixin,
    ModelAdmin,
):
    fieldsets = (
        ('Порожній кошик', {
            'fields': (
                'empty_title_uk',
                'empty_title_en',
                'empty_text_uk',
                'empty_text_en',
                'continue_shopping_label_uk',
                'continue_shopping_label_en',
            ),
        }),
        ('Заголовки секцій', {
            'fields': (
                'recommended_title_uk',
                'recommended_title_en',
                'cross_sell_title_uk',
                'cross_sell_title_en',
                'checkout_label_uk',
                'checkout_label_en',
            ),
        }),
    )
    inlines = (
        CartRecommendedItemInline,
        CartCrossSellItemInline,
        CartTrustBadgeInline,
    )

    def changelist_view(self, request, extra_context=None):
        CartPageSettings.load()
        return super().changelist_view(request, extra_context=extra_context)


class ActiveThemeAdminForm(forms.ModelForm):
    reset_to_original = forms.BooleanField(
        label='Повернути до оригіналу',
        required=False,
        help_text=(
            'Зафіксований оригінал (maroon / navy). '
            'Підставить ORIGINAL_DEFAULTS у всі колірні поля.'
        ),
    )
    clear_to_css = forms.BooleanField(
        label='Очистити → colors.css',
        required=False,
        help_text=(
            'Очистить колірні поля (порожньо = брати з поточного colors.css, '
            'зараз fog-проба).'
        ),
    )

    class Meta:
        model = ActiveTheme
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._blank_colors: set[str] = set()
        self.fields['reset_to_original'].widget.attrs.update({
            'data-theme-reset': '1',
            'data-theme-defaults': json.dumps(ActiveTheme.ORIGINAL_DEFAULTS),
        })
        self.fields['clear_to_css'].widget.attrs.update({
            'data-theme-clear': '1',
            'data-theme-css-defaults': json.dumps(ActiveTheme.FIELD_DEFAULTS),
        })
        for name in ActiveTheme.FIELD_DEFAULTS:
            field = self.fields.get(name)
            if field is None:
                continue
            stored = ''
            if self.instance and getattr(self.instance, 'pk', None):
                stored = getattr(self.instance, name, '') or ''
            if not stored:
                self._blank_colors.add(name)
            preview = stored or ActiveTheme.FIELD_DEFAULTS[name]
            field.widget = forms.TextInput(attrs={'type': 'color'})
            if not self.is_bound:
                field.initial = preview
            usage = ActiveTheme.FIELD_USAGE.get(name, '')
            if usage:
                field.label = format_html(
                    '<span class="theme-color-label">'
                    '<span class="theme-color-label__title">{}</span>'
                    '<span class="theme-color-label__desc">{}</span>'
                    '</span>',
                    field.label,
                    usage,
                )
            field.help_text = (
                f'{field.help_text} '
                f'{"Дефолт (colors.css)" if name in self._blank_colors else "Збережено"}'
                f': {preview}.'
            )

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('reset_to_original') and cleaned.get('clear_to_css'):
            raise ValidationError(
                'Оберіть лише одну дію: оригінал (maroon) або очистити → colors.css.'
            )
        return cleaned


@admin.register(ActiveTheme)
class ActiveThemeAdmin(SingletonModelAdminMixin, ModelAdmin):
    form = ActiveThemeAdminForm
    actions = ('reset_to_defaults',)
    compressed_fields = False

    class Media:
        css = {'all': ('css/admin/theme_colors.css',)}
        js = ('js/admin/theme_reset.js',)

    fieldsets = (
        (None, {
            'fields': ('reset_to_original', 'clear_to_css'),
        }),
        ('Фони', {
            'fields': (
                'color_bg', 'color_bg_grey', 'color_header_bg', 'color_header_fg',
                'color_footer_bg', 'color_footer_bg_mid', 'color_footer_bg_end',
                'color_footer_fg',
            ),
        }),
        ('Текст і посилання', {
            'fields': (
                'color_text', 'color_text_muted', 'color_link', 'color_focus',
                'color_brand', 'color_brand_hover',
            ),
        }),
        ('Кнопки', {
            'fields': (
                'color_btn_cta', 'color_btn_cta_hover', 'color_btn_search',
                'color_btn_search_hover', 'color_btn_newsletter',
                'color_btn_newsletter_hover', 'color_btn_ghost',
                'color_btn_ghost_hover_bg',
            ),
        }),
        ('Бейджі / кошик', {
            'fields': (
                'color_badge_cart', 'color_badge_yellow', 'color_badge_maroon',
                'color_badge_blue', 'color_badge_gold',
            ),
        }),
        ('Шрифти', {
            'fields': ('font_heading', 'font_body'),
        }),
    )

    def changelist_view(self, request, extra_context=None):
        ActiveTheme.get_solo()
        return super().changelist_view(request, extra_context=extra_context)

    def save_model(self, request, obj, form, change):
        if form.cleaned_data.get('reset_to_original'):
            for name, default in ActiveTheme.ORIGINAL_DEFAULTS.items():
                setattr(obj, name, default)
        elif form.cleaned_data.get('clear_to_css'):
            for name in ActiveTheme.FIELD_DEFAULTS:
                setattr(obj, name, '')
        else:
            blank_colors = getattr(form, '_blank_colors', set())
            for name, default in ActiveTheme.FIELD_DEFAULTS.items():
                posted = (getattr(obj, name, '') or '').strip()
                if name in blank_colors and posted.upper() == default.upper():
                    setattr(obj, name, '')
                else:
                    setattr(obj, name, posted)
        super().save_model(request, obj, form, change)
        cache.delete(THEME_CSS_CACHE_KEY)

    @admin.action(description='Скинути всі кольори/шрифти до colors.css (порожньо)')
    def reset_to_defaults(self, request, queryset):
        theme = ActiveTheme.get_solo()
        for field in ActiveTheme.TOKEN_MAP:
            setattr(theme, field, '')
        theme.save()
        cache.delete(THEME_CSS_CACHE_KEY)
        self.message_user(request, 'Тему скинуто до дефолтів colors.css (порожні поля).')

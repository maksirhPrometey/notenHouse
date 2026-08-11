from django import forms
from django.contrib import admin
from django.core.files.uploadedfile import UploadedFile
from unfold.admin import ModelAdmin, TabularInline
from unfold.widgets import UnfoldAdminFileFieldWidget

from src.content.admin_utils import ImagePreviewMixin

from .models import (
    PRODUCT_BADGE_TEXT_PRESETS,
    Composer,
    Format,
    Genre,
    Instrument,
    Level,
    Product,
    ProductFile,
    ProductGenre,
    ProductImage,
    ProductInstrument,
)

from . import admin_import  # noqa: F401 — реєстрація ProductImportJobAdmin

BADGE_SELECT_CHOICES = [
    ('', '— без бейджа —'),
    *((preset, preset) for preset in PRODUCT_BADGE_TEXT_PRESETS),
]

COVER_HELP = (
    'Головне фото товару. Рекомендований розмір: 800×1200 px. '
    'Значно більші фото автоматично обрізаються та стискаються. JPG/PNG → WebP.'
)


def _cover_image_widget() -> UnfoldAdminFileFieldWidget:
    widget = UnfoldAdminFileFieldWidget(attrs={'accept': 'image/*'})
    widget.clear_checkbox_label = 'Очистити'
    return widget


class ProductAdminForm(forms.ModelForm):
    badge_select = forms.ChoiceField(
        label='Бейдж на обкладинці',
        choices=BADGE_SELECT_CHOICES,
        required=False,
        help_text='Оберіть готовий варіант або залиште порожнім.',
    )
    badge_custom = forms.CharField(
        label='Свій текст бейджа',
        max_length=32,
        required=False,
        help_text='Якщо заповнено — має пріоритет над вибіркою.',
    )
    cover_image = forms.ImageField(
        label='Обкладинка',
        required=False,
        help_text=COVER_HELP,
        widget=_cover_image_widget(),
    )

    class Meta:
        model = Product
        exclude = ('badge_text',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        current = (self.instance.badge_text or '').strip() if self.instance.pk else ''
        presets = set(PRODUCT_BADGE_TEXT_PRESETS)
        choices = list(BADGE_SELECT_CHOICES)
        if current and current not in presets:
            choices.append((current, f'{current} (поточний)'))
        self.fields['badge_select'].choices = choices
        self.fields['badge_select'].initial = current
        self.fields['badge_custom'].initial = ''

        if self.instance.pk:
            main = self.instance.images.filter(is_main=True).first()
            if main and main.image:
                self.fields['cover_image'].initial = main.image

    def save(self, commit=True):
        instance = super().save(commit=False)
        custom = (self.cleaned_data.get('badge_custom') or '').strip()
        selected = (self.cleaned_data.get('badge_select') or '').strip()
        instance.badge_text = custom or selected
        if commit:
            instance.save()
            self.save_m2m()
        return instance

    def save_cover_image(self, product: Product) -> None:
        cover = self.cleaned_data.get('cover_image')
        if cover is False:
            for img in product.images.filter(is_main=True):
                if img.image:
                    img.image.delete(save=False)
                img.delete()
            return
        if not isinstance(cover, UploadedFile):
            return

        main = product.images.filter(is_main=True).first()
        if main is None:
            product.images.update(is_main=False)
            ProductImage.objects.create(product=product, image=cover, is_main=True)
            return

        main.image = cover
        main.is_main = True
        main.save()


class ProductImageInline(ImagePreviewMixin, TabularInline):
    model = ProductImage
    extra = 1
    verbose_name = 'Фото'
    verbose_name_plural = 'Галерея'
    fields = (
        'image',
        'image_preview',
        'alt_uk',
        'alt_en',
        'is_main',
        'sort_order',
    )
    readonly_fields = ('image_preview',)
    ordering_field = 'sort_order'
    hide_ordering_field = True

    def image_preview(self, obj):
        return self.get_image_preview(obj)

    image_preview.short_description = 'Превʼю'


class ProductFileInline(TabularInline):
    model = ProductFile
    extra = 0
    tab = True


class ProductInstrumentInline(TabularInline):
    model = ProductInstrument
    extra = 0
    tab = True


class ProductGenreInline(TabularInline):
    model = ProductGenre
    extra = 0
    tab = True


class TaxonomyAdmin(ModelAdmin):
    list_display = ('name_uk', 'name_en', 'slug', 'is_active', 'sort_order')
    list_filter = ('is_active',)
    search_fields = ('name_uk', 'name_en', 'slug')
    prepopulated_fields = {'slug': ('name_uk',)}
    ordering_field = 'sort_order'
    list_filter_submit = True


@admin.register(Composer)
class ComposerAdmin(TaxonomyAdmin):
    pass


@admin.register(Instrument)
class InstrumentAdmin(TaxonomyAdmin):
    pass


@admin.register(Genre)
class GenreAdmin(TaxonomyAdmin):
    pass


@admin.register(Level)
class LevelAdmin(TaxonomyAdmin):
    pass


@admin.register(Format)
class FormatAdmin(TaxonomyAdmin):
    pass


@admin.register(Product)
class ProductAdmin(ModelAdmin):
    form = ProductAdminForm
    list_display = (
        'sku',
        'barcode',
        'name_uk',
        'composer',
        'price_uah',
        'stock_qty',
        'is_published',
        'is_popular',
        'is_new',
        'badge_text',
        'badge_tone',
    )
    list_editable = ('badge_tone', 'is_popular', 'is_new')
    list_filter = ('is_published', 'is_popular', 'is_new', 'badge_tone', 'level', 'format')
    list_filter_submit = True
    search_fields = ('sku', 'barcode', 'name_uk', 'name_en', 'badge_text')
    prepopulated_fields = {'slug': ('name_uk',)}
    inlines = [
        ProductImageInline,
        ProductInstrumentInline,
        ProductGenreInline,
        ProductFileInline,
    ]
    autocomplete_fields = ('composer', 'level', 'format')
    fieldsets = (
        (None, {
            'fields': (
                'sku', 'barcode', 'slug', 'name_uk', 'name_en', 'cover_image',
                'composer', 'level', 'format',
                'description_uk', 'description_en', 'price_uah', 'stock_qty',
            ),
        }),
        ('Вітрина', {
            'fields': (
                'is_published', 'is_popular', 'is_new',
                'badge_select', 'badge_custom', 'badge_tone', 'published_at',
            ),
        }),
        ('SEO', {
            'classes': ('collapse',),
            'fields': ('seo_title', 'seo_description'),
        }),
    )

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        form.save_cover_image(form.instance)

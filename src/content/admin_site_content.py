"""CMS section form + change view (SiteBlock proxy pages)."""

from __future__ import annotations

from django import forms
from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse
from unfold.widgets import UnfoldAdminFileFieldWidget, UnfoldBooleanWidget

from .admin_hero_slides import build_hero_slide_formset
from .admin_site_content_widgets import CmsAdminTextareaWidget, CmsAdminTextInputWidget
from .block_defaults import COLOR_KEYS, INLINE_KEYS, MULTILINE_KEYS, is_visibility_key
from .image_specs import HERO, SITE_BLOCK_SPECS
from .image_webp import convert_upload_to_webp
from .models import SiteSettings
from .site_block_models import SiteBlock
from .site_blocks import invalidate_site_blocks_cache, load_section_blocks
from .site_content_registry import ContentSection, get_section, iter_section_block_keys

HERO_TEXT_COLOR_HELP = (
    'Колір бренду, заголовка та ліду в hero. '
    'Hex #RRGGBB. Підлаштуйте під світле або темне фото.'
)

_HEX_COLOR_RE = r'^#[0-9A-Fa-f]{6}$'


def _field_name(page: str, key: str, suffix: str) -> str:
    return f'block__{page}__{key}__{suffix}'


def _image_widget() -> UnfoldAdminFileFieldWidget:
    widget = UnfoldAdminFileFieldWidget(attrs={'accept': 'image/*'})
    widget.clear_checkbox_label = 'Очистити'
    return widget


class SitePageContentForm(forms.Form):
    def __init__(self, section: ContentSection, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.section = section
        keys = [key for _, key in iter_section_block_keys(section)]
        self.blocks = load_section_blocks(section.page_slug, keys)

        if section.visibility_key:
            block = self.blocks[section.visibility_key]
            self.fields['section_visible'] = forms.BooleanField(
                label='Показувати секцію на сайті',
                required=False,
                initial=block.text_uk not in {'0', 'false', 'False', ''},
                widget=UnfoldBooleanWidget(),
            )

        for page, key in section.blocks:
            block = self.blocks[key]
            if is_visibility_key(key):
                self.fields[_field_name(page, key, 'visible')] = forms.BooleanField(
                    label=block.label or key,
                    required=False,
                    initial=block.text_uk not in {'0', 'false', 'False', ''},
                    widget=UnfoldBooleanWidget(),
                )
                continue

            if block.content_type == SiteBlock.ContentType.IMAGE:
                spec = SITE_BLOCK_SPECS.get((page, key), HERO)
                field_kwargs: dict = {
                    'label': block.label or key,
                    'required': False,
                    'widget': _image_widget(),
                    'help_text': spec.help_text,
                }
                if block.image:
                    field_kwargs['initial'] = block.image
                self.fields[_field_name(page, key, 'image')] = forms.ImageField(
                    **field_kwargs,
                )
                continue

            if block.content_type == SiteBlock.ContentType.URL:
                self.fields[_field_name(page, key, 'link_url')] = forms.CharField(
                    label=f'{block.label} — URL',
                    required=False,
                    initial=block.link_url,
                    widget=CmsAdminTextInputWidget(),
                )
                self.fields[_field_name(page, key, 'link_label_uk')] = forms.CharField(
                    label=f'{block.label} — текст UK',
                    required=False,
                    initial=block.link_label_uk,
                    widget=CmsAdminTextInputWidget(),
                )
                self.fields[_field_name(page, key, 'link_label_en')] = forms.CharField(
                    label=f'{block.label} — текст EN',
                    required=False,
                    initial=block.link_label_en,
                    widget=CmsAdminTextInputWidget(),
                )
                continue

            if key in COLOR_KEYS:
                initial = (block.text_uk or '#ffffff').strip() or '#ffffff'
                if len(initial) != 7 or not initial.startswith('#'):
                    initial = '#ffffff'
                color_kwargs: dict = {
                    'label': block.label or key,
                    'required': True,
                    'initial': initial,
                    'widget': forms.TextInput(attrs={'type': 'color'}),
                }
                if page == 'home' and key == 'hero_text_color':
                    color_kwargs['help_text'] = HERO_TEXT_COLOR_HELP
                self.fields[_field_name(page, key, 'color')] = forms.RegexField(
                    regex=_HEX_COLOR_RE,
                    error_messages={'invalid': 'Колір має бути у форматі #RRGGBB.'},
                    **color_kwargs,
                )
                continue

            # TEXT (default)
            if key in INLINE_KEYS:
                uk_widget = CmsAdminTextInputWidget()
                en_widget = CmsAdminTextInputWidget()
            elif key in MULTILINE_KEYS:
                uk_widget = CmsAdminTextareaWidget(attrs={'rows': 4})
                en_widget = CmsAdminTextareaWidget(attrs={'rows': 4})
            else:
                uk_widget = CmsAdminTextareaWidget(attrs={'rows': 2})
                en_widget = CmsAdminTextareaWidget(attrs={'rows': 2})

            self.fields[_field_name(page, key, 'text_uk')] = forms.CharField(
                label=f'{block.label} (UK)',
                required=False,
                initial=block.text_uk,
                widget=uk_widget,
            )
            self.fields[_field_name(page, key, 'text_en')] = forms.CharField(
                label=f'{block.label} (EN)',
                required=False,
                initial=block.text_en,
                widget=en_widget,
            )

    def save(self) -> None:
        section = self.section
        cleaned = self.cleaned_data

        if section.visibility_key:
            block = self.blocks[section.visibility_key]
            block.text_uk = '1' if cleaned.get('section_visible') else '0'
            block.text_en = block.text_uk
            block.save(update_fields=['text_uk', 'text_en'])

        for page, key in section.blocks:
            block = self.blocks[key]
            if is_visibility_key(key):
                visible = cleaned.get(_field_name(page, key, 'visible'))
                block.text_uk = '1' if visible else '0'
                block.text_en = block.text_uk
                block.save(update_fields=['text_uk', 'text_en'])
                continue

            if block.content_type == SiteBlock.ContentType.IMAGE:
                image = cleaned.get(_field_name(page, key, 'image'))
                if image is False:
                    if block.image:
                        block.image.delete(save=False)
                    block.image = None
                    block.save(update_fields=['image'])
                elif image:
                    spec = SITE_BLOCK_SPECS.get((page, key), HERO)
                    block.image = convert_upload_to_webp(image, spec=spec)
                    block.save(update_fields=['image'])
                continue

            if block.content_type == SiteBlock.ContentType.URL:
                block.link_url = cleaned.get(_field_name(page, key, 'link_url'), '') or ''
                block.link_label_uk = cleaned.get(
                    _field_name(page, key, 'link_label_uk'), ''
                ) or ''
                block.link_label_en = cleaned.get(
                    _field_name(page, key, 'link_label_en'), ''
                ) or ''
                block.save(update_fields=['link_url', 'link_label_uk', 'link_label_en'])
                continue

            if key in COLOR_KEYS:
                color = (cleaned.get(_field_name(page, key, 'color'), '') or '#ffffff').strip()
                block.text_uk = color
                block.text_en = color
                block.save(update_fields=['text_uk', 'text_en'])
                continue

            block.text_uk = cleaned.get(_field_name(page, key, 'text_uk'), '') or ''
            block.text_en = cleaned.get(_field_name(page, key, 'text_en'), '') or ''
            block.save(update_fields=['text_uk', 'text_en'])

        invalidate_site_blocks_cache()


def site_content_section_view(request, page_slug: str, section_slug: str, model_admin=None):
    section = get_section(page_slug, section_slug)
    if section is None:
        messages.error(request, 'Секцію не знайдено.')
        return redirect('admin:index')

    SiteSettings.load()
    hero_formset = None

    if request.method == 'POST':
        form = SitePageContentForm(section, data=request.POST, files=request.FILES)
        if section.has_hero_slides:
            hero_formset = build_hero_slide_formset(data=request.POST, files=request.FILES)
        forms_ok = form.is_valid() and (hero_formset is None or hero_formset.is_valid())
        if forms_ok:
            form.save()
            if hero_formset is not None:
                hero_formset.save()
            messages.success(request, 'Збережено.')
            return redirect(request.path)
    else:
        form = SitePageContentForm(section)
        if section.has_hero_slides:
            hero_formset = build_hero_slide_formset()

    context = {
        **(model_admin.admin_site.each_context(request) if model_admin else {}),
        'title': section.title,
        'section': section,
        'form': form,
        'hero_formset': hero_formset,
        'opts': model_admin.model._meta if model_admin else None,
        'has_view_permission': True,
        'has_change_permission': True,
        'has_add_permission': False,
        'has_delete_permission': False,
        'preview_url': section.preview_url,
    }
    return render(request, 'admin/content/site_content_page.html', context)


class SiteContentSectionAdminMixin:
    page_slug: str = ''
    section_slug: str = ''

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        SiteSettings.load()
        return redirect(
            reverse(
                f'admin:{self.model._meta.app_label}_{self.model._meta.model_name}_change',
                args=[1],
            )
        )

    def change_view(self, request, object_id, form_url='', extra_context=None):
        return site_content_section_view(
            request,
            self.page_slug,
            self.section_slug,
            model_admin=self,
        )

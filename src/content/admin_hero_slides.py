"""HeroSlide ModelFormSet for CMS hero section."""

from __future__ import annotations

from django import forms
from django.forms import BaseModelFormSet, modelformset_factory

from .hero_slides import ensure_default_hero_slides
from .site_block_models import HeroSlide


class HeroSlideForm(forms.ModelForm):
    class Meta:
        model = HeroSlide
        fields = ('image', 'alt_uk', 'alt_en', 'sort_order', 'is_active')
        widgets = {
            'sort_order': forms.HiddenInput(),
            'alt_uk': forms.TextInput(attrs={'placeholder': 'Alt UK'}),
            'alt_en': forms.TextInput(attrs={'placeholder': 'Alt EN'}),
        }

    def __init__(self, *args, **kwargs):
        from .image_specs import HERO

        super().__init__(*args, **kwargs)
        if 'image' in self.fields:
            self.fields['image'].help_text = HERO.help_text

    def clean(self):
        cleaned = super().clean()
        if self.cleaned_data.get('DELETE'):
            return cleaned
        image = cleaned.get('image')
        alt_uk = (cleaned.get('alt_uk') or '').strip()
        alt_en = (cleaned.get('alt_en') or '').strip()
        if (alt_uk or alt_en) and not image and not (self.instance and self.instance.image):
            raise forms.ValidationError('Alt без зображення не зберігається.')
        return cleaned


class HeroSlideBaseFormSet(BaseModelFormSet):
    def clean(self):
        super().clean()
        order = 0
        for form in self.forms:
            if not hasattr(form, 'cleaned_data') or form.cleaned_data.get('DELETE'):
                continue
            image = form.cleaned_data.get('image')
            has_existing = form.instance and form.instance.pk and form.instance.image
            if not image and not has_existing:
                continue
            form.cleaned_data['sort_order'] = order
            form.instance.sort_order = order
            order += 1


def build_hero_slide_formset(data=None, files=None):
    ensure_default_hero_slides()
    FormSet = modelformset_factory(
        HeroSlide,
        form=HeroSlideForm,
        formset=HeroSlideBaseFormSet,
        extra=1,
        can_delete=True,
    )
    qs = HeroSlide.objects.order_by('sort_order', 'pk')
    return FormSet(data=data, files=files, queryset=qs, prefix='hero_slides')

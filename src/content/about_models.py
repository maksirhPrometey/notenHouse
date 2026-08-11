"""About page settings — singleton + editable milestones / timeline / values."""

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from src.core.i18n_fields import pick_locale_field
from src.core.models import UpdatedAtModel

from .about_defaults import (
    DEFAULT_CTA_BUTTON,
    DEFAULT_CTA_BUTTON_EN,
    DEFAULT_CTA_TITLE,
    DEFAULT_CTA_TITLE_EN,
    DEFAULT_HERO_SUBTITLE,
    DEFAULT_HERO_SUBTITLE_EN,
    DEFAULT_HERO_TITLE,
    DEFAULT_HERO_TITLE_EN,
    DEFAULT_META_DESCRIPTION,
    DEFAULT_META_DESCRIPTION_EN,
    DEFAULT_MILESTONES,
    DEFAULT_TIMELINE,
    DEFAULT_TIMELINE_LEAD,
    DEFAULT_TIMELINE_LEAD_EN,
    DEFAULT_TIMELINE_TITLE,
    DEFAULT_TIMELINE_TITLE_EN,
    DEFAULT_VALUES,
    DEFAULT_VALUES_TITLE,
    DEFAULT_VALUES_TITLE_EN,
)


class AboutValueIcon(models.TextChoices):
    BOOK = 'book', 'Нотна книга'
    PACKAGE = 'package', 'Пакування'
    EXPERTS = 'experts', 'Експерти'


class AboutPageSettings(UpdatedAtModel):
    """Singleton: контент сторінки /pro-nas/."""

    hero_title_uk = models.CharField(
        'Hero — заголовок (UK)',
        max_length=255,
        default=DEFAULT_HERO_TITLE,
    )
    hero_title_en = models.CharField(
        'Hero — заголовок (EN)',
        max_length=255,
        blank=True,
        default=DEFAULT_HERO_TITLE_EN,
    )
    hero_subtitle_uk = models.TextField(
        'Hero — підзаголовок (UK)',
        default=DEFAULT_HERO_SUBTITLE,
    )
    hero_subtitle_en = models.TextField(
        'Hero — підзаголовок (EN)',
        blank=True,
        default=DEFAULT_HERO_SUBTITLE_EN,
    )
    timeline_title_uk = models.CharField(
        'Timeline — заголовок (UK)',
        max_length=255,
        default=DEFAULT_TIMELINE_TITLE,
    )
    timeline_title_en = models.CharField(
        'Timeline — заголовок (EN)',
        max_length=255,
        blank=True,
        default=DEFAULT_TIMELINE_TITLE_EN,
    )
    timeline_lead_uk = models.TextField(
        'Timeline — лід (UK)',
        blank=True,
        default=DEFAULT_TIMELINE_LEAD,
    )
    timeline_lead_en = models.TextField(
        'Timeline — лід (EN)',
        blank=True,
        default=DEFAULT_TIMELINE_LEAD_EN,
    )
    values_title_uk = models.CharField(
        'Цінності — заголовок (UK)',
        max_length=255,
        default=DEFAULT_VALUES_TITLE,
    )
    values_title_en = models.CharField(
        'Цінності — заголовок (EN)',
        max_length=255,
        blank=True,
        default=DEFAULT_VALUES_TITLE_EN,
    )
    cta_title_uk = models.CharField(
        'CTA — заголовок (UK)',
        max_length=255,
        default=DEFAULT_CTA_TITLE,
    )
    cta_title_en = models.CharField(
        'CTA — заголовок (EN)',
        max_length=255,
        blank=True,
        default=DEFAULT_CTA_TITLE_EN,
    )
    cta_button_uk = models.CharField(
        'CTA — кнопка (UK)',
        max_length=120,
        default=DEFAULT_CTA_BUTTON,
    )
    cta_button_en = models.CharField(
        'CTA — кнопка (EN)',
        max_length=120,
        blank=True,
        default=DEFAULT_CTA_BUTTON_EN,
    )
    meta_description_uk = models.CharField(
        'Meta description (UK)',
        max_length=160,
        blank=True,
        default=DEFAULT_META_DESCRIPTION,
    )
    meta_description_en = models.CharField(
        'Meta description (EN)',
        max_length=160,
        blank=True,
        default=DEFAULT_META_DESCRIPTION_EN,
    )

    class Meta:
        verbose_name = 'Сторінка «Про нас»'
        verbose_name_plural = 'Сторінка «Про нас»'
        db_table = 'content_about_page_settings'
        constraints = [
            models.CheckConstraint(
                condition=Q(pk=1),
                name='content_about_page_settings_singleton_id_1',
            ),
        ]

    def __str__(self) -> str:
        return 'Сторінка «Про нас»'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError('Singleton AboutPageSettings не можна видаляти.')

    def hero_title_for(self, locale: str = 'uk') -> str:
        return pick_locale_field(self, 'hero_title', locale)

    def hero_subtitle_for(self, locale: str = 'uk') -> str:
        return pick_locale_field(self, 'hero_subtitle', locale)

    def timeline_title_for(self, locale: str = 'uk') -> str:
        return pick_locale_field(self, 'timeline_title', locale)

    def timeline_lead_for(self, locale: str = 'uk') -> str:
        return pick_locale_field(self, 'timeline_lead', locale)

    def values_title_for(self, locale: str = 'uk') -> str:
        return pick_locale_field(self, 'values_title', locale)

    def cta_title_for(self, locale: str = 'uk') -> str:
        return pick_locale_field(self, 'cta_title', locale)

    def cta_button_for(self, locale: str = 'uk') -> str:
        return pick_locale_field(self, 'cta_button', locale)

    def meta_description_for(self, locale: str = 'uk') -> str:
        return pick_locale_field(self, 'meta_description', locale)

    @classmethod
    def load(cls) -> 'AboutPageSettings':
        obj, created = cls.objects.get_or_create(pk=1)
        if created:
            obj.ensure_defaults()
        return obj

    def ensure_defaults(self) -> None:
        if not self.milestones.exists():
            AboutMilestone.objects.bulk_create(
                [
                    AboutMilestone(
                        settings=self,
                        value_uk=item['value_uk'],
                        value_en=item.get('value_en', ''),
                        count_target=item['count_target'],
                        count_suffix=item['count_suffix'],
                        label_uk=item['label_uk'],
                        label_en=item.get('label_en', ''),
                        sort_order=item['sort_order'],
                        is_active=True,
                    )
                    for item in DEFAULT_MILESTONES
                ]
            )
        if not self.timeline_items.exists():
            AboutTimelineItem.objects.bulk_create(
                [
                    AboutTimelineItem(
                        settings=self,
                        year_uk=item['year_uk'],
                        year_en=item.get('year_en', ''),
                        title_uk=item['title_uk'],
                        title_en=item.get('title_en', ''),
                        text_uk=item['text_uk'],
                        text_en=item.get('text_en', ''),
                        sort_order=item['sort_order'],
                        is_active=True,
                    )
                    for item in DEFAULT_TIMELINE
                ]
            )
        if not self.value_cards.exists():
            AboutValueCard.objects.bulk_create(
                [
                    AboutValueCard(
                        settings=self,
                        icon_key=item['icon_key'],
                        title_uk=item['title_uk'],
                        title_en=item.get('title_en', ''),
                        text_uk=item['text_uk'],
                        text_en=item.get('text_en', ''),
                        sort_order=item['sort_order'],
                        is_active=True,
                    )
                    for item in DEFAULT_VALUES
                ]
            )

    def active_milestones(self):
        self.ensure_defaults()
        return self.milestones.filter(is_active=True).order_by('sort_order', 'id')

    def active_timeline(self):
        self.ensure_defaults()
        return self.timeline_items.filter(is_active=True).order_by('sort_order', 'id')

    def active_values(self):
        self.ensure_defaults()
        return self.value_cards.filter(is_active=True).order_by('sort_order', 'id')


class AboutMilestone(models.Model):
    settings = models.ForeignKey(
        AboutPageSettings,
        on_delete=models.CASCADE,
        related_name='milestones',
    )
    value_uk = models.CharField(
        'Значення (UK)',
        max_length=64,
        help_text='Показується, якщо лічильник вимкнено або count_target порожній.',
    )
    value_en = models.CharField('Значення (EN)', max_length=64, blank=True, default='')
    count_target = models.PositiveIntegerField(
        'Ціль лічильника',
        null=True,
        blank=True,
        help_text='Якщо задано — анімація від 0. Порожньо = статичний текст (напр. Instant).',
    )
    count_suffix = models.CharField(
        'Суфікс лічильника',
        max_length=8,
        blank=True,
        default='',
        help_text='Напр. +, %',
    )
    label_uk = models.CharField('Підпис (UK)', max_length=255)
    label_en = models.CharField('Підпис (EN)', max_length=255, blank=True, default='')
    sort_order = models.PositiveIntegerField('Порядок', default=0)
    is_active = models.BooleanField('Активний', default=True)

    class Meta:
        verbose_name = 'Milestone'
        verbose_name_plural = 'Milestones'
        db_table = 'content_about_milestone'
        ordering = ['sort_order', 'id']

    def __str__(self) -> str:
        return self.value_uk

    def value_for(self, locale: str = 'uk') -> str:
        return pick_locale_field(self, 'value', locale)

    def label_for(self, locale: str = 'uk') -> str:
        return pick_locale_field(self, 'label', locale)


class AboutTimelineItem(models.Model):
    settings = models.ForeignKey(
        AboutPageSettings,
        on_delete=models.CASCADE,
        related_name='timeline_items',
    )
    year_uk = models.CharField('Рік / мітка (UK)', max_length=64)
    year_en = models.CharField('Рік / мітка (EN)', max_length=64, blank=True, default='')
    title_uk = models.CharField('Заголовок (UK)', max_length=255)
    title_en = models.CharField('Заголовок (EN)', max_length=255, blank=True, default='')
    text_uk = models.TextField('Опис (UK)')
    text_en = models.TextField('Опис (EN)', blank=True, default='')
    sort_order = models.PositiveIntegerField('Порядок', default=0)
    is_active = models.BooleanField('Активний', default=True)

    class Meta:
        verbose_name = 'Timeline-пункт'
        verbose_name_plural = 'Timeline'
        db_table = 'content_about_timeline_item'
        ordering = ['sort_order', 'id']

    def __str__(self) -> str:
        return f'{self.year_uk} — {self.title_uk}'

    def year_for(self, locale: str = 'uk') -> str:
        return pick_locale_field(self, 'year', locale)

    def title_for(self, locale: str = 'uk') -> str:
        return pick_locale_field(self, 'title', locale)

    def text_for(self, locale: str = 'uk') -> str:
        return pick_locale_field(self, 'text', locale)


class AboutValueCard(models.Model):
    settings = models.ForeignKey(
        AboutPageSettings,
        on_delete=models.CASCADE,
        related_name='value_cards',
    )
    icon_key = models.CharField(
        'Іконка',
        max_length=20,
        choices=AboutValueIcon.choices,
        default=AboutValueIcon.BOOK,
    )
    title_uk = models.CharField('Заголовок (UK)', max_length=255)
    title_en = models.CharField('Заголовок (EN)', max_length=255, blank=True, default='')
    text_uk = models.TextField('Текст (UK)')
    text_en = models.TextField('Текст (EN)', blank=True, default='')
    sort_order = models.PositiveIntegerField('Порядок', default=0)
    is_active = models.BooleanField('Активний', default=True)

    class Meta:
        verbose_name = 'Картка цінності'
        verbose_name_plural = 'Картки цінностей'
        db_table = 'content_about_value_card'
        ordering = ['sort_order', 'id']

    def __str__(self) -> str:
        return self.title_uk

    def title_for(self, locale: str = 'uk') -> str:
        return pick_locale_field(self, 'title', locale)

    def text_for(self, locale: str = 'uk') -> str:
        return pick_locale_field(self, 'text', locale)

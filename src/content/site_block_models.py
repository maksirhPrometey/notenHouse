"""CMS SiteBlock + HeroSlide (admin_cms_blocks_skill)."""

from django.db import models


class SiteBlock(models.Model):
    class Page(models.TextChoices):
        HOME = 'home', 'Головна'
        SITE = 'site', 'Сайт'
        SHIPPING = 'shipping', 'Доставка'
        CONTACTS = 'contacts', 'Контакти'
        CATALOG = 'catalog', 'Каталог'
        SEARCH = 'search', 'Пошук'
        CART = 'cart', 'Кошик'
        CHECKOUT = 'checkout', 'Checkout'
        THANK_YOU = 'thank_you', 'Дякуємо'
        CABINET = 'cabinet', 'Кабінет'

    class ContentType(models.TextChoices):
        TEXT = 'text', 'Текст'
        IMAGE = 'image', 'Фото'
        URL = 'url', 'Посилання'
        VIDEO = 'video', 'Відео'

    page = models.CharField('Сторінка', max_length=32, choices=Page.choices)
    key = models.CharField('Ключ', max_length=64)
    label = models.CharField('Мітка', max_length=128)
    content_type = models.CharField(
        'Тип',
        max_length=16,
        choices=ContentType.choices,
        default=ContentType.TEXT,
    )
    text_uk = models.TextField('Текст (UK)', blank=True, default='')
    text_en = models.TextField('Текст (EN)', blank=True, default='')
    image = models.ImageField(
        'Зображення',
        upload_to='content/blocks/',
        max_length=512,
        blank=True,
        null=True,
        help_text=(
            'Рекомендований розмір залежить від блоку (див. підказку в формі). '
            'Значно більші фото автоматично обробляються. JPG/PNG → WebP.'
        ),
    )
    link_url = models.CharField('URL', max_length=512, blank=True, default='')
    link_label_uk = models.CharField('Текст кнопки (UK)', max_length=128, blank=True, default='')
    link_label_en = models.CharField('Текст кнопки (EN)', max_length=128, blank=True, default='')
    video_embed_url = models.URLField('Embed URL', blank=True, default='')
    video_file = models.FileField(
        'Відеофайл',
        upload_to='content/blocks/video/',
        max_length=512,
        blank=True,
        null=True,
    )
    sort_order = models.PositiveSmallIntegerField('Порядок', default=0)
    is_active = models.BooleanField('Активний', default=True)

    class Meta:
        verbose_name = 'CMS-блок'
        verbose_name_plural = 'CMS-блоки'
        db_table = 'content_site_block'
        ordering = ['page', 'sort_order', 'key']
        constraints = [
            models.UniqueConstraint(
                fields=['page', 'key'],
                name='content_site_block_page_key_uniq',
            ),
        ]

    def __str__(self) -> str:
        return f'{self.page}.{self.key}'

    @property
    def cache_key(self) -> str:
        return f'{self.page}.{self.key}'

    def text_for(self, locale: str = 'uk') -> str:
        if locale == 'en' and self.text_en:
            return self.text_en
        return self.text_uk

    def link_label_for(self, locale: str = 'uk') -> str:
        if locale == 'en' and self.link_label_en:
            return self.link_label_en
        return self.link_label_uk


class HeroSlide(models.Model):
    image = models.ImageField(
        'Зображення',
        upload_to='content/hero/',
        max_length=512,
        help_text=(
            'Рекомендований розмір: 1920×1080 px. '
            'Значно більші фото автоматично обрізаються та стискаються. '
            'JPG/PNG → WebP.'
        ),
    )
    alt_uk = models.CharField('Alt (UK)', max_length=200, blank=True, default='')
    alt_en = models.CharField('Alt (EN)', max_length=200, blank=True, default='')
    sort_order = models.PositiveSmallIntegerField('Порядок', default=0)
    is_active = models.BooleanField('Активний', default=True)

    class Meta:
        verbose_name = 'Hero-слайд'
        verbose_name_plural = 'Hero-слайди'
        db_table = 'content_hero_slide'
        ordering = ['sort_order', 'pk']

    def __str__(self) -> str:
        return f'HeroSlide #{self.pk}'

    def alt_for(self, locale: str = 'uk') -> str:
        if locale == 'en' and self.alt_en:
            return self.alt_en
        return self.alt_uk

    def save(self, *args, **kwargs):
        from .image_specs import HERO
        from .image_webp import maybe_process_field

        maybe_process_field(self, 'image', HERO)
        super().save(*args, **kwargs)

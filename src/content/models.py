"""Content — pages, leads, site settings (tables.md §3.11–3.13)."""

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from src.core.i18n_fields import pick_locale_field
from src.core.models import CreatedAtModel, SeoFieldsMixin, TimeStampedModel, UpdatedAtModel

from .about_models import (  # noqa: F401 — discovery + re-export
    AboutMilestone,
    AboutPageSettings,
    AboutTimelineItem,
    AboutValueCard,
    AboutValueIcon,
)
from .site_block_models import HeroSlide, SiteBlock  # noqa: F401 — discovery + re-export
from .theme import ActiveTheme  # noqa: F401 — discovery + re-export


class Page(SeoFieldsMixin, TimeStampedModel):
    slug = models.SlugField('Slug', max_length=160, unique=True)
    title_uk = models.CharField('Заголовок (UK)', max_length=255)
    title_en = models.CharField('Заголовок (EN)', max_length=255, blank=True, default='')
    body_uk = models.TextField('Текст (UK)')
    body_en = models.TextField('Текст (EN)', blank=True, default='')
    is_published = models.BooleanField('Опубліковано', default=True)

    class Meta:
        verbose_name = 'Сторінка'
        verbose_name_plural = 'Сторінки'
        db_table = 'content_page'
        ordering = ['slug']

    def __str__(self) -> str:
        return self.title_uk

    def title_for(self, locale: str = 'uk') -> str:
        return pick_locale_field(self, 'title', locale)

    def body_for(self, locale: str = 'uk') -> str:
        return pick_locale_field(self, 'body', locale)


class ContactTopic(models.TextChoices):
    ORDER = 'order', 'Питання по замовленню'
    SHEET = 'sheet', 'Пошук нот'


class ContactLead(CreatedAtModel):
    name = models.CharField('Імʼя', max_length=255, blank=True, default='')
    phone = models.CharField('Телефон', max_length=32)
    email = models.EmailField('Email', max_length=254, blank=True, default='')
    topic = models.CharField(
        'Тема',
        max_length=32,
        choices=ContactTopic.choices,
        blank=True,
        default='',
    )
    message = models.TextField('Повідомлення', blank=True, default='')
    page_url = models.CharField('URL сторінки', max_length=512, blank=True, default='')
    is_processed = models.BooleanField('Опрацьовано', default=False)

    class Meta:
        verbose_name = 'Звернення'
        verbose_name_plural = 'Звернення'
        db_table = 'content_contact_lead'
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f'{self.phone} ({self.created_at:%Y-%m-%d})'


class SiteSettings(UpdatedAtModel):
    site_name = models.CharField('Назва сайту', max_length=255, default='NotenHaus')
    logo = models.ImageField(
        'Логотип',
        upload_to='content/logo/',
        max_length=512,
        blank=True,
        null=True,
        help_text=(
            'Рекомендований розмір: 480×160 px. '
            'Значно більші фото автоматично масштабуються (без обрізки). '
            'JPG/PNG → WebP.'
        ),
    )
    contacts_json = models.JSONField(
        'Контакти',
        default=dict,
        help_text=(
            'phones, phone_display, email, email_response, hours, address, '
            'maps_url, viber, telegram, schedule{timezone,days,open,close}'
        ),
    )
    admin_notify_email = models.EmailField('Email адміна для сповіщень', max_length=254)
    notify_customer_on_status = models.BooleanField(
        'Листи клієнту при зміні статусу',
        default=True,
    )
    default_locale = models.CharField('Мова за замовчуванням', max_length=5, default='uk')
    robots_txt = models.TextField('robots.txt', blank=True, default='')
    extra_json = models.JSONField('Додаткові налаштування', default=dict, blank=True)
    shipping_show_pickup = models.BooleanField(
        'Доставка: показувати самовивіз',
        default=False,
        help_text='Картка на /dostavka-i-oplata/ і варіант у checkout.',
    )
    shipping_show_payment_cod = models.BooleanField(
        'Оплата: показувати накладений платіж',
        default=False,
        help_text='Картка на /dostavka-i-oplata/ і варіант у checkout.',
    )
    shipping_show_payment_iban = models.BooleanField(
        'Оплата: показувати IBAN / ФОП',
        default=False,
        help_text='Картка на /dostavka-i-oplata/ і варіант у checkout.',
    )
    payment_iban_recipient = models.CharField(
        'Отримувач (ФОП / ТОВ)',
        max_length=255,
        blank=True,
        default='',
    )
    payment_iban = models.CharField(
        'IBAN',
        max_length=34,
        blank=True,
        default='',
        help_text='UA + 27 цифр.',
    )
    payment_iban_edrpou = models.CharField(
        'ЄДРПОУ / ІПН',
        max_length=20,
        blank=True,
        default='',
    )
    payment_iban_bank = models.CharField(
        'Банк',
        max_length=255,
        blank=True,
        default='',
    )
    payment_iban_purpose = models.CharField(
        'Призначення платежу',
        max_length=255,
        blank=True,
        default='Оплата замовлення {order}',
        help_text='Плейсхолдер {order} замінюється на номер замовлення.',
    )

    class Meta:
        verbose_name = 'Налаштування сайту'
        verbose_name_plural = 'Налаштування сайту'
        db_table = 'content_site_settings'
        constraints = [
            models.CheckConstraint(
                condition=Q(pk=1),
                name='content_site_settings_singleton_id_1',
            ),
        ]

    def __str__(self) -> str:
        return self.site_name

    def save(self, *args, **kwargs):
        from .image_specs import LOGO
        from .image_webp import maybe_process_field

        self.pk = 1
        maybe_process_field(self, 'logo', LOGO)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError('Singleton SiteSettings не можна видаляти.')

    @classmethod
    def load(cls) -> 'SiteSettings':
        from copy import deepcopy

        from .contacts_defaults import DEFAULT_CONTACTS

        obj, _ = cls.objects.get_or_create(
            pk=1,
            defaults={
                'site_name': 'NotenHaus',
                'admin_notify_email': 'admin@example.com',
                'contacts_json': deepcopy(DEFAULT_CONTACTS),
            },
        )
        return obj


class CartTrustBadgeType(models.TextChoices):
    SSL = 'ssl', 'SSL'
    PAYMENT = 'payment', 'Оплата'
    RATING = 'rating', 'Рейтинг'
    CUSTOM = 'custom', 'Інше'


class CartPageSettings(UpdatedAtModel):
    """Singleton: рекомендації, cross-sell і trust-бейджі для сторінки кошика."""

    empty_title_uk = models.CharField(
        'Порожній кошик — заголовок (UK)',
        max_length=255,
        default='Ваш кошик зараз порожній',
    )
    empty_title_en = models.CharField(
        'Порожній кошик — заголовок (EN)',
        max_length=255,
        blank=True,
        default='Your cart is empty',
    )
    empty_text_uk = models.TextField(
        'Порожній кошик — текст (UK)',
        default=(
            'Додайте ноти з каталогу — кошик збережеться в цій сесії браузера.'
        ),
    )
    empty_text_en = models.TextField(
        'Порожній кошик — текст (EN)',
        blank=True,
        default='Add scores from the catalog — the cart is saved for this browser session.',
    )
    recommended_title_uk = models.CharField(
        'Заголовок рекомендацій (UK)',
        max_length=255,
        default='Рекомендуємо вам',
    )
    recommended_title_en = models.CharField(
        'Заголовок рекомендацій (EN)',
        max_length=255,
        blank=True,
        default='Recommended for you',
    )
    cross_sell_title_uk = models.CharField(
        'Заголовок «Часто купують разом» (UK)',
        max_length=255,
        default='Часто купують разом',
    )
    cross_sell_title_en = models.CharField(
        'Заголовок «Часто купують разом» (EN)',
        max_length=255,
        blank=True,
        default='Frequently bought together',
    )
    continue_shopping_label_uk = models.CharField(
        'Кнопка «Продовжити покупки» (UK)',
        max_length=120,
        default='Продовжити покупки',
    )
    continue_shopping_label_en = models.CharField(
        'Кнопка «Продовжити покупки» (EN)',
        max_length=120,
        blank=True,
        default='Continue shopping',
    )
    checkout_label_uk = models.CharField(
        'Кнопка оформлення (UK)',
        max_length=120,
        default='Оформити замовлення',
    )
    checkout_label_en = models.CharField(
        'Кнопка оформлення (EN)',
        max_length=120,
        blank=True,
        default='Checkout',
    )
    recommended_products = models.ManyToManyField(
        'catalog.Product',
        through='CartRecommendedItem',
        related_name='+',
        blank=True,
        verbose_name='Рекомендовані товари',
    )
    cross_sell_products = models.ManyToManyField(
        'catalog.Product',
        through='CartCrossSellItem',
        related_name='+',
        blank=True,
        verbose_name='Часто купують разом',
    )

    class Meta:
        verbose_name = 'Налаштування кошика'
        verbose_name_plural = 'Налаштування кошика'
        db_table = 'content_cart_page_settings'
        constraints = [
            models.CheckConstraint(
                condition=Q(pk=1),
                name='content_cart_page_settings_singleton_id_1',
            ),
        ]

    def __str__(self) -> str:
        return 'Налаштування кошика'

    def empty_title_for(self, locale: str = 'uk') -> str:
        return pick_locale_field(self, 'empty_title', locale)

    def empty_text_for(self, locale: str = 'uk') -> str:
        return pick_locale_field(self, 'empty_text', locale)

    def recommended_title_for(self, locale: str = 'uk') -> str:
        return pick_locale_field(self, 'recommended_title', locale)

    def cross_sell_title_for(self, locale: str = 'uk') -> str:
        return pick_locale_field(self, 'cross_sell_title', locale)

    def continue_shopping_label_for(self, locale: str = 'uk') -> str:
        return pick_locale_field(self, 'continue_shopping_label', locale)

    def checkout_label_for(self, locale: str = 'uk') -> str:
        return pick_locale_field(self, 'checkout_label', locale)

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError('Singleton CartPageSettings не можна видаляти.')

    @classmethod
    def load(cls) -> 'CartPageSettings':
        obj, created = cls.objects.get_or_create(pk=1)
        if created:
            obj.ensure_default_trust_badges()
        return obj

    def ensure_default_trust_badges(self) -> None:
        if self.trust_badges.exists():
            return
        defaults = (
            (CartTrustBadgeType.PAYMENT, 'Visa', 'Visa', 20),
            (CartTrustBadgeType.PAYMENT, 'Mastercard', 'Mastercard', 30),
            (CartTrustBadgeType.PAYMENT, 'LiqPay', 'LiqPay', 40),
            (CartTrustBadgeType.PAYMENT, 'Apple Pay', 'Apple Pay', 50),
            (CartTrustBadgeType.RATING, '4.7 ★ Google', '4.7 ★ Google', 60),
        )
        CartTrustBadge.objects.bulk_create(
            [
                CartTrustBadge(
                    settings=self,
                    badge_type=badge_type,
                    label_uk=label_uk,
                    label_en=label_en,
                    sort_order=sort_order,
                    is_active=True,
                )
                for badge_type, label_uk, label_en, sort_order in defaults
            ]
        )

    def get_recommended_products(self, *, limit: int = 8):
        from src.catalog.selectors import popular_products, published_products

        ordered_ids = list(
            self.recommended_items.order_by('sort_order', 'id').values_list(
                'product_id', flat=True
            )[:limit]
        )
        if not ordered_ids:
            return list(popular_products(limit=limit))
        by_id = {
            p.id: p
            for p in published_products().filter(pk__in=ordered_ids, is_published=True)
        }
        return [by_id[i] for i in ordered_ids if i in by_id]

    def get_cross_sell_products(self, *, limit: int = 6):
        from src.catalog.selectors import popular_products, published_products

        ordered_ids = list(
            self.cross_sell_items.order_by('sort_order', 'id').values_list(
                'product_id', flat=True
            )[:limit]
        )
        if not ordered_ids:
            return list(popular_products(limit=limit))
        by_id = {
            p.id: p
            for p in published_products().filter(pk__in=ordered_ids, is_published=True)
        }
        return [by_id[i] for i in ordered_ids if i in by_id]

    def active_trust_badges(self):
        self.ensure_default_trust_badges()
        return (
            self.trust_badges.filter(is_active=True)
            .exclude(badge_type=CartTrustBadgeType.SSL)
            .order_by('sort_order', 'id')
        )


class CartRecommendedItem(models.Model):
    settings = models.ForeignKey(
        CartPageSettings,
        on_delete=models.CASCADE,
        related_name='recommended_items',
    )
    product = models.ForeignKey(
        'catalog.Product',
        on_delete=models.CASCADE,
        related_name='+',
        verbose_name='Товар',
    )
    sort_order = models.PositiveIntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Рекомендований товар'
        verbose_name_plural = 'Рекомендовані товари'
        db_table = 'content_cart_recommended_item'
        ordering = ['sort_order', 'id']
        constraints = [
            models.UniqueConstraint(
                fields=['settings', 'product'],
                name='content_cart_recommended_uniq',
            ),
        ]

    def __str__(self) -> str:
        return str(self.product_id)


class CartCrossSellItem(models.Model):
    settings = models.ForeignKey(
        CartPageSettings,
        on_delete=models.CASCADE,
        related_name='cross_sell_items',
    )
    product = models.ForeignKey(
        'catalog.Product',
        on_delete=models.CASCADE,
        related_name='+',
        verbose_name='Товар',
    )
    sort_order = models.PositiveIntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Cross-sell товар'
        verbose_name_plural = 'Cross-sell товари'
        db_table = 'content_cart_cross_sell_item'
        ordering = ['sort_order', 'id']
        constraints = [
            models.UniqueConstraint(
                fields=['settings', 'product'],
                name='content_cart_cross_sell_uniq',
            ),
        ]

    def __str__(self) -> str:
        return str(self.product_id)


class CartTrustBadge(models.Model):
    settings = models.ForeignKey(
        CartPageSettings,
        on_delete=models.CASCADE,
        related_name='trust_badges',
    )
    badge_type = models.CharField(
        'Тип',
        max_length=20,
        choices=CartTrustBadgeType.choices,
        default=CartTrustBadgeType.CUSTOM,
    )
    label_uk = models.CharField('Підпис (UK)', max_length=120)
    label_en = models.CharField('Підпис (EN)', max_length=120, blank=True, default='')
    image = models.ImageField(
        'Зображення',
        upload_to='content/cart_badges/',
        max_length=512,
        blank=True,
        null=True,
        help_text=(
            'Рекомендований розмір: 128×128 px. '
            'Значно більші фото автоматично масштабуються (без обрізки). '
            'JPG/PNG → WebP.'
        ),
    )
    sort_order = models.PositiveIntegerField('Порядок', default=0)
    is_active = models.BooleanField('Активний', default=True)

    class Meta:
        verbose_name = 'Trust-бейдж кошика'
        verbose_name_plural = 'Trust-бейджі кошика'
        db_table = 'content_cart_trust_badge'
        ordering = ['sort_order', 'id']

    def __str__(self) -> str:
        return self.label_uk

    def label_for(self, locale: str = 'uk') -> str:
        return pick_locale_field(self, 'label', locale)

    def save(self, *args, **kwargs):
        from .image_specs import TRUST_BADGE
        from .image_webp import maybe_process_field

        maybe_process_field(self, 'image', TRUST_BADGE)
        super().save(*args, **kwargs)

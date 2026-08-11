"""Catalog models — tables.md §3.0–3.4."""

from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q
from src.core.i18n_fields import pick_locale_field
from src.core.models import CreatedAtModel, SeoFieldsMixin, TimeStampedModel


class CatalogTaxonomyBase(TimeStampedModel):
    """Спільний патерн довідника (composer / instrument / genre / level / format)."""

    name_uk = models.CharField('Назва (UK)', max_length=255)
    name_en = models.CharField('Назва (EN)', max_length=255, blank=True, default='')
    slug = models.SlugField('Slug', max_length=160, unique=True)
    is_active = models.BooleanField('Активний', default=True)
    sort_order = models.IntegerField('Порядок', default=0)

    class Meta:
        abstract = True
        ordering = ['sort_order', 'name_uk']

    def __str__(self) -> str:
        return self.name_uk

    def name_for(self, locale: str = 'uk') -> str:
        return pick_locale_field(self, 'name', locale)


class Composer(CatalogTaxonomyBase):
    class Meta(CatalogTaxonomyBase.Meta):
        verbose_name = 'Композитор'
        verbose_name_plural = 'Композитори'
        db_table = 'catalog_composer'


class Instrument(SeoFieldsMixin, CatalogTaxonomyBase):
    class Meta(CatalogTaxonomyBase.Meta):
        verbose_name = 'Інструмент'
        verbose_name_plural = 'Інструменти'
        db_table = 'catalog_instrument'


class Genre(SeoFieldsMixin, CatalogTaxonomyBase):
    class Meta(CatalogTaxonomyBase.Meta):
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанри'
        db_table = 'catalog_genre'


class Level(CatalogTaxonomyBase):
    class Meta(CatalogTaxonomyBase.Meta):
        verbose_name = 'Рівень складності'
        verbose_name_plural = 'Рівні складності'
        db_table = 'catalog_level'


class Format(CatalogTaxonomyBase):
    """Паперовий формат видання (CRUD)."""

    class Meta(CatalogTaxonomyBase.Meta):
        verbose_name = 'Формат'
        verbose_name_plural = 'Формати'
        db_table = 'catalog_format'


PRODUCT_BADGE_TEXT_PRESETS = ('NEW', 'BESTSELLER', '25% OFF')

PRODUCT_BADGE_TONE_CHOICES = [
    ('', '— без кольору —'),
    ('yellow', 'Жовтий'),
    ('maroon', 'Бордовий'),
    ('blue', 'Синій'),
    ('gold', 'Золотий'),
]


class Product(SeoFieldsMixin, TimeStampedModel):
    sku = models.CharField('Артикул', max_length=64, unique=True)
    barcode = models.CharField(
        'Штрихкод',
        max_length=64,
        blank=True,
        default='',
        db_index=True,
        help_text='EAN/ISBN тощо. Порожньо дозволено; непорожні значення мають бути унікальними.',
    )
    slug = models.SlugField('Slug', max_length=160, unique=True)
    name_uk = models.CharField('Назва (UK)', max_length=255)
    name_en = models.CharField('Назва (EN)', max_length=255, blank=True, default='')
    composer = models.ForeignKey(
        Composer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
        verbose_name='Композитор',
    )
    level = models.ForeignKey(
        Level,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
        verbose_name='Рівень',
    )
    format = models.ForeignKey(
        Format,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
        verbose_name='Формат',
    )
    description_uk = models.TextField('Опис (UK)', blank=True, default='')
    description_en = models.TextField('Опис (EN)', blank=True, default='')
    price_uah = models.DecimalField(
        'Ціна (UAH)',
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))],
    )
    stock_qty = models.PositiveIntegerField('Залишок', default=0)
    is_published = models.BooleanField('Опубліковано', default=False)
    is_popular = models.BooleanField('Популярне', default=False)
    is_new = models.BooleanField('Новинка', default=False)
    badge_text = models.CharField(
        'Бейдж на обкладинці',
        max_length=32,
        blank=True,
        default='',
        help_text='NEW, BESTSELLER, 25% OFF або свій текст. Порожньо — без бейджа.',
    )
    badge_tone = models.CharField(
        'Колір бейджа',
        max_length=16,
        choices=PRODUCT_BADGE_TONE_CHOICES,
        default='yellow',
        blank=True,
        help_text='Колір стрічки на обкладинці картки товару.',
    )
    published_at = models.DateTimeField('Дата публікації', null=True, blank=True)
    instruments = models.ManyToManyField(
        Instrument,
        through='ProductInstrument',
        related_name='products',
        blank=True,
        verbose_name='Інструменти',
    )
    genres = models.ManyToManyField(
        Genre,
        through='ProductGenre',
        related_name='products',
        blank=True,
        verbose_name='Жанри',
    )

    class Meta:
        verbose_name = 'Нота'
        verbose_name_plural = 'Ноти'
        db_table = 'catalog_product'
        ordering = ['-published_at', 'name_uk']
        indexes = [
            models.Index(fields=['is_published', '-published_at']),
            models.Index(fields=['is_popular']),
            models.Index(fields=['is_new']),
            models.Index(fields=['composer']),
            models.Index(fields=['level']),
            models.Index(fields=['format']),
            models.Index(fields=['name_uk', 'composer']),
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(price_uah__gte=0),
                name='catalog_product_price_uah_gte_0',
            ),
            models.CheckConstraint(
                condition=Q(stock_qty__gte=0),
                name='catalog_product_stock_qty_gte_0',
            ),
            models.UniqueConstraint(
                fields=['barcode'],
                condition=~Q(barcode=''),
                name='catalog_product_barcode_uniq_nonzero',
            ),
        ]

    def __str__(self) -> str:
        return f'{self.sku} — {self.name_uk}'

    def name_for(self, locale: str = 'uk') -> str:
        return pick_locale_field(self, 'name', locale)

    def description_for(self, locale: str = 'uk') -> str:
        return pick_locale_field(self, 'description', locale)

    @property
    def is_in_stock(self) -> bool:
        return self.stock_qty > 0


class ProductInstrument(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Нота ↔ інструмент'
        verbose_name_plural = 'Ноти ↔ інструменти'
        db_table = 'catalog_product_instrument'
        constraints = [
            models.UniqueConstraint(
                fields=['product', 'instrument'],
                name='catalog_product_instrument_uniq',
            ),
        ]

    def __str__(self) -> str:
        return f'{self.product_id}:{self.instrument_id}'


class ProductGenre(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Нота ↔ жанр'
        verbose_name_plural = 'Ноти ↔ жанри'
        db_table = 'catalog_product_genre'
        constraints = [
            models.UniqueConstraint(
                fields=['product', 'genre'],
                name='catalog_product_genre_uniq',
            ),
        ]

    def __str__(self) -> str:
        return f'{self.product_id}:{self.genre_id}'


class ProductImage(CreatedAtModel):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='Нота',
    )
    image = models.ImageField(
        'Зображення',
        upload_to='catalog/products/',
        max_length=512,
        help_text=(
            'Рекомендований розмір: 800×1200 px. '
            'Значно більші фото автоматично обрізаються та стискаються. '
            'JPG/PNG → WebP.'
        ),
    )
    alt_uk = models.CharField('Alt (UK)', max_length=255, blank=True, default='')
    alt_en = models.CharField('Alt (EN)', max_length=255, blank=True, default='')
    is_main = models.BooleanField('Обкладинка', default=False)
    sort_order = models.IntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Зображення ноти'
        verbose_name_plural = 'Зображення нот'
        db_table = 'catalog_product_image'
        ordering = ['sort_order', 'id']
        constraints = [
            models.UniqueConstraint(
                fields=['product'],
                condition=Q(is_main=True),
                name='catalog_product_image_one_main',
            ),
        ]

    def __str__(self) -> str:
        return f'Image #{self.pk} → {self.product_id}'

    def alt_for(self, locale: str = 'uk') -> str:
        return pick_locale_field(self, 'alt', locale)

    def save(self, *args, **kwargs):
        from src.content.image_specs import PRODUCT_COVER
        from src.content.image_webp import maybe_process_field

        maybe_process_field(self, 'image', PRODUCT_COVER)
        super().save(*args, **kwargs)


class ProductFileKind(models.TextChoices):
    PREVIEW = 'preview', 'Превʼю фрагмента'


class ProductFile(CreatedAtModel):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='files',
        verbose_name='Нота',
    )
    kind = models.CharField(
        'Тип',
        max_length=20,
        choices=ProductFileKind.choices,
        default=ProductFileKind.PREVIEW,
    )
    file = models.FileField('Файл', upload_to='catalog/previews/', max_length=512)
    title_uk = models.CharField('Назва (UK)', max_length=255, blank=True, default='')
    title_en = models.CharField('Назва (EN)', max_length=255, blank=True, default='')
    sort_order = models.IntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Файл ноти'
        verbose_name_plural = 'Файли нот'
        db_table = 'catalog_product_file'
        ordering = ['sort_order', 'id']

    def __str__(self) -> str:
        return f'{self.kind} #{self.pk} → {self.product_id}'

    def title_for(self, locale: str = 'uk') -> str:
        return pick_locale_field(self, 'title', locale)


class ProductImportJob(CreatedAtModel):
    """Завантаження CSV/YML каталогу через адмінку."""

    class Status(models.TextChoices):
        PENDING = 'pending', 'Очікує'
        RUNNING = 'running', 'Виконується'
        DONE = 'done', 'Завершено'
        FAILED = 'failed', 'Помилка'

    class FileFormat(models.TextChoices):
        CSV = 'csv', 'CSV'
        YML = 'yml', 'YML/XML'

    file = models.FileField('Файл', upload_to='catalog/imports/', max_length=512)
    format = models.CharField(
        'Формат',
        max_length=8,
        choices=FileFormat.choices,
        blank=True,
        default='',
        help_text='Порожньо — визначити за розширенням файлу.',
    )
    status = models.CharField(
        'Статус',
        max_length=16,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )
    created_count = models.PositiveIntegerField('Створено', default=0)
    updated_count = models.PositiveIntegerField('Оновлено', default=0)
    skipped_count = models.PositiveIntegerField('Пропущено', default=0)
    error_count = models.PositiveIntegerField('Помилок', default=0)
    report_json = models.JSONField('Звіт', default=dict, blank=True)
    error_message = models.TextField('Повідомлення помилки', blank=True, default='')
    started_at = models.DateTimeField('Старт', null=True, blank=True)
    finished_at = models.DateTimeField('Завершення', null=True, blank=True)

    class Meta:
        verbose_name = 'Імпорт товарів'
        verbose_name_plural = 'Імпорт товарів'
        db_table = 'catalog_product_import_job'
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f'Import #{self.pk} ({self.status})'

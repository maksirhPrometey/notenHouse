"""Seed demo taxonomy + sample product (idempotent)."""

from decimal import Decimal
from pathlib import Path

from django.core.files import File
from django.core.management.base import BaseCommand
from django.utils import timezone

from src.catalog.models import Composer, Format, Genre, Instrument, Level, Product, ProductImage
from src.catalog.taxonomy_i18n import fill_taxonomy_english
from src.content.contacts_defaults import merge_contacts
from src.content.models import AboutPageSettings, SiteSettings

SEED_ASSETS = Path(__file__).resolve().parent / 'seed_assets'


class Command(BaseCommand):
    help = 'Seed NotenHaus demo content (idempotent)'

    def handle(self, *args, **options):
        site = SiteSettings.load()
        site.site_name = 'NotenHaus'
        site.admin_notify_email = site.admin_notify_email or 'admin@example.com'
        site.contacts_json = merge_contacts(site.contacts_json)
        site.save()

        AboutPageSettings.load()

        for slug, name_uk, name_en, sort_order in (
            ('fortepiano', 'Фортепіано', 'Piano', 10),
            ('skrypka', 'Скрипка', 'Violin', 20),
        ):
            Instrument.objects.update_or_create(
                slug=slug,
                defaults={
                    'name_uk': name_uk,
                    'name_en': name_en,
                    'is_active': True,
                    'sort_order': sort_order,
                },
            )
        piano = Instrument.objects.get(slug='fortepiano')

        for slug, name_uk, name_en, sort_order in (
            ('klasyka', 'Класика', 'Classical', 10),
            ('romantyka', 'Романтика', 'Romantic', 20),
        ):
            Genre.objects.update_or_create(
                slug=slug,
                defaults={
                    'name_uk': name_uk,
                    'name_en': name_en,
                    'is_active': True,
                    'sort_order': sort_order,
                },
            )
        classic = Genre.objects.get(slug='klasyka')

        for slug, name_uk, name_en, sort_order in (
            ('pochatkivets', 'Початківець', 'Beginner', 10),
            ('seredniy', 'Середній', 'Intermediate', 20),
            ('prosunutyy', 'Просунутий', 'Advanced', 30),
        ):
            Level.objects.update_or_create(
                slug=slug,
                defaults={
                    'name_uk': name_uk,
                    'name_en': name_en,
                    'is_active': True,
                    'sort_order': sort_order,
                },
            )
        beginner = Level.objects.get(slug='pochatkivets')

        sheet, _ = Format.objects.update_or_create(
            slug='zoshyt',
            defaults={
                'name_uk': 'Зошит',
                'name_en': 'Booklet',
                'is_active': True,
                'sort_order': 10,
            },
        )

        composers = {}
        for slug, name_uk, name_en in (
            ('bach', 'Й. С. Бах', 'J. S. Bach'),
            ('chopin', 'Ф. Шопен', 'F. Chopin'),
            ('tchaikovsky', 'П. І. Чайковський', 'P. I. Tchaikovsky'),
            ('beethoven', 'Л. ван Бетховен', 'L. van Beethoven'),
            ('m-klementi', 'М. Клементі', 'M. Clementi'),
            ('r-shuman', 'Р. Шуман', 'R. Schumann'),
        ):
            composers[slug], _ = Composer.objects.update_or_create(
                slug=slug,
                defaults={'name_uk': name_uk, 'name_en': name_en, 'is_active': True},
            )

        # Довідники з імпорту без EN — доповнюємо словником.
        fill_stats = fill_taxonomy_english()
        filled = sum(fill_stats.values())
        if filled:
            self.stdout.write(f'Taxonomy EN backfill: {filled}')

        demos = [
            {
                'sku': 'NH-DEMO-001',
                'slug': 'inventarziyi-baha',
                'name_uk': 'Інвенції Баха (демо)',
                'name_en': 'Bach Inventions (demo)',
                'composer': composers['bach'],
                'price_uah': Decimal('350.00'),
                'is_popular': True,
                'is_new': True,
                'badge_text': 'NEW',
                'badge_tone': 'yellow',
                'image': 'inventarziyi-baha.jpg',
                'alt_uk': 'Обкладинка — Інвенції Баха',
                'alt_en': 'Cover — Bach Inventions',
            },
            {
                'sku': 'NH-DEMO-002',
                'slug': 'prelyudiyi-shopen',
                'name_uk': 'Прелюдії Шопена (демо)',
                'name_en': 'Chopin Preludes (demo)',
                'composer': composers['chopin'],
                'price_uah': Decimal('480.00'),
                'is_popular': True,
                'is_new': False,
                'badge_text': 'BESTSELLER',
                'badge_tone': 'maroon',
                'image': 'prelyudiyi-shopen.jpg',
                'alt_uk': 'Обкладинка — Прелюдії Шопена',
                'alt_en': 'Cover — Chopin Preludes',
            },
            {
                'sku': 'NH-DEMO-003',
                'slug': 'etyudy-chajkovskogo',
                'name_uk': 'Етюди Чайковського (демо)',
                'name_en': 'Tchaikovsky Etudes (demo)',
                'composer': composers['tchaikovsky'],
                'price_uah': Decimal('420.00'),
                'is_popular': True,
                'is_new': True,
                'badge_text': '25% OFF',
                'badge_tone': 'gold',
                'image': 'etyudy-chajkovskogo.jpg',
                'alt_uk': 'Обкладинка — Етюди Чайковського',
                'alt_en': 'Cover — Tchaikovsky Etudes',
            },
            {
                'sku': 'NH-DEMO-004',
                'slug': 'sonaty-betkhoven',
                'name_uk': 'Сонати Бетховена (демо)',
                'name_en': 'Beethoven Sonatas (demo)',
                'composer': composers['beethoven'],
                'price_uah': Decimal('560.00'),
                'is_popular': False,
                'is_new': True,
                'badge_text': 'OFFER',
                'badge_tone': 'blue',
                'image': 'sonaty-betkhoven.jpg',
                'alt_uk': 'Обкладинка — Сонати Бетховена',
                'alt_en': 'Cover — Beethoven Sonatas',
            },
        ]

        created_skus = []
        images_attached = 0
        for item in demos:
            product, created = Product.objects.update_or_create(
                sku=item['sku'],
                defaults={
                    'slug': item['slug'],
                    'name_uk': item['name_uk'],
                    'name_en': item['name_en'],
                    'composer': item['composer'],
                    'level': beginner,
                    'format': sheet,
                    'description_uk': 'Демо-товар для перевірки каталогу та кошика.',
                    'description_en': 'Demo product for catalog and cart checks.',
                    'price_uah': item['price_uah'],
                    'stock_qty': 10,
                    'is_published': True,
                    'is_popular': item['is_popular'],
                    'is_new': item['is_new'],
                    'badge_text': item['badge_text'],
                    'badge_tone': item['badge_tone'],
                    'published_at': timezone.now(),
                },
            )
            product.instruments.add(piano)
            product.genres.add(classic)
            if created:
                created_skus.append(product.sku)

            if self._ensure_main_image(product, item):
                images_attached += 1

        self.stdout.write(self.style.SUCCESS(
            f'Seed OK (created: {", ".join(created_skus) or "none"}; '
            f'total demos: {len(demos)}; images upserted: {images_attached})'
        ))

    def _ensure_main_image(self, product: Product, item: dict) -> bool:
        src = SEED_ASSETS / item['image']
        if not src.is_file():
            self.stdout.write(self.style.WARNING(f'Missing seed image: {src.name}'))
            return False

        existing = product.images.filter(is_main=True).first()
        if existing and existing.image and existing.image.storage.exists(existing.image.name):
            # Refresh file content if seed asset name differs or file empty
            if Path(existing.image.name).name == src.name and existing.image.size:
                return False

        if existing:
            existing.delete()

        with src.open('rb') as fh:
            image = ProductImage(
                product=product,
                alt_uk=item['alt_uk'],
                alt_en=item['alt_en'],
                is_main=True,
                sort_order=0,
            )
            image.image.save(src.name, File(fh), save=True)
        return True

"""Заповнити порожні name_en у довідниках каталогу зі словника UK→EN."""

from django.core.management.base import BaseCommand

from src.catalog.taxonomy_i18n import fill_taxonomy_english


class Command(BaseCommand):
    help = 'Fill missing catalog taxonomy name_en from built-in UK→EN map'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Overwrite existing name_en when dictionary has a value',
        )

    def handle(self, *args, **options):
        stats = fill_taxonomy_english(force=bool(options['force']))
        total = sum(stats.values())
        for model_name, count in stats.items():
            self.stdout.write(f'{model_name}: {count} updated')
        self.stdout.write(self.style.SUCCESS(f'Done. Total updated: {total}'))

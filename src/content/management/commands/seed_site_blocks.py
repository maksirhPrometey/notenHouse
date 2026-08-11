from django.core.management.base import BaseCommand

from src.content.block_defaults import BLOCK_DEFAULTS
from src.content.site_block_models import SiteBlock
from src.content.site_blocks import ensure_site_blocks, invalidate_site_blocks_cache


class Command(BaseCommand):
    help = 'Idempotent seed of SiteBlock rows from BLOCK_DEFAULTS'

    def add_arguments(self, parser):
        parser.add_argument(
            '--sync-text',
            action='store_true',
            help='Update text_uk/text_en/labels from defaults for existing rows',
        )

    def handle(self, *args, **options):
        created = ensure_site_blocks()
        updated = 0
        if options['sync_text']:
            for (page, key), data in BLOCK_DEFAULTS.items():
                try:
                    block = SiteBlock.objects.get(page=page, key=key)
                except SiteBlock.DoesNotExist:
                    continue
                fields = {
                    'label': data.get('label', key),
                    'text_uk': data.get('text_uk', ''),
                    'text_en': data.get('text_en', ''),
                    'link_label_uk': data.get('link_label_uk', ''),
                    'link_label_en': data.get('link_label_en', ''),
                }
                changed = False
                for name, value in fields.items():
                    if getattr(block, name) != value:
                        setattr(block, name, value)
                        changed = True
                if changed:
                    block.save(update_fields=list(fields.keys()))
                    updated += 1
            if updated:
                invalidate_site_blocks_cache()
        self.stdout.write(
            self.style.SUCCESS(f'SiteBlock created: {created}, updated: {updated}')
        )

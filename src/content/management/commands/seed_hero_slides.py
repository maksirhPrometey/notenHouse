from django.core.management.base import BaseCommand

from src.content.hero_slides import ensure_default_hero_slides


class Command(BaseCommand):
    help = 'Idempotent seed of default HeroSlide rows'

    def handle(self, *args, **options):
        created = ensure_default_hero_slides()
        self.stdout.write(self.style.SUCCESS(f'HeroSlide created: {created}'))

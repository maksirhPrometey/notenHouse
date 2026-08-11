"""SEO — redirect 301 (tables.md §3.15, M4 optional але в ядрі схеми)."""

from django.db import models

from src.core.models import CreatedAtModel


class Redirect301(CreatedAtModel):
    old_path = models.CharField('Старий шлях', max_length=512, unique=True)
    new_path = models.CharField('Новий шлях', max_length=512)
    is_active = models.BooleanField('Активний', default=True)

    class Meta:
        verbose_name = 'Редирект 301'
        verbose_name_plural = 'Редиректи 301'
        db_table = 'seo_redirect_301'
        ordering = ['old_path']

    def __str__(self) -> str:
        return f'{self.old_path} → {self.new_path}'

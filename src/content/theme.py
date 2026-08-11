"""ActiveTheme singleton — runtime CSS tokens (theme_switcher_skill)."""

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Q

HEX_VALIDATOR = RegexValidator(
    regex=r'^$|^#[0-9A-Fa-f]{6}$',
    message='Колір має бути у форматі #RRGGBB або порожнім',
)


def _hex_field(label: str, help_extra: str = '') -> models.CharField:
    help_text = 'Hex #RRGGBB. Порожньо = дефолт з colors.css.'
    if help_extra:
        help_text = f'{help_extra} {help_text}'
    return models.CharField(
        label,
        max_length=7,
        blank=True,
        default='',
        validators=[HEX_VALIDATOR],
        help_text=help_text,
    )


class ActiveTheme(models.Model):
    """Singleton id=1 — перевизначення семантичних токенів без деплою."""

    # --- Фони ---
    color_bg = _hex_field('Фон сторінки')
    color_bg_grey = _hex_field('Фон сірих секцій')
    color_header_bg = _hex_field('Фон хедера')
    color_footer_bg = _hex_field('Футер: початок градієнта')
    color_footer_bg_mid = _hex_field('Футер: середина градієнта')
    color_footer_bg_end = _hex_field('Футер: кінець градієнта')
    color_header_fg = _hex_field('Текст хедера')
    color_footer_fg = _hex_field('Текст футера')

    # --- Текст ---
    color_text = _hex_field('Основний текст')
    color_text_muted = _hex_field('Приглушений текст')
    color_link = _hex_field('Посилання')
    color_focus = _hex_field('Focus ring')

    # --- Кнопки (окремо) ---
    color_btn_cta = _hex_field('Кнопка CTA')
    color_btn_cta_hover = _hex_field('Кнопка CTA (hover)')
    color_btn_search = _hex_field('Кнопка пошуку')
    color_btn_search_hover = _hex_field('Кнопка пошуку (hover)')
    color_btn_newsletter = _hex_field('Кнопка розсилки')
    color_btn_newsletter_hover = _hex_field('Кнопка розсилки (hover)')
    color_btn_ghost = _hex_field('Кнопка ghost (текст/бордер)')
    color_btn_ghost_hover_bg = _hex_field('Кнопка ghost (фон hover)')

    # --- Акценти / бейджі ---
    color_badge_cart = _hex_field('Фон віджета кошика')
    color_badge_yellow = _hex_field('Бейдж жовтий')
    color_badge_maroon = _hex_field('Бейдж бордовий')
    color_badge_blue = _hex_field('Бейдж синій')
    color_badge_gold = _hex_field('Бейдж золотий')
    color_brand = _hex_field('Бренд (hover заголовків карток)')
    color_brand_hover = _hex_field('Бренд hover')

    # --- Шрифти ---
    FONT_HEADING_CHOICES = [
        ('', 'Дефолт (Georgia)'),
        ('Georgia, "Times New Roman", "Palatino Linotype", serif', 'Georgia (system)'),
        ('"Playfair Display", Georgia, serif', 'Playfair Display'),
        ('"Cormorant Garamond", Georgia, serif', 'Cormorant Garamond'),
        ('"Libre Baskerville", Georgia, serif', 'Libre Baskerville'),
        ('"Merriweather", Georgia, serif', 'Merriweather'),
    ]
    FONT_BODY_CHOICES = [
        ('', 'Дефолт (system sans)'),
        ('system-ui, -apple-system, "Segoe UI", sans-serif', 'System UI'),
        ('"Source Sans 3", "Segoe UI", system-ui, sans-serif', 'Source Sans 3'),
        ('"Inter", "Segoe UI", system-ui, sans-serif', 'Inter'),
        ('"Nunito Sans", "Segoe UI", system-ui, sans-serif', 'Nunito Sans'),
        ('"DM Sans", "Segoe UI", system-ui, sans-serif', 'DM Sans'),
    ]

    font_heading = models.CharField(
        'Шрифт заголовків',
        max_length=120,
        blank=True,
        default='',
        choices=FONT_HEADING_CHOICES,
        help_text='Порожньо = дефолт з CSS.',
    )
    font_body = models.CharField(
        'Шрифт тексту',
        max_length=120,
        blank=True,
        default='',
        choices=FONT_BODY_CHOICES,
        help_text='Порожньо = дефолт з CSS.',
    )

    updated_at = models.DateTimeField('Оновлено', auto_now=True)

    TOKEN_MAP = {
        'color_bg': '--color-bg',
        'color_bg_grey': '--color-bg-grey',
        'color_header_bg': '--color-header-bg',
        'color_footer_bg': '--color-footer-bg',
        'color_footer_bg_mid': '--color-footer-bg-mid',
        'color_footer_bg_end': '--color-footer-bg-end',
        'color_header_fg': '--color-header-fg',
        'color_footer_fg': '--color-footer-fg',
        'color_text': '--color-text',
        'color_text_muted': '--color-text-muted',
        'color_link': '--color-link',
        'color_focus': '--color-focus',
        'color_btn_cta': '--color-btn-cta',
        'color_btn_cta_hover': '--color-btn-cta-hover',
        'color_btn_search': '--color-btn-search',
        'color_btn_search_hover': '--color-btn-search-hover',
        'color_btn_newsletter': '--color-btn-newsletter',
        'color_btn_newsletter_hover': '--color-btn-newsletter-hover',
        'color_btn_ghost': '--color-btn-ghost',
        'color_btn_ghost_hover_bg': '--color-btn-ghost-hover-bg',
        'color_badge_cart': '--color-badge-cart',
        'color_badge_yellow': '--color-badge-yellow',
        'color_badge_maroon': '--color-badge-maroon',
        'color_badge_blue': '--color-badge-blue',
        'color_badge_gold': '--color-badge-gold',
        'color_brand': '--color-brand',
        'color_brand_hover': '--color-brand-hover',
        'font_heading': '--font-serif',
        'font_body': '--font-sans',
    }

    # Locked brand original (pre-fog maroon). Never overwrite for trials.
    # Used only by «Повернути до оригіналу».
    ORIGINAL_DEFAULTS = {
        'color_bg': '#ffffff',
        'color_bg_grey': '#f1f2f3',
        'color_header_bg': '#1b3650',
        'color_footer_bg': '#1b3650',
        'color_footer_bg_mid': '#340814',
        'color_footer_bg_end': '#630a22',
        'color_header_fg': '#ffffff',
        'color_footer_fg': '#ffffff',
        'color_text': '#1c1c1c',
        'color_text_muted': '#777475',
        'color_link': '#2158e5',
        'color_focus': '#8db6fa',
        'color_btn_cta': '#630a22',
        'color_btn_cta_hover': '#8c0d30',
        'color_btn_search': '#ffb338',
        'color_btn_search_hover': '#ffd98f',
        'color_btn_newsletter': '#630a22',
        'color_btn_newsletter_hover': '#8c0d30',
        'color_btn_ghost': '#1c1c1c',
        'color_btn_ghost_hover_bg': '#f6f4f5',
        'color_badge_cart': '#ffd98f',
        'color_badge_yellow': '#ffb338',
        'color_badge_maroon': '#630a22',
        'color_badge_blue': '#2158e5',
        'color_badge_gold': '#ffd98f',
        'color_brand': '#630a22',
        'color_brand_hover': '#8c0d30',
    }

    # Preview / empty-field fallback — must match current colors.css role map
    FIELD_DEFAULTS = {
        'color_bg': '#eaedf0',
        'color_bg_grey': '#e4e6e5',
        'color_header_bg': '#465461',
        'color_footer_bg': '#465461',
        'color_footer_bg_mid': '#79190f',
        'color_footer_bg_end': '#9b1f14',
        'color_header_fg': '#ffffff',
        'color_footer_fg': '#ffffff',
        'color_text': '#2a333c',
        'color_text_muted': '#6a7a84',
        'color_link': '#466d7a',
        'color_focus': '#95a8ad',
        'color_btn_cta': '#9b1f14',
        'color_btn_cta_hover': '#c0392b',
        'color_btn_search': '#d4785c',
        'color_btn_search_hover': '#e8c4b8',
        'color_btn_newsletter': '#9b1f14',
        'color_btn_newsletter_hover': '#c0392b',
        'color_btn_ghost': '#2a333c',
        'color_btn_ghost_hover_bg': '#eaedf0',
        'color_badge_cart': '#e8c4b8',
        'color_badge_yellow': '#d4785c',
        'color_badge_maroon': '#9b1f14',
        'color_badge_blue': '#466d7a',
        'color_badge_gold': '#e8c4b8',
        'color_brand': '#9b1f14',
        'color_brand_hover': '#c0392b',
    }

    # Short usage hints under admin field labels
    FIELD_USAGE = {
        'color_bg': 'Основний фон body усієї сторінки',
        'color_bg_grey': 'Фон сірих секцій і блоків з сірим тлом',
        'color_header_bg': 'Фон шапки та мобільного меню',
        'color_header_fg': 'Текст і іконки в шапці',
        'color_footer_bg': 'Початок градієнта футера',
        'color_footer_bg_mid': 'Середина градієнта футера',
        'color_footer_bg_end': 'Кінець градієнта футера',
        'color_footer_fg': 'Текст, посилання та логотип у футері',
        'color_text': 'Основний текст на сторінках і картках',
        'color_text_muted': 'Підписи, метадані, другорядний текст',
        'color_link': 'Посилання в контенті, меню та кабінеті',
        'color_focus': 'Focus ring кнопок і полів вводу',
        'color_btn_cta': 'Основні CTA-кнопки (купити, дії)',
        'color_btn_cta_hover': 'Hover основних CTA-кнопок',
        'color_btn_search': 'Кнопка пошуку в шапці',
        'color_btn_search_hover': 'Hover кнопки пошуку',
        'color_btn_newsletter': 'Кнопка підписки в футері',
        'color_btn_newsletter_hover': 'Hover кнопки підписки',
        'color_btn_ghost': 'Текст і бордер ghost-кнопок',
        'color_btn_ghost_hover_bg': 'Фон hover для ghost-кнопок',
        'color_badge_cart': 'Фон лічильника кошика в шапці',
        'color_badge_yellow': 'Жовтий бейдж на картках товарів',
        'color_badge_maroon': 'Бордовий бейдж на картках товарів',
        'color_badge_blue': 'Синій бейдж на картках товарів',
        'color_badge_gold': 'Золотий бейдж на картках товарів',
        'color_brand': 'Бренд-акцент: hover заголовків, активні стани',
        'color_brand_hover': 'Hover для брендових акцентів',
    }

    GOOGLE_FONT_QUERY = {
        'Playfair Display': 'Playfair+Display:wght@400;600;700',
        'Cormorant Garamond': 'Cormorant+Garamond:wght@400;600;700',
        'Libre Baskerville': 'Libre+Baskerville:wght@400;700',
        'Merriweather': 'Merriweather:wght@400;700',
        'Source Sans 3': 'Source+Sans+3:wght@400;600;700',
        'Inter': 'Inter:wght@400;600;700',
        'Nunito Sans': 'Nunito+Sans:wght@400;600;700',
        'DM Sans': 'DM+Sans:wght@400;600;700',
    }

    class Meta:
        verbose_name = 'Тема сайту'
        verbose_name_plural = 'Тема сайту'
        db_table = 'content_active_theme'
        constraints = [
            models.CheckConstraint(
                condition=Q(pk=1),
                name='content_active_theme_singleton_id_1',
            ),
        ]

    def __str__(self) -> str:
        return 'Тема сайту'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError('Singleton ActiveTheme не можна видаляти.')

    @classmethod
    def get_solo(cls) -> 'ActiveTheme':
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def build_css(self) -> str:
        lines: list[str] = []
        for field, var in self.TOKEN_MAP.items():
            value = getattr(self, field, '') or ''
            if value:
                lines.append(f'  {var}: {value};')
        if not lines:
            return '/* ActiveTheme: defaults from colors.css */\n'
        return ':root {\n' + '\n'.join(lines) + '\n}\n'

    def google_fonts_href(self) -> str:
        families: list[str] = []
        for stack in (self.font_heading, self.font_body):
            if not stack:
                continue
            for name, query in self.GOOGLE_FONT_QUERY.items():
                if name in stack and query not in families:
                    families.append(query)
        if not families:
            return ''
        family_param = '&family='.join(families)
        return (
            'https://fonts.googleapis.com/css2?family='
            + family_param
            + '&display=swap'
        )

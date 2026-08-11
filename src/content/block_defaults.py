"""Defaults + content types for SiteBlock registry (UK/EN)."""

from __future__ import annotations

from typing import Any

# Visibility / short labels → TextInput
COLOR_KEYS: frozenset[str] = frozenset({
    'hero_text_color',
})

INLINE_KEYS: frozenset[str] = frozenset({
    'hero_brand', 'hero_cta_label', 'popular_title', 'popular_link',
    'new_title', 'new_link', 'header_search_placeholder', 'header_nav_catalog',
    'header_nav_about', 'header_nav_shipping', 'header_nav_contacts',
    'header_tool_cabinet', 'header_tool_wishlist', 'header_tool_cart',
    'header_burger_label', 'footer_col_catalog', 'footer_col_service',
    'footer_col_contacts', 'footer_link_all', 'footer_link_search',
    'footer_link_shipping', 'footer_link_contacts', 'footer_link_about',
    'footer_credit', 'shipping_trust_badge', 'contacts_maps_label',
    'contacts_submit', 'contacts_form_topic_legend', 'catalog_filters_label',
    'catalog_sort_popular', 'catalog_sort_new', 'catalog_sort_price_asc',
    'catalog_sort_price_desc', 'catalog_filter_composer', 'catalog_filter_instrument',
    'catalog_filter_genre', 'catalog_filter_all', 'search_submit',
    'cart_title', 'cart_summary_heading', 'cart_summary_items', 'cart_summary_total',
    'checkout_title', 'checkout_submit', 'thank_you_title',
    'cabinet_nav_dashboard', 'cabinet_nav_orders', 'cabinet_nav_wishlist',
    'cabinet_nav_profile', 'cabinet_login_title', 'cabinet_register_title',
})

MULTILINE_KEYS: frozenset[str] = frozenset({
    'hero_lead', 'new_sub', 'footer_tagline', 'shipping_subtitle',
    'shipping_delivery_lead', 'shipping_payment_lead', 'shipping_packaging_text',
    'shipping_faq_1_a', 'shipping_faq_2_a', 'shipping_faq_3_a',
    'contacts_subtitle', 'contacts_success', 'catalog_lead',
    'search_empty_text', 'thank_you_text', 'meta_description',
})

BLOCK_CONTENT_TYPES: dict[tuple[str, str], str] = {
    ('home', 'hero_bg_image'): 'image',
    ('home', 'hero_cta'): 'url',
    ('site', 'header_logo_fallback'): 'image',
}

# (page, key): (label, text_uk, text_en [, link_url, link_label_uk, link_label_en])
BLOCK_DEFAULTS: dict[tuple[str, str], dict[str, Any]] = {
    # --- home ---
    ('home', 'hero_section_visible'): {
        'label': 'Hero: видимість',
        'text_uk': '1',
        'text_en': '1',
    },
    ('home', 'hero_brand'): {
        'label': 'Hero: бренд',
        'text_uk': 'NotenHaus',
        'text_en': 'NotenHaus',
    },
    ('home', 'hero_title'): {
        'label': 'Hero: заголовок',
        'text_uk': 'Ноти для кожного музиканта',
        'text_en': 'Sheet music for every musician',
    },
    ('home', 'hero_lead'): {
        'label': 'Hero: лід',
        'text_uk': 'Обирайте серед тисяч видань — від класики до джазу.',
        'text_en': 'Choose among thousands of editions — from classical to jazz.',
    },
    ('home', 'hero_cta'): {
        'label': 'Hero: CTA',
        'text_uk': '',
        'text_en': '',
        'link_url': '/katalog/',
        'link_label_uk': 'До каталогу',
        'link_label_en': 'To catalog',
    },
    ('home', 'hero_bg_image'): {
        'label': 'Hero: фонове фото (якщо без слайдів)',
        'text_uk': '',
        'text_en': '',
        'help_uk': (
            'Рекомендований розмір: 1920×1080 px. '
            'Значно більші фото автоматично обрізаються та стискаються. '
            'JPG/PNG → WebP.'
        ),
    },
    ('site', 'header_logo_fallback'): {
        'label': 'Header: логотип (fallback)',
        'text_uk': '',
        'text_en': '',
        'help_uk': (
            'Рекомендований розмір: 480×160 px. '
            'Значно більші фото автоматично масштабуються (без обрізки). '
            'JPG/PNG → WebP.'
        ),
    },
    ('home', 'hero_text_color'): {
        'label': 'Hero: колір тексту',
        'text_uk': '#ffffff',
        'text_en': '#ffffff',
        'help_uk': 'Hex #RRGGBB. Зручно підлаштувати під світле/темне фото.',
    },
    ('home', 'meta_description'): {
        'label': 'SEO description',
        'text_uk': 'Інтернет-магазин нотних видань',
        'text_en': 'Sheet music online store',
    },
    ('home', 'popular_section_visible'): {
        'label': 'Популярні: видимість',
        'text_uk': '1',
        'text_en': '1',
    },
    ('home', 'popular_title'): {
        'label': 'Популярні: заголовок',
        'text_uk': 'Популярні ноти',
        'text_en': 'Popular scores',
    },
    ('home', 'popular_link'): {
        'label': 'Популярні: лінк',
        'text_uk': 'Дивитись усі',
        'text_en': 'View all',
    },
    ('home', 'new_section_visible'): {
        'label': 'Новинки: видимість',
        'text_uk': '1',
        'text_en': '1',
    },
    ('home', 'new_title'): {
        'label': 'Новинки: заголовок',
        'text_uk': 'Новинки',
        'text_en': 'New arrivals',
    },
    ('home', 'new_sub'): {
        'label': 'Новинки: підзаголовок',
        'text_uk': 'Свіжі надходження нотних видань',
        'text_en': 'Fresh sheet music arrivals',
    },
    ('home', 'new_link'): {
        'label': 'Новинки: лінк',
        'text_uk': 'Дивитись усі',
        'text_en': 'View all',
    },
    # --- site header ---
    ('site', 'header_search_placeholder'): {
        'label': 'Пошук: placeholder',
        'text_uk': 'Шукати ноти, композиторів, інструменти…',
        'text_en': 'Search scores, composers, instruments…',
    },
    ('site', 'header_search_label'): {
        'label': 'Пошук: aria label',
        'text_uk': 'Пошук нот',
        'text_en': 'Search sheet music',
    },
    ('site', 'header_tool_cabinet'): {
        'label': 'Інструмент: Кабінет',
        'text_uk': 'Кабінет',
        'text_en': 'Account',
    },
    ('site', 'header_tool_wishlist'): {
        'label': 'Інструмент: Обране',
        'text_uk': 'Обране',
        'text_en': 'Wishlist',
    },
    ('site', 'header_tool_cart'): {
        'label': 'Інструмент: Кошик',
        'text_uk': 'Кошик',
        'text_en': 'Cart',
    },
    ('site', 'header_burger_label'): {
        'label': 'Бургер: aria',
        'text_uk': 'Відкрити меню',
        'text_en': 'Open menu',
    },
    ('site', 'header_nav_catalog'): {
        'label': 'Навігація: Каталог',
        'text_uk': 'Каталог',
        'text_en': 'Catalog',
    },
    ('site', 'header_nav_about'): {
        'label': 'Навігація: Про нас',
        'text_uk': 'Про нас',
        'text_en': 'About',
    },
    ('site', 'header_nav_shipping'): {
        'label': 'Навігація: Доставка',
        'text_uk': 'Доставка та оплата',
        'text_en': 'Shipping & payment',
    },
    ('site', 'header_nav_contacts'): {
        'label': 'Навігація: Контакти',
        'text_uk': 'Контакти',
        'text_en': 'Contacts',
    },
    ('site', 'header_nav_aria'): {
        'label': 'Навігація: aria',
        'text_uk': 'Основна навігація',
        'text_en': 'Main navigation',
    },
    # --- site footer ---
    ('site', 'footer_tagline'): {
        'label': 'Footer: tagline',
        'text_uk': 'Інтернет-магазин нотних видань',
        'text_en': 'Sheet music online store',
    },
    ('site', 'footer_lang_meta'): {
        'label': 'Footer: мова',
        'text_uk': 'Мова: UA | EN',
        'text_en': 'Language: UA | EN',
    },
    ('site', 'footer_currency_meta'): {
        'label': 'Footer: валюта',
        'text_uk': 'Валюта: ₴ UAH',
        'text_en': 'Currency: ₴ UAH',
    },
    ('site', 'footer_col_catalog'): {
        'label': 'Footer: колонка Каталог',
        'text_uk': 'Каталог',
        'text_en': 'Catalog',
    },
    ('site', 'footer_col_service'): {
        'label': 'Footer: колонка Сервіс',
        'text_uk': 'Сервіс',
        'text_en': 'Service',
    },
    ('site', 'footer_col_contacts'): {
        'label': 'Footer: колонка Контакти',
        'text_uk': 'Контакти',
        'text_en': 'Contacts',
    },
    ('site', 'footer_link_all'): {
        'label': 'Footer: Усі ноти',
        'text_uk': 'Усі ноти',
        'text_en': 'All scores',
    },
    ('site', 'footer_link_search'): {
        'label': 'Footer: Пошук',
        'text_uk': 'Пошук',
        'text_en': 'Search',
    },
    ('site', 'footer_link_shipping'): {
        'label': 'Footer: Доставка',
        'text_uk': 'Доставка та оплата',
        'text_en': 'Shipping & payment',
    },
    ('site', 'footer_link_contacts'): {
        'label': 'Footer: Контакти',
        'text_uk': 'Контакти',
        'text_en': 'Contacts',
    },
    ('site', 'footer_link_about'): {
        'label': 'Footer: Про нас',
        'text_uk': 'Про нас',
        'text_en': 'About',
    },
    ('site', 'footer_credit'): {
        'label': 'Footer: credit',
        'text_uk': 'Створено в PrometeyLabs',
        'text_en': 'Built by PrometeyLabs',
    },
}

# Continuations in block_defaults_2/3/4.py to stay under 500 lines
from .block_defaults_2 import BLOCK_DEFAULTS_EXTRA  # noqa: E402
from .block_defaults_3 import BLOCK_DEFAULTS_UI  # noqa: E402
from .block_defaults_4 import BLOCK_DEFAULTS_PAY  # noqa: E402

BLOCK_DEFAULTS.update(BLOCK_DEFAULTS_EXTRA)
BLOCK_DEFAULTS.update(BLOCK_DEFAULTS_UI)
BLOCK_DEFAULTS.update(BLOCK_DEFAULTS_PAY)


def is_visibility_key(key: str) -> bool:
    return key.endswith('_visible')


def get_block_default(page: str, key: str) -> dict[str, Any]:
    return BLOCK_DEFAULTS.get((page, key), {})


def default_text(page: str, key: str, locale: str = 'uk') -> str:
    data = get_block_default(page, key)
    if locale == 'en':
        return str(data.get('text_en') or data.get('text_uk') or '')
    return str(data.get('text_uk') or '')

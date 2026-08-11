"""Registry of CMS content sections for Unfold proxy admins."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from django.urls import reverse_lazy


@dataclass(frozen=True)
class FieldGroup:
    title: str
    keys: tuple[str, ...]


@dataclass(frozen=True)
class ContentSection:
    slug: str
    page_slug: str
    title: str
    blocks: tuple[tuple[str, str], ...]
    sidebar_title: str = ''
    sidebar_icon: str = 'edit_note'
    preview_url: str = '/'
    description: str = ''
    visibility_key: str = ''
    field_groups: tuple[FieldGroup, ...] = ()
    admin_model_name: str = ''
    has_hero_slides: bool = False

    def __post_init__(self):
        if not self.admin_model_name:
            page = self.page_slug.replace('_', ' ').title().replace(' ', '')
            slug = self.slug.replace('_', ' ').title().replace(' ', '')
            object.__setattr__(
                self,
                'admin_model_name',
                f'{page}{slug}Settings'.lower(),
            )


CONTENT_SECTIONS: tuple[ContentSection, ...] = (
    ContentSection(
        slug='hero',
        page_slug='home',
        title='Головна — Hero',
        sidebar_title='Hero',
        sidebar_icon='image',
        preview_url='/',
        visibility_key='hero_section_visible',
        has_hero_slides=True,
        description='Заголовок, лід, CTA, колір тексту та слайди/фото героя.',
        blocks=(
            ('home', 'hero_brand'),
            ('home', 'hero_title'),
            ('home', 'hero_lead'),
            ('home', 'hero_text_color'),
            ('home', 'hero_cta'),
            ('home', 'hero_bg_image'),
            ('home', 'meta_description'),
        ),
        field_groups=(
            FieldGroup(
                'Текст',
                ('hero_brand', 'hero_title', 'hero_lead', 'hero_text_color', 'meta_description'),
            ),
            FieldGroup('CTA / фото', ('hero_cta', 'hero_bg_image')),
        ),
    ),
    ContentSection(
        slug='popular',
        page_slug='home',
        title='Головна — Популярні',
        sidebar_title='Популярні',
        sidebar_icon='star',
        preview_url='/',
        visibility_key='popular_section_visible',
        blocks=(
            ('home', 'popular_title'),
            ('home', 'popular_link'),
        ),
    ),
    ContentSection(
        slug='new',
        page_slug='home',
        title='Головна — Новинки',
        sidebar_title='Новинки',
        sidebar_icon='new_releases',
        preview_url='/',
        visibility_key='new_section_visible',
        blocks=(
            ('home', 'new_title'),
            ('home', 'new_sub'),
            ('home', 'new_link'),
        ),
    ),
    ContentSection(
        slug='header',
        page_slug='site',
        title='Шапка сайту',
        sidebar_title='Шапка',
        sidebar_icon='web',
        preview_url='/',
        description='Підписи навігації та інструментів.',
        blocks=(
            ('site', 'header_search_placeholder'),
            ('site', 'header_search_label'),
            ('site', 'header_tool_cabinet'),
            ('site', 'header_tool_wishlist'),
            ('site', 'header_tool_cart'),
            ('site', 'header_burger_label'),
            ('site', 'header_nav_catalog'),
            ('site', 'header_nav_about'),
            ('site', 'header_nav_shipping'),
            ('site', 'header_nav_contacts'),
            ('site', 'header_nav_aria'),
        ),
    ),
    ContentSection(
        slug='footer',
        page_slug='site',
        title='Підвал сайту',
        sidebar_title='Підвал',
        sidebar_icon='vertical_align_bottom',
        preview_url='/',
        blocks=(
            ('site', 'footer_tagline'),
            ('site', 'footer_lang_meta'),
            ('site', 'footer_currency_meta'),
            ('site', 'footer_col_catalog'),
            ('site', 'footer_col_service'),
            ('site', 'footer_col_contacts'),
            ('site', 'footer_link_all'),
            ('site', 'footer_link_search'),
            ('site', 'footer_link_shipping'),
            ('site', 'footer_link_contacts'),
            ('site', 'footer_link_about'),
            ('site', 'footer_credit'),
        ),
    ),
    ContentSection(
        slug='page',
        page_slug='shipping',
        title='Доставка та оплата',
        sidebar_title='Доставка',
        sidebar_icon='local_shipping',
        preview_url='/dostavka-i-oplata/',
        blocks=tuple(
            ('shipping', k)
            for k in (
                'title', 'subtitle', 'subtitle_with_pickup', 'trust_badge', 'trust_title',
                'trust_text', 'delivery_title', 'delivery_lead',
                'card_np_branch_badge', 'card_np_branch_title', 'card_np_branch_text',
                'card_np_parcel_title', 'card_np_parcel_text',
                'card_pickup_title', 'card_pickup_text',
                'payment_title', 'payment_lead',
                'card_liqpay_title', 'card_liqpay_text',
                'card_cod_title', 'card_cod_text',
                'card_iban_title', 'card_iban_text',
                'packaging_title', 'packaging_text',
                'faq_title', 'faq_1_q', 'faq_1_a', 'faq_2_q', 'faq_2_a',
                'faq_3_q', 'faq_3_a', 'meta_description',
            )
        ),
        field_groups=(
            FieldGroup('Intro', ('title', 'subtitle', 'subtitle_with_pickup')),
            FieldGroup('Trust', ('trust_badge', 'trust_title', 'trust_text')),
            FieldGroup('Доставка', (
                'delivery_title', 'delivery_lead',
                'card_np_branch_badge', 'card_np_branch_title', 'card_np_branch_text',
                'card_np_parcel_title', 'card_np_parcel_text',
                'card_pickup_title', 'card_pickup_text',
            )),
            FieldGroup('Оплата', (
                'payment_title', 'payment_lead',
                'card_liqpay_title', 'card_liqpay_text',
                'card_cod_title', 'card_cod_text',
                'card_iban_title', 'card_iban_text',
            )),
            FieldGroup('FAQ / SEO', (
                'packaging_title', 'packaging_text', 'faq_title',
                'faq_1_q', 'faq_1_a', 'faq_2_q', 'faq_2_a',
                'faq_3_q', 'faq_3_a', 'meta_description',
            )),
        ),
    ),
    ContentSection(
        slug='page',
        page_slug='contacts',
        title='Контакти — тексти',
        sidebar_title='Контакти (тексти)',
        sidebar_icon='contact_mail',
        preview_url='/kontakty/',
        blocks=(
            ('contacts', 'title'),
            ('contacts', 'subtitle'),
            ('contacts', 'card_phone_title'),
            ('contacts', 'card_email_title'),
            ('contacts', 'card_hours_title'),
            ('contacts', 'maps_label'),
            ('contacts', 'form_topic_legend'),
            ('contacts', 'submit'),
            ('contacts', 'success'),
            ('contacts', 'meta_description'),
        ),
    ),
    ContentSection(
        slug='page',
        page_slug='catalog',
        title='Каталог — UI',
        sidebar_title='Каталог UI',
        sidebar_icon='inventory_2',
        preview_url='/katalog/',
        blocks=tuple(
            ('catalog', k)
            for k in (
                'title', 'lead', 'filters_label', 'sort_label', 'sort_popular', 'sort_new',
                'sort_price_asc', 'sort_price_desc', 'sort_price_asc_full',
                'sort_price_desc_full', 'sort_name', 'filter_composer',
                'filter_instrument', 'filter_genre', 'filter_level', 'filter_all',
                'filter_search', 'filter_search_ph', 'filters_close', 'filters_apply',
                'filters_reset', 'view_aria', 'view_grid', 'view_list',
                'add_to_cart', 'in_cart', 'in_stock', 'out_of_stock',
                'composer_label', 'format_label', 'level_label', 'instrument_label',
                'preview_label', 'preview_short', 'wishlist_remove', 'empty_results',
                'qty_label', 'currency_uah', 'pagination_pages', 'pagination_prev',
                'pagination_next',
            )
        ),
    ),
    ContentSection(
        slug='page',
        page_slug='search',
        title='Пошук — UI',
        sidebar_title='Пошук UI',
        sidebar_icon='search',
        preview_url='/poshuk/',
        blocks=(
            ('search', 'title'),
            ('search', 'placeholder'),
            ('search', 'submit'),
            ('search', 'lead'),
            ('search', 'results_prefix'),
            ('search', 'found'),
            ('search', 'clear'),
            ('search', 'to_catalog'),
            ('search', 'empty_title'),
            ('search', 'empty_text'),
        ),
    ),
    ContentSection(
        slug='chrome',
        page_slug='cart',
        title='Кошик — UI chrome',
        sidebar_title='Кошик UI',
        sidebar_icon='shopping_cart',
        preview_url='/koshyk/',
        description='Підсумок і заголовок. Empty/recommend — у «Налаштування кошика».',
        blocks=(
            ('cart', 'title'),
            ('cart', 'summary_heading'),
            ('cart', 'summary_items'),
            ('cart', 'summary_total'),
            ('cart', 'remove_label'),
            ('cart', 'qty_unit'),
            ('cart', 'items_aria'),
            ('cart', 'buy'),
            ('cart', 'add'),
        ),
    ),
    ContentSection(
        slug='page',
        page_slug='checkout',
        title='Checkout — UI',
        sidebar_title='Checkout',
        sidebar_icon='payments',
        preview_url='/oformlennya/',
        blocks=(
            ('checkout', 'title'),
            ('checkout', 'order_heading'),
            ('checkout', 'submit'),
            ('checkout', 'total_label'),
            ('checkout', 'subtotal_label'),
            ('checkout', 'shipping_label'),
            ('checkout', 'shipping_carrier'),
            ('checkout', 'edit_cart'),
            ('checkout', 'stepper_aria'),
            ('checkout', 'step_cart'),
            ('checkout', 'step_checkout'),
            ('checkout', 'step_pay'),
            ('checkout', 'contact_heading'),
            ('checkout', 'email_hint'),
            ('checkout', 'shipping_heading'),
            ('checkout', 'pickup_hint'),
            ('checkout', 'pickup_notice_title'),
            ('checkout', 'pickup_notice_text'),
            ('checkout', 'payment_heading'),
            ('checkout', 'payment_liqpay'),
            ('checkout', 'payment_liqpay_hint'),
            ('checkout', 'payment_cod'),
            ('checkout', 'payment_cod_hint'),
            ('checkout', 'payment_iban'),
            ('checkout', 'payment_iban_hint'),
            ('checkout', 'comment_toggle'),
            ('checkout', 'np_city_label'),
            ('checkout', 'np_warehouse_label'),
            ('checkout', 'trust_aria'),
            ('checkout', 'trust_ssl'),
            ('checkout', 'trust_pack'),
            ('checkout', 'liqpay_redirect_title'),
            ('checkout', 'liqpay_redirect_text'),
            ('checkout', 'payment_retry_title'),
            ('checkout', 'payment_retry_text'),
            ('checkout', 'payment_retry_btn'),
        ),
    ),
    ContentSection(
        slug='page',
        page_slug='thank_you',
        title='Дякуємо — UI',
        sidebar_title='Дякуємо',
        sidebar_icon='check_circle',
        preview_url='/dyakuyemo/',
        blocks=(
            ('thank_you', 'title'),
            ('thank_you', 'text'),
            ('thank_you', 'order_number'),
            ('thank_you', 'payment_status'),
            ('thank_you', 'instructions_cod_title'),
            ('thank_you', 'instructions_cod_text'),
            ('thank_you', 'instructions_iban_title'),
            ('thank_you', 'instructions_iban_text'),
            ('thank_you', 'iban_recipient_label'),
            ('thank_you', 'iban_label'),
            ('thank_you', 'iban_edrpou_label'),
            ('thank_you', 'iban_bank_label'),
            ('thank_you', 'iban_purpose_label'),
            ('thank_you', 'iban_amount_label'),
            ('thank_you', 'iban_missing'),
        ),
    ),
    ContentSection(
        slug='page',
        page_slug='cabinet',
        title='Кабінет — UI',
        sidebar_title='Кабінет UI',
        sidebar_icon='person',
        preview_url='/kabinet/',
        blocks=(
            ('cabinet', 'nav_dashboard'),
            ('cabinet', 'nav_orders'),
            ('cabinet', 'nav_wishlist'),
            ('cabinet', 'nav_profile'),
            ('cabinet', 'nav_aria'),
            ('cabinet', 'logout'),
            ('cabinet', 'login_title'),
            ('cabinet', 'register_title'),
            ('cabinet', 'wishlist_add'),
            ('cabinet', 'wishlist_added'),
        ),
    ),
)


def get_section(page_slug: str, section_slug: str) -> ContentSection | None:
    for section in CONTENT_SECTIONS:
        if section.page_slug == page_slug and section.slug == section_slug:
            return section
    return None


def iter_section_block_keys(section: ContentSection) -> Iterable[tuple[str, str]]:
    keys = list(section.blocks)
    if section.visibility_key:
        keys.insert(0, (section.page_slug, section.visibility_key))
    return keys


def build_content_sidebar_items() -> list[dict]:
    return [
        {
            'title': section.sidebar_title or section.title,
            'icon': section.sidebar_icon,
            'link': reverse_lazy(
                f'admin:content_{section.admin_model_name}_changelist'
            ),
        }
        for section in CONTENT_SECTIONS
    ]


def validate_registry() -> None:
    seen_keys: set[tuple[str, str]] = set()
    seen_admin: set[str] = set()
    for section in CONTENT_SECTIONS:
        if section.admin_model_name in seen_admin:
            raise ValueError(f'Duplicate admin_model_name: {section.admin_model_name}')
        seen_admin.add(section.admin_model_name)
        for page, key in iter_section_block_keys(section):
            pair = (page, key)
            if pair in seen_keys:
                raise ValueError(f'Duplicate block key: {page}.{key}')
            seen_keys.add(pair)

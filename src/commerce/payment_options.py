"""Checkout payment / shipping options driven by SiteSettings flags."""

from __future__ import annotations

from src.commerce.models import PaymentProvider, ShippingMethod
from src.content.models import SiteSettings

PAYMENT_LABELS = {
    'uk': {
        PaymentProvider.LIQPAY: 'Онлайн-оплата карткою / LiqPay',
        PaymentProvider.COD: 'Накладений платіж',
        PaymentProvider.IBAN: 'Оплата за реквізитами (IBAN / ФОП)',
    },
    'en': {
        PaymentProvider.LIQPAY: 'Online card payment / LiqPay',
        PaymentProvider.COD: 'Cash on delivery',
        PaymentProvider.IBAN: 'Bank transfer (IBAN / sole proprietor)',
    },
}

SHIPPING_LABELS = {
    'uk': {
        ShippingMethod.NP_WAREHOUSE: 'Нова Пошта — відділення',
        ShippingMethod.NP_POSHTOMAT: 'Нова Пошта — поштомат',
        ShippingMethod.PICKUP: 'Самовивіз',
    },
    'en': {
        ShippingMethod.NP_WAREHOUSE: 'Nova Poshta — branch',
        ShippingMethod.NP_POSHTOMAT: 'Nova Poshta — parcel locker',
        ShippingMethod.PICKUP: 'Pickup',
    },
}

SHIPPING_HINTS = {
    'uk': {
        ShippingMethod.NP_WAREHOUSE: '1–2 дні',
        ShippingMethod.NP_POSHTOMAT: '1–2 дні',
        ShippingMethod.PICKUP: 'За попередньою домовленістю',
    },
    'en': {
        ShippingMethod.NP_WAREHOUSE: '1–2 days',
        ShippingMethod.NP_POSHTOMAT: '1–2 days',
        ShippingMethod.PICKUP: 'By prior arrangement',
    },
}


def enabled_payment_providers(site: SiteSettings | None = None) -> list[str]:
    site = site or SiteSettings.load()
    providers = [PaymentProvider.LIQPAY]
    if site.shipping_show_payment_cod:
        providers.append(PaymentProvider.COD)
    if site.shipping_show_payment_iban:
        providers.append(PaymentProvider.IBAN)
    return providers


def payment_choice_tuples(
    locale: str = 'uk',
    site: SiteSettings | None = None,
) -> list[tuple[str, str]]:
    lang = 'en' if locale == 'en' else 'uk'
    labels = PAYMENT_LABELS[lang]
    return [(value, labels[value]) for value in enabled_payment_providers(site)]


def enabled_shipping_methods(site: SiteSettings | None = None) -> list[str]:
    site = site or SiteSettings.load()
    methods = [ShippingMethod.NP_WAREHOUSE, ShippingMethod.NP_POSHTOMAT]
    if site.shipping_show_pickup:
        methods.append(ShippingMethod.PICKUP)
    return methods


def shipping_choice_tuples(
    locale: str = 'uk',
    site: SiteSettings | None = None,
) -> list[tuple[str, str]]:
    lang = 'en' if locale == 'en' else 'uk'
    labels = SHIPPING_LABELS[lang]
    return [(value, labels[value]) for value in enabled_shipping_methods(site)]


def shipping_hints_map(locale: str = 'uk') -> dict[str, str]:
    lang = 'en' if locale == 'en' else 'uk'
    return dict(SHIPPING_HINTS[lang])


def format_iban_purpose(template: str, order_number: str) -> str:
    raw = (template or 'Оплата замовлення {order}').strip()
    return raw.replace('{order}', order_number)

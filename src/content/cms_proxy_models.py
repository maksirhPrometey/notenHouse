"""Static proxy models for CMS sections (one per ContentSection)."""

from .models import SiteSettings


class HomeHeroSettings(SiteSettings):
    class Meta:
        proxy = True
        verbose_name = 'Головна — Hero'
        verbose_name_plural = 'Головна — Hero'


class HomePopularSettings(SiteSettings):
    class Meta:
        proxy = True
        verbose_name = 'Головна — Популярні'
        verbose_name_plural = 'Головна — Популярні'


class HomeNewSettings(SiteSettings):
    class Meta:
        proxy = True
        verbose_name = 'Головна — Новинки'
        verbose_name_plural = 'Головна — Новинки'


class SiteHeaderSettings(SiteSettings):
    class Meta:
        proxy = True
        verbose_name = 'Шапка сайту'
        verbose_name_plural = 'Шапка сайту'


class SiteFooterSettings(SiteSettings):
    class Meta:
        proxy = True
        verbose_name = 'Підвал сайту'
        verbose_name_plural = 'Підвал сайту'


class ShippingPageSettings(SiteSettings):
    class Meta:
        proxy = True
        verbose_name = 'Доставка та оплата'
        verbose_name_plural = 'Доставка та оплата'


class ContactsPageSettings(SiteSettings):
    class Meta:
        proxy = True
        verbose_name = 'Контакти — тексти'
        verbose_name_plural = 'Контакти — тексти'


class CatalogPageSettings(SiteSettings):
    class Meta:
        proxy = True
        verbose_name = 'Каталог — UI'
        verbose_name_plural = 'Каталог — UI'


class SearchPageSettings(SiteSettings):
    class Meta:
        proxy = True
        verbose_name = 'Пошук — UI'
        verbose_name_plural = 'Пошук — UI'


class CartChromeSettings(SiteSettings):
    class Meta:
        proxy = True
        verbose_name = 'Кошик — UI chrome'
        verbose_name_plural = 'Кошик — UI chrome'


class CheckoutPageSettings(SiteSettings):
    class Meta:
        proxy = True
        verbose_name = 'Checkout — UI'
        verbose_name_plural = 'Checkout — UI'


class ThankYouPageSettings(SiteSettings):
    class Meta:
        proxy = True
        verbose_name = 'Дякуємо — UI'
        verbose_name_plural = 'Дякуємо — UI'


class CabinetPageSettings(SiteSettings):
    class Meta:
        proxy = True
        verbose_name = 'Кабінет — UI'
        verbose_name_plural = 'Кабінет — UI'


SECTION_PROXY_MODELS: tuple[tuple[type, str, str], ...] = (
    (HomeHeroSettings, 'home', 'hero'),
    (HomePopularSettings, 'home', 'popular'),
    (HomeNewSettings, 'home', 'new'),
    (SiteHeaderSettings, 'site', 'header'),
    (SiteFooterSettings, 'site', 'footer'),
    (ShippingPageSettings, 'shipping', 'page'),
    (ContactsPageSettings, 'contacts', 'page'),
    (CatalogPageSettings, 'catalog', 'page'),
    (SearchPageSettings, 'search', 'page'),
    (CartChromeSettings, 'cart', 'chrome'),
    (CheckoutPageSettings, 'checkout', 'page'),
    (ThankYouPageSettings, 'thank_you', 'page'),
    (CabinetPageSettings, 'cabinet', 'page'),
)

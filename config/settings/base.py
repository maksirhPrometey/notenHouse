"""NotenHaus shared settings."""

from pathlib import Path

from decouple import Csv, config
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = config('SECRET_KEY')

DEBUG = False

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='', cast=Csv())

INSTALLED_APPS = [
    'unfold',
    'unfold.contrib.filters',
    'unfold.contrib.forms',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'tinymce',
    'django_htmx',
    'src.core',
    'src.catalog',
    'src.commerce',
    'src.payments',
    'src.shipping',
    'src.content',
    'src.notifications',
    'src.seo',
    'src.cabinet',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_htmx.middleware.HtmxMiddleware',
    'csp.middleware.CSPMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
                'src.core.context_processors.site_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'uk'
LANGUAGES = [
    ('uk', 'Українська'),
    ('en', 'English'),
]
LOCALE_PATHS = [BASE_DIR / 'locale']

TIME_ZONE = 'Europe/Kyiv'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 60 * 60 * 24 * 14

LOGIN_URL = 'cabinet:login'
LOGIN_REDIRECT_URL = 'cabinet:dashboard'
LOGOUT_REDIRECT_URL = 'core:home'

CONTENT_SECURITY_POLICY = {
    'DIRECTIVES': {
        'default-src': ("'self'",),
        'script-src': ("'self'",),
        'style-src': ("'self'", 'https://fonts.googleapis.com'),
        'img-src': ("'self'", 'data:', 'blob:'),
        'font-src': ("'self'", 'https://fonts.gstatic.com'),
        'connect-src': ("'self'",),
        'frame-ancestors': ("'none'",),
        'base-uri': ("'self'",),
        'form-action': ("'self'",),
    },
    # Alpine.js Unfold потребує unsafe-eval — виключаємо /admin/
    'EXCLUDE_URL_PREFIXES': ('/admin/',),
}

TINYMCE_DEFAULT_CONFIG = {
    'height': 400,
    'menubar': False,
    'plugins': 'link lists image code',
    'toolbar': 'undo redo | bold italic underline | bullist numlist | link image | code',
    'content_css': False,
    'skin': 'oxide',
}


def _content_sidebar_items():
    from src.content.site_content_registry import build_content_sidebar_items

    return build_content_sidebar_items()


UNFOLD = {
    'SITE_TITLE': 'NotenHaus Admin',
    'SITE_HEADER': 'NotenHaus — Адмінпанель',
    'SITE_SYMBOL': 'music_note',
    'SITE_FAVICONS': [
        {
            'rel': 'icon',
            'type': 'image/x-icon',
            'sizes': 'any',
            'href': STATIC_URL + 'images/favicon.ico',
        },
    ],
    'SHOW_HISTORY': True,
    # Primary = brand maroon з colors.css (#630a22 / #8c0d30 / #340814)
    'COLORS': {
        'primary': {
            '50': '#f9f0f3',
            '100': '#f2dde4',
            '200': '#e4b8c5',
            '300': '#d08fa3',
            '400': '#b34d6a',
            '500': '#8c0d30',
            '600': '#630a22',
            '700': '#52091c',
            '800': '#340814',
            '900': '#280610',
            '950': '#1a040a',
        },
    },
    'SIDEBAR': {
        'show_search': True,
        'command_search': True,
        'show_all_applications': False,
        'navigation': [
            {
                'title': _('Налаштування'),
                'items': [
                    {
                        'title': _('Сайт'),
                        'icon': 'settings',
                        'link': reverse_lazy('admin:content_sitesettings_changelist'),
                    },
                    {
                        'title': _('Тема'),
                        'icon': 'palette',
                        'link': reverse_lazy('admin:content_activetheme_changelist'),
                    },
                ],
            },
            {
                'title': _('Контент сторінок'),
                'separator': True,
                'items': _content_sidebar_items(),
            },
            {
                'title': _('Сторінки / About / Кошик'),
                'separator': True,
                'items': [
                    {
                        'title': _('Про нас'),
                        'icon': 'info',
                        'link': reverse_lazy('admin:content_aboutpagesettings_changelist'),
                    },
                    {
                        'title': _('Налаштування кошика'),
                        'icon': 'shopping_bag',
                        'link': reverse_lazy('admin:content_cartpagesettings_changelist'),
                    },
                    {
                        'title': _('Сторінки (Page)'),
                        'icon': 'article',
                        'link': reverse_lazy('admin:content_page_changelist'),
                    },
                    {
                        'title': _('Звернення'),
                        'icon': 'mail',
                        'link': reverse_lazy('admin:content_contactlead_changelist'),
                    },
                ],
            },
            {
                'title': _('Каталог'),
                'separator': True,
                'items': [
                    {
                        'title': _('Товари'),
                        'icon': 'inventory_2',
                        'link': reverse_lazy('admin:catalog_product_changelist'),
                    },
                    {
                        'title': _('Імпорт товарів'),
                        'icon': 'upload_file',
                        'link': reverse_lazy('admin:catalog_productimportjob_changelist'),
                    },
                    {
                        'title': _('Композитори'),
                        'icon': 'person',
                        'link': reverse_lazy('admin:catalog_composer_changelist'),
                    },
                    {
                        'title': _('Інструменти'),
                        'icon': 'piano',
                        'link': reverse_lazy('admin:catalog_instrument_changelist'),
                    },
                    {
                        'title': _('Жанри'),
                        'icon': 'category',
                        'link': reverse_lazy('admin:catalog_genre_changelist'),
                    },
                    {
                        'title': _('Рівні'),
                        'icon': 'stairs',
                        'link': reverse_lazy('admin:catalog_level_changelist'),
                    },
                    {
                        'title': _('Формати'),
                        'icon': 'description',
                        'link': reverse_lazy('admin:catalog_format_changelist'),
                    },
                ],
            },
            {
                'title': _('Продажі'),
                'separator': True,
                'items': [
                    {
                        'title': _('Замовлення'),
                        'icon': 'receipt_long',
                        'link': reverse_lazy('admin:commerce_order_changelist'),
                    },
                    {
                        'title': _('Кошики'),
                        'icon': 'shopping_cart',
                        'link': reverse_lazy('admin:commerce_cart_changelist'),
                    },
                    {
                        'title': _('Платіжні події'),
                        'icon': 'payments',
                        'link': reverse_lazy('admin:payments_paymentevent_changelist'),
                    },
                ],
            },
            {
                'title': _('Клієнти'),
                'separator': True,
                'items': [
                    {
                        'title': _('Профілі'),
                        'icon': 'group',
                        'link': reverse_lazy('admin:cabinet_customerprofile_changelist'),
                    },
                    {
                        'title': _('Обране'),
                        'icon': 'favorite',
                        'link': reverse_lazy('admin:cabinet_wishlistitem_changelist'),
                    },
                ],
            },
            {
                'title': _('Система'),
                'separator': True,
                'items': [
                    {
                        'title': _('Email лог'),
                        'icon': 'outgoing_mail',
                        'link': reverse_lazy('admin:notifications_emaillog_changelist'),
                    },
                    {
                        'title': _('Redirect 301'),
                        'icon': 'alt_route',
                        'link': reverse_lazy('admin:seo_redirect301_changelist'),
                    },
                    {
                        'title': _('Користувачі'),
                        'icon': 'manage_accounts',
                        'link': reverse_lazy('admin:auth_user_changelist'),
                    },
                ],
            },
        ],
    },
}

RESEND_API_KEY = config('RESEND_API_KEY', default='')
RESEND_FROM_EMAIL = config('RESEND_FROM_EMAIL', default='NotenHaus <noreply@notenhaus.local>')
LIQPAY_PUBLIC_KEY = config('LIQPAY_PUBLIC_KEY', default='')
LIQPAY_PRIVATE_KEY = config('LIQPAY_PRIVATE_KEY', default='')
NP_API_KEY = config('NP_API_KEY', default='')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
    'loggers': {
        'src': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}

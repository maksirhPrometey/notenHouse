"""Extra UI strings for catalog / cart / checkout / site chrome (EN completion)."""

from __future__ import annotations

from typing import Any

BLOCK_DEFAULTS_UI: dict[tuple[str, str], dict[str, Any]] = {
    # --- catalog extra ---
    ('shipping', 'payment_lead_single'): {
        'label': 'Оплата: лід (лише LiqPay)',
        'text_uk': 'Безпечна онлайн-оплата через захищений шлюз LiqPay.',
        'text_en': 'Secure online payment via the LiqPay gateway.',
    },
    ('catalog', 'sort_label'): {
        'label': 'Сортування: label',
        'text_uk': 'Сортування',
        'text_en': 'Sort',
    },
    ('catalog', 'sort_name'): {
        'label': 'Сорт: назва',
        'text_uk': 'Назва',
        'text_en': 'Name',
    },
    ('catalog', 'sort_price_asc_full'): {
        'label': 'Сорт: ціна від низької',
        'text_uk': 'Ціна: від низької',
        'text_en': 'Price: low to high',
    },
    ('catalog', 'sort_price_desc_full'): {
        'label': 'Сорт: ціна від високої',
        'text_uk': 'Ціна: від високої',
        'text_en': 'Price: high to low',
    },
    ('catalog', 'filter_level'): {
        'label': 'Фільтр: рівень',
        'text_uk': 'Рівень',
        'text_en': 'Level',
    },
    ('catalog', 'filter_search'): {
        'label': 'Фільтр: пошук',
        'text_uk': 'Пошук',
        'text_en': 'Search',
    },
    ('catalog', 'filter_search_ph'): {
        'label': 'Фільтр: placeholder',
        'text_uk': 'Назва або артикул',
        'text_en': 'Title or SKU',
    },
    ('catalog', 'filters_close'): {
        'label': 'Фільтри: закрити',
        'text_uk': 'Закрити фільтри',
        'text_en': 'Close filters',
    },
    ('catalog', 'filters_apply'): {
        'label': 'Фільтри: застосувати',
        'text_uk': 'Застосувати',
        'text_en': 'Apply',
    },
    ('catalog', 'filters_reset'): {
        'label': 'Фільтри: скинути',
        'text_uk': 'Скинути',
        'text_en': 'Reset',
    },
    ('catalog', 'view_aria'): {
        'label': 'Вид: aria',
        'text_uk': 'Вигляд каталогу',
        'text_en': 'Catalog view',
    },
    ('catalog', 'view_grid'): {
        'label': 'Вид: сітка',
        'text_uk': 'Сітка',
        'text_en': 'Grid',
    },
    ('catalog', 'view_list'): {
        'label': 'Вид: список',
        'text_uk': 'Список',
        'text_en': 'List',
    },
    ('catalog', 'format_label'): {
        'label': 'PDP: формат',
        'text_uk': 'Формат',
        'text_en': 'Format',
    },
    ('catalog', 'level_label'): {
        'label': 'PDP: рівень',
        'text_uk': 'Рівень',
        'text_en': 'Level',
    },
    ('catalog', 'instrument_label'): {
        'label': 'PDP: інструмент',
        'text_uk': 'Інструмент',
        'text_en': 'Instrument',
    },
    ('catalog', 'out_of_stock'): {
        'label': 'Немає в наявності',
        'text_uk': 'Немає в наявності',
        'text_en': 'Out of stock',
    },
    ('catalog', 'in_cart'): {
        'label': 'У кошику',
        'text_uk': 'У кошику',
        'text_en': 'In cart',
    },
    ('catalog', 'preview_short'): {
        'label': 'Превʼю (коротко)',
        'text_uk': 'Превʼю',
        'text_en': 'Preview',
    },
    ('catalog', 'wishlist_remove'): {
        'label': 'Прибрати з обраного',
        'text_uk': 'Прибрати з обраного',
        'text_en': 'Remove from wishlist',
    },
    ('catalog', 'empty_results'): {
        'label': 'Порожні результати',
        'text_uk': 'Нічого не знайдено',
        'text_en': 'Nothing found',
    },
    ('catalog', 'qty_label'): {
        'label': 'Кількість',
        'text_uk': 'Кількість',
        'text_en': 'Quantity',
    },
    ('catalog', 'currency_uah'): {
        'label': 'Валюта грн',
        'text_uk': 'грн',
        'text_en': 'UAH',
    },
    ('catalog', 'pagination_pages'): {
        'label': 'Пагінація: сторінки',
        'text_uk': 'Сторінки',
        'text_en': 'Pages',
    },
    ('catalog', 'pagination_prev'): {
        'label': 'Пагінація: назад',
        'text_uk': 'Назад',
        'text_en': 'Previous',
    },
    ('catalog', 'pagination_next'): {
        'label': 'Пагінація: далі',
        'text_uk': 'Далі',
        'text_en': 'Next',
    },
    # --- search extra ---
    ('search', 'results_prefix'): {
        'label': 'Результати: префікс',
        'text_uk': 'Результати для',
        'text_en': 'Results for',
    },
    ('search', 'found'): {
        'label': 'Знайдено',
        'text_uk': 'Знайдено',
        'text_en': 'Found',
    },
    ('search', 'clear'): {
        'label': 'Очистити',
        'text_uk': 'Очистити',
        'text_en': 'Clear',
    },
    ('search', 'to_catalog'): {
        'label': 'До каталогу',
        'text_uk': 'До каталогу',
        'text_en': 'To catalog',
    },
    ('search', 'lead'): {
        'label': 'Лід пошуку',
        'text_uk': 'Шукайте за назвою, композитором або артикулом.',
        'text_en': 'Search by title, composer or SKU.',
    },
    # --- site mega / breadcrumb ---
    ('site', 'mega_title'): {
        'label': 'Mega: заголовок',
        'text_uk': 'Каталог',
        'text_en': 'Catalog',
    },
    ('site', 'mega_all'): {
        'label': 'Mega: увесь каталог',
        'text_uk': 'Увесь каталог',
        'text_en': 'Full catalog',
    },
    ('site', 'mega_close'): {
        'label': 'Mega: закрити',
        'text_uk': 'Закрити',
        'text_en': 'Close',
    },
    ('site', 'mega_instruments'): {
        'label': 'Mega: інструменти',
        'text_uk': 'Інструменти',
        'text_en': 'Instruments',
    },
    ('site', 'mega_genres'): {
        'label': 'Mega: жанри',
        'text_uk': 'Жанри',
        'text_en': 'Genres',
    },
    ('site', 'mega_composers'): {
        'label': 'Mega: композитори',
        'text_uk': 'Композитори',
        'text_en': 'Composers',
    },
    ('site', 'mega_levels'): {
        'label': 'Mega: рівні',
        'text_uk': 'Рівень',
        'text_en': 'Level',
    },
    ('site', 'mega_empty'): {
        'label': 'Mega: порожньо',
        'text_uk': 'Немає пунктів',
        'text_en': 'No items',
    },
    ('site', 'breadcrumb_expand'): {
        'label': 'Breadcrumb: розгорнути',
        'text_uk': 'Показати повний шлях',
        'text_en': 'Show full path',
    },
    # --- shipping extras / sync live copy badges ---
    ('shipping', 'trust_aria'): {
        'label': 'Trust: aria',
        'text_uk': 'Гарантія доставки',
        'text_en': 'Delivery guarantee',
    },
    ('shipping', 'card_pickup_badge'): {
        'label': 'Самовивіз: badge',
        'text_uk': 'Безкоштовно',
        'text_en': 'Free',
    },
    ('shipping', 'card_liqpay_badge'): {
        'label': 'LiqPay: badge',
        'text_uk': 'Без комісії · миттєве зарахування',
        'text_en': 'No fee · instant settlement',
    },
    ('shipping', 'card_cod_badge'): {
        'label': 'COD: badge',
        'text_uk': 'При отриманні',
        'text_en': 'On delivery',
    },
    ('shipping', 'card_iban_badge'): {
        'label': 'IBAN: badge',
        'text_uk': 'Для шкіл і ФОП',
        'text_en': 'For schools & businesses',
    },
    ('shipping', 'pay_badges_aria'): {
        'label': 'Pay badges aria',
        'text_uk': 'Підтримувані способи оплати',
        'text_en': 'Supported payment methods',
    },
    ('shipping', 'packaging_card_title'): {
        'label': 'Пакування: картка title',
        'text_uk': 'Захист клавірів і збірок',
        'text_en': 'Protection for scores and collections',
    },
    # --- contacts extras ---
    ('contacts', 'aside_aria'): {
        'label': 'Aside aria',
        'text_uk': 'Контактна інформація',
        'text_en': 'Contact information',
    },
    ('contacts', 'topic_order'): {
        'label': 'Тема: замовлення',
        'text_uk': 'Питання по замовленню',
        'text_en': 'Order inquiry',
    },
    ('contacts', 'topic_sheet'): {
        'label': 'Тема: пошук нот',
        'text_uk': 'Пошук нот',
        'text_en': 'Sheet music search',
    },
    # --- cart extras ---
    ('cart', 'qty_unit'): {
        'label': 'Од. кількості',
        'text_uk': 'шт.',
        'text_en': 'pcs',
    },
    ('cart', 'items_aria'): {
        'label': 'Товари aria',
        'text_uk': 'Товари в кошику',
        'text_en': 'Cart items',
    },
    ('cart', 'buy'): {
        'label': 'Купити',
        'text_uk': 'Купити',
        'text_en': 'Buy',
    },
    ('cart', 'add'): {
        'label': 'Додати',
        'text_uk': 'Додати',
        'text_en': 'Add',
    },
    # --- checkout extras ---
    ('checkout', 'total_label'): {
        'label': 'Разом',
        'text_uk': 'До сплати',
        'text_en': 'Amount due',
    },
    ('checkout', 'np_city_label'): {
        'label': 'НП: місто',
        'text_uk': 'Пошук міста НП',
        'text_en': 'Search Nova Poshta city',
    },
    ('checkout', 'np_warehouse_label'): {
        'label': 'НП: відділення',
        'text_uk': 'Відділення / поштомат',
        'text_en': 'Branch / parcel locker',
    },
    ('checkout', 'liqpay_redirect_title'): {
        'label': 'LiqPay redirect title',
        'text_uk': 'Переходимо до оплати',
        'text_en': 'Redirecting to payment',
    },
    ('checkout', 'liqpay_redirect_text'): {
        'label': 'LiqPay redirect text',
        'text_uk': 'Зачекайте, відкривається захищений шлюз LiqPay…',
        'text_en': 'Please wait — opening the secure LiqPay gateway…',
    },
    ('checkout', 'payment_retry_title'): {
        'label': 'Retry title',
        'text_uk': 'Повторити оплату',
        'text_en': 'Retry payment',
    },
    ('checkout', 'payment_retry_text'): {
        'label': 'Retry text',
        'text_uk': 'Оплату не завершено. Спробуйте ще раз.',
        'text_en': 'Payment was not completed. Please try again.',
    },
    ('checkout', 'payment_retry_btn'): {
        'label': 'Retry button',
        'text_uk': 'Сплатити знову',
        'text_en': 'Pay again',
    },
    ('checkout', 'stepper_aria'): {
        'label': 'Stepper aria',
        'text_uk': 'Етапи оформлення',
        'text_en': 'Checkout steps',
    },
    ('checkout', 'step_cart'): {
        'label': 'Крок: кошик',
        'text_uk': 'Кошик',
        'text_en': 'Cart',
    },
    ('checkout', 'step_checkout'): {
        'label': 'Крок: оформлення',
        'text_uk': 'Оформлення',
        'text_en': 'Checkout',
    },
    ('checkout', 'step_pay'): {
        'label': 'Крок: оплата',
        'text_uk': 'Оплата та Готово',
        'text_en': 'Pay & Done',
    },
    ('checkout', 'contact_heading'): {
        'label': 'Контактні дані',
        'text_uk': 'Контактні дані',
        'text_en': 'Contact details',
    },
    ('checkout', 'email_hint'): {
        'label': 'Email hint',
        'text_uk': 'Для доступу до PDF та статусу замовлення',
        'text_en': 'For PDF access and order status updates',
    },
    ('checkout', 'shipping_heading'): {
        'label': 'Доставка',
        'text_uk': 'Спосіб доставки',
        'text_en': 'Shipping method',
    },
    ('checkout', 'payment_heading'): {
        'label': 'Оплата',
        'text_uk': 'Спосіб оплати',
        'text_en': 'Payment method',
    },
    ('checkout', 'payment_liqpay'): {
        'label': 'LiqPay title',
        'text_uk': 'Онлайн-оплата карткою / LiqPay',
        'text_en': 'Online card payment / LiqPay',
    },
    ('checkout', 'payment_liqpay_hint'): {
        'label': 'LiqPay hint',
        'text_uk': 'Безпечна оплата на захищеному шлюзі',
        'text_en': 'Secure payment via encrypted gateway',
    },
    ('checkout', 'comment_toggle'): {
        'label': 'Коментар toggle',
        'text_uk': 'Коментар до доставки (необовʼязково)',
        'text_en': 'Delivery comment (optional)',
    },
    ('checkout', 'edit_cart'): {
        'label': 'Змінити кошик',
        'text_uk': 'Змінити кошик',
        'text_en': 'Edit cart',
    },
    ('checkout', 'subtotal_label'): {
        'label': 'Сума замовлення',
        'text_uk': 'Сума замовлення',
        'text_en': 'Order subtotal',
    },
    ('checkout', 'shipping_label'): {
        'label': 'Доставка label',
        'text_uk': 'Доставка',
        'text_en': 'Shipping',
    },
    ('checkout', 'shipping_carrier'): {
        'label': 'Тариф перевізника',
        'text_uk': 'За тарифами перевізника',
        'text_en': 'Carrier rates apply',
    },
    ('checkout', 'trust_aria'): {
        'label': 'Trust aria',
        'text_uk': 'Гарантії безпеки',
        'text_en': 'Trust & security',
    },
    ('checkout', 'trust_ssl'): {
        'label': 'SSL badge',
        'text_uk': 'SSL Encryption — захищена передача даних',
        'text_en': 'SSL Encryption — secure data transfer',
    },
    ('checkout', 'trust_pack'): {
        'label': 'Packaging badge',
        'text_uk': '100% Гарантія надійної упаковки нот',
        'text_en': '100% reliable sheet music packaging guarantee',
    },
    # --- thank you extras ---
    ('thank_you', 'order_number'): {
        'label': 'Номер замовлення',
        'text_uk': 'Номер',
        'text_en': 'Number',
    },
    ('thank_you', 'payment_status'): {
        'label': 'Статус оплати',
        'text_uk': 'Статус оплати',
        'text_en': 'Payment status',
    },
    # --- cabinet extras ---
    ('cabinet', 'logout'): {
        'label': 'Вийти',
        'text_uk': 'Вийти',
        'text_en': 'Sign out',
    },
    ('cabinet', 'nav_aria'): {
        'label': 'Nav aria',
        'text_uk': 'Навігація кабінету',
        'text_en': 'Account navigation',
    },
    ('cabinet', 'wishlist_add'): {
        'label': 'В обране',
        'text_uk': 'В обране',
        'text_en': 'Add to wishlist',
    },
    ('cabinet', 'wishlist_added'): {
        'label': 'В обраному',
        'text_uk': 'В обраному',
        'text_en': 'In wishlist',
    },
}

"""Extra SiteBlock defaults (shipping, contacts, catalog, commerce, cabinet)."""

from __future__ import annotations

from typing import Any

BLOCK_DEFAULTS_EXTRA: dict[tuple[str, str], dict[str, Any]] = {
    # --- shipping ---
    ('shipping', 'title'): {
        'label': 'Заголовок',
        'text_uk': 'Доставка та оплата 🎼',
        'text_en': 'Shipping & payment 🎼',
    },
    ('shipping', 'subtitle'): {
        'label': 'Підзаголовок',
        'text_uk': (
            'Доставляємо друковані ноти Новою Поштою по всій Україні. '
            'Оплата онлайн через захищений шлюз LiqPay.'
        ),
        'text_en': (
            'We ship printed scores via Nova Poshta across Ukraine. '
            'Online payment via LiqPay.'
        ),
    },
    ('shipping', 'subtitle_with_pickup'): {
        'label': 'Підзаголовок (з самовивозом)',
        'text_uk': (
            'Доставляємо друковані ноти Новою Поштою по всій Україні. '
            'Самовивіз — з нашого шоуруму в Києві після підтвердження замовлення.'
        ),
        'text_en': (
            'We ship printed scores via Nova Poshta across Ukraine. '
            'Pickup from our Kyiv showroom after order confirmation.'
        ),
    },
    ('shipping', 'trust_badge'): {
        'label': 'Trust ribbon',
        'text_uk': 'НП',
        'text_en': 'NP',
    },
    ('shipping', 'trust_title'): {
        'label': 'Trust: заголовок',
        'text_uk': 'Надійна доставка Новою Поштою',
        'text_en': 'Reliable Nova Poshta shipping',
    },
    ('shipping', 'trust_text'): {
        'label': 'Trust: текст',
        'text_uk': 'Пакуємо ноти так, щоб вони прибули без пошкоджень.',
        'text_en': 'We pack scores so they arrive undamaged.',
    },
    ('shipping', 'delivery_title'): {
        'label': 'Доставка: заголовок',
        'text_uk': 'Способи доставки',
        'text_en': 'Delivery methods',
    },
    ('shipping', 'delivery_lead'): {
        'label': 'Доставка: лід',
        'text_uk': 'Оберіть зручний спосіб отримання замовлення.',
        'text_en': 'Choose a convenient way to receive your order.',
    },
    ('shipping', 'card_np_branch_badge'): {
        'label': 'НП відділення: badge',
        'text_uk': 'Популярне',
        'text_en': 'Popular',
    },
    ('shipping', 'card_np_branch_title'): {
        'label': 'НП відділення: title',
        'text_uk': 'Відділення Нової Пошти',
        'text_en': 'Nova Poshta branch',
    },
    ('shipping', 'card_np_branch_text'): {
        'label': 'НП відділення: text',
        'text_uk': 'Доставка у будь-яке відділення по Україні. Термін — 1–3 дні.',
        'text_en': 'Delivery to any branch in Ukraine. 1–3 days.',
    },
    ('shipping', 'card_np_parcel_title'): {
        'label': 'Поштомат: title',
        'text_uk': 'Поштомат Нової Пошти',
        'text_en': 'Nova Poshta parcel locker',
    },
    ('shipping', 'card_np_parcel_text'): {
        'label': 'Поштомат: text',
        'text_uk': 'Заберіть посилку з поштомату у зручний час.',
        'text_en': 'Pick up your parcel from a locker at a convenient time.',
    },
    ('shipping', 'card_pickup_title'): {
        'label': 'Самовивіз: title',
        'text_uk': 'Самовивіз',
        'text_en': 'Pickup',
    },
    ('shipping', 'card_pickup_text'): {
        'label': 'Самовивіз: text',
        'text_uk': 'Заберіть замовлення з шоуруму після підтвердження.',
        'text_en': 'Pick up from the showroom after confirmation.',
    },
    ('shipping', 'payment_title'): {
        'label': 'Оплата: заголовок',
        'text_uk': 'Способи оплати',
        'text_en': 'Payment methods',
    },
    ('shipping', 'payment_lead'): {
        'label': 'Оплата: лід',
        'text_uk': (
            'Безпечні варіанти для приватних покупців і музичних шкіл. '
            'Безпечна онлайн-оплата через захищений шлюз LiqPay.'
        ),
        'text_en': (
            'Safe options for private buyers and music schools. '
            'Secure online payment via the LiqPay gateway.'
        ),
    },
    ('shipping', 'card_liqpay_title'): {
        'label': 'LiqPay: title',
        'text_uk': 'Онлайн-оплата карткою / LiqPay',
        'text_en': 'Online card payment / LiqPay',
    },
    ('shipping', 'card_liqpay_text'): {
        'label': 'LiqPay: text',
        'text_uk': (
            'Visa, Mastercard, Apple Pay та Google Pay через захищений шлюз LiqPay.'
        ),
        'text_en': (
            'Visa, Mastercard, Apple Pay and Google Pay via the secure LiqPay gateway.'
        ),
    },
    ('shipping', 'card_cod_title'): {
        'label': 'Накладений: title',
        'text_uk': 'Накладений платіж',
        'text_en': 'Cash on delivery',
    },
    ('shipping', 'card_cod_text'): {
        'label': 'Накладений: text',
        'text_uk': (
            'Оплата готівкою або карткою у відділенні / поштоматі Нової Пошти. '
            'Може стягуватись комісія перевізника за переказ коштів.'
        ),
        'text_en': (
            'Pay in cash or by card at a Nova Poshta branch / locker. '
            'The carrier may charge a cash-on-delivery fee.'
        ),
    },
    ('shipping', 'card_iban_title'): {
        'label': 'IBAN: title',
        'text_uk': 'Оплата за реквізитами (IBAN / ФОП)',
        'text_en': 'Bank transfer (IBAN / sole proprietor)',
    },
    ('shipping', 'card_iban_text'): {
        'label': 'IBAN: text',
        'text_uk': (
            'Зручно для музичних шкіл, академій і корпоративних замовлень. '
            'Реквізити надішлемо після оформлення або за запитом.'
        ),
        'text_en': (
            'Convenient for music schools, academies and corporate orders. '
            'We send bank details after checkout or on request.'
        ),
    },
    ('shipping', 'packaging_title'): {
        'label': 'Пакування: title',
        'text_uk': 'Надійна упаковка нот',
        'text_en': 'Reliable sheet music packaging',
    },
    ('shipping', 'packaging_text'): {
        'label': 'Пакування: text',
        'text_uk': (
            'Ми використовуємо щільні картонні конверти та пупирчасту плівку, '
            'щоб нотні збірки та клавіри приїхали без жодного залому.'
        ),
        'text_en': (
            'We use sturdy cardboard mailers and bubble wrap so scores '
            'and collections arrive without creases.'
        ),
    },
    ('shipping', 'faq_title'): {
        'label': 'FAQ: title',
        'text_uk': 'Часті запитання',
        'text_en': 'FAQ',
    },
    ('shipping', 'faq_1_q'): {
        'label': 'FAQ 1: питання',
        'text_uk': 'Як швидко відправляється замовлення?',
        'text_en': 'How quickly is an order shipped?',
    },
    ('shipping', 'faq_1_a'): {
        'label': 'FAQ 1: відповідь',
        'text_uk': (
            'Зазвичай відправляємо протягом 1–2 робочих днів після підтвердження '
            'оплати через LiqPay. Для інших способів оплати — після узгодження платежу. '
            'У пікові сезони термін може становити до 3 робочих днів.'
        ),
        'text_en': (
            'We usually ship within 1–2 business days after LiqPay payment confirmation. '
            'For other payment methods — after payment is confirmed. '
            'In peak seasons it may take up to 3 business days.'
        ),
    },
    ('shipping', 'faq_2_q'): {
        'label': 'FAQ 2: питання',
        'text_uk': 'Як відстежити посилку Нової Пошти?',
        'text_en': 'How do I track a Nova Poshta parcel?',
    },
    ('shipping', 'faq_2_a'): {
        'label': 'FAQ 2: відповідь',
        'text_uk': (
            'Після відправлення надішлемо номер ТТН на email або в SMS. '
            'Статус посилки можна перевірити на сайті чи в застосунку Нової Пошти. '
            'У кабінеті NotenHaus також відображається статус замовлення.'
        ),
        'text_en': (
            'After dispatch we send the tracking number by email or SMS. '
            'You can check the parcel status on the Nova Poshta website or app. '
            'Your NotenHaus account also shows the order status.'
        ),
    },
    ('shipping', 'faq_3_q'): {
        'label': 'FAQ 3: питання',
        'text_uk': 'Чи можна повернути нотне видання?',
        'text_en': 'Can I return a sheet music edition?',
    },
    ('shipping', 'faq_3_a'): {
        'label': 'FAQ 3: відповідь',
        'text_uk': (
            'Так. Відповідно до Закону України «Про захист прав споживачів» '
            'ви можете повернути товар належної якості протягом 14 днів, '
            'якщо нотне видання не використовувалось, збережено товарний вигляд, '
            'упаковку та чек / підтвердження покупки. Вартість зворотної доставки '
            'сплачує покупець, окрім випадків браку чи помилки продавця.'
        ),
        'text_en': (
            'Yes. Under Ukrainian consumer protection law you may return unused goods '
            'of proper quality within 14 days if the edition was not used and the '
            'original condition, packaging and receipt / purchase confirmation are kept. '
            'The buyer pays return shipping, except for defects or seller error.'
        ),
    },
    ('shipping', 'meta_description'): {
        'label': 'SEO description',
        'text_uk': 'Доставка нот Новою Поштою та оплата LiqPay',
        'text_en': 'Nova Poshta shipping and LiqPay payment',
    },
    # --- contacts ---
    ('contacts', 'title'): {
        'label': 'Заголовок',
        'text_uk': 'Контакти',
        'text_en': 'Contacts',
    },
    ('contacts', 'subtitle'): {
        'label': 'Підзаголовок',
        'text_uk': 'Напишіть нам — відповімо протягом робочого дня.',
        'text_en': 'Write to us — we reply within a business day.',
    },
    ('contacts', 'card_phone_title'): {
        'label': 'Картка: телефон',
        'text_uk': 'Телефон',
        'text_en': 'Phone',
    },
    ('contacts', 'card_email_title'): {
        'label': 'Картка: email',
        'text_uk': 'Email',
        'text_en': 'Email',
    },
    ('contacts', 'card_hours_title'): {
        'label': 'Картка: години',
        'text_uk': 'Години роботи',
        'text_en': 'Opening hours',
    },
    ('contacts', 'maps_label'): {
        'label': 'Google Maps',
        'text_uk': 'Відкрити в Google Maps',
        'text_en': 'Open in Google Maps',
    },
    ('contacts', 'form_topic_legend'): {
        'label': 'Форма: тема',
        'text_uk': 'Тема звернення',
        'text_en': 'Topic',
    },
    ('contacts', 'submit'): {
        'label': 'Форма: кнопка',
        'text_uk': 'Надіслати',
        'text_en': 'Send',
    },
    ('contacts', 'success'): {
        'label': 'Успіх',
        'text_uk': 'Повідомлення надіслано!',
        'text_en': 'Message sent!',
    },
    ('contacts', 'meta_description'): {
        'label': 'SEO description',
        'text_uk': 'Контакти NotenHaus',
        'text_en': 'NotenHaus contacts',
    },
    # --- catalog ---
    ('catalog', 'title'): {
        'label': 'Заголовок',
        'text_uk': 'Каталог нот',
        'text_en': 'Sheet music catalog',
    },
    ('catalog', 'lead'): {
        'label': 'Лід',
        'text_uk': 'Нотні видання з фільтрами за інструментом, жанром і рівнем.',
        'text_en': 'Sheet music with filters by instrument, genre and level.',
    },
    ('catalog', 'filters_label'): {
        'label': 'Фільтри',
        'text_uk': 'Фільтри',
        'text_en': 'Filters',
    },
    ('catalog', 'sort_popular'): {
        'label': 'Сорт: популярні',
        'text_uk': 'Популярні',
        'text_en': 'Popular',
    },
    ('catalog', 'sort_new'): {
        'label': 'Сорт: новинки',
        'text_uk': 'Новинки',
        'text_en': 'New',
    },
    ('catalog', 'sort_price_asc'): {
        'label': 'Сорт: ціна ↑',
        'text_uk': 'Ціна ↑',
        'text_en': 'Price ↑',
    },
    ('catalog', 'sort_price_desc'): {
        'label': 'Сорт: ціна ↓',
        'text_uk': 'Ціна ↓',
        'text_en': 'Price ↓',
    },
    ('catalog', 'filter_composer'): {
        'label': 'Фільтр: композитор',
        'text_uk': 'Композитор',
        'text_en': 'Composer',
    },
    ('catalog', 'filter_instrument'): {
        'label': 'Фільтр: інструмент',
        'text_uk': 'Інструмент',
        'text_en': 'Instrument',
    },
    ('catalog', 'filter_genre'): {
        'label': 'Фільтр: жанр',
        'text_uk': 'Жанр',
        'text_en': 'Genre',
    },
    ('catalog', 'filter_all'): {
        'label': 'Фільтр: усі',
        'text_uk': 'Усі',
        'text_en': 'All',
    },
    ('catalog', 'add_to_cart'): {
        'label': 'PDP: до кошика',
        'text_uk': 'До кошика',
        'text_en': 'Add to cart',
    },
    ('catalog', 'in_stock'): {
        'label': 'PDP: в наявності',
        'text_uk': 'В наявності',
        'text_en': 'In stock',
    },
    ('catalog', 'composer_label'): {
        'label': 'PDP: композитор',
        'text_uk': 'Композитор',
        'text_en': 'Composer',
    },
    ('catalog', 'preview_label'): {
        'label': 'PDP: превʼю',
        'text_uk': 'Превʼю нот',
        'text_en': 'Score preview',
    },
    # --- search ---
    ('search', 'title'): {
        'label': 'Заголовок',
        'text_uk': 'Пошук',
        'text_en': 'Search',
    },
    ('search', 'placeholder'): {
        'label': 'Placeholder',
        'text_uk': 'Введіть назву, композитора…',
        'text_en': 'Enter title, composer…',
    },
    ('search', 'submit'): {
        'label': 'Кнопка',
        'text_uk': 'Знайти',
        'text_en': 'Search',
    },
    ('search', 'empty_title'): {
        'label': 'Empty: title',
        'text_uk': 'Нічого не знайдено',
        'text_en': 'Nothing found',
    },
    ('search', 'empty_text'): {
        'label': 'Empty: text',
        'text_uk': 'Спробуйте інший запит або перейдіть у каталог.',
        'text_en': 'Try another query or browse the catalog.',
    },
    # --- cart chrome (CartPageSettings covers empty/recommend; this is summary UI) ---
    ('cart', 'title'): {
        'label': 'Заголовок',
        'text_uk': 'Кошик',
        'text_en': 'Cart',
    },
    ('cart', 'summary_heading'): {
        'label': 'Підсумок: heading',
        'text_uk': 'Підсумок',
        'text_en': 'Summary',
    },
    ('cart', 'summary_items'): {
        'label': 'Підсумок: товарів',
        'text_uk': 'Товарів',
        'text_en': 'Items',
    },
    ('cart', 'summary_total'): {
        'label': 'Підсумок: разом',
        'text_uk': 'Разом',
        'text_en': 'Total',
    },
    ('cart', 'remove_label'): {
        'label': 'Видалити',
        'text_uk': 'Видалити',
        'text_en': 'Remove',
    },
    # --- checkout ---
    ('checkout', 'title'): {
        'label': 'Заголовок',
        'text_uk': 'Оформлення замовлення',
        'text_en': 'Checkout',
    },
    ('checkout', 'order_heading'): {
        'label': 'Ваше замовлення',
        'text_uk': 'Ваше замовлення',
        'text_en': 'Your order',
    },
    ('checkout', 'submit'): {
        'label': 'Кнопка',
        'text_uk': 'Підтвердити замовлення',
        'text_en': 'Place order',
    },
    # --- thank you ---
    ('thank_you', 'title'): {
        'label': 'Заголовок',
        'text_uk': 'Дякуємо за замовлення',
        'text_en': 'Thank you for your order',
    },
    ('thank_you', 'text'): {
        'label': 'Текст',
        'text_uk': 'Ми надіслали підтвердження на вашу електронну пошту.',
        'text_en': 'We sent a confirmation to your email.',
    },
    # --- cabinet ---
    ('cabinet', 'nav_dashboard'): {
        'label': 'Nav: кабінет',
        'text_uk': 'Кабінет',
        'text_en': 'Account',
    },
    ('cabinet', 'nav_orders'): {
        'label': 'Nav: замовлення',
        'text_uk': 'Замовлення',
        'text_en': 'Orders',
    },
    ('cabinet', 'nav_wishlist'): {
        'label': 'Nav: обране',
        'text_uk': 'Обране',
        'text_en': 'Wishlist',
    },
    ('cabinet', 'nav_profile'): {
        'label': 'Nav: профіль',
        'text_uk': 'Профіль',
        'text_en': 'Profile',
    },
    ('cabinet', 'login_title'): {
        'label': 'Login title',
        'text_uk': 'Вхід',
        'text_en': 'Sign in',
    },
    ('cabinet', 'register_title'): {
        'label': 'Register title',
        'text_uk': 'Реєстрація',
        'text_en': 'Register',
    },
}

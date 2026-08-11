# NotenHaus — схема БД (tables.md)

**Версія:** 1.1 · **Дата:** 2026-07-27 · **Статус lock:** APPROVED  
**Джерела:** `Технічне завдання Шевчук.docx` · `notenhausSitemap.pdf` v1.0  
**Регламент:** Prometey `ecommerce_db_schema_skill` + `ecommerce-db-schema-reference`  
**Стек:** Django 5+ · PostgreSQL · UA default + EN (`/en/…`) · оплата **LiqPay** · email **Resend**

---

## 0. Scratchpad / lock (затверджено)

| Тема | Рішення |
|---|---|
| Ціна | лише `price_uah` |
| Level / Format | **CRUD-довідники** в адмінці (`catalog_level`, `catalog_format`) |
| Асортимент | **тільки папір**; digital / e-копії / видача файлу — **поза scope** |
| Instrument / Genre | **окремі** таблиці + M2M (не одне дерево `category.kind`) |
| Оплата | **LiqPay** only |
| i18n | колонки `*_uk` / `*_en` (два поля в адмінці; без parler) |
| Медіа | `ImageField` / `FileField` |
| Email | **Resend** для всіх листів з ТЗ (див. §3.17 / §5) |
| SMS | згадка в ТЗ §5.2 — **поза MVP** (не Resend) |
| Roadmap ядра | M0–M2 (+ admin CRUD, M4 SEO-поля) |
| Поза ядром | M5+: промокоди, відгуки |
| M5 unlock (2026-07-27) | Кабінет клієнта + Обране (wishlist) — app `cabinet`, email+пароль auth, guest checkout лишається (§10) |

`core` — shared kernel mixins лише (`TimeStampedModel`, `SeoFieldsMixin`), не app зі схеми.

---

## 1. Apps

| App | Відповідальність |
|---|---|
| `catalog` | product, composer, instrument, genre, level, format, media, M2M |
| `commerce` | cart, order, order_item, status_log |
| `payments` | LiqPay callback events / idempotency |
| `shipping` | MVP = поля НП на order; TTN — backlog |
| `content` | pages, contact_lead, site_settings |
| `notifications` | сервіс Resend (таблиця логів опційно); шаблони в коді |
| `seo` | redirect_301 за потреби |
| `cabinet` | M5: профіль клієнта, wishlist, login/register (не `accounts` — назва зафіксована) |
| ~~`pricing`~~ | не створюємо |

---

## 2. ER

```
catalog_composer ──── 1:M ──── catalog_product
catalog_level    ──── 1:M ──── catalog_product
catalog_format   ──── 1:M ──── catalog_product
catalog_instrument ── M:M ──── catalog_product   (product_instrument)
catalog_genre    ──── M:M ──── catalog_product   (product_genre)
catalog_product  ──── 1:M ──── catalog_product_image
catalog_product  ──── 1:M ──── catalog_product_file   (preview only)

commerce_cart    ──── 1:M ──── commerce_cart_item → product
commerce_order   ──── 1:M ──── commerce_order_item (snapshot)
commerce_order   ──── 1:M ──── commerce_order_status_log
commerce_order   ──── 1:M ──── payments_event
auth_user        ──── 1:M ──── commerce_order            (order.user, nullable — guest лишається)
auth_user        ──── 1:1 ──── cabinet_customer_profile
auth_user        ──── 1:M ──── cabinet_wishlist_item ──── M:1 ──── catalog_product

content_page · content_contact_lead · content_site_settings
notifications_email_log  (Resend audit)
```

Кошик: `session_key`, без User. Покупець — guest snapshot на order; якщо клієнт залогінений під час checkout, `order.user` заповнюється додатково до snapshot-полів (§10).

URL `/katalog/{slug}/`: resolve slug у `instrument` **або** `genre` (unique slug у кожній таблиці; конфлікт між таблицями — валідація на save).

---

## 3. Таблиці ядра

Типи: `PK` bigserial · гроші `numeric(12,2)` · slug `varchar(160)` · timestamps через mixin.

### 3.0. Спільний патерн довідника (composer / instrument / genre / level / format)

Базові колонки для CRUD-сутностей фільтрів:

| Колонка | Тип | Null | Примітка |
|---|---|---|---|
| id | PK | | |
| name_uk | varchar(255) | | обовʼязкове |
| name_en | varchar(255) | ✓ | друге поле в адмінці |
| slug | varchar(160) | | unique в таблиці; URL-фільтр |
| is_active | bool | | default true |
| sort_order | int | | default 0 |
| created_at / updated_at | timestamptz | | |

Таблиці з цим патерном:

| Таблиця | Фільтр URL | Додатково |
|---|---|---|
| `catalog_composer` | `?composer=` | FK на product |
| `catalog_instrument` | `?instrument=` + `/katalog/{slug}/` | M2M |
| `catalog_genre` | `?genre=` + `/katalog/{slug}/` | M2M |
| `catalog_level` | `?level=` | FK на product |
| `catalog_format` | (характеристика PDP) | FK на product; лише паперові формати |

`instrument` / `genre` додатково: `seo_title` / `seo_description` (SeoFieldsMixin) для ЧПУ-сторінок каталогу.

---

### 3.1. `catalog_product` (нота, папір)

| Колонка | Тип | Null | Примітка |
|---|---|---|---|
| id | PK | | |
| sku | varchar(64) | | unique; пошук |
| slug | varchar(160) | | unique → `/nota/{slug}/` |
| name_uk / name_en | varchar(255) | en✓ | |
| composer_id | FK → composer | ✓ | |
| level_id | FK → level | ✓ | |
| format_id | FK → format | ✓ | паперовий формат видання |
| description_uk / description_en | text | ✓ | |
| price_uah | numeric(12,2) | | ≥ 0 |
| stock_qty | int | | ≥ 0; наявність = `stock_qty > 0` |
| is_published | bool | | |
| is_popular | bool | | «Популярні ноти» |
| is_new | bool | | «Новинки» |
| badge_text | varchar(32) | ✓ | mock-стрічка на обкладинці (NEW / OFFER…) |
| badge_tone | varchar(16) | ✓ | yellow \| maroon \| blue \| gold |
| published_at | timestamptz | ✓ | |
| seo_title / seo_description | | ✓ | |
| created_at / updated_at | | | |

Індекси: `(is_published, published_at DESC)`, `(is_popular)`, `(is_new)`, `(composer_id)`, `(level_id)`, `(format_id)`.  
Check: `price_uah >= 0`, `stock_qty >= 0`.

### 3.2. `catalog_product_instrument` / `catalog_product_genre`

| Колонка | Тип |
|---|---|
| id | PK |
| product_id | FK product |
| instrument_id **або** genre_id | FK |
| Unique(product_id, *_id) | |

### 3.3. `catalog_product_image`

| Колонка | Тип | Null | Примітка |
|---|---|---|---|
| id | PK | | |
| product_id | FK | | |
| image | varchar(512) | | ImageField |
| alt_uk / alt_en | varchar(255) | ✓ | |
| is_main | bool | | обкладинка |
| sort_order | int | | |
| created_at | | | |

Partial unique: один `is_main=true` на product.

### 3.4. `catalog_product_file`

| Колонка | Тип | Null | Примітка |
|---|---|---|---|
| id | PK | | |
| product_id | FK | | |
| kind | varchar(20) | | лише `preview` (фрагмент нот на PDP) |
| file | varchar(512) | | FileField |
| title_uk / title_en | varchar(255) | ✓ | |
| sort_order | int | | |
| created_at | | | |

**Немає** `kind=full` / digital delivery.

---

### 3.5. `commerce_cart`

| Колонка | Тип | Примітка |
|---|---|---|
| id | PK | |
| session_key | varchar(40) | indexed |
| status | varchar(20) | `active` \| `converted` \| `abandoned` |
| created_at / updated_at | | |

Partial index: `(session_key)` where `status='active'`.

### 3.6. `commerce_cart_item`

| Колонка | Тип | Примітка |
|---|---|---|
| id | PK | |
| cart_id | FK cascade | |
| product_id | FK restrict | |
| qty | int | ≥ 1 |
| unit_price_uah | numeric(12,2) | на момент додавання |
| Unique(cart_id, product_id) | | |

### 3.7. `commerce_order`

| Колонка | Тип | Null | Примітка |
|---|---|---|---|
| id | PK | | |
| number | varchar(32) | | unique |
| status | varchar(20) | | `new` \| `processing` \| `shipped` \| `completed` \| `cancelled` |
| payment_status | varchar(20) | | `awaiting` \| `paid` \| `failed` |
| customer_name | varchar(255) | | |
| customer_email | varchar(254) | | отримувач листів Resend |
| customer_phone | varchar(32) | | |
| customer_comment | text | ✓ | |
| shipping_method | varchar(20) | | `np_warehouse` \| `np_poshtomat` \| `pickup` |
| np_city_ref / np_city_name | varchar | ✓ | snapshot |
| np_warehouse_ref / np_warehouse_name | varchar | ✓ | |
| np_area_ref | varchar(64) | ✓ | |
| subtotal_uah / shipping_uah / total_uah | numeric(12,2) | | |
| payment_provider | varchar(20) | | default / always `liqpay` |
| payment_external_id | varchar(128) | ✓ | |
| paid_at | timestamptz | ✓ | |
| locale | varchar(5) | | `uk` \| `en` |
| cart_id | FK cart | ✓ | SET_NULL |
| created_at / updated_at | | | |

Індекси: `(status, created_at DESC)`, `(payment_status)`, `(number)`, `(customer_email)`, `(payment_external_id)`.

### 3.8. `commerce_order_item`

| Колонка | Тип | Null | Примітка |
|---|---|---|---|
| id | PK | | |
| order_id | FK cascade | | |
| product_id | FK | ✓ | SET_NULL |
| product_sku | varchar(64) | | snapshot |
| product_name | varchar(255) | | snapshot мовою замовлення |
| qty | int | | ≥ 1 |
| unit_price_uah / line_total_uah | numeric(12,2) | | |

### 3.9. `commerce_order_status_log`

| Колонка | Тип | Примітка |
|---|---|---|
| id | PK | |
| order_id | FK | |
| from_status | varchar(20) | ✓ |
| to_status | varchar(20) | fulfillment або `payment:*` |
| note | text | ✓ |
| actor_id | FK auth.User | ✓ null = system/webhook |
| created_at | | |

Зміна статусу → тригер Resend (ТЗ §5.2), якщо увімкнено в settings.

---

### 3.10. `payments_event`

| Колонка | Тип | Null | Примітка |
|---|---|---|---|
| id | PK | | |
| order_id | FK | | |
| provider | varchar(20) | | `liqpay` |
| event_type | varchar(40) | | `callback` \| `redirect_return` |
| external_id | varchar(128) | ✓ | |
| idempotency_key | varchar(128) | | unique |
| payload | jsonb | | без PAN/CVV |
| processed_ok | bool | | |
| created_at | | | |

Секрети LiqPay — **env**, не БД.

---

### 3.11. `content_page`

| Колонка | Тип | Null | Примітка |
|---|---|---|---|
| id | PK | | |
| slug | varchar(160) | | `pro-nas`, `dostavka-i-oplata`, … |
| title_uk / title_en | varchar(255) | | |
| body_uk / body_en | text | | |
| is_published | bool | | |
| seo_title / seo_description | | ✓ | |
| created_at / updated_at | | | |

### 3.12. `content_contact_lead`

| Колонка | Тип | Null | Примітка |
|---|---|---|---|
| id | PK | | |
| name | varchar(255) | ✓ | |
| phone | varchar(32) | | |
| email | varchar(254) | ✓ | |
| message | text | ✓ | |
| page_url | varchar(512) | ✓ | |
| is_processed | bool | | default false |
| created_at | | | |

Створення lead → Resend на email адміна (ТЗ §6.3).

### 3.13. `content_site_settings` (singleton id=1)

| Колонка | Тип | Null | Примітка |
|---|---|---|---|
| id | PK | | |
| site_name | varchar(255) | | |
| logo | varchar(512) | ✓ | ImageField |
| contacts_json | jsonb | | телефони, email вітрини, графік |
| admin_notify_email | varchar(254) | | отримувач службових листів |
| notify_customer_on_status | bool | | default true; ТЗ §5.2 |
| default_locale | varchar(5) | | `uk` |
| robots_txt | text | ✓ | |
| extra_json | jsonb | ✓ | |
| updated_at | | | |

### 3.13b. `content_active_theme` (singleton id=1)

Runtime-тема (`theme_switcher_skill`): hex-токени + шрифти → динамічний `/theme.css` (CSP `style-src 'self'`). Порожнє поле = дефолт з `static/css/colors.css`.

| Група | Поля |
|---|---|
| Фони | color_bg, color_bg_grey, color_header_bg/fg, color_footer_bg/fg |
| Текст | color_text, color_text_muted, color_link, color_focus, color_brand(_hover) |
| Кнопки | color_btn_cta(_hover), search, newsletter, ghost(+hover_bg) |
| Бейджі | color_badge_cart / yellow / maroon / blue / gold |
| Шрифти | font_heading, font_body (choices; Google Fonts за потреби) |
| Meta | updated_at |

Секрети: `RESEND_API_KEY`, `LIQPAY_*`, `NP_*` — лише env.

---

### 3.14. `notifications_email_log`

| Колонка | Тип | Null | Примітка |
|---|---|---|---|
| id | PK | | |
| to_email | varchar(254) | | |
| template_key | varchar(64) | | див. §5 |
| related_object_type | varchar(40) | ✓ | `order` \| `lead` |
| related_object_id | bigint | ✓ | |
| resend_id | varchar(128) | ✓ | id з Resend API |
| status | varchar(20) | | `queued` \| `sent` \| `failed` |
| error_message | text | ✓ | |
| created_at | | | |

Шаблони листів — **код** (HTML/text), не CRUD у БД MVP.

### 3.15. `seo_redirect_301` (опційно M4)

| old_path (unique) | new_path | is_active | created_at |

---

## 4. Enums у коді (не CRUD)

| Enum | Значення |
|---|---|
| CartStatus | active, converted, abandoned |
| OrderStatus | new, processing, shipped, completed, cancelled |
| PaymentStatus | awaiting, paid, failed |
| ShippingMethod | np_warehouse, np_poshtomat, pickup |
| PaymentProvider | liqpay |
| ProductFileKind | preview |
| SortPreset | price_asc, price_desc, new, popular, name |
| EmailTemplateKey | order_created_admin, lead_created_admin, order_status_customer |

`level` / `format` / instrument / genre / composer — **не** enums (CRUD).

---

## 5. Email через Resend (ТЗ)

| template_key | Тригер | Кому | ТЗ |
|---|---|---|---|
| `order_created_admin` | створення order | `admin_notify_email` | §3 checkout «надходять сповіщення» |
| `lead_created_admin` | AJAX `/kontakty/` | `admin_notify_email` | §6.3 |
| `order_status_customer` | зміна `order.status` (якщо flag) | `customer_email` | §5.2 |

Реалізація: `notifications` services → Resend API; запис у `notifications_email_log`.  
SMS з ТЗ — не входить у Resend-scope / MVP.

---

## 6. Backlog (не мігрувати в ядрі)

| Тема | Примітка |
|---|---|
| Промо / відгуки | M5+ |
| Кабінет / wishlist | **unlocked 2026-07-27** — див. §10 |
| Digital / full PDF після оплати | **скасовано lock** |
| TTN / np_sender | shipping_* пізніше |
| CRUD шаблонів листів | зараз код |
| SMS | окремий провайдер за потреби |
| pricing / multi-currency | ні |
| seo_meta_template / keywords | немає в ТЗ |

---

## 7. Verify-матриця v1.1

### Карта сайту

| Вимога | Покриття | Статус |
|---|---|---|
| `/katalog/`, `/katalog/{slug}/` | instrument.slug \| genre.slug | ✅ |
| Фільтри composer/instrument/genre/level | окремі CRUD + M2M/FK | ✅ |
| Сортування | SortPreset у коді | ✅ |
| PDP (обкладинка, превʼю, ціна, наявність, формат, інструмент) | product + image + file + format + instruments | ✅ |
| Пошук назва/артикул | name_*, sku | ✅ |
| Популярні / новинки | is_popular, is_new | ✅ |
| Інфо UA/EN | page *_uk/*_en | ✅ |
| Контакти + lead + email адміну | lead + Resend | ✅ |
| Кошик / checkout / НП | cart + order.np_* | ✅ |
| LiqPay success/fail/callback | payment_* + payments_event | ✅ |
| Статуси + лист клієнту | status_log + Resend | ✅ |
| Лише папір | немає digital shipping/file | ✅ |
| robots/sitemap | settings + код | ✅ |

### ТЗ §

| § | Покриття | Статус |
|---|---|---|
| 2.4 i18n | *_uk/*_en | ✅ |
| 3–4 вітрина/комерція | catalog + commerce | ✅ |
| 4.1 НП | order.np_* | ✅ |
| 4.2 оплата | LiqPay + payment_status | ✅ |
| 5.1 CRUD каталогу | composer/instrument/genre/level/format/product | ✅ |
| 5.2 статуси + notify | status_log + Resend | ✅ |
| 6.3 lead → email адміна | Resend | ✅ |

---

## 8. Чеклист здачі

- [x] Lock клієнта зафіксовано (§0)
- [x] Окремі instrument/genre; level/format CRUD
- [x] Без digital
- [x] LiqPay + Resend
- [x] i18n двома колонками
- [x] Verify §7 оновлено
- [x] `django_models_from_schema_skill` → models.py + migrate + db_table verify (2026-07-27)

---

## 9. Заборонено чіпати після approve (lock)

Без окремого рішення **не** додавати: digital delivery, pricing/currency, промокоди, відгуки, зміну провайдера оплати з LiqPay, заміну Resend, злиття instrument/genre в одну `category`.

Customer accounts **unlocked 2026-07-27** — див. §10 (окреме рішення прийнято).

---

## 10. M5 unlock — Кабінет клієнта (2026-07-27)

**Рішення:** повний кабінет (реєстрація/вхід, профіль, історія замовлень, Обране); auth — email+пароль через `django.contrib.auth.User` (`username` = email); guest checkout лишається — при логіні `Order.user` заповнюється додатково до snapshot-полів `customer_*`.

App: **`cabinet`** (не `accounts`).

| Таблиця | Колонки | Примітка |
|---|---|---|
| `cabinet_customer_profile` | `user_id` (1:1, PK=FK), `phone`, `display_name`, timestamps | префіл checkout |
| `cabinet_wishlist_item` | `id`, `user_id` (FK), `product_id` (FK `catalog_product`), `created_at` | `UniqueConstraint(user, product)` |
| `commerce_order.user_id` | FK `auth.User`, `null=True`, `on_delete=SET_NULL` | історія замовлень; guest без user лишається |

URL (UA-трансліт, у `i18n_patterns`): `/kabinet/`, `/kabinet/vkhid/`, `/kabinet/reyestratsiya/`, `/kabinet/vykhid/`, `/kabinet/profil/`, `/kabinet/zamovlennya/`, `/kabinet/zamovlennya/<number>/`, `/obrane/`, `/obrane/toggle/<product_id>/`.

Wishlist — лише для авторизованих (без session-кошика для anon). Кошик і його `session_key` не змінюються.

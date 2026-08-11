"""Checkout / thank-you payment method UI copy (COD + IBAN)."""

from __future__ import annotations

from typing import Any

BLOCK_DEFAULTS_PAY: dict[tuple[str, str], dict[str, Any]] = {
    ('checkout', 'pickup_hint'): {
        'label': 'Pickup hint',
        'text_uk': 'За попередньою домовленістю',
        'text_en': 'By prior arrangement',
    },
    ('checkout', 'pickup_notice_title'): {
        'label': 'Pickup notice title',
        'text_uk': 'Самовивіз з шоуруму',
        'text_en': 'Showroom pickup',
    },
    ('checkout', 'pickup_notice_text'): {
        'label': 'Pickup notice text',
        'text_uk': (
            'Заберіть замовлення після підтвердження. '
            'Ми звʼяжемось і узгодимо зручний час.'
        ),
        'text_en': (
            'Pick up after confirmation. '
            'We will contact you to arrange a convenient time.'
        ),
    },
    ('checkout', 'payment_cod'): {
        'label': 'COD title',
        'text_uk': 'Накладений платіж',
        'text_en': 'Cash on delivery',
    },
    ('checkout', 'payment_cod_hint'): {
        'label': 'COD hint',
        'text_uk': 'Оплата при отриманні у відділенні / поштоматі',
        'text_en': 'Pay on pickup at the branch / parcel locker',
    },
    ('checkout', 'payment_iban'): {
        'label': 'IBAN title',
        'text_uk': 'Оплата за реквізитами (IBAN / ФОП)',
        'text_en': 'Bank transfer (IBAN / sole proprietor)',
    },
    ('checkout', 'payment_iban_hint'): {
        'label': 'IBAN hint',
        'text_uk': 'Реквізити покажемо після підтвердження замовлення',
        'text_en': 'Bank details will be shown after you confirm the order',
    },
    ('thank_you', 'instructions_cod_title'): {
        'label': 'COD instructions title',
        'text_uk': 'Накладений платіж',
        'text_en': 'Cash on delivery',
    },
    ('thank_you', 'instructions_cod_text'): {
        'label': 'COD instructions',
        'text_uk': (
            'Оплатіть замовлення при отриманні у відділенні або поштоматі Нової Пошти. '
            'Ми надішлемо ТТН на email після збору посилки.'
        ),
        'text_en': (
            'Pay when you pick up the parcel at Nova Poshta. '
            'We will email the tracking number after dispatch.'
        ),
    },
    ('thank_you', 'instructions_iban_title'): {
        'label': 'IBAN instructions title',
        'text_uk': 'Оплата за реквізитами',
        'text_en': 'Bank transfer details',
    },
    ('thank_you', 'instructions_iban_text'): {
        'label': 'IBAN instructions',
        'text_uk': (
            'Перекажіть суму замовлення на рахунок нижче. '
            'Після надходження коштів ми відправимо ноти.'
        ),
        'text_en': (
            'Transfer the order total to the account below. '
            'We will ship after the payment clears.'
        ),
    },
    ('thank_you', 'iban_recipient_label'): {
        'label': 'IBAN label: recipient',
        'text_uk': 'Отримувач',
        'text_en': 'Recipient',
    },
    ('thank_you', 'iban_label'): {
        'label': 'IBAN label: IBAN',
        'text_uk': 'IBAN',
        'text_en': 'IBAN',
    },
    ('thank_you', 'iban_edrpou_label'): {
        'label': 'IBAN label: EDRPOU',
        'text_uk': 'ЄДРПОУ / ІПН',
        'text_en': 'Tax ID',
    },
    ('thank_you', 'iban_bank_label'): {
        'label': 'IBAN label: bank',
        'text_uk': 'Банк',
        'text_en': 'Bank',
    },
    ('thank_you', 'iban_purpose_label'): {
        'label': 'IBAN label: purpose',
        'text_uk': 'Призначення платежу',
        'text_en': 'Payment purpose',
    },
    ('thank_you', 'iban_amount_label'): {
        'label': 'IBAN label: amount',
        'text_uk': 'Сума',
        'text_en': 'Amount',
    },
    ('thank_you', 'iban_missing'): {
        'label': 'IBAN missing notice',
        'text_uk': (
            'Реквізити ще не заповнені в адмінці (Сайт → IBAN). '
            'Ми надішлемо їх на email після обробки замовлення.'
        ),
        'text_en': (
            'Bank details are not configured yet in admin (Site → IBAN). '
            'We will email them after processing the order.'
        ),
    },
}

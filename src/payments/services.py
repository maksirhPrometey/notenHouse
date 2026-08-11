"""LiqPay checkout + callback (tables.md §3.10)."""

from __future__ import annotations

import base64
import hashlib
import json
import logging
from typing import Any

from django.conf import settings
from django.db import transaction
from django.urls import reverse

from src.commerce.models import Order, PaymentStatus
from src.commerce.services import mark_order_paid

from .models import PaymentEvent, PaymentEventType, PaymentProvider

logger = logging.getLogger(__name__)


class PaymentError(Exception):
    pass


def _keys() -> tuple[str, str]:
    public = getattr(settings, 'LIQPAY_PUBLIC_KEY', '') or ''
    private = getattr(settings, 'LIQPAY_PRIVATE_KEY', '') or ''
    return public, private


def _encode_data(payload: dict) -> str:
    raw = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    return base64.b64encode(raw).decode('ascii')


def _sign(private_key: str, data_b64: str) -> str:
    digest = hashlib.sha1(
        (private_key + data_b64 + private_key).encode('utf-8')
    ).digest()
    return base64.b64encode(digest).decode('ascii')


def build_checkout_form(order: Order, request) -> dict[str, str]:
    """Повертає data/signature для POST на https://www.liqpay.ua/api/3/checkout."""
    public, private = _keys()
    if not public or not private:
        raise PaymentError('LiqPay ключі не налаштовані')

    result_url = request.build_absolute_uri(
        reverse('commerce:thank_you') + f'?order={order.number}'
    )
    server_url = request.build_absolute_uri(reverse('payments:callback'))
    payload = {
        'public_key': public,
        'version': 3,
        'action': 'pay',
        'amount': str(order.total_uah),
        'currency': 'UAH',
        'description': f'Замовлення {order.number}',
        'order_id': order.number,
        'result_url': result_url,
        'server_url': server_url,
        'language': 'uk' if order.locale == 'uk' else 'en',
    }
    data = _encode_data(payload)
    signature = _sign(private, data)
    return {
        'data': data,
        'signature': signature,
        'action': 'https://www.liqpay.ua/api/3/checkout',
    }


def decode_callback(data_b64: str, signature: str) -> dict[str, Any]:
    public, private = _keys()
    if not private:
        raise PaymentError('LiqPay private key missing')
    expected = _sign(private, data_b64)
    if not signature or expected != signature:
        raise PaymentError('Невірний підпис LiqPay')
    raw = base64.b64decode(data_b64.encode('ascii'))
    return json.loads(raw.decode('utf-8'))


@transaction.atomic
def handle_callback(*, data_b64: str, signature: str) -> Order:
    payload = decode_callback(data_b64, signature)
    order_number = str(payload.get('order_id') or '')
    status = str(payload.get('status') or '')
    payment_id = str(payload.get('payment_id') or payload.get('transaction_id') or '')
    idempotency = f'liqpay:{order_number}:{status}:{payment_id}'

    if PaymentEvent.objects.filter(idempotency_key=idempotency).exists():
        return Order.objects.get(number=order_number)

    order = Order.objects.select_for_update().filter(number=order_number).first()
    if order is None:
        raise PaymentError(f'Замовлення не знайдено: {order_number}')

    event = PaymentEvent.objects.create(
        order=order,
        provider=PaymentProvider.LIQPAY,
        event_type=PaymentEventType.CALLBACK,
        external_id=payment_id,
        idempotency_key=idempotency,
        payload=payload,
        processed_ok=False,
    )

    success_statuses = {'success', 'sandbox', 'wait_accept'}
    if status in success_statuses:
        mark_order_paid(order, external_id=payment_id)
        event.processed_ok = True
        event.save(update_fields=['processed_ok'])
    elif status in {'failure', 'error', 'reversed'}:
        if order.payment_status != PaymentStatus.PAID:
            order.payment_status = PaymentStatus.FAILED
            order.save(update_fields=['payment_status', 'updated_at'])
        event.processed_ok = True
        event.save(update_fields=['processed_ok'])
    else:
        # waiting / processing — лишаємо awaiting
        event.processed_ok = True
        event.save(update_fields=['processed_ok'])
    return order

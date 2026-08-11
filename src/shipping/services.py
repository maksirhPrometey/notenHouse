"""Nova Poshta Address API — міста / відділення (без ТТН у MVP)."""

from __future__ import annotations

import logging
from typing import Any

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

NP_API_URL = 'https://api.novaposhta.ua/v2.0/json/'


class NovaPoshtaError(Exception):
    pass


def _api_key() -> str:
    return getattr(settings, 'NP_API_KEY', '') or ''


def _call(model_name: str, method: str, props: dict[str, Any]) -> list[dict]:
    key = _api_key()
    if not key:
        raise NovaPoshtaError('NP_API_KEY не налаштовано')
    body = {
        'apiKey': key,
        'modelName': model_name,
        'calledMethod': method,
        'methodProperties': props,
    }
    try:
        resp = requests.post(NP_API_URL, json=body, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as exc:
        logger.exception('NP API network error')
        raise NovaPoshtaError('Помилка звʼязку з Новою Поштою') from exc
    if not data.get('success'):
        errors = data.get('errors') or data.get('errorCodes') or ['unknown']
        logger.error('NP API error: %s | body=%s', errors, data)
        raise NovaPoshtaError('; '.join(str(e) for e in errors))
    return data.get('data') or []


def search_cities(query: str, limit: int = 20) -> list[dict]:
    query = (query or '').strip()
    if len(query) < 2:
        return []
    rows = _call(
        'Address',
        'searchSettlements',
        {'CityName': query, 'Limit': str(limit)},
    )
    # searchSettlements wraps Addresses
    result = []
    for block in rows:
        for addr in block.get('Addresses') or []:
            result.append(
                {
                    'ref': addr.get('DeliveryCity') or addr.get('Ref') or '',
                    'name': addr.get('Present') or addr.get('MainDescription') or '',
                    'area': addr.get('Area') or '',
                    'area_ref': addr.get('Area') or '',
                }
            )
    if result:
        return result[:limit]
    # fallback getCities
    rows = _call(
        'Address',
        'getCities',
        {'FindByString': query, 'Page': '1', 'Limit': str(limit)},
    )
    return [
        {
            'ref': r.get('Ref', ''),
            'name': r.get('Description', ''),
            'area': r.get('AreaDescription', ''),
            'area_ref': r.get('Area', ''),
        }
        for r in rows
    ]


def get_warehouses(city_ref: str, query: str = '', limit: int = 50) -> list[dict]:
    city_ref = (city_ref or '').strip()
    if not city_ref:
        return []
    props: dict[str, Any] = {
        'CityRef': city_ref,
        'Page': '1',
        'Limit': str(limit),
    }
    if query.strip():
        props['FindByString'] = query.strip()
    rows = _call('Address', 'getWarehouses', props)
    return [
        {
            'ref': r.get('Ref', ''),
            'name': r.get('Description', ''),
            'number': r.get('Number', ''),
            'type': r.get('CategoryOfWarehouse', ''),
        }
        for r in rows
    ]

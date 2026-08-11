"""Default contacts_json schema for SiteSettings (editable in admin)."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

DEFAULT_CONTACTS: dict[str, Any] = {
    'phones': ['+380441112233'],
    'phone_display': '+380 44 111 22 33',
    'email': 'info@notenhaus.example',
    'email_response': 'Відповідаємо протягом 15 хвилин',
    'hours': 'Пн–Пт 10:00–18:00',
    'address': 'м. Київ, вул. Музична, 12',
    'maps_url': 'https://www.google.com/maps/search/?api=1&query=Київ+вул.+Музична+12',
    'viber': 'viber://chat?number=%2B380441112233',
    'telegram': 'https://t.me/notenhaus',
    'schedule': {
        'timezone': 'Europe/Kyiv',
        'days': [1, 2, 3, 4, 5],
        'open': '10:00',
        'close': '18:00',
    },
}

CONTACTS_JSON_HELP = (
    'JSON вітрини контактів. Ключі: phones (list), phone_display, email, '
    'email_response, hours, address, maps_url, viber, telegram, '
    'schedule: {timezone, days[1=Пн…7=Нд], open, close}.'
)


def merge_contacts(raw: dict[str, Any] | None) -> dict[str, Any]:
    """Merge DB contacts_json with defaults (DB wins on present keys)."""
    base = deepcopy(DEFAULT_CONTACTS)
    data = raw if isinstance(raw, dict) else {}
    schedule_in = data.get('schedule') if isinstance(data.get('schedule'), dict) else {}
    merged = {**base, **data}
    merged['schedule'] = {**base['schedule'], **schedule_in}
    phones = merged.get('phones')
    if not isinstance(phones, list) or not phones:
        merged['phones'] = list(base['phones'])
    if not merged.get('phone_display') and merged['phones']:
        merged['phone_display'] = str(merged['phones'][0])
    return merged

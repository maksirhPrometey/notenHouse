"""Resend email sending + EmailLog (tables.md §5)."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.conf import settings

from src.content.models import SiteSettings

from .models import EmailLog, EmailLogStatus, EmailTemplateKey

if TYPE_CHECKING:
    from src.commerce.models import Order
    from src.content.models import ContactLead

logger = logging.getLogger(__name__)


def _send_resend(*, to: str, subject: str, html: str, template_key: str, related_type: str = '', related_id: int | None = None) -> EmailLog:
    log = EmailLog.objects.create(
        to_email=to,
        template_key=template_key,
        related_object_type=related_type,
        related_object_id=related_id,
        status=EmailLogStatus.QUEUED,
    )
    api_key = getattr(settings, 'RESEND_API_KEY', '') or ''
    from_email = getattr(settings, 'RESEND_FROM_EMAIL', 'NotenHaus <noreply@example.com>')
    if not api_key:
        log.status = EmailLogStatus.FAILED
        log.error_message = 'RESEND_API_KEY not configured'
        log.save(update_fields=['status', 'error_message'])
        logger.warning('Resend skipped: no API key (%s)', template_key)
        return log
    try:
        import resend

        resend.api_key = api_key
        result = resend.Emails.send(
            {
                'from': from_email,
                'to': [to],
                'subject': subject,
                'html': html,
            }
        )
        resend_id = ''
        if isinstance(result, dict):
            resend_id = str(result.get('id') or '')
        else:
            resend_id = str(getattr(result, 'id', '') or '')
        log.resend_id = resend_id
        log.status = EmailLogStatus.SENT
        log.save(update_fields=['resend_id', 'status'])
    except Exception as exc:  # noqa: BLE001 — лог у БД
        logger.exception('Resend failed')
        log.status = EmailLogStatus.FAILED
        log.error_message = str(exc)[:2000]
        log.save(update_fields=['status', 'error_message'])
    return log


def notify_order_created_admin(order: Order) -> None:
    try:
        site = SiteSettings.load()
        to = site.admin_notify_email
        if not to:
            return
        html = (
            f'<p>Нове замовлення <strong>{order.number}</strong></p>'
            f'<p>{order.customer_name} · {order.customer_email} · {order.customer_phone}</p>'
            f'<p>Сума: {order.total_uah} UAH</p>'
        )
        _send_resend(
            to=to,
            subject=f'NotenHaus: замовлення {order.number}',
            html=html,
            template_key=EmailTemplateKey.ORDER_CREATED_ADMIN,
            related_type='order',
            related_id=order.pk,
        )
    except Exception:  # noqa: BLE001
        logger.exception('notify_order_created_admin failed')


def notify_lead_created_admin(lead: ContactLead) -> None:
    try:
        site = SiteSettings.load()
        to = site.admin_notify_email
        if not to:
            return
        topic = lead.get_topic_display() if lead.topic else '—'
        html = (
            f'<p>Звернення з форми контактів</p>'
            f'<p>Тема: {topic}</p>'
            f'<p>{lead.name} · {lead.phone} · {lead.email}</p>'
            f'<p>{lead.message}</p>'
        )
        _send_resend(
            to=to,
            subject='NotenHaus: звернення з сайту',
            html=html,
            template_key=EmailTemplateKey.LEAD_CREATED_ADMIN,
            related_type='lead',
            related_id=lead.pk,
        )
    except Exception:  # noqa: BLE001
        logger.exception('notify_lead_created_admin failed')


def notify_order_status_customer(order: Order) -> None:
    try:
        site = SiteSettings.load()
        if not site.notify_customer_on_status:
            return
        html = (
            f'<p>Статус замовлення <strong>{order.number}</strong>: '
            f'{order.get_status_display()}</p>'
        )
        _send_resend(
            to=order.customer_email,
            subject=f'NotenHaus: статус {order.number}',
            html=html,
            template_key=EmailTemplateKey.ORDER_STATUS_CUSTOMER,
            related_type='order',
            related_id=order.pk,
        )
    except Exception:  # noqa: BLE001
        logger.exception('notify_order_status_customer failed')

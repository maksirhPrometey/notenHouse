"""Cabinet services — registration, wishlist toggle, order history (tables.md §10)."""

from __future__ import annotations

from collections import Counter
from typing import Any

from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Q, QuerySet

from src.catalog.models import Instrument, Product
from src.commerce.models import Order, OrderStatus
from src.commerce.services import CartError, add_item

from .models import CustomerProfile, WishlistItem

User = get_user_model()

ACTIVE_ORDER_STATUSES = (
    OrderStatus.NEW,
    OrderStatus.PROCESSING,
    OrderStatus.SHIPPED,
)

# Musical Level — design TZ (no loyalty column in CustomerProfile yet)
LOYALTY_TIERS = (
    {'key': 'pianissimo', 'label': 'Pianissimo', 'min_orders': 0, 'progress': 28},
    {'key': 'mezzo', 'label': 'Mezzo-Forte', 'min_orders': 2, 'progress': 62},
    {'key': 'fortissimo', 'label': 'Fortissimo', 'min_orders': 5, 'progress': 100},
)

STATUS_PILL_MAP = {
    OrderStatus.SHIPPED: ('В дорозі', 'transit'),
    OrderStatus.COMPLETED: ('Доставлено', 'done'),
    OrderStatus.PROCESSING: ('Обробляється', 'processing'),
    OrderStatus.NEW: ('Обробляється', 'processing'),
    OrderStatus.CANCELLED: ('Скасовано', 'cancelled'),
}


@transaction.atomic
def register_user(*, email: str, password: str, display_name: str, phone: str = ''):
    user = User.objects.create_user(username=email, email=email, password=password)
    if display_name:
        user.first_name = display_name[:150]
        user.save(update_fields=['first_name'])
    CustomerProfile.objects.create(user=user, display_name=display_name, phone=phone)
    return user


def user_orders_qs(user) -> QuerySet[Order]:
    return (
        Order.objects.filter(Q(user=user) | Q(customer_email__iexact=user.email))
        .distinct()
        .order_by('-created_at')
    )


def wishlist_product_ids(user) -> set[int]:
    if not user.is_authenticated:
        return set()
    return set(user.wishlist_items.values_list('product_id', flat=True))


def wishlist_products_qs(user):
    from src.catalog import selectors

    ids = wishlist_product_ids(user)
    if not ids:
        return selectors.published_products().none()
    return selectors.published_products().filter(pk__in=ids)


@transaction.atomic
def toggle_wishlist(user, product: Product) -> bool:
    """Add/remove product from wishlist. Returns True if added, False if removed."""
    item, created = WishlistItem.objects.get_or_create(user=user, product=product)
    if not created:
        item.delete()
        return False
    return True


def order_status_pill(order: Order) -> tuple[str, str]:
    return STATUS_PILL_MAP.get(
        order.status,
        (order.get_status_display(), 'processing'),
    )


def loyalty_level(*, order_count: int) -> dict[str, Any]:
    tier = LOYALTY_TIERS[0]
    for candidate in LOYALTY_TIERS:
        if order_count >= candidate['min_orders']:
            tier = candidate
    next_tier = None
    for candidate in LOYALTY_TIERS:
        if candidate['min_orders'] > order_count:
            next_tier = candidate
            break
    return {
        **tier,
        'order_count': order_count,
        'next_label': next_tier['label'] if next_tier else None,
        'orders_to_next': (
            (next_tier['min_orders'] - order_count) if next_tier else 0
        ),
    }


def infer_primary_instrument(user) -> Instrument | None:
    """Most frequent instrument from wishlist + past order items."""
    counts: Counter[int] = Counter()
    wishlist_ids = wishlist_product_ids(user)
    if wishlist_ids:
        for iid in Product.objects.filter(pk__in=wishlist_ids).values_list(
            'instruments', flat=True
        ):
            if iid:
                counts[iid] += 1

    order_ids = user_orders_qs(user).values_list('id', flat=True)
    if order_ids:
        from src.commerce.models import OrderItem

        product_ids = (
            OrderItem.objects.filter(order_id__in=order_ids, product_id__isnull=False)
            .values_list('product_id', flat=True)
            .distinct()
        )
        for iid in Product.objects.filter(pk__in=product_ids).values_list(
            'instruments', flat=True
        ):
            if iid:
                counts[iid] += 2

    if not counts:
        return None
    top_id = counts.most_common(1)[0][0]
    return Instrument.objects.filter(pk=top_id, is_active=True).first()


def recommended_products_for_user(user, *, limit: int = 4):
    from src.catalog import selectors

    instrument = infer_primary_instrument(user)
    exclude_ids = set(wishlist_product_ids(user))
    purchased = (
        user_orders_qs(user)
        .values_list('items__product_id', flat=True)
        .distinct()
    )
    exclude_ids.update(pid for pid in purchased if pid)

    if instrument:
        qs = (
            selectors.filter_catalog(instrument=instrument.slug, sort='new')
            .exclude(pk__in=exclude_ids)
        )
        return list(qs[:limit]), instrument

    qs = selectors.new_products(limit=limit + max(len(exclude_ids), 0))
    products = [p for p in qs if p.pk not in exclude_ids][:limit]
    return products, None


@transaction.atomic
def reorder_to_cart(request, order: Order) -> tuple[int, list[str]]:
    """Add available order line items back to cart. Returns (added_count, errors)."""
    added = 0
    errors: list[str] = []
    for item in order.items.select_related('product'):
        if not item.product_id:
            errors.append(f'{item.product_name}: товар недоступний')
            continue
        try:
            add_item(request, product_id=item.product_id, qty=item.qty)
            added += 1
        except CartError as exc:
            errors.append(f'{item.product_name}: {exc}')
    return added, errors

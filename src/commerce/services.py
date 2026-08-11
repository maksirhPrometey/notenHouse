"""Cart / order mutations — SEC-02 revalidate price, SEC-05 stock F()."""

from __future__ import annotations

from decimal import Decimal

from django.db import transaction
from django.db.models import F
from django.utils import timezone

from django.db.models import Prefetch

from src.catalog.models import Product, ProductImage
from src.notifications.services import notify_order_created_admin

from .models import (
    Cart,
    CartItem,
    CartStatus,
    Order,
    OrderItem,
    OrderStatus,
    OrderStatusLog,
    PaymentProvider,
    PaymentStatus,
    ShippingMethod,
)


class CartError(Exception):
    pass


class OrderError(Exception):
    pass


_CART_MESSAGES = {
    'qty_min': ('Кількість має бути не менше 1', 'Quantity must be at least 1'),
    'not_found': ('Товар не знайдено', 'Product not found'),
    'out_of_stock': ('Недостатньо на складі', 'Out of stock'),
    'item_not_found': ('Позицію не знайдено', 'Item not found'),
    'added': ('Додано до кошика', 'Added to cart'),
}


def request_locale(request) -> str:
    code = getattr(request, 'LANGUAGE_CODE', None) or 'uk'
    return 'en' if str(code).lower().startswith('en') else 'uk'


def cart_message(request, key: str) -> str:
    uk, en = _CART_MESSAGES[key]
    return en if request_locale(request) == 'en' else uk


ALLOWED_TRANSITIONS = {
    OrderStatus.NEW: {OrderStatus.PROCESSING, OrderStatus.CANCELLED},
    OrderStatus.PROCESSING: {OrderStatus.SHIPPED, OrderStatus.CANCELLED},
    OrderStatus.SHIPPED: {OrderStatus.COMPLETED, OrderStatus.CANCELLED},
    OrderStatus.COMPLETED: set(),
    OrderStatus.CANCELLED: set(),
}


def _ensure_session(request) -> str:
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key


def get_or_create_cart(request) -> Cart:
    session_key = _ensure_session(request)
    cart = (
        Cart.objects.filter(session_key=session_key, status=CartStatus.ACTIVE)
        .order_by('-updated_at')
        .first()
    )
    if cart is None:
        cart = Cart.objects.create(session_key=session_key, status=CartStatus.ACTIVE)
    return cart


def cart_items_qs(cart: Cart):
    return (
        cart.items.select_related(
            'product',
            'product__composer',
            'product__format',
        )
        .prefetch_related(
            Prefetch(
                'product__images',
                queryset=ProductImage.objects.filter(is_main=True),
                to_attr='main_images',
            ),
            'product__instruments',
        )
        .order_by('id')
    )


def cart_total(cart: Cart) -> Decimal:
    total = Decimal('0.00')
    for item in cart_items_qs(cart):
        total += item.unit_price_uah * item.qty
    return total


def cart_count(cart: Cart) -> int:
    return sum(i.qty for i in cart_items_qs(cart))


def cart_product_ids(cart: Cart) -> set[int]:
    return set(cart.items.values_list('product_id', flat=True))


@transaction.atomic
def add_item(request, *, product_id: int, qty: int = 1) -> Cart:
    if qty < 1:
        raise CartError(cart_message(request, 'qty_min'))
    product = Product.objects.filter(pk=product_id, is_published=True).first()
    if product is None:
        raise CartError(cart_message(request, 'not_found'))
    if product.stock_qty < qty:
        raise CartError(cart_message(request, 'out_of_stock'))
    cart = get_or_create_cart(request)
    item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={
            'qty': qty,
            'unit_price_uah': product.price_uah,
        },
    )
    if not created:
        new_qty = item.qty + qty
        if product.stock_qty < new_qty:
            raise CartError(cart_message(request, 'out_of_stock'))
        item.qty = new_qty
        item.unit_price_uah = product.price_uah
        item.save(update_fields=['qty', 'unit_price_uah'])
    cart.save(update_fields=['updated_at'])
    return cart


@transaction.atomic
def update_item_qty(request, *, item_id: int, qty: int) -> Cart:
    cart = get_or_create_cart(request)
    item = (
        CartItem.objects.select_related('product')
        .filter(pk=item_id, cart=cart)
        .first()
    )
    if item is None:
        raise CartError(cart_message(request, 'item_not_found'))
    if qty < 1:
        item.delete()
        cart.save(update_fields=['updated_at'])
        return cart
    if item.product.stock_qty < qty:
        raise CartError(cart_message(request, 'out_of_stock'))
    item.qty = qty
    item.unit_price_uah = item.product.price_uah
    item.save(update_fields=['qty', 'unit_price_uah'])
    cart.save(update_fields=['updated_at'])
    return cart


@transaction.atomic
def remove_item(request, *, item_id: int) -> Cart:
    cart = get_or_create_cart(request)
    deleted, _ = CartItem.objects.filter(pk=item_id, cart=cart).delete()
    if not deleted:
        raise CartError(cart_message(request, 'item_not_found'))
    cart.save(update_fields=['updated_at'])
    return cart


def _next_order_number() -> str:
    stamp = timezone.now().strftime('%Y%m%d')
    prefix = f'NH-{stamp}-'
    last = (
        Order.objects.filter(number__startswith=prefix)
        .order_by('-number')
        .values_list('number', flat=True)
        .first()
    )
    seq = 1
    if last:
        try:
            seq = int(last.rsplit('-', 1)[-1]) + 1
        except ValueError:
            seq = 1
    return f'{prefix}{seq:04d}'


@transaction.atomic
def place_order(request, cleaned: dict) -> Order:
    cart = get_or_create_cart(request)
    items = list(
        CartItem.objects.select_for_update()
        .select_related('product')
        .filter(cart=cart)
    )
    if not items:
        raise OrderError('Кошик порожній')

    lines = []
    subtotal = Decimal('0.00')
    for item in items:
        product = (
            Product.objects.select_for_update()
            .filter(pk=item.product_id, is_published=True)
            .first()
        )
        if product is None:
            raise OrderError(f'Товар недоступний: {item.product_id}')
        if product.stock_qty < item.qty:
            raise OrderError(f'Недостатньо на складі: {product.name_uk}')
        live_price = product.price_uah
        line_total = live_price * item.qty
        subtotal += line_total
        lines.append((product, item.qty, live_price, line_total))

    shipping_uah = Decimal('0.00')
    order_user = request.user if getattr(request.user, 'is_authenticated', False) else None
    order = Order.objects.create(
        number=_next_order_number(),
        status=OrderStatus.NEW,
        payment_status=PaymentStatus.AWAITING,
        user=order_user,
        customer_name=cleaned['customer_name'],
        customer_email=cleaned['customer_email'],
        customer_phone=cleaned['customer_phone'],
        customer_comment=cleaned.get('customer_comment', ''),
        shipping_method=cleaned['shipping_method'],
        np_city_ref=cleaned.get('np_city_ref', ''),
        np_city_name=cleaned.get('np_city_name', ''),
        np_warehouse_ref=cleaned.get('np_warehouse_ref', ''),
        np_warehouse_name=cleaned.get('np_warehouse_name', ''),
        np_area_ref=cleaned.get('np_area_ref', ''),
        subtotal_uah=subtotal,
        shipping_uah=shipping_uah,
        total_uah=subtotal + shipping_uah,
        payment_provider=cleaned.get('payment_provider') or PaymentProvider.LIQPAY,
        locale=cleaned.get('locale', 'uk'),
        cart=cart,
    )
    for product, qty, unit_price, line_total in lines:
        OrderItem.objects.create(
            order=order,
            product=product,
            product_sku=product.sku,
            product_name=product.name_uk if order.locale == 'uk' else (
                product.name_en or product.name_uk
            ),
            qty=qty,
            unit_price_uah=unit_price,
            line_total_uah=line_total,
        )
        updated = Product.objects.filter(
            pk=product.pk,
            stock_qty__gte=qty,
        ).update(stock_qty=F('stock_qty') - qty)
        if not updated:
            raise OrderError(f'Недостатньо на складі: {product.name_uk}')

    OrderStatusLog.objects.create(
        order=order,
        from_status='',
        to_status=OrderStatus.NEW,
        note='Замовлення створено',
    )
    cart.status = CartStatus.CONVERTED
    cart.save(update_fields=['status', 'updated_at'])

    notify_order_created_admin(order)
    return order


@transaction.atomic
def change_order_status(order: Order, to_status: str, *, user=None, note: str = '') -> Order:
    if user is not None and not (user.is_staff or user.is_superuser):
        raise OrderError('Немає права змінювати статус')
    allowed = ALLOWED_TRANSITIONS.get(order.status, set())
    if to_status not in allowed:
        raise OrderError(f'Перехід {order.status} → {to_status} заборонено')
    prev = order.status
    order.status = to_status
    order.save(update_fields=['status', 'updated_at'])
    OrderStatusLog.objects.create(
        order=order,
        from_status=prev,
        to_status=to_status,
        note=note,
        actor=user if user and user.is_authenticated else None,
    )
    from src.notifications.services import notify_order_status_customer

    notify_order_status_customer(order)
    return order


@transaction.atomic
def mark_order_paid(order: Order, *, external_id: str = '') -> Order:
    if order.payment_status == PaymentStatus.PAID:
        return order
    prev_status = order.status
    order.payment_status = PaymentStatus.PAID
    order.paid_at = timezone.now()
    if external_id:
        order.payment_external_id = external_id
    update_fields = ['payment_status', 'paid_at', 'payment_external_id', 'updated_at']
    if prev_status == OrderStatus.NEW:
        order.status = OrderStatus.PROCESSING
        update_fields.append('status')
    order.save(update_fields=update_fields)
    OrderStatusLog.objects.create(
        order=order,
        from_status=prev_status,
        to_status='payment:paid',
        note='LiqPay callback',
    )
    if prev_status == OrderStatus.NEW:
        OrderStatusLog.objects.create(
            order=order,
            from_status=OrderStatus.NEW,
            to_status=OrderStatus.PROCESSING,
            note='Авто після оплати',
        )
        from src.notifications.services import notify_order_status_customer

        notify_order_status_customer(order)
    return order


def validate_shipping_fields(cleaned: dict) -> None:
    method = cleaned.get('shipping_method')
    if method in {ShippingMethod.NP_WAREHOUSE, ShippingMethod.NP_POSHTOMAT}:
        if not cleaned.get('np_city_ref') or not cleaned.get('np_warehouse_ref'):
            raise OrderError('Оберіть місто та відділення Нової Пошти')

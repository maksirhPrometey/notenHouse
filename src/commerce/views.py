"""Commerce views: cart, checkout, thank-you, payment retry."""

from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View
from django.views.generic import FormView, TemplateView

from src.content.models import CartPageSettings
from src.payments.services import PaymentError, build_checkout_form

from .forms import CheckoutForm
from .models import Order, PaymentProvider, PaymentStatus, ShippingMethod
from .services import (
    CartError,
    OrderError,
    add_item,
    cart_count,
    cart_items_qs,
    cart_message,
    cart_total,
    get_or_create_cart,
    place_order,
    remove_item,
    update_item_qty,
    validate_shipping_fields,
)


def cart_page_context(request) -> dict:
    cart = get_or_create_cart(request)
    items = list(cart_items_qs(cart))
    settings = CartPageSettings.load()
    cart_product_ids = {item.product_id for item in items}
    recommended = [
        p
        for p in settings.get_recommended_products()
        if p.id not in cart_product_ids
    ]
    cross_sell = [
        p
        for p in settings.get_cross_sell_products()
        if p.id not in cart_product_ids
    ]
    return {
        'page_title': 'Кошик',
        'cart': cart,
        'items': items,
        'total': cart_total(cart),
        'items_qty': sum(item.qty for item in items),
        'cart_settings': settings,
        'recommended_products': recommended,
        'cross_sell_products': cross_sell,
        'trust_badges': list(settings.active_trust_badges()),
        'breadcrumbs': [
            ('Головна', reverse('core:home')),
            ('Кошик', None),
        ],
    }


def render_cart_partial(request):
    ctx = cart_page_context(request)
    ctx['cart_count'] = cart_count(ctx['cart'])
    return render(request, 'commerce/partials/cart_htmx.html', ctx)


class CartDetailView(TemplateView):
    template_name = 'commerce/cart.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(cart_page_context(self.request))
        return ctx


class CartAddView(View):
    def post(self, request, product_id: int):
        qty = int(request.POST.get('qty') or 1)
        added_ok = False
        toast_text = ''
        toast_level = 'info'
        try:
            add_item(request, product_id=product_id, qty=qty)
            toast_text = cart_message(request, 'added')
            toast_level = 'success'
            messages.success(request, toast_text)
            added_ok = True
        except CartError as exc:
            toast_text = str(exc)
            toast_level = 'error'
            messages.error(request, toast_text)
        if request.htmx:
            if request.POST.get('refresh_cart') == '1':
                return render_cart_partial(request)
            cart = get_or_create_cart(request)
            ctx = {
                'cart_count': cart_count(cart),
                'product_id': product_id,
                'wrapper_class': request.POST.get(
                    'wrapper_class', 'product-card__cart-form'
                ),
                'btn_class': request.POST.get('btn_class', 'product-card__btn'),
                'toast_text': toast_text,
                'toast_level': toast_level,
            }
            if added_ok:
                return render(
                    request,
                    'commerce/partials/cart_add_response.html',
                    ctx,
                )
            error_response = render(
                request,
                'commerce/partials/cart_add_error_response.html',
                ctx,
            )
            error_response['HX-Reswap'] = 'none'
            return error_response
        next_url = request.POST.get('next') or reverse('commerce:cart')
        return redirect(next_url)


class CartUpdateView(View):
    def post(self, request, item_id: int):
        qty = int(request.POST.get('qty') or 1)
        try:
            update_item_qty(request, item_id=item_id, qty=qty)
        except CartError as exc:
            messages.error(request, str(exc))
        if request.htmx:
            return render_cart_partial(request)
        return redirect('commerce:cart')


class CartRemoveView(View):
    def post(self, request, item_id: int):
        try:
            remove_item(request, item_id=item_id)
        except CartError as exc:
            messages.error(request, str(exc))
        if request.htmx:
            return render_cart_partial(request)
        return redirect('commerce:cart')


class CheckoutView(FormView):
    template_name = 'commerce/checkout.html'
    form_class = CheckoutForm

    def dispatch(self, request, *args, **kwargs):
        cart = get_or_create_cart(request)
        if not cart_items_qs(cart).exists():
            locale = getattr(request, 'LANGUAGE_CODE', 'uk') or 'uk'
            messages.info(
                request,
                'Cart is empty' if locale == 'en' else 'Кошик порожній',
            )
            return redirect('commerce:cart')
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['locale'] = getattr(self.request, 'LANGUAGE_CODE', 'uk') or 'uk'
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        user = self.request.user
        if user.is_authenticated:
            profile = getattr(user, 'cabinet_profile', None)
            display_name = (profile.display_name if profile else '') or user.get_full_name()
            if display_name:
                initial.setdefault('customer_name', display_name)
            initial.setdefault('customer_email', user.email)
            if profile and profile.phone:
                initial.setdefault('customer_phone', profile.phone)
        return initial

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        cart = get_or_create_cart(self.request)
        locale = getattr(self.request, 'LANGUAGE_CODE', 'uk') or 'uk'
        from src.content.site_blocks import get_block_text

        page_title = get_block_text('checkout', 'title', locale=locale)
        home = 'Home' if locale == 'en' else 'Головна'
        cart_label = get_block_text('cart', 'title', locale=locale)
        checkout_short = 'Checkout' if locale == 'en' else 'Оформлення'
        items = list(cart_items_qs(cart))
        for item in items:
            item.line_total = item.unit_price_uah * item.qty

        user = self.request.user
        logged_in_label = ''
        if user.is_authenticated:
            profile = getattr(user, 'cabinet_profile', None)
            display = (profile.display_name if profile else '') or user.get_full_name() or user.email
            if locale == 'en':
                logged_in_label = f'Signed in as {display}'
                if user.email and user.email not in display:
                    logged_in_label = f'Signed in as {display} ({user.email})'
            else:
                logged_in_label = f'Ви увійшли як {display}'
                if user.email and user.email not in display:
                    logged_in_label = f'Ви увійшли як {display} ({user.email})'

        form = ctx.get('form')
        shipping_hints = getattr(form, 'shipping_hints', {}) if form else {}
        selected_shipping = ''
        shipping_options = []
        payment_options = []
        if form:
            selected_shipping = form['shipping_method'].value() or ''
            ship_choices = list(form.fields['shipping_method'].choices)
            default_ship = ship_choices[0][0] if ship_choices else ''
            pickup_hint = get_block_text('checkout', 'pickup_hint', locale=locale)
            for value, label in ship_choices:
                hint = shipping_hints.get(value, '')
                if value == ShippingMethod.PICKUP:
                    hint = pickup_hint or hint
                shipping_options.append(
                    {
                        'value': value,
                        'label': label,
                        'hint': hint,
                        'selected': selected_shipping == value
                        or (not selected_shipping and value == default_ship),
                    }
                )
            selected_pay = form['payment_provider'].value() or ''
            pay_choices = list(form.fields['payment_provider'].choices)
            default_pay = pay_choices[0][0] if pay_choices else PaymentProvider.LIQPAY
            for value, _label in pay_choices:
                payment_options.append(
                    {
                        'value': value,
                        'selected': selected_pay == value
                        or (not selected_pay and value == default_pay),
                    }
                )

        def _methods_grid(count: int) -> str:
            grid = 'checkout-methods__grid'
            if count == 1:
                return f'{grid} checkout-methods__grid--single'
            if count >= 3:
                return f'{grid} checkout-methods__grid--triple'
            return grid

        from src.content.contacts_defaults import merge_contacts
        from src.content.models import SiteSettings

        site = SiteSettings.load()
        contacts = merge_contacts(site.contacts_json)
        pickup_selected = any(
            opt['selected'] and opt['value'] == ShippingMethod.PICKUP
            for opt in shipping_options
        )

        ctx.update(
            {
                'page_title': page_title,
                'items': items,
                'total': cart_total(cart),
                'logged_in_label': logged_in_label,
                'shipping_options': shipping_options,
                'payment_options': payment_options,
                'shipping_methods_grid_class': _methods_grid(len(shipping_options)),
                'payment_methods_grid_class': _methods_grid(len(payment_options)),
                'pickup_address': contacts.get('address') or '',
                'pickup_selected': pickup_selected,
                'breadcrumbs': [
                    (home, reverse('core:home')),
                    (cart_label, reverse('commerce:cart')),
                    (checkout_short, None),
                ],
            }
        )
        return ctx

    def form_valid(self, form):
        cleaned = form.cleaned_data.copy()
        cleaned['locale'] = getattr(self.request, 'LANGUAGE_CODE', 'uk')[:2] or 'uk'
        if cleaned.get('shipping_method') == ShippingMethod.PICKUP:
            cleaned.update(
                {
                    'np_city_ref': '',
                    'np_city_name': '',
                    'np_warehouse_ref': '',
                    'np_warehouse_name': '',
                    'np_area_ref': '',
                }
            )
        try:
            validate_shipping_fields(cleaned)
            order = place_order(self.request, cleaned)
        except OrderError as exc:
            form.add_error(None, str(exc))
            return self.form_invalid(form)

        if order.payment_provider != PaymentProvider.LIQPAY:
            return redirect(
                reverse('commerce:thank_you') + f'?order={order.number}'
            )

        try:
            pay = build_checkout_form(order, self.request)
        except PaymentError:
            messages.warning(
                self.request,
                'Замовлення створено. Оплату буде доступно після налаштування LiqPay.',
            )
            return redirect(
                reverse('commerce:payment_retry') + f'?order={order.number}'
            )
        return render(
            self.request,
            'commerce/liqpay_redirect.html',
            {'page_title': 'Перехід до оплати', 'order': order, 'pay': pay},
        )


class ThankYouView(TemplateView):
    template_name = 'commerce/thank_you.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        number = self.request.GET.get('order', '')
        order = Order.objects.filter(number=number).first()
        from src.content.models import SiteSettings
        from src.content.site_blocks import get_block_text
        from .payment_options import format_iban_purpose

        locale = getattr(self.request, 'LANGUAGE_CODE', 'uk') or 'uk'
        page_title = get_block_text('thank_you', 'title', locale=locale)
        iban_details = None
        if order and order.payment_provider == PaymentProvider.IBAN:
            site = SiteSettings.load()
            purpose = format_iban_purpose(site.payment_iban_purpose, order.number)
            iban_details = {
                'recipient': site.payment_iban_recipient,
                'iban': site.payment_iban,
                'edrpou': site.payment_iban_edrpou,
                'bank': site.payment_iban_bank,
                'purpose': purpose,
                'has_requisites': bool(
                    site.payment_iban or site.payment_iban_recipient
                ),
            }
        ctx.update(
            {
                'page_title': page_title,
                'order': order,
                'iban_details': iban_details,
                'is_cod': bool(
                    order and order.payment_provider == PaymentProvider.COD
                ),
                'is_iban': bool(
                    order and order.payment_provider == PaymentProvider.IBAN
                ),
            }
        )
        return ctx


class PaymentRetryView(TemplateView):
    template_name = 'commerce/payment_retry.html'

    def get(self, request, *args, **kwargs):
        number = request.GET.get('order', '')
        order = get_object_or_404(Order, number=number)
        if order.payment_status == PaymentStatus.PAID:
            return redirect(reverse('commerce:thank_you') + f'?order={order.number}')
        if order.payment_provider != PaymentProvider.LIQPAY:
            return redirect(reverse('commerce:thank_you') + f'?order={order.number}')
        ctx = {
            'page_title': 'Очікує оплати',
            'order': order,
            'pay': None,
        }
        try:
            ctx['pay'] = build_checkout_form(order, request)
        except PaymentError:
            pass
        return render(request, self.template_name, ctx)

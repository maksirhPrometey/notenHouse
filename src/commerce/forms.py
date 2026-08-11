from django import forms

from .models import PaymentProvider
from .payment_options import (
    payment_choice_tuples,
    shipping_choice_tuples,
    shipping_hints_map,
)

CHECKOUT_LABELS = {
    'uk': {
        'customer_name': 'Імʼя',
        'customer_email': 'Email',
        'customer_phone': 'Телефон',
        'customer_comment': 'Коментар до замовлення',
        'shipping_method': 'Спосіб доставки',
        'np_city_name': 'Місто',
        'np_warehouse_name': 'Відділення / поштомат',
        'phone_invalid': 'Введіть коректний номер телефону',
    },
    'en': {
        'customer_name': 'Name',
        'customer_email': 'Email',
        'customer_phone': 'Phone',
        'customer_comment': 'Order comment',
        'shipping_method': 'Shipping method',
        'np_city_name': 'City',
        'np_warehouse_name': 'Branch / parcel locker',
        'phone_invalid': 'Enter a valid phone number',
    },
}


class CheckoutForm(forms.Form):
    customer_name = forms.CharField(label='Імʼя', max_length=255)
    customer_email = forms.EmailField(label='Email')
    customer_phone = forms.RegexField(
        label='Телефон',
        regex=r'^\+?[0-9\s\-]{10,20}$',
        max_length=32,
        error_messages={'invalid': 'Введіть коректний номер телефону'},
    )
    customer_comment = forms.CharField(
        label='Коментар',
        required=False,
        widget=forms.Textarea(attrs={'rows': 3}),
    )
    shipping_method = forms.ChoiceField(
        label='Доставка',
        choices=[],
        widget=forms.RadioSelect,
    )
    np_city_ref = forms.CharField(required=False, widget=forms.HiddenInput)
    np_city_name = forms.CharField(required=False, widget=forms.HiddenInput)
    np_warehouse_ref = forms.CharField(required=False, widget=forms.HiddenInput)
    np_warehouse_name = forms.CharField(required=False, widget=forms.HiddenInput)
    np_area_ref = forms.CharField(required=False, widget=forms.HiddenInput)
    payment_provider = forms.ChoiceField(
        label='Оплата',
        choices=[],
        widget=forms.RadioSelect,
        initial=PaymentProvider.LIQPAY,
    )

    def __init__(self, *args, locale: str = 'uk', **kwargs):
        super().__init__(*args, **kwargs)
        lang = 'en' if locale == 'en' else 'uk'
        labels = CHECKOUT_LABELS[lang]
        for key in (
            'customer_name',
            'customer_email',
            'customer_phone',
            'customer_comment',
            'shipping_method',
        ):
            self.fields[key].label = labels[key]
        self.fields['customer_phone'].error_messages['invalid'] = labels['phone_invalid']
        ship_choices = shipping_choice_tuples(locale=locale)
        self.fields['shipping_method'].choices = ship_choices
        hints = shipping_hints_map(locale=locale)
        self.shipping_hints = {value: hints.get(value, '') for value, _ in ship_choices}
        if ship_choices and not self.is_bound:
            self.fields['shipping_method'].initial = ship_choices[0][0]
        pay_choices = payment_choice_tuples(locale=locale)
        self.fields['payment_provider'].choices = pay_choices
        self.fields['payment_provider'].label = (
            'Payment method' if lang == 'en' else 'Спосіб оплати'
        )
        if pay_choices and not self.is_bound:
            self.fields['payment_provider'].initial = pay_choices[0][0]
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.HiddenInput):
                continue
            if name in {'shipping_method', 'payment_provider'}:
                continue
            css = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f'{css} form-control checkout-input'.strip()
            field.widget.attrs.setdefault('autocomplete', _autocomplete_for(name))


def _autocomplete_for(name: str) -> str:
    return {
        'customer_name': 'name',
        'customer_email': 'email',
        'customer_phone': 'tel',
        'np_city_name': 'address-level2',
        'np_warehouse_name': 'off',
        'customer_comment': 'off',
    }.get(name, 'on')

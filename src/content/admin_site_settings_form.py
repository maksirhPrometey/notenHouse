"""Friendly SiteSettings admin form (no raw JSON editing)."""

from __future__ import annotations

from django import forms

from .admin_site_content_widgets import CmsAdminTextareaWidget, CmsAdminTextInputWidget
from .contacts_defaults import merge_contacts
from .models import SiteSettings

SCHEDULE_DAY_CHOICES = (
    (1, 'Пн'),
    (2, 'Вт'),
    (3, 'Ср'),
    (4, 'Чт'),
    (5, 'Пт'),
    (6, 'Сб'),
    (7, 'Нд'),
)

_TIME_HELP = 'Формат HH:MM, напр. 10:00'


class SiteSettingsAdminForm(forms.ModelForm):
    phones = forms.CharField(
        label='Телефони',
        required=True,
        widget=CmsAdminTextareaWidget(attrs={'rows': 3}),
        help_text='Один номер на рядок (E.164, напр. +380441112233).',
    )
    phone_display = forms.CharField(
        label='Телефон (відображення)',
        required=False,
        max_length=64,
        widget=CmsAdminTextInputWidget(),
        help_text='Як показувати на вітрині, напр. +380 44 111 22 33.',
    )
    email = forms.EmailField(
        label='Email',
        required=True,
        widget=CmsAdminTextInputWidget(),
    )
    email_response = forms.CharField(
        label='Відповідь по email',
        required=False,
        max_length=255,
        widget=CmsAdminTextInputWidget(),
        help_text='Підпис під email, напр. «Відповідаємо протягом 15 хвилин».',
    )
    hours = forms.CharField(
        label='Години (текст)',
        required=False,
        max_length=120,
        widget=CmsAdminTextInputWidget(),
        help_text='Текст для картки, напр. Пн–Пт 10:00–18:00.',
    )
    address = forms.CharField(
        label='Адреса',
        required=False,
        max_length=255,
        widget=CmsAdminTextInputWidget(),
    )
    maps_url = forms.CharField(
        label='Google Maps URL',
        required=False,
        max_length=512,
        widget=CmsAdminTextInputWidget(),
    )
    viber = forms.CharField(
        label='Viber',
        required=False,
        max_length=255,
        widget=CmsAdminTextInputWidget(),
        help_text='viber://chat?number=%2B380…',
    )
    telegram = forms.CharField(
        label='Telegram',
        required=False,
        max_length=255,
        widget=CmsAdminTextInputWidget(),
        help_text='https://t.me/…',
    )
    schedule_timezone = forms.CharField(
        label='Часовий пояс',
        required=True,
        max_length=64,
        widget=CmsAdminTextInputWidget(),
        help_text='IANA, напр. Europe/Kyiv.',
    )
    schedule_days = forms.TypedMultipleChoiceField(
        label='Робочі дні',
        required=False,
        coerce=int,
        choices=SCHEDULE_DAY_CHOICES,
        widget=forms.CheckboxSelectMultiple,
    )
    schedule_open = forms.RegexField(
        label='Відкриття',
        required=True,
        regex=r'^\d{1,2}:\d{2}$',
        widget=CmsAdminTextInputWidget(),
        help_text=_TIME_HELP,
        error_messages={'invalid': 'Вкажіть час у форматі HH:MM.'},
    )
    schedule_close = forms.RegexField(
        label='Закриття',
        required=True,
        regex=r'^\d{1,2}:\d{2}$',
        widget=CmsAdminTextInputWidget(),
        help_text=_TIME_HELP,
        error_messages={'invalid': 'Вкажіть час у форматі HH:MM.'},
    )

    class Meta:
        model = SiteSettings
        fields = (
            'site_name',
            'logo',
            'admin_notify_email',
            'default_locale',
            'shipping_show_pickup',
            'shipping_show_payment_cod',
            'shipping_show_payment_iban',
            'payment_iban_recipient',
            'payment_iban',
            'payment_iban_edrpou',
            'payment_iban_bank',
            'payment_iban_purpose',
            'notify_customer_on_status',
            'robots_txt',
        )

    def __init__(self, *args, **kwargs):
        from .image_specs import LOGO

        super().__init__(*args, **kwargs)
        if 'logo' in self.fields:
            self.fields['logo'].help_text = LOGO.help_text
        contacts = merge_contacts(
            self.instance.contacts_json if self.instance and self.instance.pk else None,
        )
        schedule = contacts.get('schedule') or {}
        if not self.is_bound:
            phones = contacts.get('phones') or []
            self.fields['phones'].initial = '\n'.join(str(p) for p in phones if p)
            self.fields['phone_display'].initial = contacts.get('phone_display') or ''
            self.fields['email'].initial = contacts.get('email') or ''
            self.fields['email_response'].initial = contacts.get('email_response') or ''
            self.fields['hours'].initial = contacts.get('hours') or ''
            self.fields['address'].initial = contacts.get('address') or ''
            self.fields['maps_url'].initial = contacts.get('maps_url') or ''
            self.fields['viber'].initial = contacts.get('viber') or ''
            self.fields['telegram'].initial = contacts.get('telegram') or ''
            self.fields['schedule_timezone'].initial = schedule.get('timezone') or 'Europe/Kyiv'
            days = schedule.get('days') or []
            self.fields['schedule_days'].initial = [
                int(d) for d in days if str(d).isdigit()
            ]
            self.fields['schedule_open'].initial = schedule.get('open') or '10:00'
            self.fields['schedule_close'].initial = schedule.get('close') or '18:00'

    def clean_phones(self) -> list[str]:
        raw = self.cleaned_data.get('phones') or ''
        phones = [line.strip() for line in raw.splitlines() if line.strip()]
        if not phones:
            raise forms.ValidationError('Додайте хоча б один телефон.')
        return phones

    def _build_contacts_json(self) -> dict:
        phones = self.cleaned_data['phones']
        phone_display = (self.cleaned_data.get('phone_display') or '').strip()
        if not phone_display and phones:
            phone_display = phones[0]
        days = sorted({int(d) for d in (self.cleaned_data.get('schedule_days') or [])})
        return {
            'phones': phones,
            'phone_display': phone_display,
            'email': (self.cleaned_data.get('email') or '').strip(),
            'email_response': (self.cleaned_data.get('email_response') or '').strip(),
            'hours': (self.cleaned_data.get('hours') or '').strip(),
            'address': (self.cleaned_data.get('address') or '').strip(),
            'maps_url': (self.cleaned_data.get('maps_url') or '').strip(),
            'viber': (self.cleaned_data.get('viber') or '').strip(),
            'telegram': (self.cleaned_data.get('telegram') or '').strip(),
            'schedule': {
                'timezone': (self.cleaned_data.get('schedule_timezone') or '').strip(),
                'days': days,
                'open': (self.cleaned_data.get('schedule_open') or '').strip(),
                'close': (self.cleaned_data.get('schedule_close') or '').strip(),
            },
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.contacts_json = self._build_contacts_json()
        if commit:
            instance.save()
            self.save_m2m()
        return instance

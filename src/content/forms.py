from django import forms

from .models import ContactTopic

CONTACT_TOPIC_LABELS = {
    'uk': {
        ContactTopic.ORDER: 'Питання по замовленню',
        ContactTopic.SHEET: 'Пошук нот',
    },
    'en': {
        ContactTopic.ORDER: 'Order inquiry',
        ContactTopic.SHEET: 'Sheet music search',
    },
}

FORM_LABELS = {
    'uk': {
        'topic': 'Тема',
        'name': 'Імʼя',
        'phone': 'Телефон',
        'email': 'Email',
        'message': 'Повідомлення',
        'phone_invalid': 'Введіть коректний номер телефону',
    },
    'en': {
        'topic': 'Topic',
        'name': 'Name',
        'phone': 'Phone',
        'email': 'Email',
        'message': 'Message',
        'phone_invalid': 'Enter a valid phone number',
    },
}


class ContactLeadForm(forms.Form):
    topic = forms.ChoiceField(
        label='Тема',
        choices=ContactTopic.choices,
        required=False,
        widget=forms.RadioSelect,
    )
    name = forms.CharField(label='Імʼя', max_length=255, required=False)
    phone = forms.RegexField(
        label='Телефон',
        regex=r'^\+?[0-9\s\-]{10,20}$',
        max_length=32,
        error_messages={'invalid': 'Введіть коректний номер телефону'},
    )
    email = forms.EmailField(label='Email', required=False)
    message = forms.CharField(
        label='Повідомлення',
        required=False,
        widget=forms.Textarea(attrs={'rows': 4}),
    )

    def __init__(self, *args, locale: str = 'uk', **kwargs):
        super().__init__(*args, **kwargs)
        lang = 'en' if locale == 'en' else 'uk'
        labels = FORM_LABELS[lang]
        topics = CONTACT_TOPIC_LABELS[lang]
        self.fields['topic'].label = labels['topic']
        self.fields['topic'].choices = [
            (value, topics[value]) for value, _ in ContactTopic.choices
        ]
        self.fields['name'].label = labels['name']
        self.fields['phone'].label = labels['phone']
        self.fields['phone'].error_messages['invalid'] = labels['phone_invalid']
        self.fields['email'].label = labels['email']
        self.fields['message'].label = labels['message']

        floating = ('name', 'phone', 'email', 'message')
        for name, field in self.fields.items():
            css = field.widget.attrs.get('class', '')
            if name in floating:
                field.widget.attrs['class'] = f'{css} contacts-input'.strip()
                field.widget.attrs['placeholder'] = ' '
                field.widget.attrs['autocomplete'] = {
                    'name': 'name',
                    'phone': 'tel',
                    'email': 'email',
                    'message': 'off',
                }.get(name, 'off')
            if name == 'phone':
                field.widget.attrs['inputmode'] = 'tel'
            if name == 'message':
                field.widget.attrs['rows'] = 4

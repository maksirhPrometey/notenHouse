from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import CustomerProfile

User = get_user_model()


class RegisterForm(forms.Form):
    display_name = forms.CharField(label='Імʼя', max_length=255)
    email = forms.EmailField(label='Email')
    phone = forms.RegexField(
        label='Телефон',
        regex=r'^\+?[0-9\s\-]{10,20}$',
        max_length=32,
        required=False,
        error_messages={'invalid': 'Введіть коректний номер телефону'},
    )
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Повторіть пароль', widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f'{css} form-control'.strip()

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError('Користувач з таким email вже зареєстрований')
        return email

    def clean_password1(self):
        password = self.cleaned_data.get('password1', '')
        validate_password(password)
        return password

    def clean(self):
        cleaned = super().clean()
        p1, p2 = cleaned.get('password1'), cleaned.get('password2')
        if p1 and p2 and p1 != p2:
            self.add_error('password2', 'Паролі не збігаються')
        return cleaned


class CabinetAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'autofocus': True}),
    )

    error_messages = {
        **AuthenticationForm.error_messages,
        'invalid_login': 'Невірний email або пароль.',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f'{css} form-control'.strip()


class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomerProfile
        fields = ['display_name', 'phone']
        labels = {'display_name': 'Імʼя', 'phone': 'Телефон'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['phone'].required = False
        self.fields['phone'].widget.attrs['pattern'] = r'^\+?[0-9\s\-]{10,20}$'
        for field in self.fields.values():
            css = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f'{css} form-control'.strip()

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0011_remove_reserved_page_stubs'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sitesettings',
            name='shipping_show_payment_cod',
            field=models.BooleanField(
                default=False,
                help_text='Картка на /dostavka-i-oplata/ і варіант у checkout.',
                verbose_name='Оплата: показувати накладений платіж',
            ),
        ),
        migrations.AlterField(
            model_name='sitesettings',
            name='shipping_show_payment_iban',
            field=models.BooleanField(
                default=False,
                help_text='Картка на /dostavka-i-oplata/ і варіант у checkout.',
                verbose_name='Оплата: показувати IBAN / ФОП',
            ),
        ),
        migrations.AddField(
            model_name='sitesettings',
            name='payment_iban_recipient',
            field=models.CharField(
                blank=True,
                default='',
                max_length=255,
                verbose_name='Отримувач (ФОП / ТОВ)',
            ),
        ),
        migrations.AddField(
            model_name='sitesettings',
            name='payment_iban',
            field=models.CharField(
                blank=True,
                default='',
                help_text='UA + 27 цифр.',
                max_length=34,
                verbose_name='IBAN',
            ),
        ),
        migrations.AddField(
            model_name='sitesettings',
            name='payment_iban_edrpou',
            field=models.CharField(
                blank=True,
                default='',
                max_length=20,
                verbose_name='ЄДРПОУ / ІПН',
            ),
        ),
        migrations.AddField(
            model_name='sitesettings',
            name='payment_iban_bank',
            field=models.CharField(
                blank=True,
                default='',
                max_length=255,
                verbose_name='Банк',
            ),
        ),
        migrations.AddField(
            model_name='sitesettings',
            name='payment_iban_purpose',
            field=models.CharField(
                blank=True,
                default='Оплата замовлення {order}',
                help_text='Плейсхолдер {order} замінюється на номер замовлення.',
                max_length=255,
                verbose_name='Призначення платежу',
            ),
        ),
    ]

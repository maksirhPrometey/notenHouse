from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0012_site_settings_payment_iban_and_help'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sitesettings',
            name='shipping_show_pickup',
            field=models.BooleanField(
                default=False,
                help_text='Картка на /dostavka-i-oplata/ і варіант у checkout.',
                verbose_name='Доставка: показувати самовивіз',
            ),
        ),
    ]

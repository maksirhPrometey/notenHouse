from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('commerce', '0002_order_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='payment_provider',
            field=models.CharField(
                choices=[
                    ('liqpay', 'LiqPay'),
                    ('cod', 'Накладений платіж'),
                    ('iban', 'IBAN / ФОП'),
                ],
                default='liqpay',
                max_length=20,
                verbose_name='Провайдер',
            ),
        ),
    ]

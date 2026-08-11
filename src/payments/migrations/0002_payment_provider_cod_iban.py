from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paymentevent',
            name='provider',
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
